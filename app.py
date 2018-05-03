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
from camera_pi_cv import Camera as Pi_Camera

# USB Camera Module, requires cv2
from camera_usb import Camera

app = Flask(__name__)

# Database configuration
DATABASE = './media/media.db'

# To initalize the database if it doesn't exist
def init_db():
    with closing(sqlite3.connect(DATABASE)) as db:
        with app.open_resource('media_schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Connect to the database
def connect_db():
    if os.path.isfile(DATABASE) == False:
        init_db() # Create the database if it doesn't exist
    return sqlite3.connect(DATABASE)

def grab_entries():
    cur = g.db.execute('SELECT date, fileName FROM media ORDER BY id ASC') # Grabs all the file names in the database
    entries = [dict(date=row[0], fileName=row[1]) for row in cur.fetchall()] # Puts that into a structure that will be read by the webpage
    return entries

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
    entries = grab_entries()
    return render_template('index.html', pictures=entries) # Entires gets sent to a variable in the webpage

@app.route('/camera/<int:mode>')
def camera_display(mode):
    """Video streaming home page."""
    return render_template('usbcamera.html', mode=mode)

@app.route('/picamera/<int:mode>')
def picamera_display(mode):
    """Video streaming home page."""
    return render_template('picamera.html', mode=mode)

@app.route('/red_filter')
def red_filter():
    """Video streaming home page."""
    return render_template('red.html')

def gen(camera, mode):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame(mode)
        if(type(frame) == None):
            time.sleep(1)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

cam = Camera()
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/pivideo_feed/<int:mode>')
def pi_video_feed(mode):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Pi_Camera(), mode),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot', methods=['GET'])
def take_snapshot():
    filename = request.args.get('filename')
    today = datetime.date.today()
    full_filename = filename + ".jpg"
    g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [today, full_filename]) # Inserts information into the database
    g.db.commit()
    return str(cam.take_snapshot(filename))

@app.route('/video_capture', methods=['GET'])
def video_capture():
    status = request.args.get('status')
    filename = request.args.get('filename')
    if status == 'true' or status == 'True': #Only when we are done saving a video do we add it to the database
        today = datetime.date.today()
        full_filename = filename + ".avi"
        g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [today, full_filename]) # Inserts information into the database
        g.db.commit()
    return str(cam.take_video(filename, status))

# Way to edit database from web browser
@app.route('/database')
def edit_database():
    entries = grab_entries()
    return render_template('database.html', pictures=entries)

@app.route('/database/add', methods=['GET'])
def add_to_database():
    #filename = request.args.get('file')
    filename = request.args.items()[0][1][:-1]
    path = './media/' + filename
    if os.path.isfile(path) == True:
        date = datetime.date.today()
        g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [date, filename])
        g.db.commit()
    return str(400)

@app.route('/database/remove', methods=['GET'])
def remove_from_database():
    #filename = request.args.get('file')
    filename = request.args.items()[0][1][:-1]
    exist = g.db.execute('SELECT EXISTS (SELECT 1 FROM media WHERE fileName=? LIMIT 1)', [filename]).fetchone()[0]
    if exist == 1:
        g.db.execute('DELETE FROM media WHERE fileName=?', [filename])
        g.db.commit()
    return str(400)

@app.route('/database/new', methods=['GET'])
def new_database():
    init_db()
    return str(400)

#Creating a way to get media information
#Sends the file to users device, meaning video files will need a player on that device
@app.route('/media/<path:path>')
def send_media(path):
    return send_from_directory('media', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
