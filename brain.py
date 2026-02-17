"""
brain.py

Handles integration with Ollama for language model interactions.
Supports both simple prompt-based and full messages-based chat calls.
"""

import ollama
from typing import Dict, Any, Optional, List
from config import DEFAULT_MAIN_MODEL, DEFAULT_CODING_MODEL, CODING_MODEL_FALLBACK


class Brain:
    def __init__(self):
        self.main_model: str = DEFAULT_MAIN_MODEL
        self.coding_model: str = DEFAULT_CODING_MODEL
        self.coding_model_fallback: str = CODING_MODEL_FALLBACK
        print(f"Brain initialized. Main model: {self.main_model}, Coding model: {self.coding_model}")

    def _call_ollama(self, model: str, prompt: Optional[str] = None, messages: Optional[List[Dict]] = None, **kwargs) -> Dict[str, Any]:
        """
        Call Ollama API. Supports either a simple prompt or full messages list.
        If messages is provided, prompt is ignored.
        """
        try:
            if messages:
                response = ollama.chat(model=model, messages=messages, **kwargs)
            elif prompt:
                response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}], **kwargs)
            else:
                raise ValueError("Either prompt or messages must be provided")
            return response
        except Exception as e:
            print(f"Error calling Ollama model {model}: {e}")
            raise

    def think(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate a response using the main brain model."""
        selected_model = model if model else self.main_model
        print(f"Thinking with model: {selected_model}")
        response = self._call_ollama(selected_model, prompt=prompt, **kwargs)
        return response['message']['content']

    def code(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate code using the coding model with fallback."""
        selected_model = model if model else self.coding_model
        print(f"Coding with model: {selected_model}")
        try:
            response = self._call_ollama(selected_model, prompt=prompt, **kwargs)
            return response['message']['content']
        except Exception as e:
            print(f"Failed with {selected_model}, falling back to {self.coding_model_fallback}: {e}")
            response = self._call_ollama(self.coding_model_fallback, prompt=prompt, **kwargs)
            return response['message']['content']

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
