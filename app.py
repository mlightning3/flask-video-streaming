#!/usr/bin/env python
from flask import Flask, render_template, Response
import time

# emulated camera
#from camera import Camera

# Raspberry Pi camera module (requires picamera package)
#from camera_pi_cv import Camera

# USB Camera Module, requires cv2
from camera_usb import Camera

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/red_filter')
def red_filter():
    """Video streaming home page."""
    return render_template('red.html')

def gen(camera, mode):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame(mode)
        if(type(frame) == None):
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed/<int:mode>')
def video_feed(mode):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(), mode),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
