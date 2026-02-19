"""
brain.py

Handles integration with Ollama for language model interactions.
Supports both simple prompt-based and full messages-based chat calls with streaming.
"""

import ollama
import re
from typing import Dict, Any, Optional, List, Generator
from config import DEFAULT_MAIN_MODEL, DEFAULT_CODING_MODEL, CODING_MODEL_FALLBACK


class Brain:
    def __init__(self):
        self.main_model: str = DEFAULT_MAIN_MODEL
        self.coding_model: str = DEFAULT_CODING_MODEL
        self.coding_model_fallback: str = CODING_MODEL_FALLBACK
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

    def generate_response(self, messages: List[Dict], model: Optional[str] = None, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Generate a streaming response, yielding chunks that distinguish between thinking and content.
        """
        selected_model = model if model else self.main_model
        
        full_content = ""
        is_thinking = False
        
        for chunk in self._call_ollama_stream(selected_model, messages, **kwargs):
            token = chunk['message']['content']
            full_content += token
            
            # Simple heuristic for thinking blocks if the model uses them (e.g., <thought> or similar)
            # If the model doesn't use tags, we'll treat the first part of the response as thinking 
            # if it's explicitly requested in the system prompt.
            
            yield {"type": "chunk", "content": token}

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
