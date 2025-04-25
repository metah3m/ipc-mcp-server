from session_manager import SessionManager
from ptz_control import PTZClient
import asyncio
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi_mcp import FastApiMCP
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import json
import time

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 摄像头控制配置
CAMERA_HOST = "http://192.168.6.100"  # 请替换为实际的摄像头IP地址

# 创建 FastAPI 应用
app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://demo.daan.one"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建会话管理器和PTZ客户端
session_manager = SessionManager(CAMERA_HOST)
ptz_client = PTZClient(CAMERA_HOST, session_manager)



@app.post("/api/ptz/control")
async def ptz_control(
    x_speed: int = 0,
    y_speed: int = 0,
    zoom_speed: int = 0,
    auto_pan_speed: int = 0,
    focus_speed: int = 0,
    iris_speed: int = 0,
    channel: int = 0
) -> str:
    """控制PTZ摄像头的所有参数
    
    Args:
        x_speed: X轴速度 (-100到100)
        y_speed: Y轴速度 (-100到100)
        zoom_speed: 变焦速度 (-100到100)
        auto_pan_speed: 自动旋转速度 (-100到100)
        focus_speed: 聚焦速度 (-100到100)
        iris_speed: 光圈速度 (-100到100)
        channel: 通道号，默认0
    """
    return await ptz_client.control(
        x_speed=x_speed,
        y_speed=y_speed,
        zoom_speed=zoom_speed,
        auto_pan_speed=auto_pan_speed,
        focus_speed=focus_speed,
        iris_speed=iris_speed,
        channel=channel
    )

@app.post("/api/ptz/reboot")
async def ptz_reboot(channel: int = 0) -> str:
    """重启PTZ设备
    
    Args:
        channel: 通道号，默认0
    """
    return await ptz_client.reboot(channel)

@app.post("/api/ptz/reset")
async def ptz_reset_position(channel: int = 0) -> str:
    """重置PTZ位置到零坐标
    
    Args:
        channel: 通道号，默认0
    """
    return await ptz_client.reset_position(channel)

async def startup():
    """启动服务器前的初始化"""
    # 暂时注释掉会话管理器启动
    # await session_manager.start()
    pass

if __name__ == "__main__":
    # 启动会话管理器
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    

    mcp = FastApiMCP(app)
    mcp.mount()  # 立即挂载 MCP 服务器
    
    # 运行服务器
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)


