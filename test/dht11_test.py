#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

import RPi.GPIO as GPIO
import dht11

def set_gpio():
    # initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    #GPIO.cleanup()

def main():
    print('start')
    while True:
        try:
            set_gpio()
            instance = dht11.DHT11(pin=17)
            result = instance.read()
            if result.is_valid():
                print("Temperature: %-3.1f C" % result.temperature)
                print("Humidity: %-3.1f %%" % result.humidity)
            else:
                #print("Error: %d" % result.error_code)
                pass
            time.sleep(1)
        except KeyboardInterrupt:
            break
        finally:
            GPIO.cleanup()
    
if __name__ == '__main__':
    #instance = dht11.DHT11(pin=17)
    main()
