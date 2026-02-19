"""
code_architect.py

Implements Timmy's "Code-Architect."
A high-level engineering tool that allows Timmy to architect 
and build entire multi-file applications in the 'tim's Stuff' 
folder with a single command. Includes system monitoring.
"""

import json
import os
import time
import subprocess
from typing import List, Dict, Any, Optional
from config import TIMS_STUFF_PATH

class CodeArchitect:
    def __init__(self, brain):
        self.brain = brain
        self.projects_path = os.path.join(TIMS_STUFF_PATH, "Projects")
        os.makedirs(self.projects_path, exist_ok=True)

    def architect_project(self, description: str) -> str:
        """Architect and build a multi-file project based on a description."""
        # 1. Generate a project plan
        prompt = f"""
        You are Timmy's Code-Architect. You've been asked to build: {description}.
        Create a detailed project plan, including a list of files and their purposes.
        Format your output as a JSON object: {{"project_name": "name", "files": [{{"path": "path", "purpose": "purpose"}}]}}
        """
        plan_json = self.brain.think(prompt)
        plan = json.loads(plan_json)
        
        project_name = plan.get("project_name", "New_Project")
        project_dir = os.path.join(self.projects_path, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 2. Build each file
        for file_info in plan.get("files", []):
            file_path = os.path.join(project_dir, file_info.get("path", ""))
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            file_prompt = f"""
            You are Timmy's Code-Architect. You're building the file: {file_info.get('path')} 
            for the project: {project_name}. 
            Purpose: {file_info.get('purpose')}.
            Write the full, high-quality code for this file.
            """
            code = self.brain.think(file_prompt)
            
            with open(file_path, 'w') as f:
                f.write(code)
        
        return f"I've architected and built the project '{project_name}' in 'tim's Stuff/Projects'."

    def monitor_system(self) -> str:
        """Monitor the M4 Max system performance (CPU, GPU, RAM)."""
        # Placeholder for actual system monitoring logic (e.g., using psutil or top)
        # For now, we'll use a simple shell command
        try:
            result = subprocess.run(["top", "-l", "1", "-n", "0"], capture_output=True, text=True)
            if result.returncode == 0:
                # Extract CPU and RAM usage
                lines = result.stdout.strip().split('\n')
                cpu_usage = lines[3] if len(lines) > 3 else "Unknown"
                ram_usage = lines[6] if len(lines) > 6 else "Unknown"
                return f"M4 Max Pulse: {cpu_usage} | {ram_usage}"
        except Exception as e:
            print(f"Error monitoring system: {e}")
        return "M4 Max Pulse: Monitoring unavailable."
