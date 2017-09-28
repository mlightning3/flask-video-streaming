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
    def _thread(cls):

        #=========================
        #    Video Settings      
        #=========================

        camera = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc('X','V','I','D')

        frame_width = int(camera.get(3)) # These pull the camera size from what opencv loads
        frame_height = int(camera.get(4))

        started = False # For keeping track of if we started saving to a file or not

        font = cv2.FONT_HERSHEY_SIMPLEX

        #FPS variables
        start = time.time()
        frames = 0
        fps = 0

        while(True):
            ret, frame = camera.read()

            timeon = time.time() # For keeping track of when the loop starts again

            #FPS testing 
            frames = frames + 1
            if(frames == 100):
                fps = frames / (time.time() - start)
                start = time.time()
                frames = 0

            cv2.putText(frame,str(Camera.status),(30,30),font,1,(0,0,255),2)
            cv2.putText(frame,str(Camera.prev_status),(30,80),font,1,(0,0,255),2)
            cv2.putText(frame,str(fps),(30,130),font,1,(0,255,255),2) # FPS testing


            cls.frame = frame
            
            if(cls.status == True and cls.prev_status == False):
                if(started == False): # Only start writing to file if we haven't already started
                    video = cv2.VideoWriter('./media/' + cls.filename + '.avi', fourcc, 7, (frame_width, frame_height))
                    started = True
            elif cls.status == False and cls.prev_status == True:
                video.release()
                started = False
                cls.prev_status = False
                camera.release() # Since I found this needed to be closed to finish writing to the file
                camera = cv2.VideoCapture(0) # Since we closed the camera, reopen it to keep stream

            if(cls.status == True or started == True):
                video.write(frame)
                
            if time.time() - cls.last_access > 2:
                if started == True: # If things didn't close nicely before, we should close things now to save any file we started
                    video.release()
                    camera.release()
                    started = False
                break

            # To try to keep the framerate constant
            waittime = .125 - (time.time() - timeon)
            if waittime < 0:
                waittime = 0
            time.sleep(waittime)

        cls.thread = None
