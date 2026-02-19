"""
brain.py

Handles integration with Ollama for language model interactions.
Supports both simple prompt-based and full messages-based chat calls with streaming.
Includes support for visual models like Qwen-VL.
"""

import ollama
import re
import os
from typing import Dict, Any, Optional, List, Generator
from config import DEFAULT_MAIN_MODEL, DEFAULT_CODING_MODEL, CODING_MODEL_FALLBACK


class Brain:
    def __init__(self):
        self.main_model: str = DEFAULT_MAIN_MODEL
        self.coding_model: str = DEFAULT_CODING_MODEL
        self.coding_model_fallback: str = CODING_MODEL_FALLBACK
        self.visual_model: str = "qwen3-vl:32b" # User's visual model
        print(f"Brain initialized. Main model: {self.main_model}, Coding model: {self.coding_model}")

    def _call_ollama_stream(self, model: str, messages: List[Dict], **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Call Ollama API with streaming enabled.
        """
        try:
            stream = ollama.chat(model=model, messages=messages, stream=True, **kwargs)
            for chunk in stream:
                yield chunk
        except Exception as e:
            print(f"Error calling Ollama model {model}: {e}")
            raise

    def think(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate a non-streaming response using the specified model."""
        selected_model = model if model else self.main_model
        print(f"Thinking with model: {selected_model}")
        try:
            response = ollama.chat(model=selected_model, messages=[{'role': 'user', 'content': prompt}], **kwargs)
            return response['message']['content']
        except Exception as e:
            print(f"Error calling Ollama model {selected_model}: {e}")
            raise

    def analyze_image(self, image_path: str, prompt: str) -> str:
        """Analyze an image using the visual model (Qwen-VL)."""
        if not os.path.exists(image_path):
            return f"Error: Image path {image_path} does not exist."
            
        print(f"Analyzing image with model: {self.visual_model}")
        try:
            response = ollama.chat(
                model=self.visual_model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_path]
                }]
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error calling visual model {self.visual_model}: {e}")
            return f"Error analyzing image: {e}"

    def switch_model(self, task_type: str, new_model: str) -> None:
        if task_type == 'main':
            self.main_model = new_model
            print(f"Main model switched to: {self.main_model}")
        elif task_type == 'coding':
            self.coding_model = new_model
            print(f"Coding model switched to: {self.coding_model}")

    def get_available_models(self) -> List[str]:
        from config import AVAILABLE_MODELS
        return AVAILABLE_MODELS
