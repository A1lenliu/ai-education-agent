#!/bin/bash

echo "==================================="
echo "    停止 AI 教育智能体服务"
echo "==================================="

# 停止所有相关进程
echo "正在停止服务..."
pkill -f "uvicorn backend.main:app"
pkill -f "python -m http.server 3000"

echo "所有服务已停止"
echo "===================================" 