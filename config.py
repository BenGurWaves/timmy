"""
config.py

Configuration for the Timmy AI agent.
All paths are dynamically resolved relative to this file's location.
"""
import os
from typing import List

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

# Paths — dynamically resolved from this file's location
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
MEMORY_PATH = os.path.join(DATA_PATH, "memory")
LOGS_PATH = os.path.join(DATA_PATH, "logs")
KNOWLEDGE_PATH = os.path.join(DATA_PATH, "knowledge")
SKILLS_PATH = os.path.join(PROJECT_ROOT, "skills")

# Loop Detection
LOOP_DETECTION_WINDOW = 5
LOOP_DETECTION_THRESHOLD = 3

# Web Server
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = 8000
