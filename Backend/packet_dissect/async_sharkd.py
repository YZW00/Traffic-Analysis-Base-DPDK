import os
import sys
import json
import asyncio
import threading

class AsyncSharkdSession:
    JSONRPC_VERSION = "2.0"
    def __init__(self, addr: tuple=None, exec_name="sharkd") -> None:
        self.req_id = 1
        self.req_queue = {}
        self.req_id_lock = asyncio.Lock()
        self.communicate_lock = asyncio.Lock()
        self.addr = addr
        self.exec_name = exec_name
        self.task = None
        self.socket = None
        self.proc = None
    async def __run(self, init_future=None):
        try:
            async with self.communicate_lock: # avoid None in self.communicate()
                if self.addr:
                    if self.addr is tuple:
                        host, port = self.addr
                        self.socket = await asyncio.open_connection(host, port)
                    else:
                        self.socket = await asyncio.open_unix_connection(self.addr)
                else:
                    self.socket = None
                    self.proc = await asyncio.create_subprocess_exec(
                        *[self.exec_name, "-"],
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=sys.stderr,
                        env=os.environ.copy(),
                        limit=1024*1024*128
                    )
                if init_future: # notify init finished
                    init_future.set_result(None)
            if self.socket:
                reader, writer = self.socket
            else:
                reader = self.proc.stdout
            while True:
                response = b""
                await asyncio.sleep(0.1)
                while not response.endswith(b"\n"):
                    await asyncio.sleep(0.1)
                    response += await reader.read(1024*1024*128)
                # response = await reader.readline()
                res_data = json.loads(response.decode("utf8", errors="ignore"))
                assert res_data["jsonrpc"] == AsyncSharkdSession.JSONRPC_VERSION, \
                    "jsonrpc版本错误"
                res_id = res_data["id"]
                if res_id in self.req_queue:
                    result_future = self.req_queue[res_id]
                    result_future.set_result(res_data)
        except asyncio.CancelledError:
            if init_future and not init_future.done():
                init_future.cancel()
            if self.socket:
                reader, writer = self.socket
                writer.close()
                await writer.wait_closed()
            elif self.proc:
                self.proc.kill()
                await self.proc.communicate()
            for res_id in self.req_queue:
                result_future = self.req_queue[res_id]
                result_future.cancel()
                del self.req_queue[res_id]
    def cancel(self):
        if self.task:
            self.task.cancel()
            self.task = None # avoid canceled task used
            self.req_id = 1
    def close(self):
        self.cancel()
    async def __communicate(self, data, id):
        loop = asyncio.get_running_loop()
        if self.task is None:
            init_future = loop.create_future()
            task = asyncio.create_task(self.__run(init_future))
            self.task = task
            await init_future
        async with self.communicate_lock:
            if self.socket:
                reader, writer = self.socket
            else:
                writer = self.proc.stdin
            writer.write(data)
            writer.write(b"\n")
            await writer.drain()
        result_future = loop.create_future()
        self.req_queue[id] = result_future
        await result_future
        del self.req_queue[id]
        return result_future.result()
    async def jsonrpc_request(self, method: str, params={}, no_return=False, raw_response=False) -> dict:
        async with self.req_id_lock:
            # TODO: use thread lock instead
            req_id = self.req_id
            self.req_id += 1
        req_data = json.dumps({
            "jsonrpc": AsyncSharkdSession.JSONRPC_VERSION,
            "id": req_id,
            "method": method,
            "params": params
        }).encode()
        res_data = await self.__communicate(req_data, req_id)
        if raw_response:
            return res_data
        if "error" in res_data:
            raise ValueError(res_data["error"]["message"])
        if no_return:
            assert res_data["result"] == {"status": "OK"}, \
                "函数应返回status=OK"
        return res_data["result"]

class AsyncSharkdSessionHelper:
    __loop = None
    __thread = None
    __lock = threading.Lock()
    def __init__(self, warp_class=AsyncSharkdSession, *params, **kparams) -> None:
        self.session = warp_class(*params, **kparams)
        with AsyncSharkdSessionHelper.__lock:
            if AsyncSharkdSessionHelper.__loop is None:
                AsyncSharkdSessionHelper.__loop = asyncio.new_event_loop()
            if AsyncSharkdSessionHelper.__thread is None:
                AsyncSharkdSessionHelper.__thread = threading.Thread(
                    target=self.event_loop, args=(AsyncSharkdSessionHelper.__loop,)
                )
                AsyncSharkdSessionHelper.__thread.daemon = True
                AsyncSharkdSessionHelper.__thread.start()
    def close(self):
        pass
    def event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
    def jsonrpc_request(self, method: str, params={}, no_return=False, raw_response=False):
        async def async_callback(): # avoid "A coroutine object is required"
            return await self.session.jsonrpc_request(method, params, no_return, raw_response)
        future = asyncio.run_coroutine_threadsafe(
            async_callback(),
            AsyncSharkdSessionHelper.__loop
        )
        return future.result()
