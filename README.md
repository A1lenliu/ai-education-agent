**/project-root
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
