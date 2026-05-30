function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const text = input.value.trim();
    
    if (!text) return;

    // 顯示使用者訊息
    chatBox.innerHTML += `<div class="msg user">${text}</div>`;
    input.value = '';
    
    // 讓對話框自動捲動到最底部
    chatBox.scrollTop = chatBox.scrollHeight;

    // TODO (Member D): 這裡之後要串接 Member A 弄好的 AI 代理人 API
    // 模擬 AI 思考中...
    setTimeout(() => {
        chatBox.innerHTML += `<div class="msg bot">（系統開發中：這段訊息之後會接上 AI 的真實回覆）</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 1000);
}