#!/usr/bin/env python3
# -*- coding: utf-8 -*
import subprocess
import time

# 温度表示
# GPU: sudo /opt/vc/bin/vcgencmd measure_temp
# CPU: vcgencmd measure_temp

# CPU使用率表示

def cmd_run(cmd: str):
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, text=True)
    # result.stdout.splitlines()
    # result.stdout.split('=')

def get_cpu_temp():
    test_cmd = 'vcgencmd measure_temp'
    return cmd_run(test_cmd).stdout.split('=')

def get_cpu_state():
    cpu_sum = 'cat /proc/stat | grep cpu'
    result = cmd_run(cpu_sum).stdout.splitlines()
    result_list = []
    for line in result:
        #print(line)
        cpu_state_list = line.split()
        idle_time = int(cpu_state_list[4])
        busy_time = (int(cpu_state_list[1])
                    + int(cpu_state_list[2]) + int(cpu_state_list[3]))
        all_time = busy_time + idle_time
        result_list.append([busy_time, all_time])
    return result_list

def cpu_rate_mesure(pre_cpu_rate: list):
    # list[busy_time, all_time]
    now_cpu_rate = get_cpu_state()
    cpu_rate_list = []
    for pre, now in zip(pre_cpu_rate, now_cpu_rate):
        diff = [now - pre for pre, now in zip(pre, now)]
        diff_busy = diff[0]
        diff_all = diff[1]
        cpu_rate = int(diff_busy * 100 / diff_all)
        cpu_rate_list.append(cpu_rate)
    
    return cpu_rate_list

def test_():
    #CPU(arm)メモリ使用量
    cpu_cmd = 'vcgencmd get_mem arm'
    result = cmd_run(cpu_cmd)
    print(f'CPU: {result}')

    # GPUのメモリ使用量
    gpu_cmd = 'vcgencmd get_mem gpu'
    result = cmd_run(gpu_cmd)
    print(f'GPU: {result}')

def main():
    cpu_state = get_cpu_state()
    time.sleep(1)
    
    cpu_state = cpu_rate_mesure(cpu_state)
    msg = (f'CPU: {cpu_state[0]} CPU-0: {cpu_state[1]} CPU-1: {cpu_state[2]} CPU-2: {cpu_state[3]} CPU-3: {cpu_state[4]}')
    print(msg)
    print(f'CPU温度: {int(get_cpu_temp()[1]):4d}')

if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
