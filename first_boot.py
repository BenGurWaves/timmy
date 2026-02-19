"""
first_boot.py

Implements Timmy's "First-Boot" Protocol.
Checks the local environment (Ollama, Python version, folders) and 
sets everything up perfectly before Timmy starts his first "Dream."
"""

import os
import sys
import subprocess
import requests
from config import DATA_PATH, TIMS_STUFF_PATH

def check_python_version():
    print("Checking Python version...")
    if sys.version_info.major == 3 and sys.version_info.minor == 12:
        print("Python 3.12 detected. Perfect.")
    else:
        print(f"Warning: Python {sys.version_info.major}.{sys.version_info.minor} detected. Python 3.12 is recommended.")

def check_ollama():
    print("Checking Ollama status...")
    try:
        res = requests.get("http://localhost:11434/api/tags")
        if res.status_code == 200:
            models = [m['name'] for m in res.json().get('models', [])]
            print(f"Ollama is running. Models found: {', '.join(models)}")
            if "qwen3:30b" not in models:
                print("Warning: 'qwen3:30b' not found. Timmy might be slow or less smart.")
        else:
            print("Error: Ollama is running but returned an error.")
    except:
        print("Error: Ollama is not running. Please start Ollama before launching Timmy.")

def setup_folders():
    print("Setting up folders...")
    for path in [DATA_PATH, TIMS_STUFF_PATH, os.path.join(TIMS_STUFF_PATH, "Projects"), os.path.join(TIMS_STUFF_PATH, "Opportunity Reports")]:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created folder: {path}")
        else:
            print(f"Folder already exists: {path}")

def run_first_boot():
    print("--- TIMMY FIRST-BOOT PROTOCOL ---")
    check_python_version()
    check_ollama()
    setup_folders()
    print("--- FIRST-BOOT COMPLETE. TIMMY IS READY. ---")

if __name__ == "__main__":
    run_first_boot()
