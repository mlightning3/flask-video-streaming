flask-video-streaming
=====================
A small camera streaming server and project for the University of Michigan.

Installing and Setup
====================
Use Python3 and pip3 if your system has multiple versions of Python installed.

Grab our key dependencies, Flask and OpenCV. If you are going to be running
this on a Raspberry Pi, you may have to build OpenCV from source. The versions
that we are looking for are:

```
Flask  >= 0.10.1
OpenCV >= 3.0.0
```

Using pip, we should grab all the dependencies we need when we get Flask:

```
$ pip install Flask
```

Then clone or download the server:

```
$ git clone https://github.com/mlightning/flask-video-streaming
```

Now connect a camera to the computer, and run:

```
$ python app.py
```

You should now have a live status update from the Flask server in the terminal.
To connect to it, load up a web browser (any except IE) and go to 127.0.0.1:5000
and you should see a live feed from the camera.

Now to set up the database for saving pictures and video, go to 127.0.0.1:5000/database
and click on the "New Database" button. Now you are all set to save pictures and videos.

To use this, point the browser of the device you want to view your stream from
to the IP address of the computer running the server with :5000 appended to the end.
You can have multiple devices viewing the stream, but that hasn't been tested as
throughly as when just one device is viewing the stream.

Copyright
=========
University of Michigan 2017-2018

Based on Miguel Grinberg's [video streaming with Flask](http://blog.miguelgrinberg.com/post/video-streaming-with-flask) 2014.

Licensed under the MIT license.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.