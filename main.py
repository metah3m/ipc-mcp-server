from mcp.server.fastmcp import FastMCP
import asyncio
from session_manager import SessionManager
from ptz_control import PTZClient

# 摄像头控制配置
CAMERA_HOST = "http://192.168.6.100"

# Initialize FastMCP server
mcp = FastMCP(
    "camera_control", 
    host="0.0.0.0",
    port=8000
)

# 创建会话管理器和PTZ客户端
session_manager = SessionManager(CAMERA_HOST)
ptz_client = PTZClient(CAMERA_HOST, session_manager)

@mcp.tool()
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

@mcp.tool()
async def ptz_reboot(channel: int = 0) -> str:
    """重启PTZ设备
    
    Args:
        channel: 通道号，默认0
    """
    return await ptz_client.reboot(channel)

@mcp.tool()
async def ptz_reset_position(channel: int = 0) -> str:
    """重置PTZ位置到零坐标
    
    Args:
        channel: 通道号，默认0
    """
    return await ptz_client.reset_position(channel)

async def startup():
    """启动服务器前的初始化"""
    await session_manager.start()

if __name__ == "__main__":
    # 启动会话管理器
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())
    
    # 运行MCP服务器
    mcp.run(transport='sse')


