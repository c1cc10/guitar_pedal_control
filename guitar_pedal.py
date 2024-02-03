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

rotary_clk = 20
rotary_data = 26
rotary_button = 21

led_states = [GPIO.LOW, GPIO.HIGH]

def send_cc(channel, ccnum, val):
  msg = mido.Message('control_change', channel=channel, control=ccnum, value=val)
  output = mido.open_output(output_name)
  output.send(msg)

def read_button_state(button, led):
  global led_states
  btn_state =  GPIO.input(button)
  midi_state = 127 * btn_state
  send_cc(0, button, midi_state)
  GPIO.output(led, led_states[btn_state])

def button_1_push(btn):
  read_button_state(btn1, led1)

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
  GPIO.add_event_detect(btn1, GPIO.BOTH, callback=button_1_push, bouncetime=220)

  # rotary encoder
  #GPIO.add_event_detect(rotary_clk,GPIO.BOTH,callback=rotary_callback)
  # keep running
  while True:
    time.sleep(0.3)
  GPIO.cleanup()
