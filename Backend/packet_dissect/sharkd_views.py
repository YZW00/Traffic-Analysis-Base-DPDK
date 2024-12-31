import uuid, json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.gzip import gzip_page
from .sharkd import SharkdSession
from .async_sharkd import SharkdSessionCache
import os

session_map = {}

@require_http_methods(["GET"])
def creat_session(request):
    try:
        session = SharkdSessionCache(warp_class=SharkdSession, exec_name=os.environ["SHARKD"])
        session_uuid = str(uuid.uuid4())
        if session_uuid in session_map:
            print(session_map[session_uuid])
            session_map[session_uuid].close()
        session_map[session_uuid] = session
        return JsonResponse({ "success": True, "result": session_uuid})
    except Exception as e:
        print(e)
        return JsonResponse({ "success": False, "result": str(e) })

@require_http_methods(["GET"])
def close_session(request):
    user_uuid = request.GET.get("uuid")
    if not user_uuid:
        return JsonResponse({ "success": False, "result": "UUID required" })
    if user_uuid in session_map:
        session = session_map[user_uuid]
        session.close()
        del session_map[user_uuid]
        return JsonResponse({ "success": True, "result": user_uuid})
    else:
        return JsonResponse({ "success": False, "result": "Session not found" })

@gzip_page
@require_http_methods(["GET"])
def session_request(request):
    user_uuid = request.GET.get("uuid")
    user_method = request.GET.get("method")
    user_params_json = request.GET.get("params")
    if not user_params_json or not user_method:
        return JsonResponse({ "success": False, "result": "Bad params or method" })
    if user_uuid in session_map:
        session = session_map[user_uuid]
        try:
            user_params = json.loads(user_params_json)
            result = session.jsonrpc_request(user_method, user_params, no_return=False, raw_response=False)
            return JsonResponse({ "success": True, "result": result})
        except AssertionError as e:
            print(e)
            return JsonResponse({ "success": False, "result": "JSON-RPC Exception" })
        except Exception as e:
            print(e)
            return JsonResponse({ "success": False, "result": "Unexcepted Exception" })
    else:
        return JsonResponse({ "success": False, "result": "Session not found" })

from django.core.cache import cache
@require_http_methods(["GET"])
def redis_test(request):
    key = request.GET.get("key")
    value = request.GET.get("value")
    if not value:
        value = cache.get(key)
        return JsonResponse({ "key": key, "value": value })
    else:
        cache.set(key, value, timeout=None)
        return JsonResponse({ "key": key, "value": value })