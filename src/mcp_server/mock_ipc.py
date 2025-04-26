from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, Any

app = FastAPI()

# 用户数据库（示例用户）
users = {
    "admin": {
        "password_md5": "21232f297a57a5a743894a0e4a801fc3"
    }
}

# 会话存储
sessions: Dict[int, Dict[str, Any]] = {}
session_lock = threading.Lock()
current_session_id = 0
session_id_lock = threading.Lock()

# 请求模型


class CallInfo(BaseModel):
    service: str
    method: str


class RequestBody(BaseModel):
    session: int
    id: int
    call: CallInfo
    params: Dict[str, Any] = {}

# 工具函数


def generate_session_id() -> int:
    global current_session_id
    with session_id_lock:
        current_session_id += 1
        return current_session_id


def is_valid_session(session_id: int) -> bool:
    with session_lock:
        if session_id not in sessions:
            return False
        if datetime.now() > sessions[session_id]["expires_at"]:
            del sessions[session_id]
            return False
        return True


def error_response(request: RequestBody, code: int, message: str) -> Dict:
    return {
        "session": request.session,
        "id": request.id,
        "result": False,
        "error": {"code": code, "message": message}
    }

# 请求处理


@app.post("/")
async def handle_request(request: RequestBody):
    method = request.call.method
    if method == "login":
        return handle_login(request)
    elif method == "logout":
        return handle_logout(request)
    elif method == "keepAlive":
        return handle_keep_alive(request)
    else:
        if not is_valid_session(request.session):
            return error_response(request, 0x10000003, "Invalid session")
        return {"session": request.session, "id": request.id, "result": True}


def handle_login(request: RequestBody) -> Dict:
    params = request.params
    required = ["userName", "password", "random", "ip", "port", "encryptType"]
    if any(field not in params for field in required):
        return error_response(request, 0x10000001, "Missing parameters")

    user_name = params["userName"]
    if user_name not in users:
        return error_response(request, 0x10000001, "NoAuthorityLogin")

    stored_hash = users[user_name]["password_md5"]
    combined = stored_hash + params["random"]
    expected = hashlib.md5(combined.encode()).hexdigest().lower()
    print(expected)

    if params["password"].lower() != expected:
        return error_response(request, 0x10000001, "NoAuthorityLogin")

    session_id = generate_session_id()
    with session_lock:
        sessions[session_id] = {
            "user": user_name,
            "expires_at": datetime.now() + timedelta(seconds=1800)
        }

    return {
        "session": 0,
        "id": request.id,
        "result": True,
        "param": {"session": session_id, "randomKey": "", "times": 5}
    }


def handle_logout(request: RequestBody) -> Dict:
    if not is_valid_session(request.session):
        return error_response(request, 0x10000003, "Invalid session")

    with session_lock:
        if request.session in sessions:
            del sessions[request.session]

    return {"session": request.session, "id": request.id, "result": True}


def handle_keep_alive(request: RequestBody) -> Dict:
    if not is_valid_session(request.session):
        return error_response(request, 0x10000003, "Invalid session")

    timeout = request.params.get("timeout", 30)
    with session_lock:
        sessions[request.session]["expires_at"] = datetime.now() + \
            timedelta(seconds=timeout)

    return {
        "session": request.session,
        "id": request.id,
        "result": True,
        "params": {"timeout": timeout}
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
