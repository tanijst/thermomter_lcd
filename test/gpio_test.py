#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

test1_pin = 17
test2_pin = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(test1_pin, GPIO.IN, GPIO.PUD_UP)
#GPIO.setup(test2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(test2_pin, GPIO.IN)

def main():
    res = []
    while True:
        try:
            res = [GPIO.input(test1_pin), GPIO.input(test2_pin)]
            #res = GPIO.input(test2_pin)
            print(f'pin {test1_pin}: {res[0]} pin {test2_pin}: {res[1]}')
            #print(f'pin {test2_pin}: {res}')
            #print(f'GPIO: LOW {GPIO.LOW} HIGH {GPIO.HIGH}')
            time.sleep(1)
        except KeyboardInterrupt:
            break

def destory():
    GPIO.cleanup()

if __name__ == '__main__':
    main()
    destory()
