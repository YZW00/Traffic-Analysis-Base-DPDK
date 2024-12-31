import asyncio
import websockets
import json

connected_web_skt = []
recv_buffer = {}

async def at_skt_connected(reader, writer):
    ip, port = writer.get_extra_info('peername')
    src_addr = f"{ip}:{port}"
    print(f"Socket from {src_addr}")
    recv_buffer[src_addr] = []
    websockets.broadcast(connected_web_skt, json.dumps({
        "type": "start",
        "data": src_addr
    }))
    while True:
        try:
            data = (await reader.readline()).decode()
            if data == '': break
            if len(recv_buffer[src_addr]) >= 20:
                recv_buffer[src_addr].pop(0)
            recv_buffer[src_addr].append(data)
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
