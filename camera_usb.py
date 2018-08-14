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
    type = "default" # String defining the camera, so we know what functionality it has
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
    grayscale = False
    low_resolution = False
    autofocus = 0
    autofocus_changed = False
    manual_focus = 0.5
    manual_focus_changed = False

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    ## Sets the camera type
    #
    # Given the type of camera, certain options will be enabled/disabled
    # @param cameraType String describing the type of camera
    def set_cameratype(self, cameraType):
        Camera.type = cameraType
        if (Camera.type == "LiquidLens"):
            Camera.autofocus = 1

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return cv2.imencode('.jpeg', self.frame)[1].tostring()

    def take_snapshot(self, filename):
        try:
            cv2.imwrite('./media/' + filename + ".jpg", self.frame)
            return 200
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

    def set_grayscale(self, status):
        if(status == "false" or status == False):
            Camera.grayscale = True
        if(status == "true" or status == True):
            Camera.grayscale = False
        return 200

    def drop_resolution(self, status):
        if(status == "false" or status == False):
            Camera.low_resolution = True
        if(status == "true" or status == True):
            Camera.low_resolution = False
        return 200

    ## Toggles the autofocus
    #
    # ONLY WORKS ON SUPPORTED CAMERAS
    def change_autofocus(self, status):
        if(Camera.type == "LiquidLens"):
            if (status == "false" or status == False):
                Camera.autofocus = 1
                Camera.autofocus_changed = True
            if (status == "true" or status == True):
                Camera.autofocus = 0
                Camera.autofocus_changed = True
            return 200
        else:
            return 403

    ## Steps the focus in a direction
    #
    # Moves the plane of focus by 0.05 in either a positive or negative direction
    # ONLY WORKS ON SUPPORTED CAMERAS
    # @param direction Should be either a positive or negative number
    def step_focus(self, direction):
        if(Camera.type == "LiquidLens"):
            if(direction > 0):
                Camera.manual_focus += 0.05
                Camera.manual_focus_changed = True
            elif(direction < 0):
                Camera.manual_focus -= 0.05
                Camera.manual_focus_changed = True
            if(Camera.manual_focus > 1):
                Camera.manual_focus = 1
            elif(Camera.manual_focus < 0):
                Camera.manual_focus = 0
            return 200
        else:
            return 403

    ## Sets the focus to a specific value
    #
    # ONLY WORKDS ON SUPPORTED CAMERAS
    # @param value Should be a value between 0 and 1, above or below that will set to 0 or 1
    def set_focus(self, value):
        if(Camera.type == "LiquidLens"):
            Camera.manual_focus = value
            if (Camera.manual_focus > 1):
                Camera.manual_focus = 1
            elif (Camera.manual_focus < 0):
                Camera.manual_focus = 0
            Camera.manual_focus_changed = True
            return 200
        else:
            return 403

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
        cls.fps = int(camera.get(5))

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        #camera.set(15, -5) # Setting exposeure value, which should turn off auto-white balance
        #camera.set(21, 0) # Turn off auto exposure
        #camera.set(cv2.CAP_PROP_GAIN , 1)
        camera.set(cv2.CAP_PROP_AUTOFOCUS, cls.autofocus) # Set autofocus

        cls.frame_width = int(camera.get(3))  # These pull the camera size from what opencv loads
        cls.frame_height = int(camera.get(4))
        print('Width:', cls.frame_width, 'Height:', cls.frame_height)

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
                tosave = frame
                if(cls.low_resolution == True):
                    frame = cv2.resize(frame,None,fx=.5,fy=.5, interpolation = cv2.INTER_AREA) # Resizes the image
                if(cls.grayscale == True):
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if(cls.autofocus_changed == True):
                    camera.set(cv2.CAP_PROP_AUTOFOCUS, cls.autofocus)
                    cls.autofocus_changed = False
                if(cls.manual_focus_changed == True):
                    cls.autofocus = 0
                    camera.set(cv2.CAP_PROP_AUTOFOCUS, cls.autofocus)
                    camera.set(cv2.CAP_PROP_FOCUS, cls.manual_focus)
                    cls.manual_focus_changed = False
                #frame = res
            cls.frame = frame
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

            if time.time() - cls.last_access > 2:
                break

        camera.release()
        cls.thread = None
