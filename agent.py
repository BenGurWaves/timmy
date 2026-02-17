import logging
import re
from brain import Brain
from memory import Memory
from tools import ToolManager
from learning.youtube import YouTubeLearner
from learning.web_scraper import WebScraper
from learning.knowledge import KnowledgeProcessor
from skills import SkillManager
from config import config

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, model_name: str = config.OLLAMA_MODEL):
        self.brain = Brain(model_name=model_name)
        self.memory = Memory(persist_directory=config.CHROMA_PATH)
        self.tool_manager = ToolManager()
        self.skill_manager = SkillManager()
        self.youtube_learner = YouTubeLearner()
        self.web_scraper = WebScraper()
        self.knowledge_processor = KnowledgeProcessor(self.memory)
        self.conversation_history = [] # Short-term memory

        logger.info("Agent initialized.")

    def handle_message(self, user_message: str) -> str:
        self.conversation_history.append(("user", user_message))
        logger.info(f"User message: {user_message}")

        # 1. Retrieve relevant memories
        relevant_memories = self.memory.retrieve_relevant_memories(user_message)
        if relevant_memories:
            logger.info(f"Retrieved relevant memories: {relevant_memories}")

        # 2. Decide action based on prompt, history, tools, and memories
        # For now, a simple pass-through to the brain. Later, this will involve tool/skill selection.
        prompt_with_context = self._build_prompt_with_context(user_message, relevant_memories)
        response = self.brain.get_response(prompt_with_context)

        self.conversation_history.append(("timmy", response))
        logger.info(f"Timmy response: {response}")

        # 3. Store conversation in episodic memory (simplified for now)
        self.memory.add_episodic_memory(user_message, response)

        return response

    def stream_response(self, user_message: str):
        self.conversation_history.append(("user", user_message))
        logger.info(f"User message (streaming): {user_message}")

        relevant_memories = self.memory.retrieve_relevant_memories(user_message)
        if relevant_memories:
            logger.info(f"Retrieved relevant memories (streaming): {relevant_memories}")

        prompt_with_context = self._build_prompt_with_context(user_message, relevant_memories)
        
        full_response = ""
        for chunk in self.brain.stream_response(prompt_with_context):
            full_response += chunk
            yield chunk
        
        self.conversation_history.append(("timmy", full_response))
        logger.info(f"Timmy response (streaming): {full_response}")
        self.memory.add_episodic_memory(user_message, full_response)


    def _build_prompt_with_context(self, user_message: str, relevant_memories: list) -> str:
        # This is a simplified prompt building. A more sophisticated system would format this better.
        prompt = "You are Timmy, a helpful AI assistant.\n\n"
        if relevant_memories:
            prompt += "Relevant past information:\n"
            for mem in relevant_memories:
                prompt += f"- {mem}\n"
            prompt += "\n"
        
        prompt += "Conversation history:\n"
        for speaker, text in self.conversation_history:
            prompt += f"{speaker.capitalize()}: {text}\n"
        prompt += f"User: {user_message}\nTimmy:"
        return prompt

    def learn_from_url(self, url: str) -> str:
        logger.info(f"Agent initiated learning from URL: {url}")
        if "youtube.com/watch?v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
            content = self.youtube_learner.get_transcript(video_id)
            source_type = "youtube"
        else:
            content = self.web_scraper.scrape_page(url)
            source_type = "webpage"

        if content.startswith("Error:"):
            return content

        self.knowledge_processor.process_and_store(content, source=f"{source_type}-{url}")
        return f"Successfully learned from {url} and stored knowledge."

    def list_available_skills(self):
        return self.skill_manager.list_skills()

    def execute_skill(self, skill_name: str, *args, **kwargs):
        return self.skill_manager.execute_skill(skill_name, *args, **kwargs)

    def execute_tool(self, tool_name: str, *args, **kwargs):
        return self.tool_manager.execute_tool(tool_name, *args, **kwargs)
