##
# This class does all the work of pulling images off of the camera and sending them to the server, as well as saving off
# pictures and videos.
#
##

import time
import io
import threading
import cv2
import numpy as np
import queue

avg = np.repeat(0.0, 100)

class Camera(object):
    thread = None  # background thread that reads frames from camera
    watcher = None # background thread that writes vidoes file
    frame = None  # current frame is stored here by background thread
    buff = queue.Queue()
    writers = queue.Queue() # Holds our video writing threads while they work
    status = False;
    prev_status = False;
    filename = '';
    frame_width = 0
    frame_height = 0
    ontime = 0 # When we started recording video
    totaltime = 0 # Amount of time we recorded video

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

    def take_video(self, filename, status): 
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
    # Writes the buffer to file, then ends itself
    #
    # frames - Number of frames captured
    # runtime - Amount of time spent recording
    # fbuffer - Queue with buffer of frames that were recorded
    #=========================
    @classmethod
    def _watcher(cls, frames, runtime, fbuffer):
        
        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        fps = frames / runtime
        video = cv2.VideoWriter('./media/' + cls.filename + '.avi', fourcc, fps, (cls.frame_width, cls.frame_height))
        while fbuffer.empty() == False:
            video.write(fbuffer.get())
        video.release()

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
            else:
                res = cv2.resize(frame,None,fx=.25,fy=.25, interpolation = cv2.INTER_AREA) # Resizes the image
                frame = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
            cls.frame = frame
            if cls.status == True:
                cls.buff.put(frame)
                fcount = fcount + 1
            elif cls.status == False and cls.prev_status == True:
                temp = threading.Thread(target=cls._watcher, args=(fcount, cls.totaltime, cls.buff))
                temp.start()
                cls.writers.put(temp)
                cls.buff = queue.Queue()
                fcount = 0
                cls.prev_status = False

            if time.time() - cls.last_access > 2:
                break

        camera.release()
        cls.thread = None
