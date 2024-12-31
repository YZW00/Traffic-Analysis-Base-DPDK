import os
import json
import signal
import threading
import subprocess
import sys
from .mapl_skt import start_socket_daemon

from django.http import HttpResponse, JsonResponse

DEV_NUMS = 1

DEFAULT_SNAPLEN = 64
DEFAULT_FILE_SIZE = 200         # 以MB为单位
DEFAULT_INTERVAL = 1            # 默认的统计时间间隔

SOCKET_RES_LEN = 1024

if "runserver" in sys.argv:
    socket_daemon = threading.Thread(target=start_socket_daemon)
    socket_daemon.daemon = True
    socket_daemon.start()

capture_process: subprocess.Popen = None
feature_process: subprocess.Popen = None

def capture_handler(snaplen, timeout, filesize, port, ip, protocol, send_timeval):
    global capture_process
    capture_process = subprocess.Popen(
        args=["/app/classify/dpdk_anomaly_flow_detector",
              "--", "-s", str(snaplen), "-T", str(timeout), "-C", str(filesize),
              "-P", str(port), "-I", str(ip), "--protocol", str(protocol), "--send", str(send_timeval)
        ],
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stderr,
        preexec_fn=os.setpgrp
    )
    return

def stop_capture(request):
    global capture_process
    if capture_process and capture_process.poll() is None:
        pid = capture_process.pid
        os.killpg(os.getpgid(pid), signal.SIGINT) 
        capture_process.wait()
        return JsonResponse({'status': 'Capture Stoped'})
    else:
        print("[debug]", capture_process and capture_process.poll())
        return JsonResponse({'status': 'Nothing to do'})

def start_capture(request):
    global capture_process
    timeout = 10    # 以s为单位  
    port = 0
    ip = "0"
    protocol = 0

    if capture_process and capture_process.poll() is None:
        return JsonResponse({'status': 'Capture Busy'})
    
    if request.method == "POST":
        rb = json.loads(request.body)
        # 获取request请求中的抓包时间和端口
        if 'timeout' in rb and rb['timeout'] != None:
            timeout = rb['timeout']
        if 'port' in rb and rb['port'] != None:
            port = rb['port']
        if 'ip' in rb and rb['ip'] != None:
            ip = rb['ip']
        if 'protocol' in rb and rb['protocol'] != None:
            protocol = rb['protocol']

    # 执行抓包程序
    send_timeval = max(timeout / SOCKET_RES_LEN, DEFAULT_INTERVAL)
    capture_handler(DEFAULT_SNAPLEN, timeout, DEFAULT_FILE_SIZE, port, ip, protocol, send_timeval)
    if not capture_process:
        return JsonResponse({'status': 'Capture Error'})

    return HttpResponse(json.dumps({'status': 'Capture Success', 'timeout': timeout, 'ip': ip, 'port': port, 'protocol': protocol}), content_type='application/json')

def start_feature_extract(request):
    global feature_process
    timeout = 10    # 以s为单位  
    port = 0
    ip = "0"
    protocol = 0

    if feature_process and feature_process.poll() is None:
        return JsonResponse({'status': 'Capture Busy'})
    
    if request.method == "POST":
        rb = json.loads(request.body)
        # 获取request请求中的抓包时间和端口
        if 'timeout' in rb and rb['timeout'] != None:
            timeout = rb['timeout']
        if 'port' in rb and rb['port'] != None:
            port = rb['port']
        if 'ip' in rb and rb['ip'] != None:
            ip = rb['ip']
        if 'protocol' in rb and rb['protocol'] != None:
            protocol = rb['protocol']

    feature_process = subprocess.Popen(
        args=["/app/classify/dpdk_feature_extractor",
              "--", "-s", str(DEFAULT_SNAPLEN), "-T", str(timeout),
              "-P", str(port), "-I", str(ip), "--protocol", str(protocol)
        ],
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stderr,
        preexec_fn=os.setpgrp
    )
    if not feature_process:
        return JsonResponse({'status': 'Capture Error'})

    return HttpResponse(json.dumps({'status': 'Capture Success', 'timeout': timeout, 'ip': ip, 'port': port, 'protocol': protocol}), content_type='application/json')

def stop_feature_extract(request):
    global feature_process
    if feature_process and feature_process.poll() is None:
        pid = feature_process.pid
        os.killpg(os.getpgid(pid), signal.SIGINT) 
        feature_process.wait()
        return JsonResponse({'status': 'Capture Stoped'})
    else:
        print("[debug]", feature_process and feature_process.poll())
        return JsonResponse({'status': 'Nothing to do'})


# 获取pcap包信息
def view_pcaps(request):
    time = ""
    if request.GET.get("time"):
        time = request.GET.get("time")      # 类似20221219-160000(可以只写一部分)
    # user = request.GET.get('user')
    # dirname = '/home/Pcaps/'+ user + '/' + time
    # ansible_command = 'ansible -i /etc/ansible/hosts webservers -m shell -a "ls -lh '+ dirname +'/*.pcap"'
    ls_command = "ls -lh /data/pcaps/output-{}*.pcap".format(time)

    print("***************************")

    command_output = os.popen(ls_command).read().strip()

    all_pcap_file = []

    if command_output != "":
        for line in command_output.split('\n'):
            contens = line.split()
            pcap_infos = dict.fromkeys(['file', 'dir', 'size', 'time'])
            pcap_infos['file'] = os.path.basename(contens[8])
            pcap_infos['dir'] = os.path.dirname(contens[8])
            pcap_infos['size'] = contens[4]
            pcap_infos['time'] = "{} {} {}".format(contens[5], contens[6], contens[7])
            
            all_pcap_file.append(pcap_infos)

    file_json = {"pcap_files": all_pcap_file}

    response_json = json.dumps(file_json)

    return HttpResponse(response_json, content_type='application/json')
