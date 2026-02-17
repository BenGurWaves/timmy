document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");

    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = (event) => {
        console.log("WebSocket opened:", event);
        appendMessage("Timmy AI: Hello! How can I help you today?", "timmy-message");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WebSocket message received:", data);

        if (data.type === "text") {
            appendMessage(`Timmy AI: ${data.text}`, "timmy-message");
        } else if (data.type === "status") {
            appendMessage(data.text, "status-message");
        } else if (data.type === "tool_output") {
            appendMessage(`Tool Output (${data.tool_name}):\n${data.output}`, "tool-output");
        } else if (data.type === "council_activated") {
            appendMessage("Council Activated: Timmy is consulting with other models.", "council-message");
        } else if (data.type === "error") {
            appendMessage(`Error: ${data.text}`, "timmy-message");
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    ws.onclose = (event) => {
        console.log("WebSocket closed:", event);
        appendMessage("Disconnected from Timmy AI. Please refresh the page.", "status-message");
    };

    ws.onerror = (event) => {
        console.error("WebSocket error:", event);
        appendMessage("WebSocket error occurred. Check console for details.", "status-message");
    };

    sendButton.addEventListener("click", sendMessage);
    messageInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            appendMessage(`You: ${message}`, "user-message");
            ws.send(JSON.stringify({ message: message }));
            messageInput.value = "";
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function appendMessage(text, className) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message-bubble", className);
        messageElement.innerText = text;
        chatMessages.appendChild(messageElement);
    }
});
