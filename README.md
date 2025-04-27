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
# 安装uv
pip3 install uv
# 创建虚拟环境
uv venv
# 激活虚拟环境
source .venv/bin/activate
# 安装依赖
uv pip install .
```

## 运行服务器

```bash
python3 -m src.mcp_server.main
```
如果是模拟测试，先运行 mock_ipc.py

```bash
python3 -m src.mcp_server.mock_ipc
```

