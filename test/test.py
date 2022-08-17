#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def echo(*args, **kargs):
    print(args)
    print(kargs)
    print(*args)
    print(str(**kargs))
    

echo(1, 2, 3, test=4)


