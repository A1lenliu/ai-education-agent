# AI教育辅助系统

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> 北京交通大学计算机科学与技术专业毕业设计  
> 作者：柳思阳

## 项目概述

AI教育辅助系统是一个综合性教育支持平台，融合了先进的大语言模型与智能检索技术，为教育工作者和学习者提供全方位的智能辅助工具。系统通过两个核心模块：智能体系统（基于"思考-行动-观察"ReAct框架）和知识库问答系统（基于RAG技术），帮助用户解决复杂教育问题，提升教学和学习效率。

本项目是北京交通大学计算机科学与技术专业柳思阳的毕业设计作品，旨在探索大语言模型在教育领域的创新应用，为教学和学习过程提供智能化支持。

## 系统架构

系统采用前后端分离架构，主要组件如下：

```
/project-root
│
├── /frontend               # 前端 Web UI
│   ├── /components         # 组件（登录表单、用户管理等）
│   ├── /pages              # 页面（登录页、注册页、首页等）
│   ├── /public             # 静态资源（如图片、样式文件等）
│   ├── /styles             # 样式文件（CSS/SCSS）
│   └── index.html          # 入口 HTML 文件
│
├── /backend                # 后端服务（API）
│   ├── /auth_service       # 认证服务（注册、登录、JWT）
│   ├── /user_service       # 用户管理（查询、更新用户信息、权限验证）
│   ├── /llm_service        # LLM 交互（DeepSeek 或其他模型服务）
│   ├── /rag_service        # RAG 知识库检索（FAISS/Milvus）
│   ├── /models             # 数据库模型（MySQL 用户表、管理员权限）
│   ├── /routes             # API 路由（用户登录、知识库管理等）
│   ├── /configs            # 配置文件（数据库连接、JWT 密钥、模型配置等）
│   ├── main.py             # FastAPI 启动文件（后端入口）
│   ├── /requirements.txt   # 项目依赖文件
│   └── /tests              # 单元测试 & 集成测试
│
├── /scripts                # 部署、管理脚本（如数据库初始化、数据处理等）
│   ├── /deploy.sh          # 部署脚本
│   └── /init_db.py         # 初始化数据库脚本
│
├── /docs                   # 项目文档
│   └── API_Documentation.md # API 文档
│
├── /docker-compose.yml     # Docker 配置（如果需要容器化部署）
│
└── README.md               # 项目说明文件
```

### 技术栈

- **前端**：HTML5, CSS3, JavaScript (原生)
- **后端**：Python, FastAPI
- **数据存储**：MySQL (用户数据), Chroma/FAISS (向量数据库用于RAG)
- **AI模型**：DeepSeek LLM (支持自定义API密钥)
- **部署**：Docker支持容器化部署

## 核心功能

### 1. 智能体系统

基于"思考-行动-观察"(ReAct)框架设计的智能代理，能够分析复杂问题并执行一系列推理和操作：

- **多步骤推理能力**：拆解复杂问题，逐步分析解决
- **思考过程透明化**：展示智能体的思考、行动和观察过程
- **工具使用能力**：可以使用多种工具辅助分析和解决问题，包括：
  - 文件读取：读取指定文件内容
  - 文件搜索：根据模式查找文件
  - 代码分析：分析代码结构和复杂度
  - 内容搜索：在文件中查找特定内容
  - 依赖分析：分析代码依赖关系
  - 目录分析：生成目录树结构

### 2. 知识库问答系统

基于检索增强生成(RAG)技术的问答系统，能从上传的文档中精准检索信息：

- **智能问答**：根据知识库内容回答用户问题
- **文档上传管理**：支持多种格式文档（PDF, DOCX, TXT, MD等）的上传与管理
- **知识库检索**：从已上传文档中检索相关信息
- **引用来源**：回答中自动添加信息来源引用，增强可信度
- **文档预览**：支持在线预览已上传文档内容

### 3. 用户管理系统

- **用户注册登录**：账号创建与身份验证
- **权限管理**：区分普通用户和管理员权限
- **个人设置**：用户可以设置个人偏好和API密钥

## 安装与部署

### 前提条件

- Python 3.8+
- Docker & Docker Compose (可选，用于容器化部署)
- MySQL

### 本地开发环境设置

1. **克隆仓库**

```bash
git clone <repository-url>
cd ai-education-agent
```

2. **设置后端**

```bash
cd backend

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows使用: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py
```

3. **配置环境变量**

创建`.env`文件，配置必要的环境变量：

```
DB_HOST=localhost
DB_USER=yourusername
DB_PASSWORD=yourpassword
DB_NAME=aieducation
JWT_SECRET=your_jwt_secret
LLM_API_BASE=https://api.deepseek.com/v1
DEFAULT_LLM_API_KEY=your_default_api_key (可选)
```

4. **启动后端服务**

```bash
uvicorn main:app --reload --port 8001
```

5. **部署前端**

前端为纯静态文件，可以使用任何Web服务器部署，或者直接打开HTML文件进行开发测试。
确保在前端配置中正确设置后端API地址。

### Docker部署（生产环境）

使用Docker Compose一键部署：

```bash
docker-compose up -d
```

## 使用指南

### 基础使用流程

1. **访问系统**：打开浏览器，访问系统地址（开发环境通常为`http://localhost:8080`）
2. **用户登录**：使用您的账号密码登录系统
3. **系统导航**：通过顶部导航栏切换不同功能模块

### 智能体系统使用

1. 在导航栏选择"智能体系统"
2. （可选）输入您的DeepSeek API密钥以提升性能
3. 在输入框中提供详细、明确的问题描述
4. 点击"发送"按钮，等待智能体处理您的问题
5. 智能体会展示思考过程、执行的操作及最终答案

### 知识库问答系统使用

1. 在导航栏选择"知识库问答"
2. 首次使用需上传相关文档：
   - 切换到"文档上传"标签
   - 上传与您问题领域相关的文档（支持PDF、DOCX、TXT、MD等格式）
   - 可以添加文档元数据如标题、作者等（可选）
3. 切换到"问答"标签，输入您的问题
4. 系统会从已上传文档中检索相关信息并生成回答，同时提供信息来源
5. 如需管理文档，可切换到"文档管理"标签，查看、删除或刷新文档列表

## 自定义与扩展

### 添加新的工具到智能体系统

在`backend/react_agent/tools`目录下创建新的工具类，并在`tools_manager.py`中注册。

### 扩展知识库功能

可以在`backend/rag_service`中修改或添加新的检索方法，或增强文档处理能力。

### 替换底层LLM模型

系统设计允许轻松替换底层大语言模型，只需修改`backend/llm_service`中的接口实现。

## 故障排除

### 常见问题

1. **后端连接失败**：
   - 检查后端服务是否正常运行
   - 确认API地址配置是否正确
   - 检查网络连接和防火墙设置

2. **文档上传失败**：
   - 确保文件格式受支持
   - 检查文件大小是否超过限制(50MB)
   - 检查存储空间是否充足

3. **API密钥问题**：
   - 确认DeepSeek API密钥格式正确
   - 检查API密钥是否有足够的调用额度


## 致谢

特别感谢北京交通大学计算机与信息技术学院的老师们对本项目的指导与支持。本系统的开发过程中得到了刘海洋导师的宝贵建议，特别是在大语言模型应用和教育场景融合方面的专业指导。


---

<div align="center">
    <img src="frontend/img/BJTU.jpeg" alt="北京交通大学" width="60" height="60">
    <p>北京交通大学计算机与信息技术学院</p>
    <p>© 2024 柳思阳. 保留所有权利。</p>
</div>

