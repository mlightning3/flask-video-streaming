import time
import io
import threading
import cv2
import numpy as np


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

    def get_frame(self, mode):
        Camera.last_access = time.time()
        self.initialize()
        if mode == 0:
            tmp = cv2.imencode('.jpeg', self.frame)[1].tostring()
        elif mode == 1:
            img_np = self.frame
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

#=========================
#    Video Settings      
#=========================

#CV_CAP_PROP_FRAME_WIDTH Width of the frames in the video stream.
#CV_CAP_PROP_FRAME_HEIGHT Height of the frames in the video stream.
#CV_CAP_PROP_FPS Frame rate

        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        camera.set(cv2.CAP_PROP_FPS, 30)
        while(True):
            ret, frame = camera.read()
                # store frame
                #stream.seek(0)
            cls.frame = frame#cv2.imencode('.jpeg',frame)[1].tostring()
                # reset stream for next frame
                #stream.seek(0)
                #stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
            if time.time() - cls.last_access > 1:
                break
        cls.thread = None
