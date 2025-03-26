const API_BASE_URL = 'http://localhost:8000';

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
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('登录成功！正在跳转...', false);
                localStorage.setItem('username', username);
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } else {
                showMessage(data.detail || '登录失败', true);
            }
        } catch (error) {
            showMessage('服务器错误，请稍后重试', true);
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
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (password !== confirmPassword) {
            showMessage('两次输入的密码不一致', true);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/register?username=${username}&password=${password}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('注册成功！正在跳转到登录页面...', false);
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            } else {
                showMessage(data.detail || '注册失败', true);
            }
        } catch (error) {
            showMessage('服务器错误，请稍后重试', true);
        }
    });
}

// 显示消息
function showMessage(message, isError = false) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${isError ? 'error' : 'success'}`;
} 