# temp
class ReuseableCoroutine:
    def __init__(self, coroutine):
        self.coroutine = coroutine
        self.result = None
    def __await__(self):
        if self.result is None:
            self.result = yield from self.coroutine.__await__()
        async def result_callback():
            await asyncio.sleep(0)
            return self.result
        result = yield from result_callback().__await__()
        return result

class SharkdSessionCache:
    __pool = {}
    __lru = []
    __lock = threading.Lock()
    __cache = {}
    LRU_LIMIT = 10
    def __init__(self, warp_class=AsyncSharkdSession, *params, **kparams) -> None:
        self.key = warp_class, params, json.dumps(kparams)
        self.session = None
        with SharkdSessionCache.__lock:
            if self.key not in SharkdSessionCache.__pool:
                SharkdSessionCache.__pool[self.key] = {}
    def close(self):
        pass
    def jsonrpc_request(self, method: str, params={}, no_return=False, raw_response=False):
        if method == "load":
            print("==method:", method)
            file_name = params["file"]
            with SharkdSessionCache.__lock:
                pool = SharkdSessionCache.__pool[self.key]
                if file_name not in pool:
                    session_class, init_params, init_kparams = self.key
                    init_kparams = json.loads(init_kparams)
                    self.session = session_class(*init_params, **init_kparams)
                    result = self.session.jsonrpc_request(method, params, no_return, raw_response)
                    if asyncio.iscoroutine(result):
                        result = ReuseableCoroutine(result)
                    pool[file_name] = self.session, result
                    SharkdSessionCache.__cache[self.session] = {}
                    while len(SharkdSessionCache.__lru) >= SharkdSessionCache.LRU_LIMIT:
                        old_file_name, old_key = SharkdSessionCache.__lru.pop()
                        old_session = SharkdSessionCache.__pool[old_key][old_file_name]
                        del SharkdSessionCache.__cache[old_session]
                        del SharkdSessionCache.__pool[old_key][old_file_name]
                        print(f"@lru: remove {old_file_name} #{old_key[0].__name__}")
                else:
                    print(f"@lru: cached {file_name}")
                    self.session, result = pool[file_name]
                    try:
                        SharkdSessionCache.__lru.remove((file_name, self.key))
                    finally:
                        pass
                SharkdSessionCache.__lru.insert(0, (file_name, self.key))
                return result
        else:
            print("==method:", method)
            if self.session is None:
                raise ValueError("load before")
            if method in ["status", "frames"]:
                cache = SharkdSessionCache.__cache[self.session]
                key = (method, json.dumps(params))
                if key in cache:
                    print("===key in cache, key:", key, "method:", method)
                    data = cache[key]
                    return data
                else:
                    print("====send request, key:", key, "method:", method)
                    data = self.session.jsonrpc_request(method, params, no_return, raw_response)
                    if asyncio.iscoroutine(data):
                        data = ReuseableCoroutine(data)
                    cache[key] = data
                    return data
        return self.session.jsonrpc_request(method, params, no_return, raw_response)
            
if __name__ == "__main__":
    async def test():
        # 启动sharkd
        sharkd = "C:\\Users\\MaPl\\Downloads\\WiresharkPortable64\\App\\Wireshark\\sharkd.exe"
        # sharkd = "sharkd"

        # 功能测试
        SharkdSessionCache.LRU_LIMIT = 1
        session = SharkdSessionCache(exec_name=sharkd)
        session2 = SharkdSessionCache(exec_name=sharkd)
        session3 = SharkdSessionCache(exec_name=sharkd)
        await session.jsonrpc_request("load", {
            "file": "E:\\MaPl\\Sharkd\\test.pcapng"
        }, no_return=True)
        await session2.jsonrpc_request("load", {
            "file": "E:\\.\\MaPl\\Sharkd\\test.pcapng"
        }, no_return=True)
        await session3.jsonrpc_request("load", {
            "file": "E:\\.\\MaPl\\Sharkd\\test.pcapng"
        }, no_return=True)
        await session.jsonrpc_request("status")
        await asyncio.gather(
            session.jsonrpc_request("status"),
            session.jsonrpc_request("status"),
            session.jsonrpc_request("status"),
            session.jsonrpc_request("status"),
            session.jsonrpc_request("status")
        )
        # session.cancel()
        sync_session = SharkdSessionCache(warp_class=AsyncSharkdSessionHelper, exec_name=sharkd)
        sync_session2 = AsyncSharkdSessionHelper(warp_class=SharkdSessionCache, exec_name=sharkd)
        sync_session.jsonrpc_request("load", {
            "file": "E:\\MaPl\\Sharkd\\test.pcapng"
        }, no_return=True)
        status = sync_session.jsonrpc_request("status")
        print(status)
        sync_session2.jsonrpc_request("load", {
            "file": "E:\\.\\MaPl\\Sharkd\\test.pcapng"
        }, no_return=True)


    asyncio.run(test(), debug=True)
