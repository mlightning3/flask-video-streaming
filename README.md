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

### Hardware Requirements

* 1Ghz processor
* 512Mb RAM
* ?? Space for all the videos and pictures

Runs on Raspberry Pi Zero W, 3, 3B+ and whatever x86 box you have around. The video
saving will benifit from having multiple cores and a fast connection to your storage
medium.

Works with any camera OpenCV can talk to (webcams, PlayStaion Eye, etc.), and
has support of the Raspberry Pi camera.
Higher resolution cameras will require a stronger processor to keep the stream going
at a resonable rate, though if the camera is supported by OpenCV then you can drop the
resolution for weaker hardware.

Installing and Setup
====================
Use Python3 and pip3 if your system has multiple versions of Python installed.

There are two ways of installing and running the server, the first and easier way
is to use the handy script flaskstart.sh, the second is all done manually. It is
reconmended that for either method (but required by the script) that you use a
virtual enrivonment to allow for specific versions of libraries to be used.

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

### Script Method

To use the script we first are assuming you have a Linux enviroment (actual
Linux or WSL) and we need to make sure that we have a virtual environment set up
to use (this will also be done with a script in the future).
Install the python virtual environment manger like so:

```
$ pip install virtualenv virtualenvwrapper
```

Next we need to add some helper things to our ~/.profile file. So open that
with your favorite text editor and add the following lines to the bottom of it:

```
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

Now we need to set up our virtual environment, and install all the needed
dependicies of the server. Currently, the script is looking for an
environment named cv3, though this too will be changed in the future so
that you can give the script the name of the environment you wish to use.
Enter the following commands:

```
$ source ~/.profile
$ mkvirtualenv cv3 -p python3
$ pip install Flask numpy
```

You are also going to need OpenCv installed with it being at least version
3.3.0. Instructions on a way to compile that will come later.

Once you have all of that done, you are now ready to use the script. As long
as you make sure the script is executable, you can run the script from
anywhere. Run the script anytime you want to run the server with:

```
$ cd Path/To/Flask/Server/Directory
$ ./flaskstart.sh
```

Once the server is started, you will need to do some initial set-up.
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

### Manual Method

OpenCV can be installed a couple of different ways, just make sure you have a
version that will fit the requirements. (Instructions on building OpenCV will
be added at a later point).
Using pip, we should grab all the dependencies we need when we get Flask and a
couple of other needed things:

```
$ pip install Flask numpy
```

Then clone or download the server:

```
$ git clone https://github.com/mlightning3/flask-video-streaming
```

Now connect a camera to the computer, and run:

```
$ python app.py
```

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
University of Michigan 2017-2018

All rights reserved.

Based on Miguel Grinberg's [video streaming with Flask](http://blog.miguelgrinberg.com/post/video-streaming-with-flask) 2014 under the MIT license.
[Link to Miguel's Github repo](https://github.com/miguelgrinberg/flask-video-streaming)
