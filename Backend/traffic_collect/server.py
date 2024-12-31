import queue
import socket
import threading
import sys
import asyncio

DEV_NUMS = 1

host = '127.0.0.1'  # 获取本地主机名
port = 21345                 # 设置端口
# websocket_host = ''
msg_queue = queue.Queue()
res_static = {}
end_symbol = 0

def deal_data(conn, addr):
    while True:
        data = conn.recv(1024).decode()
        # print(data)
        if data == 'exit' or not data:
            print('{} connection close'.format(addr))
            break
        key = data.split(':')[0]
        if key == 'final':
            value = data.split(':')[-1]
        else:
            value = data.split(':')[-1].split(',')[0]
        if key not in res_static:
            res_static[key] = []
            res_static[key].append(value)
        else:
            res_static[key].append(value)
        if(len(res_static[key]) == DEV_NUMS):
            msg_queue.put(key)
        print('{} client send data is {}'.format(addr, data))
        # msg_queue.put(data)
    global end_symbol
    end_symbol = end_symbol + 1
    conn.close()

def serv_socket():
    # 创建socket服务器
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(DEV_NUMS)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    connection_count = 0
    threads = []
    while connection_count < DEV_NUMS:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()
        threads.append(t)
        
        connection_count += 1
    # 等待线程结束
    for t in threads:
        t.join()
    # print(res_static)
    s.close()

async def send(websocket):
    while not msg_queue.empty():
        key = msg_queue.get()
        if key == 'final':
            receive_pkts = 0
            capture_pkts = 0
            for i in range(len(res_static[key])):
                receive_pkts += int(res_static[key][i].split(',')[0])
                capture_pkts += int(res_static[key][i].split(',')[2])
            print('send receive_pkts:%d capture_pkts:%d' % (receive_pkts, capture_pkts))
            await websocket.send(str(key)+':'+str(receive_pkts)+','+str(capture_pkts))
        else:
            total_pkts = 0
            for i in range(len(res_static[key])):
                total_pkts += int(res_static[key][i])
            print("send %d" % total_pkts)
            await websocket.send(str(key)+':'+str(total_pkts))
    if end_symbol == DEV_NUMS and msg_queue.empty():
        await websocket.send('exit')
        asyncio.get_event_loop().stop()        
