#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from typing import Any

import dht11
import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

import cpu_state

DHT_PIN = 17

class LCD(CharLCD):
    def __init__(self, i2c_expander, address, port, cols, rows, dotsize, charmap, auto_linebreaks, backlight_enabled) -> None:
        super().__init__(i2c_expander, address, None, port, cols, rows, dotsize, charmap, auto_linebreaks, backlight_enabled)
    
    def write_shift_jis(self, message: str) -> None:
        for char_index in range(len(message)):
            self.write(int(message[char_index].encode('shift-jis').hex(), 16))

    def write_string(self, message: str, kana_mode: bool=True) -> None:
        # クラス変数にする
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

        if kana_mode:
            message2 = ''
            for i in range(len(message)):
                if (message[i] in dic.keys()):
                    message2 += dic[message[i]]
                else:
                    message2 += message[i]

            for i in range(len(message2)):
                if message2[i] == ' ':
                    super().write_string(message2[i])
                elif (codes.find(message2[i]) >= 0):
                    self.write(codes.find(message2[i]))

        else:
            return super().write_string(message)
        # TODO create_charでバイトコードを渡すと動作しない

class ThermomterLCD(object):
    #DHT_PIN = 17
    # lcd backlight_enabled
    def __init__(self):
        self._set_gpio()
        self._thermomter_reader = dht11.DHT11(pin=DHT_PIN)
        self._lcd = LCD(i2c_expander='PCF8574', address=0x27, port=1,
            cols=20, rows=4, dotsize=8, charmap='A02', 
            auto_linebreaks=True, backlight_enabled=True)
        self._temperature = None
        self._humidity = None
        self._cpu_temp = None
        self._cpu_rate = None
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
        self._lcd.write_string(u'\x00', False)
        print('start')
        time.sleep(0.5)
        self.main_loop()

    def __del__(self):
        GPIO.cleanup()
        self._lcd.clear()

    @property
    def cpu_temp(self):
        self._cpu_temp = cpu_state.get_cpu_temp()
        return self._cpu_temp

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
            str_temp = f'Temperature: {temperature}℃'
        if not humidity is None:
            str_humi = f'Humidity: {humidity}%'
        str_cpu_temp = f'CPU Temp: {cpu_temp}℃'
        str_cpu_rate = f'CPU Rate: {cpu_rate[0]}%'
        # Noneのとき
        self._lcd.cursor_pos = (0, 0)
        self._lcd.write_string(str_temp)
        self._lcd.cursor_pos = (1, 0)
        self._lcd.write_string(str_humi)
        self._lcd.cursor_pos = (2, 0)
        self._lcd.write_string(str_cpu_temp)
        self._lcd.cursor_pos = (3, 0)
        self._lcd.write_string(str_cpu_rate)

    # backlight_enabledを有効無効にできるようにする
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
    