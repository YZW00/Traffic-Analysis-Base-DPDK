import asyncio
import websockets
import json

lock = asyncio.Lock()
connected_web_skt = []
recv_buffer = {}

# 新加内容
src_addr_0 = ''

async def at_skt_connected(reader, writer):
    ip, port = writer.get_extra_info('peername')
    src_addr = f"{ip}:{port}"
    print(f"Socket from {src_addr}")

    global recv_buffer
    recv_buffer[src_addr] = []
    
    # 新加内容
    global src_addr_0
    if src_addr_0 == '':
        src_addr_0 = src_addr
        websockets.broadcast(connected_web_skt, json.dumps({
            "type": "start",
            "data": src_addr
        }))

    while True:
        try:
            data = (await reader.readline()).decode()
            if data == '': break

            # 新加内容
            recv_buffer[src_addr].append(data)
            async with asyncio.Lock():
                if src_addr_0 == '':
                    src_addr_0 = src_addr
            if src_addr != src_addr_0:
                continue
            parsed_data = {}
            
            for all_src_addr in recv_buffer.keys():
                if len(recv_buffer[all_src_addr]) <= 0:
                    continue
                temp_data = json.loads(recv_buffer[all_src_addr][0])
                print(f'{all_src_addr}: {temp_data}')
                for key in temp_data.keys():
                    if key == 'sequence':
                        parsed_data[key] = temp_data[key]
                        continue
                    try:
                        parsed_data[key] += temp_data[key]
                    except KeyError:
                        parsed_data[key] = temp_data[key]
                recv_buffer[all_src_addr].pop(0)
            print(f'total: {parsed_data}')
            data = f'{{"sequence": {parsed_data["sequence"]}, "packets_captured": {parsed_data["packets_captured"]}, "packets_missed": {parsed_data["packets_missed"]}, "packets_droped": {parsed_data["packets_droped"]}, "packets_written": {parsed_data["packets_written"]}, "packets_filtered": {parsed_data["packets_filtered"]}, "bytes_written": {parsed_data["bytes_written"]}, "bytes_compressed": {parsed_data["bytes_compressed"]}}}\n'
            
            
            # 修改后注释掉的
            # if len(recv_buffer[src_addr]) >= 20:
            #     recv_buffer[src_addr].pop(0)
            # recv_buffer[src_addr].append(data)
            websockets.broadcast(connected_web_skt, json.dumps({
                "type": "update",
                "data": {
                    "ip": src_addr,
                    "data": data
                }
            }))
        except Exception as e:
            print(e)
            break
    del recv_buffer[src_addr]
    if src_addr == src_addr_0:
        src_addr_0 = ''
        websockets.broadcast(connected_web_skt, json.dumps({
            "type": "stop",
            "data": src_addr
        }))

async def at_web_skt_connected(websocket):
    connected_web_skt.append(websocket)
    try:
        if len(recv_buffer):
            await websocket.send(json.dumps({
                "type": "sync",
                "data": recv_buffer
            }))
        await websocket.wait_closed()
    finally:
        connected_web_skt.remove(websocket)

async def socket_daemon():
    skt_srv = await asyncio.start_server(at_skt_connected, "0.0.0.0", 21345)
    web_skt_srv = await websockets.serve(at_web_skt_connected, "0.0.0.0", 21346)
    await asyncio.gather(
        skt_srv.serve_forever(),
        web_skt_srv.serve_forever()
    )

def start_socket_daemon():
    asyncio.run(socket_daemon(), debug=False)

if __name__ == "__main__":
    asyncio.run(socket_daemon(), debug=True)
