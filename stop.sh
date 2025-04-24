#!/bin/bash

echo "==================================="
echo "    停止 AI 教育智能体服务"
echo "==================================="

# 停止所有相关进程
echo "正在停止服务..."
pkill -f "uvicorn backend.main:app"
pkill -f "uvicorn backend.rag_main:app"
pkill -f "uvicorn backend.react_main:app"
pkill -f "python -m http.server 3000"
pkill -f "python3 -m http.server 3000"
pkill -f "auth_server.py"

# 确保端口释放
kill_port() {
    local port=$1
    if lsof -i :$port > /dev/null; then
        echo "正在释放端口 $port..."
        lsof -ti:$port | xargs kill -9
    fi
}

# 确保关闭所有可能的端口
kill_port 8000
kill_port 8001
kill_port 8002
kill_port 3000

echo "所有服务已停止"
echo "===================================" 