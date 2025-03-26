#!/bin/bash

echo "==================================="
echo "    AI 教育智能体服务启动程序"
echo "==================================="

# 检查并关闭已占用的端口
check_and_kill_port() {
    local port=$1
    if lsof -i :$port > /dev/null; then
        echo "端口 $port 已被占用，正在关闭..."
        lsof -ti:$port | xargs kill -9
        sleep 1
    fi
}

# 检查必要的端口
check_and_kill_port 8000
check_and_kill_port 3000

# 启动后端服务器
echo "正在启动后端服务..."
(python -m uvicorn backend.main:app --reload --port 8000 &)

# 等待2秒确保后端启动
sleep 2

# 启动前端服务器
echo "正在启动前端服务..."
(cd frontend && python -m http.server 3000 &)

# 等待2秒
sleep 2

# 自动打开浏览器（根据操作系统）
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:3000 2>/dev/null || sensible-browser http://localhost:3000 2>/dev/null || x-www-browser http://localhost:3000 2>/dev/null
fi

echo "==================================="
echo "服务已启动:"
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
echo "==================================="
echo "如需停止服务，请运行 ./stop.sh"

# 保持脚本运行
echo "按 Ctrl+C 停止服务..."
wait 