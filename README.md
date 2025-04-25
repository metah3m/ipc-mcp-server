# IPC Camera MCP Server

基于 FastAPI 的网络摄像头控制服务器，实现了 MCP（Message Control Protocol）协议。

## 功能特性

- PTZ 摄像头控制
  - 平移/倾斜控制
  - 变焦控制
  - 自动旋转
  - 聚焦控制
  - 光圈控制
  - 重启和归零
- 会话管理
  - 自动登录
  - 会话保活
  - 会话状态维护
- HTTP/1.1 协议支持
- JSON 数据格式
- CORS 支持

## 安装

确保你的系统已安装 Python 3.8 或更高版本：

```bash
# 安装依赖
pip install -e .
```

## 运行服务器

```bash
python main.py
```

服务器将在 http://localhost:8000 上启动。

## 项目结构

- `main.py`: 主程序入口，包含 MCP 服务器初始化和路由定义
- `session_manager.py`: 会话管理模块，处理登录和会话保活
- `ptz_control.py`: PTZ 控制模块，实现摄像头的各种控制功能

## API 示例

### PTZ 控制

```bash
curl -X POST "http://localhost:8000/SDK/UNIV_API%20HTTP/1.1" \
     -H "Content-Type: application/json" \
     -d '{
       "service": "ptz",
       "method": "control",
       "params": {
         "pan": 50,
         "tilt": 30,
         "zoom": 0
       }
     }'
```

### 响应示例

```json
{
    "result": "success",
    "session": "550e8400-e29b-41d4-a716-446655440000"
}
```
