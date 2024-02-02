#!/usr/bin/python3

# main idea is taken from https://github.com/whofferbert/rpi-midi-rotary-encoder/blob/master/rotary_encoder.py
# by William Hofferbert which I heartfully thank!

import RPi.GPIO as GPIO
import time
import mido
import os
import re

#initialize
mido.set_backend('mido.backends.rtmidi')
# we know that by default on patchbox OS there are 2 midi ports in passthrough mode, the second one is for touchosc, so it's plugged into depmod
output_name=mido.get_output_names()[1]

def send_cc(channel, ccnum, val):
  msg = mido.Message('control_change', channel=channel, control=ccnum, value=val)
  output = mido.open_output(output_name)
  output.send(msg)
