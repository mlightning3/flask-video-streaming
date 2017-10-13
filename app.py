#!/usr/bin/env python
from flask import Flask, render_template, Response, request, g, send_from_directory

# emulated camera
from camera_usb import Camera

# For database
import sqlite3
import datetime
import os
from contextlib import closing


# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

# Database configuration
DATABASE = './media/media.db'

# To initalize the database if it doesn't exist
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('media_schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Connect to the database
def connect_db():
    #if os.path.isfile(DATABASE) == False:
    #    init_db() # Create the database if it doesn't exist
    return sqlite3.connect(DATABASE)

# Things to do before dealing with outside connections
@app.before_request
def before_request():
    g.db = connect_db()

# Things to do when shutting down server
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Routing
@app.route('/')
def index():
    """Video streaming home page."""
    cur = g.db.execute('SELECT date, fileName FROM media ORDER BY id desc') # Grabs all the file names in the database
    entries = [dict(date=row[0], fileName=row[1]) for row in cur.fetchall()] # Puts that into a structure that will be read by the webpage
    return render_template('index.html', pictures=entries) # Entires gets sent to a variable in the webpage


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
    today = datetime.date.today()
    full_filename = filename + ".jpg"
    g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [today, full_filename]) # Inserts information into the database
    g.db.commit()
    return str(cam.take_snapshot(filename))

@app.route('/video_capture', methods=['GET'])
def video_capture():
    status = request.args.get('status')
    filename = request.args.get('filename')
    #today = datetime.date.today()
    #g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [today, filename]) # Inserts information into the database
    #g.db.commit()
    return str(cam.take_video(filename, status))

#Creating a way to get media information
#Probably not a great idea to keep forever
@app.route('/media/<path:path>')
def send_media(path):
    return send_from_directory('media', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
