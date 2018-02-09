import time
import io
import threading
import cv2
import numpy as np

avg = np.repeat(0.0, 100)

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    status = False;
    prev_status = False;
    filename = '';
    frame_width = 0
    frame_height = 0
    fps = 30 # The target frames per second we want to get to

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
            cv2.imwrite('./media/' + filename + ".jpg", self.frame)
            return 400
        except Exception as e:
            print(str(e))
            return 401

    def take_video(self, filename, status): # I took this from Brandon's code, so that is why this changed
        if(status == "false" or status == False):
            Camera.prev_status = False
            Camera.status = True
        else:
            Camera.prev_status = True
            Camera.status = False
        Camera.filename = filename
        print(Camera.status)

    @classmethod
    def _thread(cls):

        #=========================
        #    Video Settings      
        #=========================

        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        started = False
        camera = cv2.VideoCapture(0)
        camera.set(5, cls.fps)
        cls.frame_width = int(camera.get(3)) # These pull the camera size from what opencv loads
        cls.frame_height = int(camera.get(4))
        while(True):
            ret, frame = camera.read()
            cls.frame = frame

            if(cls.status == True and cls.prev_status == False):
                if(started == False): # Only start writing to file if we haven't already started
                    video = cv2.VideoWriter('./media/' + cls.filename + '.avi', fourcc, cls.fps, (cls.frame_width, cls.frame_height))
                    started = True
            elif cls.status == False and cls.prev_status == True:
                video.release()
                started = False
                cls.prev_status = False

            if(cls.status == True or started == True):
                video.write(frame)

            if time.time() - cls.last_access > 2:
                if started == True: # If things didn't close nicely before, we should close things now to save any file we started
                    video.release()
                    started = False
                break

        cls.thread = None
