#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import subprocess
import sys

def GetCpuFreq():
    Cmd = "vcgencmd measure_clock arm"
    res = subprocess.Popen(Cmd, shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
    Rstdout, Rstderr = res.communicate()
    CpuFreq = Rstdout.split("=")
    return int(CpuFreq[1])

def GetCpuTemp():
    Cmd = "vcgencmd measure_temp"
    res = subprocess.Popen(Cmd, shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
    Rstdout, Rstderr = res.communicate()
    Cputemp = Rstdout.split()
    return Cputemp[0]

def GetCpuStat():
    Cmd = "cat /proc/stat | grep cpu"
    res = subprocess.Popen(Cmd, shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
    Rstdout,Rstderr = res.communicate()
    #  行ごとに分割
    LineList = Rstdout.splitlines()
    Tcklist = []
    for line in LineList:
        ItemList = line.split()
        Idle = int(ItemList[4])
        Busy = int(ItemList[1]) + int(ItemList[2]) + int(ItemList[3])
        All = Busy + Idle
        Tcklist.append([ Busy, All ])
    # tcklist = [CPU[busy, all], CPU0[busy, all], ]
    return Tcklist

class CpuUsage:
    def __init__(self):
        self.__Tcklist = GetCpuStat()

    def get(self):
        # 前回値を入れる
        TcklistPre = self.__Tcklist
        # 現在の値を入れる
        TcklistNow = GetCpuStat()
        self.__Tcklist = TcklistNow
        CpuRateList = []
        # リストを取り出す
        for (TckNow, TckPre) in zip(TcklistNow, TcklistPre):
            # リストを取り出して両方の差分をリストに格納
            Diff = [ Now - Pre for (Now, Pre) in zip(TckNow, TckPre) ]
            Busy = Diff[0]
            All = Diff[1]
            CpuRate = int(Busy * 100 / All)
            CpuRateList.append(CpuRate)
        return CpuRateList

if __name__ == "__main__":
    #  初期化
    gCpuUsage = CpuUsage()
    for ix in range(10000):
        time.sleep(1)
        CpuRateList = gCpuUsage.get()
        CpuRate = CpuRateList[0]
        CpuRate_str = "CPU:{:3d}".format(CpuRate)
        # 残りのリストを表示するために削除
        del CpuRateList[0]
        Cputemp = GetCpuTemp()
        CpuFreq = int(GetCpuFreq() / 1000000)
        CpuFreq_str = "ARM {:4d}MHz".format(CpuFreq)
        Info_str = CpuFreq_str + "\t" + Cputemp + "\t" + CpuRate_str + "%"
        print(Info_str, CpuRateList)
