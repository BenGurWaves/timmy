"""
brain.py

This module handles the integration with Ollama for language model interactions.
It provides functionalities for dynamic model switching and managing different models
for various tasks (e.g., main brain, coding tasks).
"""

import ollama
from typing import Dict, Any, Optional
from config import DEFAULT_MAIN_MODEL, DEFAULT_CODING_MODEL, CODING_MODEL_FALLBACK

class Brain:
    """
    Manages interactions with Ollama models, including model selection and dynamic switching.
    """

    def __init__(self):
        self.main_model: str = DEFAULT_MAIN_MODEL
        self.coding_model: str = DEFAULT_CODING_MODEL
        self.coding_model_fallback: str = CODING_MODEL_FALLBACK
        print(f"Brain initialized. Main model: {self.main_model}, Coding model: {self.coding_model}")

    def _call_ollama(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Internal method to call the Ollama API.
        """
        try:
            response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}], **kwargs)
            return response
        except Exception as e:
            print(f"Error calling Ollama model {model}: {e}")
            raise

    def think(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Generates a response using the main brain model or a specified model.
        """
        selected_model = model if model else self.main_model
        print(f"Thinking with model: {selected_model}")
        response = self._call_ollama(selected_model, prompt, **kwargs)
        return response['message']['content']

    def code(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Generates code or assists with coding tasks using the coding model.
        Includes a fallback mechanism.
        """
        selected_model = model if model else self.coding_model
        print(f"Coding with model: {selected_model}")
        try:
            response = self._call_ollama(selected_model, prompt, **kwargs)
            return response['message']['content']
        except Exception as e:
            print(f"Failed with {selected_model}, falling back to {self.coding_model_fallback}: {e}")
            response = self._call_ollama(self.coding_model_fallback, prompt, **kwargs)
            return response['message']['content']

    def switch_model(self, task_type: str, new_model: str) -> None:
        """
        Dynamically switches the model used for a specific task type.
        Task types can be 'main' or 'coding'.
        """
        if task_type == 'main':
            self.main_model = new_model
            print(f"Main model switched to: {self.main_model}")
        elif task_type == 'coding':
            self.coding_model = new_model
            print(f"Coding model switched to: {self.coding_model}")
        else:
            print(f"Unknown task type: {task_type}. Models can only be 'main' or 'coding'.")

    def get_available_models(self) -> List[str]:
        """
        Returns a list of models available in Ollama.
        This would typically query the Ollama server, but for now, we'll use the config list.
        """
        # In a real scenario, this would query `ollama.list()`
        # For now, we rely on the configured list.
        from config import AVAILABLE_MODELS
        return AVAILABLE_MODELS

