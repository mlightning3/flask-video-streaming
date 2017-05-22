import time
import io
import threading
import picamera
from picamera.array import PiRGBArray
import numpy as np
import cv2

#Mode is the camera mode
mode = 0

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

#==========================================#
#   This part determines what is sent to   #
#   the web browser, so filter here        #
#==========================================#

    def get_frame(self, mode):
        if mode == 0:
            Camera.last_access = time.time()
            self.initialize()
            return self.frame
        elif mode == 1: 
            #Checks last camera access, and initializes the camera (if it's not already running)
            Camera.last_access = time.time()
            self.initialize()
            
            #Convert the image from bytestream to numpy array, might be able to make this more efficient...
            tmp = np.fromstring(self.frame, np.uint8)
            img_np = cv2.imdecode(tmp,cv2.IMREAD_COLOR)


            #Red Filter Code
            hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
            lower_red = np.array([0,50,50])
            upper_red = np.array([10,255,255])
            mask0 = cv2.inRange(hsv, lower_red, upper_red)

            lower_red = np.array([160,50,50])
            upper_red = np.array([180,255,255])
            mask1 = cv2.inRange(hsv, lower_red, upper_red)
            mask = mask0 + mask1

            # Bitwise-AND mask and original image
            res = cv2.bitwise_and(img_np, img_np, mask = mask) #didn't work until I changed frame to image


            #Re-encode the numpy array as a bitstream and output it.
            tmp = cv2.imencode('.jpg',res)[1].tostring()
        
            return tmp

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = False

            # let camera warm up
        #    camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                cls.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 1:
                    break
        cls.thread = None
