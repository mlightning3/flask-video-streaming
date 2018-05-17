#!/usr/bin/env python
from flask import Flask, render_template, Response, request, g, send_from_directory

# For database
import sqlite3
import datetime
import os
from contextlib import closing

# USB Camera Module, requires cv2
from camera_usb import Camera

app = Flask(__name__)

# Database configuration
DATABASE = './media/media.db'

## Initialize The Database
#
# To initialize the database if it doesn't exist
def init_db():
    with closing(sqlite3.connect(DATABASE)) as db:
        with app.open_resource('media_schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

## Connect To Database
#
# Connects to the database
def connect_db():
    if os.path.isfile(DATABASE) == False:
        init_db() # Create the database if it doesn't exist
    return sqlite3.connect(DATABASE)

## Grab Entries
#
# Gets all the data in the database and sets it up to be sent to the webpage
def grab_entries():
    cur = g.db.execute('SELECT date, fileName FROM media ORDER BY id ASC') # Grabs all the file names in the database
    entries = [dict(date=row[0], fileName=row[1]) for row in cur.fetchall()] # Puts that into a structure that will be read by the webpage
    return entries

## Setting Up The Environment
#
# Things to do before dealing with outside connections, such as connecting to the database
@app.before_request
def before_request():
    g.db = connect_db()

## Shutdown Cleanup
#
# Things to do when shutting down server, such as disconnecting from the database.
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Routing

## Root Route
#
# This is where everyone will go to see the video feed and interact with the application
@app.route('/')
def index():
    """Video streaming home page."""
    entries = grab_entries()
    return render_template('index.html', pictures=entries) # Entires gets sent to a variable in the webpage

## Camera Generator Function
#
# Sets up the camera for the video feed
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

cam = Camera()

## Video Feed Route
#
# Streams the video to the webpage by sending new images as they become available
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

## Picture Taking Route
#
# Saves a single frame from the camera when this gets called, as long as there is a valid filename
@app.route('/snapshot', methods=['GET'])
def take_snapshot():
    filename = request.args.get('filename')
    today = datetime.date.today()
    full_filename = filename + ".jpg"
    g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [today, full_filename]) # Inserts information into the database
    g.db.commit()
    return str(cam.take_snapshot(filename))

## Video Capture Route
#
# Takes the state of the capture video button from the webpage, and then starts or stops recording video as is necessary
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

## Slider Value Route
#
# Changes the brightness of the light on the camera
# This is mainly listening to a slider on the webpage and shouldn't really be used by other things
@app.route('/slidervalue', methods=['GET'])
def slide():
    value = request.args.get('value')
    # TODO: Change the light level
    print("Light: ", value)
    return str(400)

## Light Route
#
# Toggles the camera's light on and off
@app.route('/light', methods=['GET'])
def light():
    status = request.args.get('status')
    if status == 'true' or status == 'True':
        print("Light: ON")
        # TODO: turn light on
    if status == 'false' or status == 'False':
        print("Light: OFF")
        # TODO: turn light off
    return str(400)

## Database Editor Route
#
# Way to edit database from web browser
@app.route('/database')
def edit_database():
    entries = grab_entries()
    return render_template('database.html', pictures=entries)

## Add To Database Route
#
# Adds a file to the database, so it will appear on the media list
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

## Remove From Database Route
#
# Removes a file from the database (but does not delete the file) so it no longer appears on the media list
@app.route('/database/remove', methods=['GET'])
def remove_from_database():
    #filename = request.args.get('file')
    filename = request.args.items()[0][1][:-1]
    exist = g.db.execute('SELECT EXISTS (SELECT 1 FROM media WHERE fileName=? LIMIT 1)', [filename]).fetchone()[0]
    if exist == 1:
        g.db.execute('DELETE FROM media WHERE fileName=?', [filename])
        g.db.commit()
    return str(400)

## New Database Route
#
# Creates a new database for storing pictures and video. Overwrites the old database if there was one.
@app.route('/database/new', methods=['GET'])
def new_database():
    init_db()
    return str(400)

## Media Downloading Route
#
# Sends the file to users device, meaning video files will need a player on that device.
@app.route('/media/<path:path>')
def send_media(path):
    return send_from_directory('media', path)

## Autostart
#
# This gets everything going well called by Python. Needed to get Flask set up properly
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
