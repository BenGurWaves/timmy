import os

class Config:
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3") # Default to llama3

    # ChromaDB Configuration
    CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/memory")

    # Safety Guardrails
    CONFIRM_DESTRUCTIVE_ACTIONS = True
    RATE_LIMIT_ACTIONS_PER_MINUTE = 60
    COMMAND_BLACKLIST = [
        "rm -rf /",
        "format C:",
        # Add other dangerous commands here
    ]

    # Logging
    LOG_FILE = os.getenv("LOG_FILE", "./data/logs/timmy.log")

    # Playwright Browser
    PLAYWRIGHT_HEADLESS = True

    # System Paths (Mac specific, will need adjustment for other OS)
    # APPS_PATH = "/Applications"

config = Config()
