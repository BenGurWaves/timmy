# Timmy AI Agent

Timmy is a local AI agent with full control over your macOS system. He uses Ollama models as his brain, has a web-based chat interface, persistent memory, a learning pipeline, and a Council system for complex problems.

## Features

- **Multi-Model Brain**: qwen3:30b for thinking, qwen3-coder:30b for coding, auto-switches based on task
- **Council System**: Queries all local models for complex problems, synthesizes the best answer
- **Full Computer Control**: Shell, file system, browser, web search, app control, Apple Notes
- **Deep Search**: Multiple searches with different keywords for comprehensive research
- **Smart Loop Detection**: Detects when stuck and rethinks instead of repeating
- **Persistent Memory**: ChromaDB for semantic search + JSON for chat history, all local
- **Learning Pipeline**: Learn from YouTube transcripts and web pages
- **Human Personality**: Talks like a real person, not a chatbot

## Quick Start (macOS)

### Prerequisites
- **Ollama** installed and running ([ollama.com](https://ollama.com/))
- **Python 3.12** (NOT 3.14 — ChromaDB doesn't support it yet)
- **Git**

### Step-by-Step Setup

```bash
# 1. Install Python 3.12 if you don't have it
brew install python@3.12

# 2. Clone the repo
cd ~/Desktop
git clone https://github.com/BenGurWaves/timmy.git
cd timmy

# 3. Create virtual environment with Python 3.12
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate

# 4. Verify Python version (should say 3.12.x)
python --version

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install Playwright browsers
playwright install

# 7. Make sure Ollama is running (check menu bar or run)
ollama list

# 8. Start Timmy
python main.py

# 9. Open in browser
# Go to http://localhost:8000
```

### Updating Timmy

When there's an update:
```bash
cd ~/Desktop/timmy
source venv/bin/activate
git pull
pip install -r requirements.txt
python main.py
```

## Project Structure

```
timmy/
├── main.py              # Entry point
├── agent.py             # Core agent — planning, tool execution, auto-chaining
├── brain.py             # Ollama integration, model switching
├── council.py           # Council system — all models weigh in
├── memory.py            # ChromaDB semantic memory
├── loop_detector.py     # Loop detection and rethink
├── config.py            # Models, paths, settings
├── server.py            # FastAPI web server
├── templates/index.html # Chat UI
├── static/
│   ├── style.css        # Dark minimal theme
│   └── script.js        # WebSocket chat, thinking indicators
├── tools/               # Shell, filesystem, browser, web search, app control
├── skills/              # Extensible skill modules
├── learning/            # YouTube + web scraper learning
└── data/                # Local memory storage (auto-created)
```

## How It Works

1. You type a message in the chat
2. Timmy's brain (qwen3:30b) reads it and decides what to do
3. If it needs to act, it outputs a tool call (search, create file, run command, etc.)
4. The agent executes the tool and feeds the result back to the brain
5. The brain decides the next step — more actions or a final response
6. This loops up to 20 steps per request (auto-chaining)

For coding tasks, the system automatically switches to qwen3-coder:30b.
For complex/uncertain tasks, the Council queries all your local models.

## Adding Skills

1. Create `skills/my_skill.py` inheriting from `skills.base.Skill`
2. Add it to `ALL_SKILLS` in `skills/__init__.py`
3. Restart Timmy
