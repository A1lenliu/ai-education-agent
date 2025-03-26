// 显示消息的辅助函数
function showMessage(elementId, message, isError = false) {
    const messageElement = document.getElementById(elementId);
    messageElement.textContent = message;
    messageElement.className = `message ${isError ? 'error' : 'success'}`;
}

// 处理知识库管理按钮
console.log('开始初始化知识库管理按钮');
const knowledgeBtn = document.getElementById('knowledgeBtn');
console.log('知识库管理按钮元素:', knowledgeBtn);

if (knowledgeBtn) {
    console.log('找到知识库管理按钮，添加点击事件');
    knowledgeBtn.addEventListener('click', function(e) {
        console.log('知识库管理按钮被点击');
        e.preventDefault();
        window.location.href = 'knowledge.html';
    });
} else {
    console.error('未找到知识库管理按钮元素');
}

// 处理登录表单
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${API_BASE_URL}/login?username=${username}&password=${password}`, {
                method: 'POST',
            });
            const data = await response.json();

            if (response.ok) {
                // 登录成功
                localStorage.setItem('username', username);
                showMessage('message', '登录成功！');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } else {
                showMessage('message', data.detail || '登录失败', true);
            }
        } catch (error) {
            showMessage('message', '服务器错误', true);
        }
    });
}

// 处理注册表单
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch(`${API_BASE_URL}/register?username=${username}&password=${password}`, {
                method: 'POST',
            });
            const data = await response.json();

            if (response.ok) {
                showMessage('message', '注册成功！');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            } else {
                showMessage('message', data.detail || '注册失败', true);
            }
        } catch (error) {
            showMessage('message', '服务器错误', true);
        }
    });
}

// 处理仪表板页面
const welcomeMessage = document.getElementById('welcomeMessage');
if (welcomeMessage) {
    const username = localStorage.getItem('username');
    if (username) {
        welcomeMessage.textContent = `欢迎回来，${username}！`;
    } else {
        window.location.href = 'login.html';
    }
}

// 处理退出登录
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('username');
        window.location.href = 'login.html';
    });
}

// 处理聊天功能
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM加载完成');
    chatInput.focus();
    
    // 发送按钮点击事件
    sendBtn.addEventListener('click', sendMessage);
    
    // 输入框回车事件
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // 禁用输入
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // 显示用户消息
    appendMessage(message, 'user');
    chatInput.value = '';

    // 显示加载动画
    const loadingDiv = showLoadingIndicator();

    try {
        // 首先获取 RAG 结果
        let ragResults = [];
        try {
            const ragResponse = await fetch(`${API_BASE_URL}/api/rag/retrieve?query=${encodeURIComponent(message)}`);
            const ragData = await ragResponse.json();
            if (ragData.results && ragData.results.length > 0) {
                ragResults = ragData.results;
            }
        } catch (ragError) {
            console.error('获取 RAG 结果失败:', ragError);
        }
        
        // 构建提示
        let prompt = message;
        if (ragResults.length > 0) {
            // 如果找到相关知识，将其整合到提示中
            prompt = `你是一个智能助手。如果以下知识库内容与问题相关，请基于这些知识回答；如果不相关，请直接回答你的理解。\n\n知识库内容：\n${ragResults.join('\n\n')}\n\n问题：${message}`;
        } else {
            // 如果没有找到相关知识，直接让模型回答
            prompt = `你是一个智能助手，请直接回答以下问题：${message}`;
        }

        // 发送到 LLM
        const response = await fetch(`${API_BASE_URL}/llm/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: prompt })
        });

        // 移除加载动画
        loadingDiv.remove();

        if (response.ok) {
            const data = await response.json();
            appendMessage(data.response, 'ai');
        } else {
            const errorData = await response.json();
            appendMessage('抱歉，发生错误: ' + (errorData.detail || '未知错误'), 'ai');
        }
    } catch (error) {
        loadingDiv.remove();
        appendMessage('抱歉，请求失败，请稍后重试', 'ai');
    } finally {
        // 恢复输入
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function showLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message-item ai-message';
    loadingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return loadingDiv;
}

function appendMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-item ${type}-message`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 添加错误处理
window.onerror = function(msg, url, line, col, error) {
    console.error('全局错误:', { msg, url, line, col, error });
    return false;
};
