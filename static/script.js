document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const statusDot = document.getElementById("status-dot");
    const connectionStatus = document.getElementById("connection-status");
    const thinkingBar = document.getElementById("thinking-bar");
    const thinkingText = document.getElementById("thinking-text");

    let ws = null;
    let reconnectAttempts = 0;
    let currentTimmyMessage = null;
    let currentThinkingMessage = null;

    // Load chat history first
    loadHistory().then(() => {
        connectWebSocket();
    });

    function connectWebSocket() {
        ws = new WebSocket(`ws://${window.location.host}/ws`);

        ws.onopen = () => {
            statusDot.className = "status-dot connected";
            connectionStatus.textContent = "Online";
            reconnectAttempts = 0;
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === "text_chunk") {
                hideThinking();
                if (!currentTimmyMessage) {
                    currentTimmyMessage = createMessageBubble("timmy-message");
                }
                currentTimmyMessage.textContent += data.text;
            } else if (data.type === "thinking") {
                showThinking(data.text);
                if (!currentThinkingMessage) {
                    currentThinkingMessage = createMessageBubble("thinking-message");
                }
                currentThinkingMessage.textContent = "Thinking: " + data.text;
            } else if (data.type === "status") {
                showThinking(data.text);
            } else if (data.type === "tool_output") {
                appendToolOutput(data.tool_name, data.output);
                currentTimmyMessage = null;
                currentThinkingMessage = null;
            } else if (data.type === "error") {
                hideThinking();
                appendMessage(data.text, "error-message");
                currentTimmyMessage = null;
                currentThinkingMessage = null;
            }

            scrollToBottom();
        };

        ws.onclose = () => {
            statusDot.className = "status-dot";
            connectionStatus.textContent = "Disconnected";
            hideThinking();

            // Auto-reconnect
            if (reconnectAttempts < 5) {
                reconnectAttempts++;
                setTimeout(connectWebSocket, 2000 * reconnectAttempts);
            }
        };

        ws.onerror = () => {
            console.error("WebSocket error");
        };
    }

    // Send message
    sendButton.addEventListener("click", sendMessage);
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    messageInput.addEventListener("input", () => {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message && ws && ws.readyState === WebSocket.OPEN) {
            appendMessage(message, "user-message");
            ws.send(JSON.stringify({ message: message }));
            messageInput.value = "";
            messageInput.style.height = "auto";
            currentTimmyMessage = null;
            currentThinkingMessage = null;
            scrollToBottom();
        }
    }

    function createMessageBubble(className) {
        const el = document.createElement("div");
        el.classList.add("message-bubble", className);
        chatMessages.appendChild(el);
        return el;
    }

    function appendMessage(text, className) {
        const el = createMessageBubble(className);
        el.textContent = text;
    }

    function appendToolOutput(toolName, output) {
        const wrapper = document.createElement("div");
        wrapper.classList.add("tool-output-wrapper");

        const toggle = document.createElement("div");
        toggle.classList.add("tool-output-toggle");
        toggle.innerHTML = `<span class="arrow">▶</span> ${toolName} output`;

        const content = document.createElement("div");
        content.classList.add("tool-output-content");
        content.textContent = output;

        toggle.addEventListener("click", () => {
            const arrow = toggle.querySelector(".arrow");
            if (content.classList.contains("visible")) {
                content.classList.remove("visible");
                arrow.classList.remove("open");
            } else {
                content.classList.add("visible");
                arrow.classList.add("open");
            }
        });

        wrapper.appendChild(toggle);
        wrapper.appendChild(content);
        chatMessages.appendChild(wrapper);
    }

    function showThinking(text) {
        thinkingBar.style.display = "flex";
        thinkingText.textContent = text || "Thinking...";
        statusDot.className = "status-dot thinking";
    }

    function hideThinking() {
        thinkingBar.style.display = "none";
        statusDot.className = "status-dot connected";
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function loadHistory() {
        try {
            const response = await fetch("/history");
            const data = await response.json();
            if (data.messages && data.messages.length > 0) {
                const divider = document.createElement("div");
                divider.classList.add("history-divider");
                divider.textContent = "— previous conversation —";
                chatMessages.appendChild(divider);

                data.messages.forEach((msg) => {
                    if (msg.role === "user") {
                        appendMessage(msg.content, "user-message");
                    } else if (msg.role === "assistant") {
                        appendMessage(msg.content, "timmy-message");
                    }
                });

                const endDivider = document.createElement("div");
                endDivider.classList.add("history-divider");
                endDivider.textContent = "— now —";
                chatMessages.appendChild(endDivider);

                scrollToBottom();
            }
        } catch (e) {
            console.log("Could not load history:", e);
        }
    }
});
