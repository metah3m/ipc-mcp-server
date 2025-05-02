from mcp_server.session_manager import SessionManager
from mcp_server.ptz_control import PTZClient
import asyncio
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, logger
from fastapi_mcp import FastApiMCP
import os
import threading

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
# 配置参数
BACKEND_BASE_URL = os.getenv(
    "BACKEND_URL", "http://192.168.102.78/SDK/UNIV_API")
USER_NAME = os.getenv("USER_NAME", "mcptest")
PASSWORD = os.getenv("PASSWORD", "abcd1234")
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# 创建 FastAPI 应用
app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建会话管理器和PTZ客户端
session_manager = SessionManager(BACKEND_BASE_URL, USER_NAME, PASSWORD)
ptz_client = PTZClient(BACKEND_BASE_URL, session_manager)


@app.post("/api/ptz/control")
async def ptz_control(
    x_speed: int = 0,
    y_speed: int = 0,
    zoom_speed: int = 0,
    auto_pan_speed: int = 0,
    focus_speed: int = 0,
    iris_speed: int = 0,
    channel: int = 0,
    time: int = 1
) -> str:
    """控制PTZ摄像头的所有参数

    Args:
        x_speed: X轴速度为固定值60 或 -60 每秒转动角度为10度
        y_speed: Y轴速度为固定值60 或 -60 每秒转动角度为10度
        z_speed: 变焦速度
        auto_pan_speed: 旋转速度 (-100到100)
        focus_speed: 聚焦速度 (-100到100)
        iris_speed: 光圈速度 (-100到100)
        channel: 通道号,默认0
        time: 运动时间, 需要通过角度计算运动时间,每秒转动角度为10度
    """
    try:
        return await ptz_client.control(
            x_speed=x_speed,
            y_speed=y_speed,
            zoom_speed=zoom_speed,
            auto_pan_speed=auto_pan_speed,
            focus_speed=focus_speed,
            iris_speed=iris_speed,
            channel=channel,
            time=time
        )
    except ValueError as e:
        # 处理参数错误
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        # 处理设备连接失败
        raise HTTPException(status_code=503, detail="PTZ device offline")
    except Exception as e:
        # 捕获其他异常并记录日志
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/ptz/reboot")
async def ptz_reboot(channel: int = 0) -> str:
    """重启PTZ设备

    Args:
        channel: 通道号,默认0
    """
    return await ptz_client.reboot(channel)


@app.post("/api/ptz/reset")
async def ptz_reset_position(channel: int = 0) -> str:
    """重置PTZ位置到零坐标

    Args:
        channel: 通道号,默认0
    """
    return await ptz_client.reset_position(channel)


async def startup():
    """启动服务器前的初始化"""
    # 暂时注释掉会话管理器启动
    await session_manager.start()
    pass

if __name__ == "__main__":
    # 启动会话管理器
    # lib/python3.3/site-packages/mcp/server/sesion.py:162
    # https://github.com/tadata-org/fastapi_mcp/issues/36
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())

    mcp = FastApiMCP(app)
    mcp.mount()  # 立即挂载 MCP 服务器

    # 运行服务器
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
