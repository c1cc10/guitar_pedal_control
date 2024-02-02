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

les_states = [GPIO.LOW, GPIO.HIGH]

def read_button_state(button):
  btn_state =  GPIO.input(btn1)
  midi_state = 127 * btn_state
  send_cc(button_channel, button_cc_num, midi_state)
  GPIO.output(self.led1, led_states[btn_state])

# MAIN #
if __name__=="__main__":
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  GPIO.setup(led1,GPIO.OUT)
  GPIO.setup(led2,GPIO.OUT)
  GPIO.setup(led3,GPIO.OUT)
  GPIO.setup(led4,GPIO.OUT)
        
  GPIO.setup(btn1,GPIO.IN)
  GPIO.setup(btn2,GPIO.IN)
  GPIO.setup(btn3,GPIO.IN)
  GPIO.setup(btn4,GPIO.IN)
  GPIO.setup(rotary_clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(rotary_data, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(rotary_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
        
  GPIO.add_event_detect(btn1,GPIO.BOTH,callback=button_1_push)

  # rotary encoder
  #GPIO.add_event_detect(rotary_clk,GPIO.BOTH,callback=rotary_callback)
