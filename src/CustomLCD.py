import mojimoji
from RPLCD.i2c import CharLCD


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

    def clear_row(self, row: int) -> None:
        for i in range(self.lcd.cols):
            self.cursor_pos = (row, i)
            self.write(0x20)       

        self.cursor_pos = (row, 0)
