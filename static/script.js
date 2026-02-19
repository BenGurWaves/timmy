let socket;
let currentTab = 'chat';
let currentAssistantMessage = null;

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initWebSocket();
    initInput();
    loadHistory();
});

function initTabs() {
    const navLinks = document.querySelectorAll('.nav-links li');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const tabId = link.getAttribute('data-tab');
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Update active tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });

            currentTab = tabId;
        });
    });
}

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

    socket.onopen = () => {
        console.log('Connected to Timmy Singularity-Horizon');
        addStatusMessage('CONNECTED TO OMNI-KERNEL');
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleIncomingData(data);
    };

    socket.onclose = () => {
        addStatusMessage('DISCONNECTED FROM OMNI-KERNEL');
        setTimeout(initWebSocket, 3000);
    };
}

function handleIncomingData(data) {
    switch (data.type) {
        case 'text_chunk':
            appendAssistantChunk(data.text);
            break;
        case 'thinking':
            updateThinking(data.text);
            break;
        case 'status':
            updateStatus(data.text);
            break;
        case 'tool_output':
            appendToolOutput(data.tool_name, data.output);
            break;
        case 'subconscious_thought':
            appendDream(data.text);
            break;
        case 'synapse_update':
            appendSynapse(data.synapse.source, data.synapse.target, data.synapse.relationship);
            break;
        case 'evolution':
            appendEvolution(data.text);
            break;
        case 'market':
            updateMarket(data.text);
            break;
        case 'draft':
            appendDraft(data.text);
            break;
        case 'vibe':
            updateVibe(data.text);
            break;
        case 'pulse':
            updatePulse(data.temp);
            break;
    }
}

function initInput() {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);
}

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const text = userInput.value.trim();

    if (text && socket.readyState === WebSocket.OPEN) {
        appendUserMessage(text);
        socket.send(JSON.stringify({ message: text }));
        userInput.value = '';
        userInput.style.height = 'auto';
        
        // Reset thinking
        document.getElementById('thinking-container').classList.add('hidden');
        document.getElementById('thinking-text').innerText = '';
        currentAssistantMessage = null;
    }
}

// UI Helpers
function appendUserMessage(text) {
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'message user';
    div.innerText = text;
    messages.appendChild(div);
    scrollToBottom();
}

function appendAssistantChunk(text) {
    const messages = document.getElementById('messages');
    if (!currentAssistantMessage) {
        currentAssistantMessage = document.createElement('div');
        currentAssistantMessage.className = 'message assistant';
        messages.appendChild(currentAssistantMessage);
    }
    currentAssistantMessage.innerText += text;
    scrollToBottom();
}

function updateThinking(text) {
    const container = document.getElementById('thinking-container');
    const textEl = document.getElementById('thinking-text');
    container.classList.remove('hidden');
    textEl.innerText = text;
    scrollToBottom();
}

function updateStatus(text) {
    currentAssistantMessage = null;
    console.log('Status:', text);
}

function appendToolOutput(name, output) {
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'message assistant tool-output';
    div.innerHTML = `<strong><i class="fas fa-terminal"></i> ${name}</strong><pre style="font-size: 0.8rem; margin-top: 10px; background: #000; padding: 10px; border-radius: 4px; overflow-x: auto;">${output}</pre>`;
    messages.appendChild(div);
    scrollToBottom();
}

function appendDream(text) {
    const feed = document.getElementById('dream-feed');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.style.marginBottom = '15px';
    div.innerText = text;
    feed.prepend(div);
}

function appendSynapse(source, target, rel) {
    const grid = document.getElementById('synapse-grid');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.style.marginBottom = '15px';
    div.innerHTML = `<strong>${source}</strong> <i class="fas fa-link"></i> <strong>${target}</strong><p style="font-size: 0.85rem; color: var(--text-dim); margin-top: 5px;">${rel}</p>`;
    grid.prepend(div);
}

function appendEvolution(text) {
    const list = document.getElementById('evolution-list');
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.style.marginBottom = '10px';
    div.innerText = text;
    list.prepend(div);
}

function updateMarket(text) {
    const ticker = document.getElementById('market-ticker');
    const span = document.createElement('span');
    span.style.marginRight = '30px';
    span.innerText = text;
    ticker.appendChild(span);
}

function appendDraft(text) {
    const list = document.getElementById('drafts-list');
    const div = document.createElement('div');
    div.className = 'draft-card';
    div.innerText = text;
    list.prepend(div);
}

function updateVibe(vibe) {
    document.getElementById('current-vibe').innerText = vibe.toUpperCase();
}

function updatePulse(temp) {
    document.getElementById('cpu-temp').innerText = `${temp}°C`;
}

function addStatusMessage(text) {
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'status-message';
    div.style.textAlign = 'center';
    div.style.fontSize = '0.7rem';
    div.style.color = 'var(--text-dim)';
    div.style.margin = '10px 0';
    div.innerText = `— ${text} —`;
    messages.appendChild(div);
    scrollToBottom();
}

async function loadHistory() {
    try {
        const response = await fetch('/history');
        const data = await response.json();
        if (data.messages) {
            data.messages.forEach(msg => {
                if (msg.role === 'user') appendUserMessage(msg.content);
                else if (msg.role === 'assistant') {
                    currentAssistantMessage = null;
                    appendAssistantChunk(msg.content);
                }
            });
        }
    } catch (e) {
        console.error('History load failed:', e);
    }
}

function scrollToBottom() {
    const window = document.getElementById('chat-window');
    window.scrollTop = window.scrollHeight;
}
