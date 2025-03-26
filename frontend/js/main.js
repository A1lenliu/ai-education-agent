const API_BASE_URL = 'http://localhost:8000';

// 显示消息的辅助函数
function showMessage(elementId, message, isError = false) {
    const messageElement = document.getElementById(elementId);
    messageElement.textContent = message;
    messageElement.className = `message ${isError ? 'error' : 'success'}`;
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
        const response = await fetch(`${API_BASE_URL}/llm/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
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
