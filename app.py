#!/usr/bin/env python3
from flask import Flask, render_template, Response, abort, request, g, send_from_directory, json

# For database
import sqlite3
import datetime
import os
from contextlib import closing
import configparser

# USB Camera Module, requires cv2
from camera_usb import Camera
from camera_pi_cv import Camera as PiCamera

app = Flask(__name__)

# Load settings from config file
config = configparser.ConfigParser()
config.read('config.txt')
try:
    CAMERA = config['SETTINGS']['camera']
except Exception as e:
    CAMERA = "default"
try:
    MASTERKEY = config['KEYS']['userkey']
except Exception as e:
    MASTERKEY = 'developmentkey'

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

# Set up our camera based on what was given in config file
if CAMERA == "Pi" or CAMERA == "PiCamera":
    cam = PiCamera()
else:
    cam = Camera()
    cam.set_cameratype(CAMERA) # Set up camera passing along camera information from config

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
    filename.replace(" ", "_")
    today = request.args.get('date')
    if today is None:
        today = datetime.date.today()
    full_filename = filename + ".jpg"
    g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [today, full_filename]) # Inserts information into the database
    g.db.commit()
    result = cam.take_snapshot(filename)
    if result == 200:
        return str(200)
    else:
        return Response('Error with snapshot', status=result)

## Video Capture Route
#
# Takes the state of the capture video button from the webpage, and then starts or stops recording video as is necessary
@app.route('/video_capture', methods=['GET'])
def video_capture():
    status = request.args.get('status')
    filename = request.args.get('filename')
    filename.replace(" ", "_")
    if status == 'true' or status == 'True': #Only when we are done saving a video do we add it to the database
        today = request.args.get('date')
        if today is None:
            today = datetime.date.today()
        full_filename = filename + ".avi"
        g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [today, full_filename]) # Inserts information into the database
        g.db.commit()
    result = cam.take_video(filename, status)
    if result == 200:
        return str(200)
    else:
        return Response('Error with recording video', status=result)

## Grayscale Toggle Route
#
# Changes the video feed between grayscale and color
@app.route('/grayscale', methods=['GET'])
def grayscale():
    status = request.args.get('status')
    result = cam.set_grayscale(status)
    if result == 200:
        return str(200)
    else:
        return Response('Error with grayscale', status=result)

## Resolution Toggle Route
#
# Changes between low and high resolution video feeds
@app.route('/resolution', methods=['GET'])
def resolution():
    status = request.args.get('status')
    result = cam.drop_resolution(status)
    if result == 200:
        return str(200)
    else:
        return Response('Error with resolution', status=result)

## Autofocus Toggle Route
#
# Changes between autofocus on and off. ONLY ON SUPPORTED CAMERAS
@app.route('/autofocus', methods=['GET'])
def autofocus():
    status = request.args.get('status')
    if CAMERA == "LiquidLens":
        result = cam.change_autofocus(status)
        if result == 200:
            return str(200)
        else:
            return Response('Error with autofocus', status=result)
    else:
        return Response('Autofocus not supported', status=403)

## Step Focus Route
#
# Adjusts the manual focus up or down a step at a time. ONLY ON SUPPORTED CAMERAS
@app.route('/step_focus', methods=['GET'])
def step_focus():
    direction = int(request.args.get('direction'))
    if CAMERA == "LiquidLens":
        return str(cam.step_focus(direction))
    else:
        return Response('Changing focus not supported', status=403)

## Set Focus Value Route
#
# Sets the manual focus to a specific value. ONLY ON SUPPORTED CAMERAS
@app.route('/set_focus', methods=['GET'])
def set_focus():
    value = float(request.args.get('value'))
    if CAMERA == "LiquidLens":
        return str(cam.set_focus(value))
    else:
        return Response('Changing focus not supported', status=403)

## Database Retrieval Route
#
# Sends the information in the database in JSON format
@app.route('/get_database')
def get_database():
    entries = g.db.execute('SELECT date, fileName FROM media ORDER BY id ASC')
    empList = []
    for emp in entries:
        empDict = {
            'date': emp[0],
            'filename': emp[1]}
        empList.append(empDict)
    response = app.response_class(
        response=json.dumps(empList),
        status=200,
        mimetype='application/json'
    )
    return response

## Log Fetching Route
#
# Gets server log and system log for debugging
@app.route('/logs', methods=['GET'])
def fetch_logs():
    try:
        os.system('sudo dmesg > system.log')
        syslog = open('system.log', 'r')
        logdict = {
            'System' : syslog.read()
        }
        logs = []
        logs.append(logdict)
        response = app.response_class(
            response=json.dumps(logs),
            status=200,
            mimetype='application/json'
        )
        return response
    except os.error:
        abort(500)

## Shutdown Pi Route
#
# Has the Pi shutdown if a valid key is given
@app.route('/shutdown', methods=['GET'])
def shutdown():
    recievedkey = request.args.get('key')
    if recievedkey == MASTERKEY:
        try:
            os.system('sudo shutdown -h 1')
            print('Shutting down ...')
            return str(200)
        except os.error:
            print('Error with shutdown')
            return Response('Server unable to shutdown', status=500)
    else:
        print('Invalid key')
        return Response('Invalid key', status=401)

## Restart Pi Route
#
# Has the Pi restart if a valid key is given
@app.route('/reboot', methods=['GET'])
def reboot():
    recievedkey = request.args.get('key')
    if recievedkey == MASTERKEY:
        try:
            os.system('sudo shutdown -r 1')
            print('Rebooting ...')
            return str(200)
        except os.error:
            print('Error with reboot')
            return Response('Server unable to reboot', status=500)
    else:
        print('Invalid key')
        return Response('Invalid key', status=401)

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
    filename = request.args.get('filename')
    filename.replace(" ", "_")
    path = './media/' + filename
    if os.path.isfile(path) == True:
        date = datetime.date.today()
        g.db.execute('INSERT INTO media (date, fileName) VALUES (?, ?)', [date, filename])
        g.db.commit()
    return str(200)

## Remove From Database Route
#
# Removes a file from the database (but does not delete the file) so it no longer appears on the media list
@app.route('/database/remove', methods=['GET'])
def remove_from_database():
    filename = request.args.get('filename')
    filename.replace(" ", "_")
    exist = g.db.execute('SELECT EXISTS (SELECT 1 FROM media WHERE fileName=? LIMIT 1)', [filename]).fetchone()[0]
    if exist == 1:
        g.db.execute('DELETE FROM media WHERE fileName=?', [filename])
        g.db.commit()
        os.remove('media/' + filename)
    return str(200)

## New Database Route
#
# Creates a new database for storing pictures and video. Overwrites the old database if there was one.
@app.route('/database/new', methods=['GET'])
def new_database():
    init_db()
    return str(200)

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
