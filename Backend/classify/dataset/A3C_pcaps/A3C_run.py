import datetime
import time
import subprocess
import os
import sys

A3C_path = './A3C_Linux'    # A3C 可执行文件路径
net_interface_id = int(sys.argv[1])      # 要监听的网卡id  1
listen_Delay = int(sys.argv[2])          # 单次监听时长(秒)  300

def listen(delay):
    A3C_pro = None
    try:
        logFile = open('log.txt', 'a')
        logFile.write('\nNew subProcess Start listening at {}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
        A3C_pro = subprocess.Popen(A3C_path, stdin=subprocess.PIPE, stdout=logFile, stderr=subprocess.STDOUT)
        A3C_pro.stdin.write('{}\n'.format(net_interface_id).encode('utf-8'))
        A3C_pro.stdin.flush()
        print("A3C进程 {} 启动".format(A3C_pro.pid))
        time.sleep(delay)
    except Exception as e:
        print(e)
    finally:
        if A3C_pro:
            A3C_pro.terminate()
            print("A3C进程 {} 结束".format(A3C_pro.pid))
            logFile.write('\nsubProcess {} End at {}\n'.format(A3C_pro.pid, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")))
            A3C_pro.kill()
        else:
            print('A3C进程启动失败')
        logFile.close()
    
if __name__ == '__main__':
    while(True):
        listen(listen_Delay)
        time.sleep(3)