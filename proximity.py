#!/usr/bin/env python

import time
import RPi.GPIO as GPIO
 
PROXIMITY = 30	# distance (cm) at which we start 'warning'
SLEEPTIME = 0.1 # delay (sec) between proximity checks

# set warnings to none
GPIO.setwarnings(False)

# set GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
 
# set GPIO Pins being used
GPIO_TRIGGER = 12
GPIO_ECHO = 18
GPIO_LED = 22
GPIO_BUZZER = 32
 
# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_BUZZER, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(GPIO_LED, GPIO.OUT, initial = GPIO.LOW)

# initialize PWM on 100Hz frequency
buzzer_PWM = GPIO.PWM(GPIO_BUZZER, 100)
led_PWM = GPIO.PWM(GPIO_LED, 100)
buzzer_PWM.start(0)
led_PWM.start(0)

def distance():
    """ return distance to any object currently being sensed """

    # set trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set trigger to LOW after 0.01 msec
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    # save time of echo send
    start_time = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
 
    # save time of arrival
    end_time = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        end_time = time.time()
 
    # multiply the time difference with the speed of sound
    # (34300 cm/s) divided by 2 (for there and back again)
    return ((end_time - start_time) * 34300) / 2
 

try:
    previous_proximity = 0

    while True:
        proximity = distance()
        print("Distance = %.1f cm" % proximity)

        if (proximity == previous_proximity): # no movement detected
            time.sleep(SLEEPTIME)
            continue

        if proximity < PROXIMITY:
            # set inverse PWM duty cycle (closer -> louder/brighter)
            duty_cycle = 100 - (proximity / PROXIMITY * 100)
        else:
            duty_cycle = 0  # 'off'
        print("PWM duty cycle: %d" % duty_cycle)

        buzzer_PWM.ChangeDutyCycle(duty_cycle)
        led_PWM.ChangeDutyCycle(duty_cycle)

        previous_proximity = proximity
        time.sleep(SLEEPTIME)

except KeyboardInterrupt:
    pass

buzzer_PWM.stop()
led_PWM.stop()
GPIO.cleanup()
