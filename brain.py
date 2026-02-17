import ollama
import logging
from config import config

logger = logging.getLogger(__name__)

class Brain:
    def __init__(self, model_name: str = config.OLLAMA_MODEL):
        self.model_name = model_name
        self.client = ollama.Client(host=config.OLLAMA_BASE_URL)
        logger.info(f"Ollama Brain initialized with model: {self.model_name} and host: {config.OLLAMA_BASE_URL}")

    def get_response(self, prompt: str, conversation_history: list = None) -> str:
        messages = []
        if conversation_history:
            for role, content in conversation_history:
                messages.append({"role": role, "content": content})
        
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(model=self.model_name, messages=messages, stream=False)
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Error getting response from Ollama: {e}")
            return f"Error: Could not get response from Ollama. {e}"

    def stream_response(self, prompt: str, conversation_history: list = None):
        messages = []
        if conversation_history:
            for role, content in conversation_history:
                messages.append({"role": role, "content": content})
        
        messages.append({"role": "user", "content": prompt})

        try:
            for chunk in self.client.chat(model=self.model_name, messages=messages, stream=True):
                yield chunk["message"]["content"]
        except Exception as e:
            logger.error(f"Error streaming response from Ollama: {e}")
            yield f"Error: Could not stream response from Ollama. {e}"
