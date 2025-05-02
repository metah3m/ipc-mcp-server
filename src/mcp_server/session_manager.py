import threading
import httpx
import asyncio
import hashlib

initial_session = "1"


class SessionManager:
    def __init__(self, host: str, username: str = "admin", password: str = "admin"):
        print(f"初始化会话管理器: {host} {username} {password}")
        self.host = host
        self.username = username
        self.password = password
        self.session_id = initial_session
        self.keep_alive_task = None
        self.api_path = "/SDK/UNIV_API"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json; charset = UTF-8",
            "Origin": "http://192.168.102.78",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://192.168.102.78/",
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
            random = "WKNQ3H"  # 这里可以改成真实的随机数生成

            # 计算密码哈希
            pwd_hash = hashlib.sha256(self.password.encode()).hexdigest()
            final_hash = hashlib.sha256(
                (pwd_hash+random).encode()).hexdigest()
            print(f"密码哈希: {final_hash}")

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
                    "encryptType": 1
                }
            }

            async with httpx.AsyncClient() as client:
                print(f"正在登录 {self.host}...")
                response = await client.post(
                    url=self.host,
                    headers=self.headers,
                    json=payload
                )
                result = response.json()
                print(f"登录结果: {result}")
                if result.get("result") is True:
                    self.session_id = result["params"]["session"]
                    print(f"登录成功，会话ID: {self.session_id} {result}")
                    return True
                print(f"登录失败: {result}")
                return False
        except Exception as e:
            print(f"登录失败: {str(e)}")
            return False

    async def keep_alive(self):
        """保持会话活跃"""
        print("启动会话保活...")
        while True:
            print("发送保活请求...")
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
                        f"{self.host}",
                        headers=self.get_headers(),
                        json=payload
                    )
                    result = response.json()
                    if not result.get("result"):
                        print("会话已过期，尝试重新登录")
                        await self.login()

                await asyncio.sleep(1)  # 每30秒发送一次保活请求
            except Exception as e:
                print(f"保活失败: {str(e)}")
                await asyncio.sleep(1)  # 发生错误时等待5秒后重试

    def _run_async_in_thread(self):
        """在新线程中运行事件循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.keep_alive())

    async def start(self):
        """启动会话管理"""
        if await self.login():
            print("会话管理器启动成功")
            thread = threading.Thread(
                target=self._run_async_in_thread, daemon=True)
            thread.start()
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
