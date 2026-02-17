"""
agent.py

This module defines the core Agent class for Timmy AI. It orchestrates interactions
between the Brain, Council, Memory, Loop Detector, Tools, and Skills.
It processes user messages, decides on actions, and manages the agent's state.
"""

import json
import datetime
from typing import Dict, Any, List, Generator

from brain import Brain
from council import Council
from memory import Memory
from loop_detector import LoopDetector
from tools import ALL_TOOLS, Tool
from skills import ALL_SKILLS, Skill, CodeWriterSkill
from learning import YouTubeLearner, WebScraper


class Agent:
    """
    The core AI agent, responsible for processing messages, making decisions,
    and orchestrating various components like Brain, Council, Memory, Tools, and Skills.
    """

    def __init__(self):
        self.brain = Brain()
        self.council = Council(self.brain)
        self.memory = Memory()
        self.loop_detector = LoopDetector()

        # Initialize tools and skills
        self.tools: Dict[str, Tool] = {tool.name: tool for tool in ALL_TOOLS}
        self.skills: Dict[str, Skill] = {skill.name: skill for skill in ALL_SKILLS}

        # CodeWriterSkill needs a Brain instance
        self.skills["Code Writer"] = CodeWriterSkill(self.brain)

        # Initialize learning modules
        self.youtube_learner = YouTubeLearner(self.memory)
        self.web_scraper = WebScraper(self.memory)

        print("Agent initialized with Brain, Council, Memory, Loop Detector, Tools, Skills, and Learning modules.")

    def _decide_action(self, user_message: str) -> Dict[str, Any]:
        """
        Uses the main brain model to decide the next action based on the user message.
        """
        if "learn from youtube" in user_message.lower() and "http" in user_message:
            url = "http" + user_message.split("http")[-1].strip()
            return {"action": "learn_youtube", "url": url}
        elif "learn from webpage" in user_message.lower() and "http" in user_message:
            url = "http" + user_message.split("http")[-1].strip()
            return {"action": "learn_webpage", "url": url}
        elif "learn from" in user_message.lower() and "http" in user_message:
            url = "http" + user_message.split("http")[-1].strip()
            if "youtube.com" in url or "youtu.be" in url:
                return {"action": "learn_youtube", "url": url}
            else:
                return {"action": "learn_webpage", "url": url}
        elif "search" in user_message.lower():
            query = user_message.lower().replace("search", "").strip()
            return {"action": "use_skill", "skill_name": "Web Search", "query": query}
        elif "read file" in user_message.lower():
            path = user_message.lower().replace("read file", "").strip()
            return {"action": "use_skill", "skill_name": "File Manager", "operation": "read", "path": path}
        elif "write file" in user_message.lower():
            return {"action": "respond", "response": "To write a file, please specify the path and content clearly."}
        elif "system info" in user_message.lower():
            return {"action": "use_skill", "skill_name": "System Information", "info_type": "all"}
        elif "take note" in user_message.lower():
            note_content = user_message.lower().replace("take note", "").strip()
            return {"action": "use_skill", "skill_name": "Note Taking", "operation": "take", "content": note_content}
        elif "retrieve note" in user_message.lower():
            query = user_message.lower().replace("retrieve note", "").strip()
            return {"action": "use_skill", "skill_name": "Note Taking", "operation": "retrieve", "query": query}
        elif "council" in user_message.lower() or len(user_message.split()) > 20:
            return {"action": "convene_council", "problem": user_message}
        else:
            return {"action": "respond", "response": None}

    def handle_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """
        Processes a user message, decides on an action, executes it, and yields responses.
        """
        self.memory.add_to_memory("conversation_history", f"User: {user_message}",
                                   metadata={"role": "user", "timestamp": datetime.datetime.now().isoformat()})
        self.loop_detector.record_action("user_message", {"message": user_message})

        action_decision = self._decide_action(user_message)
        action_type = action_decision["action"]

        if self.loop_detector.detect_loop():
            yield {"type": "status", "text": "Loop detected! Timmy is rethinking its approach..."}
            yield {"type": "text", "text": "It seems I might be stuck. Let me try a different approach or ask for clarification."}
            self.loop_detector.reset()
            rethink_response = self.brain.think(
                f"I detected a loop while trying to respond to: {user_message}. Please help me rethink or provide more context."
            )
            yield {"type": "text", "text": rethink_response}
            self.memory.add_to_memory("conversation_history", f"Timmy: {rethink_response}",
                                       metadata={"role": "assistant", "timestamp": datetime.datetime.now().isoformat()})
            return

        response_text = ""

        if action_type == "learn_youtube":
            yield {"type": "status", "text": "Learning from YouTube..."}
            result = self.youtube_learner.learn_from_youtube(action_decision["url"])
            yield {"type": "tool_output", "tool_name": "YouTube Learner", "output": json.dumps(result, indent=2)}
            response_text = f"YouTube learning complete: {result.get('message', '')}"
            yield {"type": "text", "text": response_text}
        elif action_type == "learn_webpage":
            yield {"type": "status", "text": "Learning from Webpage..."}
            result = self.web_scraper.learn_from_webpage(action_decision["url"])
            yield {"type": "tool_output", "tool_name": "Web Scraper", "output": json.dumps(result, indent=2)}
            response_text = f"Web page learning complete: {result.get('message', '')}"
            yield {"type": "text", "text": response_text}
        elif action_type == "use_skill":
            skill_name = action_decision["skill_name"]
            if skill_name in self.skills:
                yield {"type": "status", "text": f"Using skill: {skill_name}..."}
                try:
                    skill_args = {k: v for k, v in action_decision.items() if k not in ["action", "skill_name"]}
                    result = self.skills[skill_name].execute(**skill_args)
                    yield {"type": "tool_output", "tool_name": skill_name, "output": json.dumps(result, indent=2)}
                    response_text = f"Skill '{skill_name}' executed. Result: {result.get('message', json.dumps(result))}"
                    yield {"type": "text", "text": response_text}
                except Exception as e:
                    self.loop_detector.record_error(str(e), {"skill": skill_name, "args": skill_args})
                    response_text = f"Error executing skill {skill_name}: {e}"
                    yield {"type": "error", "text": response_text}
            else:
                response_text = f"Unknown skill: {skill_name}"
                yield {"type": "error", "text": response_text}
        elif action_type == "convene_council":
            yield {"type": "council_activated"}
            problem = action_decision["problem"]
            try:
                final_answer = self.council.convene(problem)
                response_text = f"Council's synthesized answer: {final_answer}"
                yield {"type": "text", "text": response_text}
            except Exception as e:
                self.loop_detector.record_error(str(e), {"council_problem": problem})
                response_text = f"Error convening council: {e}"
                yield {"type": "error", "text": response_text}
        else:  # Direct response from brain
            yield {"type": "status", "text": "Timmy is thinking..."}
            try:
                # Retrieve relevant memory for context
                relevant_memories = self.memory.retrieve_from_memory("semantic_knowledge", user_message, n_results=3)
                context = "\n".join(relevant_memories) if relevant_memories else ""

                prompt_with_context = f"""You are Timmy, an AI assistant. Respond to the user's query.
Context from memory: {context}
User: {user_message}"""

                response_text = self.brain.think(prompt_with_context)
                yield {"type": "text", "text": response_text}
            except Exception as e:
                self.loop_detector.record_error(str(e), {"user_message": user_message})
                response_text = f"Error generating response: {e}"
                yield {"type": "error", "text": response_text}

        if response_text:
            self.memory.add_to_memory("conversation_history", f"Timmy: {response_text}",
                                       metadata={"role": "assistant", "timestamp": datetime.datetime.now().isoformat()})
