#!/usr/bin/env python3
# -*- coding: utf-8 -*
import subprocess
import time

def _com_run(cmd: str):
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, text=True)

def get_cpu_temp() -> str:
    test_cmd = 'vcgencmd measure_temp'
    result = _com_run(test_cmd).stdout.split('=')
    cpu_temp = result[1]
    return cpu_temp[:4]

def _cmd_cpu_rate() -> list:
    # list[busy_time, all_time]
    cpu_cmd = 'cat /proc/stat | grep cpu'
    result = _com_run(cpu_cmd).stdout.splitlines()
    result_list = []
    for line in result:
        cpu_state_list = line.split()
        idle_time = int(cpu_state_list[4])
        busy_time = (int(cpu_state_list[1])
                    + int(cpu_state_list[2]) + int(cpu_state_list[3]))
        all_time = busy_time + idle_time
        result_list.append([busy_time, all_time])
    return result_list

def get_cpu_rate(delay: int=1) -> list:
    pre_cpu_rate = _cmd_cpu_rate()
    time.sleep(delay)
    now_cpu_rate = _cmd_cpu_rate()
    cpu_rate_list = []
    for pre, now in zip(pre_cpu_rate, now_cpu_rate):
        diff = [now - pre for pre, now in zip(pre, now)]
        diff_busy = diff[0]
        diff_all = diff[1]
        cpu_rate = int(diff_busy * 100 / diff_all)
        cpu_rate_list.append(cpu_rate)
    return cpu_rate_list

def main():
    cpu_state = get_cpu_rate(delay=1)
    print(f'CPU使用率: {cpu_state[0]} CPU-0: {cpu_state[1]} CPU-1: {cpu_state[2]} CPU-2: {cpu_state[3]} CPU-3: {cpu_state[4]}')
    print(f'CPU温度: {get_cpu_temp()}')

if __name__ == '__main__':
    while True:
        try:
            main()
            time.sleep(1)
        except KeyboardInterrupt:
            break
