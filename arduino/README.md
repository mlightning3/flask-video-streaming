This folder holds all the versions of the software that runs on the companion
board for the Otoscope system. All communication happens over serial, with
the flask server using trinket.py (which is incorrectly named since we don't
use a trinket any more).

At a minimum, the companion board is responsible for controlling a light.
Additional sensors may be connected to it and then the information can be
passed back to the flask server.
