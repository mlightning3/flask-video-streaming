import time
import io
import threading
import cv2
import numpy as np

avg = np.repeat(0.0, 100)


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

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return cv2.imencode('.jpeg', self.frame)[1].tostring()

    def take_snapshot(self, filename):
        try:
            cv2.imwrite('./pictures/' + filename + ".jpg", self.frame)
            return 400
        except Exception as e:
            print(str(e))
            return 401

        

    @classmethod
    def _thread(cls):

#=========================
#    Video Settings      
#=========================

#CV_CAP_PROP_FRAME_WIDTH Width of the frames in the video stream.
#CV_CAP_PROP_FRAME_HEIGHT Height of the frames in the video stream.
#CV_CAP_PROP_FPS Frame rate

        camera = cv2.VideoCapture(0)
        camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
        camera.set(cv2.cv.CV_CAP_PROP_FPS, 30)
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
            if time.time() - cls.last_access > 2:
                break
        cls.thread = None
