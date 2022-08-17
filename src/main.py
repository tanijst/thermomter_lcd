#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time

import dht11
import mojimoji
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

import cpu_state


class LCDja(CharLCD):
    codes = u'線線線線線線線線線線線線線線線線　　　　　　　　　　'\
            u'　　　　　　　!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFG'\
            u'HIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{'\
            u'|}→←　　　　　　　　　　　　　　　　　　　　　　　　'\
            u'　　　　　　　　　。「」、・ヲァィゥェォャュョッーア'\
            u'イウエオカキクケコサシスセソタチツテトナニヌネノハヒ'\
            u'フヘホマミムメモヤユヨラリルレロワン゛゜αäβεμσρq√陰ι'\
            u'×￠￡nöpqθ∞ΩüΣπxν千万円÷　塗'

    dic = {u'ガ':u'カ゛',u'ギ':u'キ゛',u'グ':u'ク゛',\
            u'ゲ':u'ケ゛',u'ゴ':u'コ゛',u'ザ':u'サ゛',\
            u'ジ':u'シ゛',u'ズ':u'ス゛',u'ゼ':u'セ゛',\
            u'ゾ':u'ソ゛',u'ダ':u'タ゛',u'ヂ':u'チ゛',\
            u'ヅ':u'ツ゛',u'デ':u'テ゛',u'ド':u'ト゛',\
            u'バ':u'ハ゛',u'ビ':u'ヒ゛',u'ブ':u'フ゛',\
            u'ベ':u'ヘ゛',u'ボ':u'ホ゛',u'パ':u'ハ゜',\
            u'ピ':u'ヒ゜',u'プ':u'フ゜',u'ペ':u'ヘ゜',\
            u'ポ':u'ホ゜',u'℃':u'゜C'}

    def __init__(self, i2c_expander, address, port, cols, rows, dotsize, charmap, 
                auto_linebreaks, backlight_enabled, kana_mode=True) -> None:
        super().__init__(i2c_expander, address, None, port, cols, rows, dotsize, charmap, 
                auto_linebreaks, backlight_enabled)
        self._kana_mode = kana_mode
    
    def write_shift_jis(self, message: str) -> None:
        for char_index in range(len(message)):
            self.write(int(message[char_index].encode('shift-jis').hex(), 16))

    def write_string(self, message: str) -> None:
        if self._kana_mode:
            message = mojimoji.zen_to_han(message)
            message = mojimoji.han_to_zen(message, kana=True, digit=False, ascii=False)
            
            message2 = ''
            for i in range(len(message)):
                if (message[i] in self.dic.keys()):
                    message2 += self.dic[message[i]]
                else:
                    message2 += message[i]

            for i in range(len(message2)):
                if message2[i] == ' ':
                    super().write_string(message2[i])
                elif (self.codes.find(message2[i]) >= 0):
                    self.write(self.codes.find(message2[i]))
        else:
            return super().write_string(message)

    def clear_row(self, row):
        for i in range(self.lcd.cols):
            self.cursor_pos = (row, i)
            self.write(0x20)       

        self.cursor_pos = (row, 0)


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
                if args is None:
                    self.task()
                else:
                    self.task(*args)
                time.sleep(self.loop_delay)
            except Exception as err:
                print(err)
                break
            except KeyboardInterrupt:
                break


class ThermomterLCD(object):
    DHT_PIN = 17

    def __init__(self) -> None:
        self._set_gpio()
        self._thermomter_reader = dht11.DHT11(pin=self.DHT_PIN)
        self._lcd = LCDja(i2c_expander='PCF8574', address=0x27, port=1,
            cols=20, rows=4, dotsize=8, charmap='A02', 
            auto_linebreaks=True, backlight_enabled=True)
        self._temperature = 0
        self._humidity = 0
        self._cpu_temp = '0'
        self._cpu_rate = [0, 0, 0, 0]
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
        self._lcd.create_char(0, smiley)
        # self._lcd.write_string(u'\x00')
        self._lcd.write(0x00)
        sub_task = threading.Thread(target=self.sub_task, args=(5,))
        sub_task.setDaemon(True)
        sub_task.start()

        self.main_loop()

    def __del__(self) -> None:
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
        pass

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
        # self._lcd.clear_row(0)
        # if prev_str == current_str:
        self._lcd.write_string(f'Temperature: {self.temperature}℃')
        self._lcd.cursor_pos = (1, 0)
        # self._lcd.clear_row(1)
        self._lcd.write_string(f'Humidity: {self.humidity}%')
        self._lcd.cursor_pos = (2, 0)
        # self._lcd.clear_row(2)
        self._lcd.write_string(f'CPU Temp: {self.cpu_temp}℃')
        self._lcd.cursor_pos = (3, 0)
        # self._lcd.clear_row(3)
        self._lcd.write_string(f'CPU Rate: {self.cpu_rate[0]}%')

    def main_loop(self) -> None:
        while True:
            try:
                self.display_output()
                time.sleep(3)
            # except Exception as err:
            #     print(err)
            except KeyboardInterrupt:
                break

    def sub_task(self, delay):
        while True:
            try:
                self._get_thermomter()
                self._get_cpu_state(delay=delay)
                time.sleep(delay)
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    thermomter = ThermomterLCD()
    thermomter.__del__()
