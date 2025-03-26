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
