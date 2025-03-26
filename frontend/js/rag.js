async function fetchRAGResults(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/rag/retrieve?query=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayRAGResults(data.results);
        } else {
            console.error("Failed to fetch RAG results");
        }
    } catch (error) {
        console.error("Error fetching RAG results:", error);
    }
}

function displayRAGResults(results) {
    const resultsContainer = document.getElementById('ragResults');
    if (resultsContainer) {
        resultsContainer.innerHTML = ''; // 清空之前的结果

        results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            resultItem.textContent = result;
            resultsContainer.appendChild(resultItem);
        });
    }
}

// 文件上传处理
const uploadForm = document.getElementById('uploadForm');
const uploadMessage = document.getElementById('uploadMessage');
const knowledgeCount = document.getElementById('knowledgeCount');

if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('knowledgeFile');
        const file = fileInput.files[0];

        if (!file) {
            showMessage('请选择要上传的文件', true);
            return;
        }

        if (!file.name.endsWith('.txt')) {
            showMessage('只支持上传 .txt 文件', true);
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE_URL}/api/rag/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showMessage(data.message, false);
                fileInput.value = ''; // 清空文件输入
                updateKnowledgeCount(); // 更新知识库统计
            } else {
                showMessage(data.detail || '上传失败', true);
            }
        } catch (error) {
            showMessage('服务器错误，请稍后重试', true);
        }
    });
}

// 更新知识库统计
async function updateKnowledgeCount() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/rag/stats`);
        const data = await response.json();
        if (response.ok && knowledgeCount) {
            knowledgeCount.textContent = data.count;
        }
    } catch (error) {
        console.error('获取知识库统计失败:', error);
    }
}

// 显示消息
function showMessage(message, isError = false) {
    if (uploadMessage) {
        uploadMessage.textContent = message;
        uploadMessage.className = `message ${isError ? 'error' : 'success'}`;
        setTimeout(() => {
            uploadMessage.className = 'message';
        }, 3000);
    }
}

// 页面加载时更新知识库统计（仅在知识库管理页面）
document.addEventListener('DOMContentLoaded', () => {
    if (knowledgeCount) {
        updateKnowledgeCount();
    }
}); 