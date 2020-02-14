##
# This class does all the work of pulling images off of the camera and sending them to the server, as well as saving off
# pictures and videos.
#
##

import time
import copy
import threading
import cv2
import numpy as np
import queue
from datetime import datetime
import pytesseract
import pyzbar
import imutils

avg = np.repeat(0.0, 100)

class Camera(object):
    type = "default" # String defining the camera, so we know what functionality it has
    thread = None  # background thread that reads frames from camera
    watcher = None # background thread that writes vidoes file
    tess_thread = None # Thread that gets spun up to do tesseract work
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
    tesseract = False
    tesseractLCD = False
    tess_frame = None
    tess_text = ""
    barcode = False
    bar_frame = None
    bar_text = ""

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
            return 500

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

    # Where we get any desired action for an OpenCV action
    # @param payload The string for the desired payload to do something with
    # @param args A dictionary of all the keys and values sent in the query request (anything after the ? in the url like ?status=true&name=pi)
    def video_payload(self, payload, args):
        if payload == "snapshot":
            filename = "default-" + str(datetime.now()) # May want to pick something better than date, this will be wrong quickly (Pi has no RTC backup)
            if "filename" in args:
                filename = args.get("filename")
            self.take_snapshot(filename)
            return 200

        if payload == "tesseract":
            if "status" in args:    # Turn OCR on and off
                enable = args.get("status")
                enable = enable.lower()
                if enable == "false":
                    enable = True
                else:
                    enable = False
                Camera.tesseract = enable
            if "lcd" in args:   # Turn LCD reading on and off
                lcdEnable = args.get("lcd")
                lcdEnable = lcdEnable.lower()
                if lcdEnable == "false":
                    lcdEnable = True
                else:
                    lcdEnable = False
                Camera.tesseractLCD = lcdEnable
            # if "" in args:    # Other switches for tesseract would go here
            return 200

        if payload == "barcode":
            if "status" in args:    # Turn OCR on and off
                enable = args.get("status")
                enable = enable.lower()
                if enable == "false":
                    enable = True
                else:
                    enable = False
                Camera.barcode = enable
            # if "" in args:    # Other switches for barcode would go here
            return 200

        # TODO: Fill this out with other OpenCV things
        # Until then, just return Not Found to everything
        return 404

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

    # =========================
    # Tesseract OCR thread
    #
    # Currently is only started when there is a request for some OCR. Takes whatever frame of the video is passed to
    # tess_frame and does some OCR on it. If any special image related editing needs to take place to improve the OCR
    # process, it should be done here to reduce the workload on the main thread.
    # =========================
    @classmethod
    def _tesseract_thread(cls):
        while cls.tesseract == True:
            if cls.tess_frame != None:
                temp_img = copy.deepcopy(cls.tess_frame) # This is an expensive operation, but gives us a local copy to work with
                cls.tess_frame = None

                # Do any special things to image here

                if cls.tesseractLCD:    # If we want to OCR an LCD
                    hsvImage = cv2.cvtColor(temp_img, cv2.COLOR_BGR2HSV)
                    lowerBlack = np.array([0, 0, 0])    # Pure black
                    upperBlack = np.array([31, 31, 31]) # Mostly black, but some color
                    mask = cv2.inRange(hsvImage, lowerBlack, upperBlack)

                    maskedImg = cv2.bitwise_and(temp_img, temp_img, mask=mask) # Highlight just black things in image
                    maskedImg = cv2.GaussianBlur(maskedImg, (13, 13), 0) # Change the (13, 13) to adjust amount of blur
                    maskedImg = cv2.Canny(maskedImg, 100, 200) # Edge detection
                    dilate = cv2.dilate(maskedImg, None, iterations=4)
                    erode = cv2.erode(dilate, None, iterations=4)

                    contours = cv2.findContours(erode.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                    contours = contours[0] if imutils.is_cv2() else contours[1]
                    emptyMask = np.ones(temp_img.shape[:2], dtype="uint8") * 255

                    for contour in contours:
                        if cv2.contourArea(contour) < 600:  # Remove small contour areas
                            cv2.drawContours(emptyMask, [contour], -1, 0, -1)
                            continue

                    temp_img = cv2.bitwise_and(erode.copy(), dilate.copy(), mask=emptyMask)
                    temp_img = cv2.dilate(temp_img, None, iterations=7)
                    temp_img = cv2.erode(temp_img, None, iterations=7)
                    ret, temp_img = cv2.threshold(temp_img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

                cls.tess_text = pytesseract.image_to_string(temp_img)
            time.sleep(.5)
        cls.tess_thread = None

    # =========================
    # Barcode reading thread
    #
    # Currently is only started when there is a request for some barcode reading. Takes whatever frame of the video is
    # passed to bar_frame and analyzes it. If any special image related editing needs to take place to improve the reading
    # process, it should be done here to reduce the workload on the main thread.
    # =========================
    @classmethod
    def _barcode_thread(cls):
        while cls.barcode == True:
            if cls.bar_frame != None:
                temp_img = copy.deepcopy(cls.bar_frame)  # This is an expensive operation, but gives us a local copy to work with
                cls.bar_frame = None

                # Do any special things to image here

                barcodes = pyzbar.decode(temp_img)
                barcode = barcodes[0]
                cls.bar_text = barcode.data.decode("utf-8")
            time.sleep(.5)
        cls.bar_thread = None

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
                tosave = frame
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
                if cls.tesseract: # If we are doing a tesseract thing, give it a frame and put any text it gives on current video feed
                    if cls.tess_thread == None:
                        cls.tess_frame = None
                        cls.tess_text = ""
                        cls.tess_thread = threading.Thread(target=cls._tesseract_thread)
                        cls.tess_thread.start()
                    cls.tess_frame = frame
                    cv2.putText(frame, cls.tess_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2)
                if cls.barcode: # If we are doing a barcode thing, give it a frame and put any text it gives on current video feed
                    if cls.bar_thread == None:
                        cls.bar_frame = None
                        cls.bar_text = ""
                        cls.bar_thread = threading.Thread(target=cls._barcode_thread)
                        cls.bar_thread.start()
                    cls.bar_frame = frame
                    cv2.putText(frame, cls.bar_text, (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2)
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
