"""
agent.py

This module defines the core Agent class for Timmy AI. It orchestrates interactions
between the Brain, Council, Memory, Loop Detector, Tools, and Skills.
It processes user messages, decides on actions, and manages the agent's state.
"""

import json
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
        The decision includes whether to use a tool, a skill, convene the council, or respond directly.
        """
        # Placeholder for a more sophisticated decision-making process.
        # In a real implementation, this would involve a structured prompt to the LLM
        # to output a JSON object indicating the action.
        
        # For now, a simple keyword-based decision.
        if "learn from youtube" in user_message.lower() and "http" in user_message:
            url = user_message.split("http")[-1].strip()
            return {"action": "learn_youtube", "url": "http" + url}
        elif "learn from webpage" in user_message.lower() and "http" in user_message:
            url = user_message.split("http")[-1].strip()
            return {"action": "learn_webpage", "url": "http" + url}
        elif "search" in user_message.lower():
            query = user_message.lower().replace("search", "").strip()
            return {"action": "use_skill", "skill_name": "Web Search", "query": query}
        elif "read file" in user_message.lower():
            path = user_message.lower().replace("read file", "").strip()
            return {"action": "use_skill", "skill_name": "File Manager", "operation": "read", "path": path}
        elif "write file" in user_message.lower():
            # This would need more sophisticated parsing or a structured tool call from the LLM
            return {"action": "respond", "response": "To write a file, please specify the path and content clearly."}
        elif "system info" in user_message.lower():
            return {"action": "use_skill", "skill_name": "System Information", "info_type": "all"}
        elif "take note" in user_message.lower():
            note_content = user_message.lower().replace("take note", "").strip()
            return {"action": "use_skill", "skill_name": "Note Taking", "operation": "take", "content": note_content}
        elif "retrieve note" in user_message.lower():
            query = user_message.lower().replace("retrieve note", "").strip()
            return {"action": "use_skill", "skill_name": "Note Taking", "operation": "retrieve", "query": query}
        elif "council" in user_message.lower() or len(user_message.split()) > 20: # Heuristic for complex problems
            return {"action": "convene_council", "problem": user_message}
        else:
            return {"action": "respond", "response": None} # Let the brain respond directly

    def handle_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """
        Processes a user message, decides on an action, executes it, and yields responses.
        """
        self.memory.add_to_memory("conversation_history", f"User: {user_message}")
        self.loop_detector.record_action("user_message", {"message": user_message})

        action_decision = self._decide_action(user_message)
        action_type = action_decision["action"]

        if self.loop_detector.detect_loop():
            yield {"type": "status", "text": "Loop detected! Timmy is rethinking its approach..."}
            # In a real scenario, the agent would use its brain to summarize and brainstorm.
            yield {"type": "text", "text": "It seems I might be stuck. Let me try a different approach or ask for clarification."}
            self.loop_detector.reset()
            # Fallback to direct response or ask for user input
            yield {"type": "text", "text": self.brain.think(f"I detected a loop while trying to respond to: {user_message}. Please help me rethink or provide more context.")}
            return

        if action_type == "learn_youtube":
            yield {"type": "status", "text": "Learning from YouTube..."}
            result = self.youtube_learner.learn_from_youtube(action_decision["url"])
            yield {"type": "tool_output", "tool_name": "YouTube Learner", "output": json.dumps(result, indent=2)}
            yield {"type": "text", "text": f"YouTube learning complete: {result.get("message", "")}"}
        elif action_type == "learn_webpage":
            yield {"type": "status", "text": "Learning from Webpage..."}
            result = self.web_scraper.learn_from_webpage(action_decision["url"])
            yield {"type": "tool_output", "tool_name": "Web Scraper", "output": json.dumps(result, indent=2)}
            yield {"type": "text", "text": f"Web page learning complete: {result.get("message", "")}"}
        elif action_type == "use_skill":
            skill_name = action_decision["skill_name"]
            if skill_name in self.skills:
                yield {"type": "status", "text": f"Using skill: {skill_name}..."}
                try:
                    skill_args = {k: v for k, v in action_decision.items() if k not in ["action", "skill_name"]}
                    result = self.skills[skill_name].execute(**skill_args)
                    yield {"type": "tool_output", "tool_name": skill_name, "output": json.dumps(result, indent=2)}
                    yield {"type": "text", "text": f"Skill \'{skill_name}\' executed. Result: {result.get("message", json.dumps(result))}"}
                except Exception as e:
                    self.loop_detector.record_error(str(e), {"skill": skill_name, "args": skill_args})
                    yield {"type": "error", "text": f"Error executing skill {skill_name}: {e}"}
            else:
                yield {"type": "error", "text": f"Unknown skill: {skill_name}"}
        elif action_type == "convene_council":
            yield {"type": "council_activated"}
            problem = action_decision["problem"]
            try:
                final_answer = self.council.convene(problem)
                yield {"type": "text", "text": f"Council's synthesized answer: {final_answer}"}
            except Exception as e:
                self.loop_detector.record_error(str(e), {"council_problem": problem})
                yield {"type": "error", "text": f"Error convening council: {e}"}
        else: # Direct response from brain
            yield {"type": "status", "text": "Timmy is thinking..."}
            try:
                # Retrieve relevant memory for context
                relevant_memories = self.memory.retrieve_from_memory("semantic_knowledge", user_message, n_results=3)
                context = "\n".join(relevant_memories) if relevant_memories else ""
                
                prompt_with_context = f"""You are Timmy, an AI assistant. Respond to the user's query.
                \nContext from memory: {context}\nUser: {user_message}"""
                
                response = self.brain.think(prompt_with_context)
                yield {"type": "text", "text": response}
            except Exception as e:
                self.loop_detector.record_error(str(e), {"user_message": user_message})
                yield {"type": "error", "text": f"Error generating response: {e}"}

        self.memory.add_to_memory("conversation_history", f"Timmy: {response}")
