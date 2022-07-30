#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

import dht11
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

import cpu_state

DHT_PIN = 17

def set_gpio():
    # initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    #GPIO.cleanup().

def lcd_init():
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
            cols=20, rows=4, dotsize=8, charmap='A02', 
            auto_linebreaks=True,
            backlight_enabled=True)
    return lcd

def thermomter():
    set_gpio()
    thermomter_reader = dht11.DHT11(pin=DHT_PIN)
    result = thermomter_reader.read()
    return result

def lcd_echo(lcd: CharLCD, temperature: str, humidity):
    #lcd.clear()
    lcd.write_string(f'Temperature: {temperature:-3.1f}')
    lcd.cursor_pos = (1, 0)
    lcd.write_string(f'humidity: {humidity:-3.1f}')
    lcd.cursor_pos = (2, 0)
    cpu_temp = cpu_state.get_cpu_temp()
    cpu_rate = cpu_state.get_cpu_rate()
    lcd.write_string(f'CpuTemp: {cpu_temp}')
    lcd.cursor_pos = (3, 0)
    lcd.write_string(f'CpuRate: {cpu_rate[0]}')
    lcd.cursor_pos = (0, 0)
    return
    
def main():
    lcd = lcd_init()
    while True:
        try:
            time.sleep(1)
            read_result = thermomter()
            if read_result.is_valid():
                lcd_echo(lcd, read_result.temperature, read_result.humidity)
            else:
                # error code
                pass
        except Exception as err:
            print(err)
            break
        except KeyboardInterrupt:
            break

    GPIO.cleanup()
    lcd.clear()

if __name__ == '__main__':
    main()