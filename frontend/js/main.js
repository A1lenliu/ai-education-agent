// 显示消息的辅助函数
function showMessage(elementId, message, isError = false) {
    const messageElement = document.getElementById(elementId);
    if (messageElement) {
        messageElement.textContent = message;
        messageElement.className = `message ${isError ? 'error' : 'success'}`;
    } else {
        console.error(`未找到消息元素: ${elementId}`);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化...');
    
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

    // 处理聊天功能
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');

    // 初始化
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

// 发送消息函数
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // 清空输入框
    chatInput.value = '';
    
    // 显示用户消息
    appendMessage(message, 'user');
    
    // 显示加载指示器
    showLoadingIndicator();
    
    try {
        // 发送消息到服务器
        const requestData = {
            message: message,
            history: []  // 如果需要保持对话历史，可以从 localStorage 中获取
        };
        
        console.log('准备发送请求到:', `${API_BASE_URL}/llm/chat`);
        console.log('请求数据:', JSON.stringify(requestData, null, 2));
        
        const response = await fetch(`${API_BASE_URL}/llm/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('收到响应状态:', response.status);
        console.log('响应头:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('服务器响应错误:', {
                status: response.status,
                statusText: response.statusText,
                errorText: errorText
            });
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('收到的响应数据:', data);
        
        // 隐藏加载指示器
        hideLoadingIndicator();
        
        // 使用 setTimeout 确保 DOM 已更新
        setTimeout(() => {
            // 显示AI回复
            appendMessage(data.response, 'assistant');
            
            // 滚动到底部
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }, 0);
        
    } catch (error) {
        console.error('发送消息时出错:', error);
        hideLoadingIndicator();
        appendMessage('抱歉，发生错误，请稍后重试。', 'error');
    }
}

// 显示加载指示器
function showLoadingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.innerHTML = '<div class="loading">正在思考...</div>';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 隐藏加载指示器
function hideLoadingIndicator() {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// 添加消息到聊天界面
function appendMessage(message, type) {
    console.log('正在添加消息:', { message, type });
    
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) {
        console.error('未找到 chatMessages 元素');
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    messageDiv.textContent = message;
    
    console.log('创建的消息元素:', messageDiv);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    console.log('消息已添加到聊天界面');
}

// 添加错误处理
window.onerror = function(msg, url, line, col, error) {
    console.error('全局错误:', { msg, url, line, col, error });
    return false;
};
