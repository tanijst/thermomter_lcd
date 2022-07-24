#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from RPLCD.i2c import CharLCD
# from RPLCD.gpio import CharLCD
# i2c address 0x27 
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
        cols=20, rows=4, dotsize=8, charmap='A02', 
        auto_linebreaks=True,
        backlight_enabled=True)

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

def main(): 
    #lcd.clear()
    lcd.write_string('Hello world')
    lcd.cursor_pos = (2, 0)
    lcd.create_char(0, smiley)
    lcd.write_string('Hello there \x03')
    time.sleep(1)
    lcd.clear()

if __name__ == '__main__':
    main()
