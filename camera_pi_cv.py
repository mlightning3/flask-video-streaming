import time
import io
import threading
import picamera
from picamera.array import PiRGBArray
import numpy as np
import cv2
import queue

# Mode is the camera mode
mode = 0


class Camera(object):
    thread = None  # background thread that reads frames from camera
    watcher = None # Thread for writing video
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    filename = 'default';  # filename of any saved pictures or video
    grayscale = False  # setting grayscale on or not
    low_resolution = False  # # setting low resolution or not
    status = False
    prev_status = False
    buff = queue.Queue()
    writers = queue.Queue()
    ontime = 0
    totaltime = 0

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    # ==========================================#
    #   This part determines what is sent to   #
    #   the web browser, so filter here        #
    # ==========================================#

    def get_frame(self, mode=0):
        if mode == 0:
            Camera.last_access = time.time()
            self.initialize()
            return cv2.imencode('.jpg', self.frame)[1].tostring()
        elif mode == 1:
            # Checks last camera access, and initializes the camera (if it's not already running)
            Camera.last_access = time.time()
            self.initialize()

            # Convert the image from bytestream to numpy array, might be able to make this more efficient...
            tmp = np.fromstring(self.frame, np.uint8)
            img_np = cv2.imdecode(tmp, cv2.IMREAD_COLOR)

            # Red Filter Code
            hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
            lower_red = np.array([0, 50, 50])
            upper_red = np.array([10, 255, 255])
            mask0 = cv2.inRange(hsv, lower_red, upper_red)

            lower_red = np.array([160, 50, 50])
            upper_red = np.array([180, 255, 255])
            mask1 = cv2.inRange(hsv, lower_red, upper_red)
            mask = mask0 + mask1

            # Bitwise-AND mask and original image
            res = cv2.bitwise_and(img_np, img_np, mask=mask)  # didn't work until I changed frame to image

            # Re-encode the numpy array as a bitstream and output it.
            tmp = cv2.imencode('.jpg', res)[1].tostring()

            return tmp

    def take_snapshot(self, filename):
        try:
            cv2.imwrite('./media/' + filename + ".jpg", self.frame)
            return 200
        except Exception as e:
            print(str(e))
            return 500

    def take_video(self, filename, status):
        if (status == "false" or status == False):
            Camera.prev_status = False
            Camera.status = True
            Camera.ontime = time.time()
        else:
            Camera.prev_status = True
            Camera.status = False
            Camera.totaltime = time.time() - Camera.ontime
        Camera.filename = filename

    def set_grayscale(self, status):
        if (status == "false" or status == False):
            Camera.grayscale = True
        if (status == "true" or status == True):
            Camera.grayscale = False
        return 200

    def drop_resolution(self, status):
        if (status == "false" or status == False):
            Camera.low_resolution = True
        if (status == "true" or status == True):
            Camera.low_resolution = False
        return 200

    # Where we get any desired action for an OpenCV action
    # @param payload The string for the desired payload to do something with
    # @param args A dictionary of all the keys and values sent in the query request (anything after the ? in the url like ?status=true&name=pi)
    def opencv(self, payload, args):
        # TODO: Fill out with OpenCV things
        # Until then, just return Not Found to everything
        return 404

    # =========================
    # Video writing thread
    #
    # This takes the frames made by the other thread to write a video with a constant framerate
    # Writes the buffer to file, then ends itself
    #
    # frames - Number of frames captured
    # runtime - Amount of time spent recording
    # fbuffer - Queue with buffer of frames that were recorded
    # =========================
    @classmethod
    def _watcher(cls, frames, runtime, fbuffer):
        fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
        fps = frames / runtime
        video = cv2.VideoWriter('./media/' + cls.filename + '.avi', fourcc, fps, (320, 240))
        while fbuffer.empty() == False:
            video.write(fbuffer.get())
        video.release()

    # =========================
    # Video capture thread
    #
    # This takes frames off of the camera and places it in frame
    # =========================
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

            fcount = 0

            rawImage = PiRGBArray(camera, size=(320,240))
            for frame in camera.capture_continuous(rawImage, format="bgr", use_video_port=True):
                # store frame
                image = frame.array
                tosave = image # keep a copy of the unedited image for saving video
                if (cls.low_resolution == True):
                    image = cv2.resize(image, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA)  # Resizes the image
                if (cls.grayscale == True):
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                cls.frame = image
                if cls.status == True:
                    cls.buff.put(tosave)
                    fcount = fcount + 1
                elif cls.status == False and cls.prev_status == True:
                    temp = threading.Thread(target=cls._watcher, args=(fcount, cls.totaltime, cls.buff))
                    temp.start()
                    cls.writers.put(temp)
                    cls.buff = queue.Queue()
                    fcount = 0
                    cls.prev_status = False

                # reset stream for next frame
                rawImage.truncate(0)

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 1:
                    break
        cls.thread = None
