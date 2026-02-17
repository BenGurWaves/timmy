document.addEventListener("DOMContentLoaded", () => {
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");

    // Load chat history on page load
    loadHistory();

    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = (event) => {
        console.log("WebSocket opened:", event);
        appendMessage("Timmy AI: Connected and ready.", "status-message");
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

    async function loadHistory() {
        try {
            const response = await fetch("/history");
            const data = await response.json();
            if (data.messages && data.messages.length > 0) {
                appendMessage("--- Previous conversation ---", "status-message");
                data.messages.forEach((msg) => {
                    if (msg.startsWith("User: ")) {
                        appendMessage("You: " + msg.slice(6), "user-message");
                    } else if (msg.startsWith("Timmy: ")) {
                        appendMessage("Timmy AI: " + msg.slice(7), "timmy-message");
                    } else {
                        appendMessage(msg, "timmy-message");
                    }
                });
                appendMessage("--- End of previous conversation ---", "status-message");
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (e) {
            console.log("Could not load history:", e);
        }
    }
});
