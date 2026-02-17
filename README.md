# Timmy AI Agent

Timmy is an advanced AI agent designed to operate with full control over a macOS system, leveraging local Ollama models for intelligent decision-making, code generation, and task automation. It features a web-based chat interface, a sophisticated memory system, a learning pipeline, and a unique "Council" system for complex problem-solving.

## Features

-   **Multi-Model Support**: Utilizes various local Ollama models (e.g., `qwen3:30b`, `qwen3-coder:30b`) for different tasks, with dynamic switching capabilities.
-   **Council System**: Activates when facing complex problems, querying all available local models and synthesizing their responses for a comprehensive answer.
-   **No Rate Limits, Full Control**: Operates without artificial limitations, with full access to system commands. Destructive actions are subject to a confirmation prompt.
-   **Smart Loop Detection**: Prevents repetitive actions or errors by detecting loops and triggering a "rethink mode" to brainstorm new strategies.
-   **Web-based Chat Interface**: A clean, modern dark-themed GUI for interacting with Timmy, featuring conversation history, streaming responses, tool execution results, and Council activation indicators.
-   **Full Computer Control (macOS)**:
    -   **Shell**: Execute any terminal command.
    -   **File System**: Read, write, create, delete, search files/folders.
    -   **Browser**: Playwright automation for web navigation, content extraction, form filling, and clicks.
    -   **Web Search**: DuckDuckGo search with parsed results.
    -   **App Control**: Open, close, and interact with Mac applications via AppleScript.
-   **Local Memory System (ChromaDB)**: Stores conversation history, task summaries, learned knowledge, and episodic memory locally.
-   **Learning Pipeline**: Extracts and embeds knowledge from YouTube transcripts and web pages into its semantic memory.
-   **Skill Registry**: Modular Python modules for easily adding new capabilities.

## Project Structure

```
timmy/
├── main.py              # Entry point — starts the web server and agent
├── agent.py             # Core agent orchestration
├── brain.py             # Ollama integration, multi-model support
├── council.py           # Council system — query all models, synthesize
├── memory.py            # ChromaDB memory system
├── loop_detector.py     # Smart loop detection and rethink system
├── config.py            # All configuration — models, paths, settings
├── requirements.txt     # Python dependencies
├── server.py            # FastAPI web server for chat GUI
├── templates/
│   └── index.html       # Chat interface HTML
├── static/
│   ├── style.css        # Chat interface styling
│   └── script.js        # Chat interface JS (websocket/SSE for streaming)
├── tools/
│   ├── __init__.py
│   ├── base.py
│   ├── shell.py
│   ├── filesystem.py
│   ├── browser.py
│   ├── web_search.py
│   └── app_control.py
├── skills/
│   ├── __init__.py
│   ├── base.py
│   ├── web_search.py
│   ├── file_manager.py
│   ├── note_taking.py
│   ├── system_info.py
│   └── code_writer.py
├── learning/
│   ├── __init__.py
│   ├── youtube.py
│   ├── web_scraper.py
└── README.md
```

## Step-by-Step Tutorial for MacBook Users

This guide will walk you through setting up and running your Timmy AI agent on a MacBook Pro.

### 1. Prerequisites

Before you begin, ensure you have the following installed on your MacBook:

-   **Homebrew**: A package manager for macOS. Install it by running:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
-   **Python 3.9+**: Install via Homebrew:
    ```bash
    brew install python
    ```
-   **Git**: Usually pre-installed on macOS. Verify with `git --version`.
-   **Ollama**: Download and install from [ollama.com](https://ollama.com/). Ensure it's running in the background.
-   **Ollama Models**: Download the required models using the Ollama CLI. Timmy is configured to use:
    -   `qwen3:30b` (main brain model)
    -   `qwen3-coder:30b` (coding tasks)
    -   `deepseek-coder:33b` (coding tasks, alternative)
    -   You can download them with commands like: `ollama pull qwen3:30b`

### 2. Clone the Repository

Open your Terminal application and clone the Timmy repository:

```bash
cd ~ # Navigate to your home directory or preferred location
git clone https://github.com/BenGurWaves/timmy.git
cd timmy
```

### 3. Set up a Python Virtual Environment

It's best practice to use a virtual environment to manage project dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Install the Python packages required by Timmy:

```bash
pip install -r requirements.txt
```

This will install all dependencies including sentence-transformers for the memory embedding system.
The first run may take a minute to download the embedding model.

### 5. Install Playwright Browsers

Timmy uses Playwright for browser automation. Install the necessary browser binaries:

```bash
playwright install
```

### 6. Verify Ollama is Running

Ensure the Ollama application is running in your macOS menu bar. You can also check its status via the terminal:

```bash
ollama list
```
This command should list the models you've pulled.

### 7. Start Timmy

With all dependencies installed and Ollama running, you can now start the Timmy AI agent:

```bash
python main.py
```

You should see output indicating the FastAPI server starting, typically on `http://0.0.0.0:8000`.

### 8. Open the Chat Interface in Browser

Open your web browser and navigate to:

```
http://localhost:8000
```

You will see the Timmy AI chat interface.

### 9. How to Talk to Timmy

Type your messages into the input box at the bottom and press Enter or click "Send". Timmy will respond, and you'll see status updates like "Timmy is thinking..." or "Using skill: Web Search...".

### 10. How to Tell Timmy to Learn from a URL

Timmy can learn from online content. Try these commands:

-   **Learn from a YouTube video**: `learn from youtube https://www.youtube.com/watch?v=your_video_id`
-   **Learn from a web page**: `learn from webpage https://example.com/article`

Timmy will process the content and store it in its semantic memory.

### 11. How to Add New Skills

To add a new skill to Timmy:

1.  Create a new Python file (e.g., `my_new_skill.py`) in the `timmy/skills/` directory.
2.  Define a class that inherits from `skills.base.Skill` and implements the `execute` method.
3.  Add your new skill to the `ALL_SKILLS` list in `timmy/skills/__init__.py`.
4.  Restart Timmy (`python main.py`) for the new skill to be loaded.

### 12. What the Council System Is and When It Activates

The **Council System** is Timmy's mechanism for handling complex, ambiguous, or critical tasks. When Timmy detects such a situation (e.g., a very long or complex query, or if explicitly asked to "convene council"), it will:

1.  Query **all available local Ollama models** (as defined in `config.py`) with the same problem statement.
2.  Collect individual responses from each model.
3.  Use its main brain model (`qwen3:30b`) to **synthesize** these diverse responses into a single, comprehensive, and well-reasoned answer.

This process ensures that Timmy benefits from multiple perspectives and reduces the risk of single-model biases or failures, leading to more robust decision-making.

Enjoy interacting with your enhanced Timmy AI agent!
