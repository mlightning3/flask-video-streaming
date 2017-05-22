import cv2
import numpy as np
import sys
from time import sleep

cap = cv2.VideoCapture(0)
cap.set(3,320)
cap.set(4,240)
cap.set(5, 30) #frame rate 30 fps

while(True):
    _, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #following two lines didn't work until I added import numpy line
    lower_red = np.array([0,50,50])
    upper_red = np.array([10,255,255])
    # Threshold the HSV image to get only red colors
    mask0 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([160,50,50])
    upper_red = np.array([180,255,255])
    # Threshold the HSV image to get only red colors
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    mask = mask0 + mask1

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask) #didn't work until I changed frame to image
    
#    cv2.imshow('Video',frame)
    cv2.imshow('Video',res)

    if cv2.waitKey(1)==27:#esc Key
        break
cap.release()

cv2.destroyAllWindows()
