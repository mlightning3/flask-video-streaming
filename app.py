#!/usr/bin/env python
from flask import Flask, render_template, Response, request

# emulated camera
from camera_usb import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


cam = Camera()
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/snapshot', methods=['GET'])
def take_snapshot():
    filename = request.args.items()[0][1][:-1]
    return str(cam.take_snapshot(filename))

@app.route('/video_capture', methods=['GET'])
def video_capture():
    status = request.args.get('status')
    filename = request.args.get('filename')
    return str(cam.take_video(filename, status))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
