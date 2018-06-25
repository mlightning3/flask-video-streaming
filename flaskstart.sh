#!/bin/bash

## Flask Start Script
#
# Sets up everything required to run the Flask server. Useful for running at
# boot, or when you need to start it manually but don't want to remember all
# the steps involved.
#
# Copyright University of Michigan 2018

source ~/.profile
workon cv3
cd ~/projects/umich/flask-video-streaming
python app.py