flask-video-streaming
=====================
A small camera streaming server and project for the University of Michigan. Built using
Python Flask and JQuery.

The main idea behind this project to to take advantage of the inexpensive hardware that
has come on the market recently, and use it to stream video to hardware everyone already
uses. For example, you could put a camera on a Raspberry Pi strapped onto an RC car, and
stream the video back to your phone for an inexpensive FPV vehicle.

### Features

* Real-Time video streaming
* Camera and image manipulation (on supported devices)
* Picture taking
* Video Recording
* Downloading saved pictures and video
* Adding/Removing pictures and video from listing
* Controlling external devices (such as a light)
* Reading from external devices (such as a sensor)

### Hardware Requirements

* 1Ghz processor
* 512Mb RAM
* ?? Space for all the videos and pictures
* (Optional but recommended) external controller for LEDs and sensors

Runs on Raspberry Pi Zero W, 3, 3B+ and whatever x86 box you have around. The video
saving will benefit from having a fast connection to your storage medium. Currently
having extra cores will only benefit you if you use the external controller for LED
and sensor reading.

Works with any camera OpenCV can talk to (webcams, PlayStation Eye, etc.), and
has support of the Raspberry Pi camera (both clones and genuine).
Higher resolution cameras will require a stronger processor to keep the stream going
at a reasonable rate, though if the camera is supported by OpenCV then you can drop the
resolution for weaker hardware.

Installing and Setup
====================
Use Python3 and pip3 if your system has multiple versions of Python installed.

There are two ways of running the server, the first and easier way
is to use the handy script flaskstart.sh, the second is all done manually.

There is also a configuration file that should be created before doing either
method of setting up and running the server. This file is used to give the server
some information about what hardware is going to be used with it, as well as
setting up a simple form of permissions to allow only people with a special key
the ability to control certain functions. Look at config.txt.example for how to
format the file, and what options and settings are supported. Name the file you
create config.txt and keep it in the same directory as app.py so the settings
can be applied at runtime.

Key requirements for install are:

```
Flask  >= 0.10.1
OpenCV >= 3.0.0
```

Using pip, we should grab all the dependencies we need when we get Flask and a
couple of other needed things:

```
$ pip install Flask numpy
```

If you are using an external controller, you will also need the serial library:

```
$ pip install serial
```

If you are going to run this on a Raspberry Pi, you may need to compile OpenCV
on your own. Also should you want to use neopixels for light, checkout
[rpi_281x](https://github.com/jgarff/rpi_ws281x) and compile that too.
*It is not recommended to have the raspberry pi directly control a neopixel if
having a constant framerate is important to your application. Instead use an
external controller such as an Arduino.*

Then either clone this git repository, or grab a zip from the release folder:

```
$ git clone https://github.com/mlightning3/flask-video-streaming
```

### Script Method

To use the script we are assuming you have a Linux environment (actual
Linux or WSL).

As long as you make sure the script is executable, you can run the script from
anywhere. Run the script anytime you want to run the server with:

```
$ cd Path/To/Flask/Server/Directory
$ ./flaskstart.sh
```

Now follow up with first time setup.

### Manual Method

Now connect a camera to the computer, and run:

```
$ ./app.py
```

If you are using neopixels attached to a Raspberry Pi, run it like this instead:

```
$ sudo ./app.py
```

Now follow up with first time setup.

## First Time Setup

You should now have a live status update from the Flask server in the terminal.
To connect to it, load up a web browser (any except IE) and go to 127.0.0.1:5000
and you should see a live feed from the camera.

![Connecting locally on Raspberry Pi](documentation/images/connect_local.png)

Now to set up the database for saving pictures and video, go to 127.0.0.1:5000/database
and click on the "New Database" button. Now you are all set to save pictures and videos.

![Setting up database](documentation/images/database_editor.png)

To use this, point the browser of the device you want to view your stream from
to the IP address of the computer running the server with :5000 appended to the end.

![Connecting remotely](documentation/images/connect_remote.jpeg)

You can have multiple devices viewing the stream, but that hasn't been tested as
throughly as when just one device is viewing the stream.

Copyright
=========
University of Michigan 2017-2019

All rights reserved.

Based on Miguel Grinberg's [video streaming with Flask](http://blog.miguelgrinberg.com/post/video-streaming-with-flask) 2014 under the MIT license.
[Link to Miguel's Github repo](https://github.com/miguelgrinberg/flask-video-streaming)

Uses [rpi_281x](https://github.com/jgarff/rpi_ws281x) for neopixel control. Copyright 2014, jgarff under MIT License.
