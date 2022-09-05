#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time

import dht11
import RPi.GPIO as GPIO

import cpu_state
import CustomLCD

class TaskManager(object):
    def __init__(self, task, args=(), loop_delay: float=1.0) -> None:
        self.task = task
        self.task_args = args
        self.loop_delay = loop_delay
        self.loop_task = threading.Thread(target=self.task_loop, args=self.task_args) 
        self.loop_task.setDaemon(True)
        self.loop_task.start()

    def task_loop(self, *args) -> None:
        while True:
            try:
                self.task(*args)
                time.sleep(self.loop_delay)
            except Exception as err:
                print(err)
                break
            except KeyboardInterrupt:
                break


class Node(object):
    def __init__(self, data: str) -> None:
        self.current_data = data
        self.previous_data = None

class ThermomterLCD(object):
    DHT_PIN = 17

    def __init__(self) -> None:
        self._set_gpio()
        self._thermomter_reader = dht11.DHT11(pin=self.DHT_PIN)
        self._lcd = CustomLCD.LCDja(i2c_expander='PCF8574', address=0x27, port=1,
            cols=20, rows=4, dotsize=8, charmap='A02', 
            auto_linebreaks=True, backlight_enabled=True)
        self._temperature = 0
        self._humidity = 0
        self._cpu_temp = '0'
        self._cpu_rate = [0, 0, 0, 0]
        self.temp_node = Node(self._temperature)
        self.humi_node = Node(self._humidity)
        self.cpu_temp_node = Node(self._cpu_temp)
        self.cpu_rate_node = Node(self._cpu_rate[0])
        self._create_char()
        self._lcd.write(0x00)
        TaskManager(task=self._get_cpu_state, args=(5,), loop_delay=2)
        TaskManager(task=self._get_thermomter, loop_delay=2)

        self.main_loop()

    # def __del__(self) -> None:
    #     GPIO.cleanup()
    #     self._lcd.clear()

    def destroy(self) -> None:
        GPIO.cleanup()
        self._lcd.clear()

    @property
    def temperature(self) -> int:
        return self._temperature

    @property
    def humidity(self) -> int:
        return self._humidity
    
    @property
    def cpu_temp(self) -> str:
        return self._cpu_temp

    @property
    def cpu_rate(self) -> list:
        return self._cpu_rate

    def _create_char(self) -> None:
        smiley = (
            0b00000,
            0b01010,
            0b01010,
            0b00000,
            0b10001,
            0b10001,
            0b01110,
            0b00000,
        )
        self._lcd.cursor_pos = (3, 19)
        self._lcd.create_char(location=0, bitmap=smiley)

    def _set_gpio(self) -> None:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

    def _get_thermomter(self) -> None:
        result = self._thermomter_reader.read()
        if result.is_valid():
            self._temperature = result.temperature
            self._humidity = result.humidity

    def _get_cpu_state(self, delay: int) -> None:
        self._cpu_temp = cpu_state.get_cpu_temp()
        self._cpu_rate = cpu_state.get_cpu_rate(delay=delay)

    def display_output(self) -> None:
        self._lcd.cursor_pos = (0, 0)
        if len(str(self.temp_node.current_data)) != len(str(self.temperature)):
            self._lcd.clear_row(0)
        self.temp_node.current_data = self.temperature
        self._lcd.write_string(f'Temperature: {self.temperature}℃')

        self._lcd.cursor_pos = (1, 0)
        if len(str(self.humi_node.current_data)) != len(str(self.humidity)):
            self._lcd.clear_row(1)
        self.humi_node.current_data = self.humidity
        self._lcd.write_string(f'Humidity: {self.humidity}%')

        self._lcd.cursor_pos = (2, 0)
        if len(str(self.cpu_temp_node.current_data)) != len(str(self.cpu_temp)):
            self._lcd.clear_row(2)
        self.cpu_temp_node.current_data = self.cpu_temp
        self._lcd.write_string(f'CPU Temp: {self.cpu_temp}℃')

        self._lcd.cursor_pos = (3, 0)
        if len(str(self.cpu_rate_node.current_data)) != len(str(self.cpu_rate[0])):
            self._lcd.clear_row(3)
        self.cpu_rate_node.current_data = self.cpu_rate[0]
        self._lcd.write_string(f'CPU Rate: {self.cpu_rate[0]}%')

    def main_loop(self) -> None:
        while True:
            try:
                self.display_output()
                time.sleep(3)
            except Exception as err:
                print(err)
            except KeyboardInterrupt:
                break

    
if __name__ == '__main__':
    thermomter = ThermomterLCD()
    time.sleep(0.3)
    thermomter.destroy()
    