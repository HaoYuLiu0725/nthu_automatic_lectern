#!/usr/bin/env python3
# coding: utf-8
from gpiozero import Button, LED
from signal import pause
import os, sys

offGPIO = int(sys.argv[1]) if len(sys.argv) >= 2 else 21 # default: use GPIO21(pin 40) for button
holdTime = int(sys.argv[2]) if len(sys.argv) >= 3 else 5 # default: press 5 second to shutdown 
ledGPIO = int(sys.argv[3]) if len(sys.argv) >= 4 else 13 # default: use GPIO13(pin 33) for LED

def when_pressed():
    # start blinking with 0.5 second rate
    led.blink(on_time=0.5, off_time=0.5)

def when_released():
    # turn on LED as default, indicate this script is running
    led.on()

def shutdown():
    print("going to 'sudo shutdown now' process")
    os.system("sudo shutdown now")
    

led = LED(ledGPIO)
led.on()
btn = Button(offGPIO, hold_time=holdTime)
btn.when_held = shutdown
btn.when_pressed = when_pressed
btn.when_released = when_released
pause()