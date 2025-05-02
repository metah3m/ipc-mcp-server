import asyncio
import httpx
import json
from mcp_server.session_manager import SessionManager


class PTZControl:
    def __init__(self, channel: int = 0):
        self.channel = channel
        self.config = {
            "channel": channel,
            "continuousPanTiltSpace": {"x": 0, "y": 0},
        }

    def set_pan_tilt(self, x: int = 0, y: int = 0):
        """设置平移和倾斜速度"""
        self.config["continuousPanTiltSpace"]["x"] = x
        self.config["continuousPanTiltSpace"]["y"] = y
        return self

    def set_zoom(self, z: int = 0):
        """设置z轴速度"""
        self.config["continuousZoomSpace"]["z"] = z
        return self

    def set_auto_pan(self, speed: int = 0):
        """设置自动旋转速度"""
        self.config["autoPanCtrl"]["autoPan"] = speed
        return self

    def set_focus(self, speed: int = 0):
        """设置聚焦速度"""
        self.config["focusCtrl"]["focus"] = speed
        return self

    def set_iris(self, speed: int = 0):
        """设置光圈速度"""
        self.config["irisCtrl"]["iris"] = speed
        return self

    def get_config(self) -> dict:
        """获取当前配置"""
        return self.config


class PTZClient:
    def __init__(self, host: str, session_manager: SessionManager):
        self.host = host
        self.api_path = "/SDK/UNIV_API"
        self.session_manager = session_manager

    async def control(
        self,
        x_speed: int = 0,
        y_speed: int = 0,
        zoom_speed: int = 0,
        auto_pan_speed: int = 0,
        focus_speed: int = 0,
        iris_speed: int = 0,
        channel: int = 0,
        time: int = 1,
    ) -> str:
        """控制PTZ摄像头并在指定时间后发送停止命令"""
        if not self.session_manager.session_id:
            return "未登录或会话已过期"

        try:
            # 验证所有速度值是否在有效范围内
            for name, value in [
                ("x_speed", x_speed),
                ("y_speed", y_speed),
                ("zoom_speed", zoom_speed),
                ("auto_pan_speed", auto_pan_speed),
                ("focus_speed", focus_speed),
                ("iris_speed", iris_speed)
            ]:
                if not -100 <= value <= 100:
                    return f"{name} 必须在 -100 到 100 之间"

            # 构建初始PTZ配置
            ptz = PTZControl(channel)
            if x_speed or y_speed:
                ptz.set_pan_tilt(x_speed, y_speed)

            print(f"PTZ配置: {ptz.get_config()}")
            # 构建初始请求
            payload = {
                "session": self.session_manager.session_id,
                "id": 2,
                "call": {"service": "ptz", "method": "setPTZCmd"},
                "params": ptz.get_config()
            }

            print(f"请求: {json.dumps(payload)}")

            async with httpx.AsyncClient() as client:
                # 发送初始运动请求
                motion_resp = await client.post(
                    url=self.host,
                    headers=self.session_manager.get_headers(),
                    json=payload
                )
                motion_resp.raise_for_status()
                motion_result = f"运动请求成功 响应: {json.dumps(motion_resp.json())}"
                print(f"运动请求成功 响应: {json.dumps(motion_resp.json())}")
                # 等待指定时间
                await asyncio.sleep(time)

                # 构建停止配置
                stop_ptz = PTZControl(channel)
                stop_ptz.set_pan_tilt(0, 0)
                print(f"停止配置: {stop_ptz.get_config()}")
                # 构建停止请求
                stop_payload = {
                    "session": self.session_manager.session_id,
                    "id": 2,
                    "call": {"service": "ptz", "method": "setPTZCmd"},
                    "params": stop_ptz.get_config()
                }

                print(f"停止配置: {stop_ptz.get_config()}")

                # 发送停止请求
                try:
                    stop_resp = await client.post(
                        url=self.host,
                        headers=self.session_manager.get_headers(),
                        json=stop_payload
                    )
                    stop_resp.raise_for_status()
                    stop_result = f"停止请求成功 响应: {json.dumps(stop_resp.json())}"
                except Exception as e:
                    stop_result = f"停止请求失败: {str(e)}"

                return f"{motion_result}\n{stop_result}"

        except Exception as e:
            return f"控制PTZ时发生错误: {str(e)}"

        async def reboot(self, channel: int = 0) -> str:
            """重启PTZ设备"""
            if not self.session_manager.session_id:
                return "未登录或会话已过期"

            try:
                payload = {
                    "session": self.session_manager.session_id,
                    "id": 2,
                    "call": {
                        "service": "ptz",
                        "method": "rebootPTDevice"
                    },
                    "params": {
                        "channel": channel
                    }
                }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url=self.host,
                        headers=self.session_manager.get_headers(),
                        json=payload
                    )
                    response.raise_for_status()
                    result = response.json()
                    return f"PTZ重启命令已发送. 响应: {json.dumps(result)}"

            except Exception as e:
                return f"重启PTZ时发生错误: {str(e)}"

    async def reset_position(self, channel: int = 0) -> str:
        """重置PTZ位置到零坐标"""
        if not self.session_manager.session_id:
            return "未登录或会话已过期"

        try:
            payload = {
                "session": self.session_manager.session_id,
                "id": 2,
                "call": {
                    "service": "ptz",
                    "method": "setPTPositionZero"
                },
                "params": {
                    "channel": channel
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.host,
                    headers=self.session_manager.get_headers(),
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return f"PTZ归零命令已发送. 响应: {json.dumps(result)}"

        except Exception as e:
            return f"重置PTZ位置时发生错误: {str(e)}"
