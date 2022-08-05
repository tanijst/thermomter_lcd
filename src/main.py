#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

import dht11
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

import cpu_state

DHT_PIN = 17

# 日本語も表示できるクラス
class LCD(CharLCD):
    def __init__(self, i2c_expander, address, port, cols, rows, dotsize, charmap, auto_linebreaks, backlight_enabled):
        super().__init__(i2c_expander, address, None, port, cols, rows, dotsize, charmap, auto_linebreaks, backlight_enabled)
    
    def output(self, *args :str):
        i = 0
        for arg in args:
            self.cursor_pos = (i, 0)
            print(arg)
            if not arg is None:
                self.write_string(arg)
            i += 1
        
    def japanese(self):
        pass

class ThermomterLCD(object):
    #DHT_PIN = 17
    def __init__(self):
        self._set_gpio()
        self._thermomter_reader = dht11.DHT11(pin=DHT_PIN)
        self._lcd = LCD(i2c_expander='PCF8574', address=0x27, port=1,
            cols=20, rows=4, dotsize=8, charmap='A02', 
            auto_linebreaks=True,
            backlight_enabled=True)
        self.main_loop()
         
    def __del__(self):
        GPIO.cleanup()
        self._lcd.clear()
    
    def _set_gpio(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

    def _get_thermomter(self):
        result = self._thermomter_reader.read()
        #print(result.is_valid())
        if not result.is_valid():
            return None, None
        return str(result.temperature), str(result.humidity)

    # TODO イテレータで受け取るようにする
    def _output_handler(self, temperature: int, humidity: int, cpu_temp: str, cpu_rate: list):
        str_temp = None
        str_humi = None
        if not temperature is None:
            str_temp = f'Temperature: {temperature}'
        if not humidity is None:
            str_humi = f'Humidity: {humidity}'
        str_cpu_temp = f'CPU Temp: {cpu_temp}'
        str_cpu_rate = f'CPU Rate: {cpu_rate[0]}'
        self._lcd.output(str_temp, str_humi, str_cpu_temp, str_cpu_rate)

    def main_loop(self):
        while True:
            try:
                time.sleep(1)
                temperature, humidity = self._get_thermomter()
                cpu_temp = cpu_state.get_cpu_temp()
                cpu_rate = cpu_state.get_cpu_rate()
                self._output_handler(temperature, humidity, cpu_temp, cpu_rate)
            except Exception as err:
                print(err)
            except KeyboardInterrupt:
                break

if __name__ == '__main__':
    ThermomterLCD()