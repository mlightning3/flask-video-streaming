import time
import io
import threading
import cv2
import numpy as np
import Queue # When running on the Tinkerboard/Debian 9 or less, use queue and queue.Queue()

avg = np.repeat(0.0, 100)

class Camera(object):
    thread = None  # background thread that reads frames from camera
    watcher = None # background thread that writes vidoes file
    frame = None  # current frame is stored here by background thread
    buff = Queue.Queue()
    status = False;
    prev_status = False;
    filename = '';
    frame_width = 0
    frame_height = 0
    fps = 30 # The target frames per second we want to get to
    fps_time = 1/fps

    write = false # Flag to start writing the video file
    ontime = 0 # When we started recording video
    totaltime = 0 # Amount of time we recorded video
    rcount = 0 # Number of frames read in while recording

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()
            # start background video writing thread
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
            Camera.ontime = time.time()
        else:
            Camera.prev_status = True
            Camera.status = False
            Camera.totaltime = time.time() - Camera.ontime
        Camera.filename = filename
        print(Camera.status)

    #=========================
    # Video writing thread
    #
    # This takes the frames made by the other thread to write a video with a constant framerate
    #=========================
    @classmethod
    def _watcher(cls):
        
        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        while(True):
            if cls.write == True:
                fps = cls.rcount / cls.totaltime
                video = cv2.VideoWriter('./media/' + cls.filename + '.avi', fourcc, fps, (cls.frame_width, cls.frame_height))
                while cls.buff.empty() == False:
                    video.write(cls.buff.get())
                video.release()
                cls.prev_status = False
                write = False

            if time.time() - cls.last_access > 2:
                break

        cls.watcher = None

    #=========================
    # Video capture thread
    #
    # This takes frames off of the camera and places it in frame
    #=========================
    @classmethod
    def _thread(cls):

        #=========================
        #    Video Settings      
        #=========================       
        camera = cv2.VideoCapture(0)
        #camera.set(5, cls.fps)
        cls.fps = int(camera.get(5))
        cls.frame_width = int(camera.get(3)) # These pull the camera size from what opencv loads
        cls.frame_height = int(camera.get(4))
        blank_frame = np.zeros((cls.frame_height, cls.frame_width, 3), np.uint8) # Creates a black image when there is nothing on the camera
        fcount = 0
        while(True):
            try:
                ret, frame = camera.read()
            except:
                ret, frame = (-1, blank_frame)
            if ret == False:
                frame = blank_frame
            cls.frame = frame
            if cls.status == True:
                cls.buff.put(frame)
                fcount = fcount + 1
            elif cls.status == False and cls.prev_status == True:
                cls.rcount = fcount
                cls.write = True
                fcount = 0
                cls.prev_status = False

            if time.time() - cls.last_access > 2:
                break

        camera.release()
        cls.thread = None
