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
led1 = 23
led2 = 27
led3 = 18
led4 = 4
        
btn1 = 22
btn2 = 17
btn3 = 15
btn4 = 14

encoder_clk = 20
encoder_data = 26
encoder_button = 21

def send_cc(channel, ccnum, val):
  msg = mido.Message('control_change', channel=channel, control=ccnum, value=val)
  output = mido.open_output(output_name)
  output.send(msg)

# MAIN #
if __name__=="__main__":
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(self.led1,GPIO.OUT)
  GPIO.setup(self.led2,GPIO.OUT)
  GPIO.setup(self.led3,GPIO.OUT)
  GPIO.setup(self.led4,GPIO.OUT)
        
  GPIO.setup(self.btn1,GPIO.IN)
  GPIO.setup(self.btn2,GPIO.IN)
  GPIO.setup(self.btn3,GPIO.IN)
  GPIO.setup(self.btn4,GPIO.IN)
  GPIO.setup(self.encoder_clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(self.encoder_data, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(self.encoder_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
  GPIO.add_event_detect(dt_pin,GPIO.FALLING,callback=button_push)

  # rotary encoder
  GPIO.add_event_detect(clk_pin,GPIO.BOTH,callback=rotary_callback)
