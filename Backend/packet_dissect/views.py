from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse
from packet_dissect.models import packet
import queue
import socket
from threading import Thread
from django.core.cache import cache

indexPaging = {"ether_point":"ether_endpoints", "ip_point":"ip_endpoints", "ether_conv":"ether_conv", "ip_conv":"ip_conv"}
pageCount = 20
q_file = queue.Queue(10)

def stream():
    def event_stream():
        while True:
            if not q_file.empty():
                # mutex.acquire()
                file_tmp = q_file.get()
                # mutex.release()                
                res_packet.add(packet(file_tmp))
                data_tmp = {"ether_point":res_packet.ether_endpoints, "ip_point":res_packet.ip_endpoints, "ether_conv":res_packet.ether_conv, "ip_conv":res_packet.ip_conv}
                data[file] = data_tmp
                pageNum_ip_endpoints = len(res_packet.ip_endpoints['data'][0])/pageCount
                if(len(res_packet.ip_endpoints['data'][0]) % pageCount != 0):
                    pageNum_ip_endpoints = pageNum_ip_endpoints + 1
                pageNum_ip_conv = len(res_packet.ip_conv['data'][0])/pageCount
                if(len(res_packet.ip_conv['data'][0]) % pageCount != 0):
                    pageNum_ip_conv = pageNum_ip_conv + 1
                res_list = [res_packet.outline, res_packet.len_packet, res_packet.ether_endpoints, pageNum_ip_endpoints, res_packet.ether_conv, pageNum_ip_conv, res_packet.protos]
                yield f'data: {res_list}\n\n'
    response = Response(stream_with_context(event_stream()), mimetype='text/event-stream')
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

def serve():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_port = ("0.0.0.0", 21347)
    server.bind(ip_port)
    server.listen(1)
    buf,client = server.accept()
    while True:
        data = buf.recv(1024).decode('utf-8')
        if data == 'exit':
            break
        else:
            # mutex.acquire()
            q_file.put(data)
            # mutex.release()

# Create your views here.
def packet_outline(request):
    rb = request.GET.get('file')
    value = cache.get(rb)
    if value:
        res_packet = value
    else:
        res_packet = packet(rb)
        cache.set(rb, res_packet, timeout=24*60*60)
    pageNum_ip_endpoints = len(res_packet.ip_endpoints['data'][0])/pageCount
    if(len(res_packet.ip_endpoints['data'][0]) % pageCount != 0):
        pageNum_ip_endpoints = pageNum_ip_endpoints + 1
    pageNum_ip_conv = len(res_packet.ip_conv['data'][0])/pageCount
    if(len(res_packet.ip_conv['data'][0]) % pageCount != 0):
        pageNum_ip_conv = pageNum_ip_conv + 1
    res_list = [res_packet.outline, res_packet.len_packet, res_packet.ether_endpoints, pageNum_ip_endpoints, res_packet.ether_conv, pageNum_ip_conv, res_packet.protos]
    return JsonResponse(res_list, safe=False)

def packet_main(request):
    rb = request.GET.get('file')
    return render(request, 'packet_main.html', {"file": rb})

def fragment_data(request):
    page = request.GET.get("pageIndex")
    item = request.GET.get("item")
    rb = request.GET.get('file')
    value = cache.get(rb)
    page_data = eval("value."+indexPaging[item])['data']
    page_index = eval("value."+indexPaging[item])['filed']
    if value:
        res_data = []
        if(int(page)*pageCount > len(page_data[0])):
            for i in range(len(page_data)):
                res_data.append(page_data[i][(int(page)-1)*pageCount:])
        else:
            for i in range(len(page_data)):
                res_data.append(page_data[i][(int(page)-1)*pageCount:(int(page))*pageCount])
        res = {'filed':page_index,'data':res_data}
        return JsonResponse(res, safe=False)
    else:
        res = {'filed':"error", 'data':"请求数据已失效"}
        return JsonResponse(res, safe=False)
    