"""
简单的认证模块，用于演示和测试，不依赖数据库
"""

from fastapi import HTTPException
import os

# 保存用户凭证的内存字典
users = {
    "admin": "admin123",
    "test": "test123",
    "user": "password",
    "buluga1sy": "123"  # 添加您的用户名和密码
}

def verify_user(username: str, password: str) -> bool:
    """
    验证用户凭证
    
    Args:
        username: 用户名
        password: 密码
    
    Returns:
        如果验证成功返回True，否则返回False
    """
    if username in users and users[username] == password:
        return True
    return False

def login(username: str, password: str):
    """
    登录接口
    
    Args:
        username: 用户名
        password: 密码
    
    Returns:
        登录成功的消息
    
    Raises:
        HTTPException: 如果凭证无效
    """
    if verify_user(username, password):
        return {"message": "登录成功"}
    raise HTTPException(status_code=400, detail="用户名或密码错误")

def register(username: str, password: str):
    """
    注册新用户
    
    Args:
        username: 用户名
        password: 密码
    
    Returns:
        注册成功的消息
    
    Raises:
        HTTPException: 如果用户名已存在
    """
    if username in users:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    users[username] = password
    return {"message": "注册成功", "username": username} 