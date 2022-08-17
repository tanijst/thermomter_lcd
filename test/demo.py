#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time

import HD44780 as LCD
from RPLCD.i2c import CharLCD


def hd44():
    lcd = LCD.HD44780('lcdsample.conf')
    lcd.init()
    #            0123456789012345
    # lcd.message('https://raspberr', 1)
    # lcd.message('ypi.mongonta.com', 2)
    lcd.message('コンニチハ', 3)
    lcd.message('オンド℃千', 4)

def charlcd():
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
        cols=20, rows=4, dotsize=8, charmap='A02', 
        auto_linebreaks=True,
        backlight_enabled=True)

    lcd.clear()
    lcd.cursor_pos = (0, 0)
    # shift-jisの決まったバイトコードを送る1byte
    # lcd.write(177)
    lcd.write(0xb1)
    lcd.write(0xb5) # オ 181
    lcd.write(182) #カ
    lcd.write(183)
    lcd.write(221)
    lcd.write(250) # 温度
    lcd.write(251)
    lcd.cursor_pos = (1, 0)
    lcd.write(0x84)
    lcd.write(0x01)
    lcd.write(0x26)
    lcd.write(0x25)
    lcd.cursor_pos = (2, 0)
    data = 'ｺﾝﾆﾁ'
    data = data.encode('shift-jis')
    print(data)
    lcd.write_string(b'\x89\xb9')
    lcd.write(252)
    # 221, 8, 193
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
    lcd.create_char(0, smiley)
    lcd.cursor_pos = (3, 0)
    lcd.write_string(u'\x00')
    # lcd.write_string(u'Temperature: 30\xc3C')
    lcd.cursor_pos = (0, 0)
    time.sleep(1)
    # for i in range(20):
    #     lcd.cursor_pos = (0, i)
    #     # lcd.write(0x20)

# hd44()
charlcd()