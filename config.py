"""
Configuration for the Timmy AI agent.
"""
from typing import List, Dict, Union

# Model Configuration
DEFAULT_MAIN_MODEL = "qwen3:30b"
DEFAULT_CODING_MODEL = "qwen3-coder:30b"
CODING_MODEL_FALLBACK = "deepseek-coder:33b"

# List of all available models for the Council
AVAILABLE_MODELS: List[str] = [
    "qwen3:30b",
    "qwen3-coder:30b",
    "deepseek-coder:33b",
    "qwen2.5-coder:32b",
    "qwen2.5-coder:7b",
    "llama3.1:70b",
    "deepseek-coder:6.7b",
    "gpt-oss:20b",
    "qwen-insane:latest",
]

# Paths
PROJECT_ROOT = "/home/ubuntu/timmy"  # Assuming the project is in the home directory
DATA_PATH = f"{PROJECT_ROOT}/data"
MEMORY_PATH = f"{DATA_PATH}/memory"
LOGS_PATH = f"{DATA_PATH}/logs"
KNOWLEDGE_PATH = f"{DATA_PATH}/knowledge"
SKILLS_PATH = f"{PROJECT_ROOT}/skills"

# Loop Detection
LOOP_DETECTION_WINDOW = 5
LOOP_DETECTION_THRESHOLD = 3

# Web Server
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 8000
