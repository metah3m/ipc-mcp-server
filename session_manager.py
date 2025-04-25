import httpx
import asyncio
import hashlib
from typing import Optional

class SessionManager:
    def __init__(self, host: str, username: str = "admin", password: str = "admin"):
        self.host = host
        self.username = username
        self.password = password
        self.session_id = None
        self.keep_alive_task = None
        self.api_path = "/SDK/UNIV_API"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=utf-8",
            "Accept-Language": "zh-CN",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Connection": "Keep-Alive",
            "Cache-Control": "no-cache"
        }

    def get_headers(self):
        """获取当前请求头"""
        if self.session_id:
            self.headers["Cookie"] = f"WebSessionID={self.session_id}"
        return self.headers

    async def login(self) -> bool:
        """登录并获取会话ID"""
        try:
            # 生成随机数
            random = "310000"  # 这里可以改成真实的随机数生成
            
            # 计算密码哈希
            pwd_hash = hashlib.md5(self.password.encode()).hexdigest()
            final_hash = hashlib.md5((pwd_hash + random).encode()).hexdigest()

            payload = {
                "session": 0,
                "id": 1,
                "call": {
                    "service": "rpc",
                    "method": "login"
                },
                "params": {
                    "userName": self.username,
                    "password": final_hash,
                    "random": random,
                    "ip": "127.0.0.1",
                    "port": 80,
                    "encryptType": 0  # 使用MD5加密
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}{self.api_path}",
                    headers=self.headers,
                    json=payload
                )
                result = response.json()
                if result.get("result") is True and "session" in result:
                    self.session_id = result["session"]
                    print(f"登录成功，会话ID: {self.session_id}")
                    return True
                return False
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return False

    async def keep_alive(self):
        """保持会话活跃"""
        while True:
            try:
                if not self.session_id:
                    await asyncio.sleep(1)
                    continue

                payload = {
                    "session": self.session_id,
                    "id": 2,
                    "call": {
                        "service": "rpc",
                        "method": "keepAlive"
                    },
                    "params": {
                        "timeout": 60
                    }
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.host}{self.api_path}",
                        headers=self.get_headers(),
                        json=payload
                    )
                    result = response.json()
                    if not result.get("result"):
                        print("会话已过期，尝试重新登录")
                        await self.login()
                
                await asyncio.sleep(30)  # 每30秒发送一次保活请求
            except Exception as e:
                print(f"保活失败: {str(e)}")
                await asyncio.sleep(5)  # 发生错误时等待5秒后重试

    async def start(self):
        """启动会话管理"""
        if await self.login():
            self.keep_alive_task = asyncio.create_task(self.keep_alive())
        else:
            raise Exception("登录失败")

    async def stop(self):
        """停止会话管理"""
        if self.keep_alive_task:
            self.keep_alive_task.cancel()
            try:
                await self.keep_alive_task
            except asyncio.CancelledError:
                pass 