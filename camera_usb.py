import time
import io
import threading
import cv2
import numpy as np

avg = np.repeat(0.0, 100)


class Camera(object):
    thread = None  # background thread that reads frames from camera
    watcher = None # background thread that creates video from frames
    frame = None  # current frame is stored here by background thread
    status = False;
    prev_status = False;
    filename = '';
    last_access = 0  # time of last client access to the camera
    frame_width = 0
    frame_height = 0

    max_width = 320
    max_height = 240

    fps = 20 # The target frames per second we want to get to
    fps_time = 1 / fps# How long max we have to wait to get that fps

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()
            # start background video thread
            Camera.watcher = threading.Thread(target=self._watcher)
            Camera.watcher.start()

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
        #if(status):
        #    fourcc = cv2.cv.CV_FOURCC(*'XVID')
        #    global video = cv2.VideoWriter('./pictures/video.avi', fourcc, 30, (int(cap.get(320), int(240)))


    @classmethod
    def _watcher(cls):

        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        started = False
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #FPS variables
        start = time.time()

        while(True):
            timeon = time.time()
            constframe = cls.frame

            #cv2.putText(constframe,str(Camera.status),(30,30),font,1,(0,0,255),2)
            #cv2.putText(constframe,str(Camera.prev_status),(30,80),font,1,(0,0,255),2)

            if(cls.status == True and cls.prev_status == False):
                if(started == False): # Only start writing to file if we haven't already started
                    video = cv2.VideoWriter('./media/' + cls.filename + '.avi', fourcc, cls.fps, (cls.frame_width, cls.frame_height))
                    started = True
            elif cls.status == False and cls.prev_status == True:
                video.release()
                started = False
                cls.prev_status = False

            if(cls.status == True or started == True):
                video.write(constframe)

            if time.time() - cls.last_access > 2:
                if started == True: # If things didn't close nicely before, we should close things now to save any file we started
                    video.release()
                    started = False
                break

            # To try to keep the framerate constant
            waittime = cls.fps_time - (time.time() - timeon)
            if waittime < 0:
                waittime = 0
            time.sleep(waittime)

        cls.watcher = None


    @classmethod
    def _thread(cls):

        #=========================
        #    Video Settings      
        #=========================

        camera = cv2.VideoCapture(0)
        cls.frame_width = int(camera.get(3)) # These pull the camera size from what opencv loads
        cls.frame_height = int(camera.get(4))

        while(True):
            ret, frame = camera.read()
            if cls.frame_width > cls.max_width or cls.frame_height > cls.max_height:
                scaling = cls.max_width/float(cls.frame_width)
                cls.frame = cv2.resize(frame, None, fx=scaling, fy=scaling, interpolation=cv2.INTER_AREA)
            else:
                cls.frame = frame
            
            if time.time() - cls.last_access > 2:
                break

        cls.thread = None
