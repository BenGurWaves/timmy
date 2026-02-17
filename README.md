# Timmy: Your Local AI Agent

Timmy is a powerful, locally-run AI agent designed to give you full control over your computer. Built with a modular architecture, Timmy integrates with local Large Language Models (LLMs) via Ollama, provides a robust tool system for computer control, manages memory locally with ChromaDB, and includes a learning pipeline to continuously expand its knowledge. All core functionalities are designed to run without cloud dependencies, ensuring privacy and performance.

## Core Architecture

### 1. Brain — Ollama Integration
- Uses [Ollama](https://ollama.ai/) as the local LLM backend.
- Supports configurable models (default: `llama3` or `mistral`).
- Structured prompt system with system prompt, conversation history, and tool results.

### 2. Chat Interface
- Terminal-based chat interface for immediate interaction.
- Manages conversation history with context window management.
- Provides streaming responses from Ollama for a more natural interaction.

### 3. Tool System — Full Computer Control
Timmy's tool system allows it to interact with your computer environment.
- **Shell/Terminal**: Execute commands and run scripts.
- **File System**: Read, write, create, delete, and search files and folders.
- **Browser Automation**: Utilizes Playwright to open URLs, search the web, extract content, fill forms, and click buttons.
- **Web Search**: Performs web searches using Google/DuckDuckGo and returns results.
- **App Control (macOS only)**: Opens/closes Mac applications using AppleScript/osascript.
- Each tool is implemented as a Python module in the `tools/` directory.
- **Safety Guardrails**: Includes confirmation prompts for destructive actions (delete, overwrite), rate limiting to prevent spam, and a command blacklist for dangerous operations.

### 4. Memory System — All Local
- **Short-term Memory**: Manages conversation history in memory.
- **Long-term Memory**: Uses a [ChromaDB](https://www.trychroma.com/) vector database stored locally.
- **Episodic Memory**: Stores summaries of past tasks and conversations.
- **Semantic Memory**: Stores learned knowledge from tutorials, documentation, and other sources.
- **Memory Retrieval**: Queries relevant memories when answering questions or performing tasks.

### 5. Skill Registry
- Skills are real Python modules located in the `skills/` directory.
- Each skill has a name, description, and an `execute` function.
- Timmy can list available skills and use them as needed.
- Easily extensible: new skills can be added by simply dropping a Python file into the directory.
- **Starter Skills Included**:
    - `web_search`: Performs web searches.
    - `file_manager`: Manages file system operations.
    - `note_taking`: Saves notes to local files.
    - `system_info`: Gathers system information (macOS).

### 6. Learning Pipeline
- **YouTube Transcript Extraction**: Extracts transcripts from YouTube videos using `youtube-transcript-api`.
- **Web Page Content Extraction**: Extracts content from web pages using BeautifulSoup and requests.
- **Content Chunking and Embedding**: Chunks extracted content and embeds it into ChromaDB for semantic memory.
- Timmy can be instructed to "learn from [URL]", processing and storing the knowledge for future use.

### 7. Safety & Guardrails
- **Confirmation Prompts**: Required for file deletion, system commands that modify system settings, and software installation.
- **Rate Limiting**: Configurable maximum actions per minute.
- **Logging**: All actions are logged to a local file (`data/logs/timmy.log`).
- **Kill Switch**: `Ctrl+C` gracefully stops all operations.

## Project Structure

```
timmy/
├── main.py              # Entry point, chat loop
├── agent.py             # Core agent logic, orchestration
├── brain.py             # Ollama integration, prompt management
├── memory.py            # ChromaDB memory system
├── config.py            # Configuration (model, safety settings, etc.)
├── requirements.txt     # Python dependencies
├── tools/
│   ├── __init__.py
│   ├── base.py          # Base tool class
│   ├── shell.py         # Terminal/shell commands
│   ├── filesystem.py    # File operations
│   ├── browser.py       # Playwright browser automation
│   ├── web_search.py    # Web search
│   └── app_control.py   # Mac app control via osascript
├── skills/
│   ├── __init__.py
│   ├── base.py          # Base skill class
│   ├── web_search.py    # Web search skill
│   ├── file_manager.py  # File management skill
│   ├── note_taking.py   # Note taking skill
│   └── system_info.py   # System information skill
├── learning/
│   ├── __init__.py
│   ├── youtube.py       # YouTube transcript extraction
│   ├── web_scraper.py   # Web page content extraction
│   └── knowledge.py     # Knowledge processing and storage
├── data/                # Local data storage
│   ├── memory/          # ChromaDB storage
│   ├── logs/            # Action logs
│   └── knowledge/       # Learned content
└── README.md            # Setup instructions for MacBook
```

## Prerequisites

To run Timmy on your MacBook, you will need:

- **Python 3.11+**
- **Ollama**: Installed and running locally. You can download it from [ollama.ai](https://ollama.ai/). Ensure you have a model downloaded (e.g., `ollama run llama3`).
- **Playwright Dependencies**: For browser automation, you'll need to install Playwright's browser binaries. This is typically done after installing the `playwright` Python package.

## Step-by-Step Setup Instructions for MacBook

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/BenGurWaves/timmy.git
    cd timmy
    ```

2.  **Install Python Dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Install Playwright Browser Binaries**:
    ```bash
    playwright install
    ```

4.  **Install Ollama and Download a Model**:
    If you haven't already, download and install Ollama from [ollama.ai](https://ollama.ai/).
    Then, download a model (e.g., Llama3):
    ```bash
    ollama run llama3
    ```
    Ensure Ollama is running in the background.

## How to Run Timmy

From the `timmy/` directory (with your virtual environment activated):

```bash
python main.py
```

You can also specify a different Ollama model:

```bash
python main.py --model mistral
```

## How to Add New Skills

To add a new skill to Timmy:

1.  Create a new Python file (e.g., `my_new_skill.py`) in the `timmy/skills/` directory.
2.  Define a class in this file that inherits from `BaseSkill` (from `skills.base`).
3.  Implement the `__init__` method to set the skill's `name` and `description`.
4.  Implement the `execute` method with the logic for your skill.

Example (`timmy/skills/my_new_skill.py`):

```python
from .base import BaseSkill
import logging

logger = logging.getLogger(__name__)

class MyNewSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="my_new_skill",
            description="A description of what my new skill does."
        )

    def execute(self, *args, **kwargs):
        logger.info("My new skill is executing!")
        # Add your skill logic here
        return "My new skill completed successfully!"
```

Timmy will automatically discover and load this new skill when it starts.

## Available Commands (within Timmy's chat interface)

-   `exit`: Quits the Timmy application.
-   You can interact with Timmy by typing natural language prompts. Timmy will use its brain, memory, tools, and skills to respond.

## Future Enhancements

-   GUI-based chat interface.
-   More sophisticated tool and skill selection logic.
-   Advanced context window management.
-   Integration with more local LLMs and embedding models.
-   Improved web parsing for search results and learning.
