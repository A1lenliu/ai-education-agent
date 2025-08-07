# AI-Powered Educational Assistant System

> 🎓 Graduation Project @ Beijing Jiaotong University  
> 👨‍💻 Major: Computer Science and Technology  
> ✍️ Author: Siyang Liu  
> 🧠 Keywords: LLM, RAG, ReAct, Education, FastAPI, AI Agent

---

## 🚀 Project Description

An intelligent educational assistant system powered by Large Language Models (LLMs), built to support both educators and students in solving complex tasks with:

- 🧠 A ReAct-based Reasoning Agent  
- 📚 A RAG-based Document Question-Answering System

This system is designed to bring **AI-powered insights** into the learning environment by integrating **reasoning**, **tool use**, and **knowledge retrieval**.

---

## 🧱 Architecture Overview

```bash
/project-root
│
├── frontend/                # 🎨 UI built with vanilla JS, HTML, CSS
│   ├── components/          # Common UI components
│   ├── pages/               # Page-level views (Login, Home, etc.)
│   ├── public/              # Static assets (images, fonts)
│   └── styles/              # Stylesheets
│
├── backend/                 # ⚙️ FastAPI backend
│   ├── auth_service/        # User auth (JWT, login, signup)
│   ├── user_service/        # User profile & roles
│   ├── llm_service/         # LLM API wrapper (e.g. DeepSeek)
│   ├── rag_service/         # RAG logic (retrieval + generation)
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API routes
│   ├── configs/             # Env & DB configs
│   ├── main.py              # App entrypoint
│   └── requirements.txt     # Python deps
│
├── scripts/                 # 🛠️ Dev & deploy scripts
│   ├── deploy.sh            # Docker compose runner
│   └── init_db.py           # DB initialization
│
├── docs/                    # 📄 Docs & API references
│   └── API_Documentation.md
│
├── docker-compose.yml       # 🐳 Optional docker deployment
└── README.md                # 👋 You are here

⚙️ Tech Stack
Frontend   : HTML5 + CSS3 + JavaScript (Vanilla)
Backend    : Python 3.8+ + FastAPI
Database   : MySQL (User DB), FAISS / Chroma (Vector DB for RAG)
LLM API    : DeepSeek (Custom API Key supported)
Deployment : Local + Docker (optional)

🚀 Core Features
🧠 ReAct-Based Intelligent Agent System
Follows Think → Act → Observe logic

Performs multi-step reasoning and analysis

Supports tool invocation, including:

File reading

File searching

Code analysis

Content matching

Dependency analysis

Directory listing

Displays the full reasoning trace of the agent

📚 Knowledge Base Q&A System (RAG)
Uses Retrieval-Augmented Generation (RAG)

Allows users to upload documents (PDF, DOCX, TXT, MD)

Supports semantic document search

Generates answers based on retrieved content

Includes source citation in answers

Document preview and management support

👤 User Management System
User registration and login

Role-based access (user vs. admin)

Personal API key configuration

Preferences and settings

🛠️ Installation & Deployment
✅ Prerequisites
Python 3.8+
MySQL server
(Optional) Docker & Docker Compose

🔧 Local Setup
# 1. Clone the repository
git clone <repository-url>
cd ai-education-agent

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize the database
python scripts/init_db.py

🔐 Configure Environment
Create a .env file in the backend root:
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=aieducation
JWT_SECRET=your_jwt_secret
LLM_API_BASE=https://api.deepseek.com/v1
DEFAULT_LLM_API_KEY=your_default_api_key

▶️ Run Backend Server
uvicorn main:app --reload --port 8001


📒 User Guide
🔎 Agent System
Navigate to the “Agent System” page

(Optional) Set your DeepSeek API key

Enter a complex task or question

Submit and let the agent reason

View intermediate steps and the final result

📖 Knowledge Q&A System
Go to “Knowledge Q&A” tab

Upload documents relevant to your topic

Switch to the Q&A section and ask a question

The system retrieves and generates an answer with source citation

Manage uploaded documents via the “Document Management” tab

🧩 Customization & Extension
➕ Add New Tools to the Agent
Create a tool file in:
backend/react_agent/tools/your_tool.py

Register it in:
tools_manager.py

🔁 Replace or Extend LLM Provider
Edit the file:
backend/llm_service/deepseek.py
Replace DeepSeek API calls with OpenAI, Claude, etc.

🧠 Enhance Knowledge Retrieval
Improve rag_service logic to support custom vector search or hybrid ranking techniques.

🙏 Acknowledgements
Special thanks to the faculty of the School of Computer and Information Technology at Beijing Jiaotong University.

Gratitude to Professor Haiyang Liu for his guidance on LLM applications in education and valuable feedback during the development process.
