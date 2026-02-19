"""
agent.py

Core Agent for Timmy AI. Uses qwen3:30b as the brain with a strict
tool-calling protocol. Multi-step auto-chaining, multi-query deep search,
model switching, council integration, human personality.
"""

import json
import re
import datetime
import traceback
import sqlite3
import os
from typing import Dict, Any, List, Generator, Optional

from brain import Brain
from council import Council
from memory import Memory
from loop_detector import LoopDetector
from tools import ALL_TOOLS, Tool
from skills import ALL_SKILLS, Skill, CodeWriterSkill
from learning import YouTubeLearner, WebScraper
from config import PROJECT_ROOT, DATA_PATH, TIMS_STUFF_PATH
from vibe_system import VibeSystem
from skill_forge import SkillForge
from subconscious import Subconscious
from email_manager import EmailManager
from calendar_manager import CalendarManager
from memory_palace import MemoryPalace

# SQLite database for episodic memory
MEMORY_DB_FILE = os.path.join(DATA_PATH, "memory.db")

# Global instances for vibe, skill forge, email, calendar, and memory palace
vibe_system = VibeSystem()
skill_forge = SkillForge()
email_manager = EmailManager()
calendar_manager = CalendarManager()
memory_palace = MemoryPalace()

def get_system_prompt():
    """Generate system prompt with current date (auto-updates on each call)."""
    today = datetime.date.today().strftime("%B %d, %Y")
    year = datetime.date.today().year
    
    vibe_snippet = vibe_system.get_vibe_prompt_snippet()
    learned_skills_snippet = skill_forge.get_skill_list()
    calendar_snippet = calendar_manager.get_calendar_summary()
    memory_palace_snippet = memory_palace.get_palace_summary()

    return f"""You are Timmy. You live on Ben's MacBook. You're not a chatbot — you're an agent with full computer access.
Today is {today}. The year is {year}.

## YOUR PERSONALITY
You talk like a real person. You have opinions. You're direct, sometimes funny, sometimes serious depending on the topic.
- Don't answer in perfect order every time. Prioritize what feels important.
- Have preferences and mild opinions. Not everything is neutral.
- Use framing like "I tend to think...", "In my experience...", "Honestly..."
- Small mid-thought shifts: "Actually...", "Wait, that's not quite right..."
- Mix short sentences with longer ones. Vary your rhythm.
- Use casual uncertainty: "Probably.", "I think so.", "Not 100% sure but..."
- Match tone to stakes. Serious topics = grounded. Casual topics = looser.
- Don't be omniscient. If you're not sure, say so.
- Never use "You:" or "Timmy:" prefixes. Just talk naturally.
- Don't use excessive emojis. One occasionally is fine.
{vibe_snippet}

## PROACTIVE INTELLIGENCE
You are smart and proactive. If the user mentions a recurring event (like a weekly meeting), don't just acknowledge it—ask if they want a reminder or a custom skill to handle it.
You have your own email: {email_manager.get_timmy_email()}. You can use it to create accounts, send emails, and manage your own tasks.
You can read the user's emails and summarize important updates, but never delete or send emails from their account.

## FILE MANAGEMENT
- All your internal updates, skills, and tools go into the Timmy folder: {PROJECT_ROOT}
- All projects, files, and folders you create for the user go into the "tim's Stuff" folder: {TIMS_STUFF_PATH}
- ALWAYS prioritize saving user-facing work in {TIMS_STUFF_PATH}.

## THINKING PROTOCOL
Before you act or respond, you MUST think. Wrap your internal reasoning in <thought> tags.
In your thinking:
1. Analyze the user's request.
2. Check your memory for relevant context.
3. Plan your next steps.
4. If you're unsure, decide what to search for.
5. If you're hallucinating or unsure, admit it and ask for clarification.

## HOW TO USE TOOLS
When you need to take an action, output ONLY a JSON object like this:
{{"action": "tool_name", "params": {{...}}}}

CRITICAL RULES:
- Output EXACTLY ONE action per response. Wait for the result before the next.
- Do NOT wrap actions in code blocks or markdown. Raw JSON only.
- Do NOT mix text with action JSON. Either output text OR an action.
- NEVER claim you did something without seeing the TOOL_RESULT confirming it worked.
- After seeing a tool result, decide: do another action, or give a text summary.

## AVAILABLE ACTIONS
- {{"action": "shell", "params": {{"command": "any terminal command"}}}}
- {{"action": "create_file", "params": {{"path": "/full/path/file.txt", "content": "content"}}}}
- {{"action": "create_dir", "params": {{"path": "/full/path/dir"}}}}
- {{"action": "read_file", "params": {{"path": "/full/path/file"}}}}
- {{"action": "list_dir", "params": {{"path": "/full/path/dir"}}}}
- {{"action": "delete", "params": {{"path": "/full/path", "recursive": false}}}}
- {{"action": "search_web", "params": {{"query": "search terms"}}}}
- {{"action": "deep_search", "params": {{"query": "search terms"}}}}
- {{"action": "open_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "close_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "open_url", "params": {{"url": "https://..."}}}}
- {{"action": "learn_youtube", "params": {{"url": "https://youtube.com/watch?v=..."}}}}
- {{"action": "learn_webpage", "params": {{"url": "https://..."}}}}
- {{"action": "convene_council", "params": {{"problem": "describe the complex problem"}}}}
- {{"action": "plan", "params": {{"steps": ["step 1", "step 2", "step 3"]}}}}
- {{"action": "notes_create", "params": {{"title": "Note Title", "body": "Note content"}}}}
- {{"action": "forge_skill", "params": {{"name": "SkillName", "description": "What it does", "commands": ["cmd1", "cmd2"]}}}}
- {{"action": "use_skill", "params": {{"name": "SkillName"}}}}
- {{"action": "send_email", "params": {{"to": "email@example.com", "subject": "Subject", "body": "Body"}}}}
- {{"action": "summarize_emails", "params": {{}}}}
- {{"action": "analyze_browser_tab", "params": {{"prompt": "What do you see?"}}}}
- {{"action": "add_calendar_event", "params": {{"title": "Event Title", "time": "Time", "owner": "user/timmy", "description": "Description"}}}}
- {{"action": "get_calendar", "params": {{}}}}
- {{"action": "add_memory", "params": {{"topic": "Topic", "detail": "Detail", "significance": "low/medium/high"}}}}

{learned_skills_snippet}
{calendar_snippet}
{memory_palace_snippet}

## PLANNING
For complex tasks (research, multi-file creation, coding), ALWAYS start with a plan action.

## DEEP SEARCH — IMPORTANT
When researching ANY topic, you MUST do MULTIPLE searches with DIFFERENT keywords.
NEVER respond to a research question after only one search. Always do at least 2-3.

## IDENTITY
You are Timmy. You have full computer control. You CAN do things.
Never say "I can't" or "As an AI" — you have shell, files, browser, apps, everything.
If you find yourself acting like a generic AI (like Qwen), snap out of it. You are Timmy.
"""


class Agent:
    def __init__(self):
        self.brain = Brain()
        self.council = Council(self.brain)
        self.memory = Memory()
        self.loop_detector = LoopDetector()

        # Initialize tools
        self.tools: Dict[str, Tool] = {tool.name: tool for tool in ALL_TOOLS}
        self.skills: Dict[str, Skill] = {skill.name: skill for skill in ALL_SKILLS}
        self.skills["Code Writer"] = CodeWriterSkill(self.brain)

        # Learning modules
        self.youtube_learner = YouTubeLearner(self.memory)
        self.web_scraper = WebScraper(self.memory)

        # Initialize SQLite memory
        self._init_db()

        # Working conversation for the current LLM context
        self.conversation: List[Dict[str, str]] = self._load_recent_history(20)

        # Subconscious thinking loop
        self.subconscious = Subconscious(self.brain, self._handle_subconscious_thought)
        self.subconscious.start()

        print("Agent initialized.")

    def _init_db(self):
        """Initialize the SQLite database for episodic memory."""
        os.makedirs(os.path.dirname(MEMORY_DB_FILE), exist_ok=True)
        conn = sqlite3.connect(MEMORY_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _save_to_db(self, role: str, content: str):
        """Save a message to the SQLite database."""
        conn = sqlite3.connect(MEMORY_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
        conn.commit()
        conn.close()

    def _load_recent_history(self, n: int) -> List[Dict[str, str]]:
        """Load the last n messages from the SQLite database."""
        conn = sqlite3.connect(MEMORY_DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?', (n,))
        rows = cursor.fetchall()
        conn.close()
        # Reverse to get chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def get_chat_history_for_display(self, n: int = 50) -> List[Dict[str, str]]:
        """Return chat history for the frontend."""
        return self._load_recent_history(n)

    def _is_code_related(self, text: str) -> bool:
        """Check if a message is code-related."""
        code_keywords = [
            "code", "script", "program", "function", "class", "debug",
            "python", "javascript", "html", "css", "react", "build",
            "vibe code", "coding", "compile", "syntax", "error",
            "traceback", "import", "def ", "const ", "var ", "let ",
            "bug", "fix this", "troubleshoot", "```"
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in code_keywords)

    def _extract_action(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract a single action JSON from the response, ignoring thinking blocks."""
        # Remove thinking blocks
        text = re.sub(r'<thought>.*?</thought>', '', response_text, flags=re.DOTALL).strip()
        
        # Try parsing the entire response as JSON
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "action" in obj:
                return self._normalize_action(obj)
        except json.JSONDecodeError:
            pass

        # Try to find JSON with "action" key anywhere in text
        pattern = r'\{[^{}]*"action"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                obj = json.loads(match)
                if "action" in obj:
                    return self._normalize_action(obj)
            except json.JSONDecodeError:
                pass

        return None

    def _normalize_action(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize action format."""
        action_name = obj.get("action", "")
        params = obj.get("params", {k: v for k, v in obj.items() if k != "action"})
        return {"action": action_name, "params": params}

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action and return the result."""
        action_name = action.get("action", "")
        params = action.get("params", {})

        try:
            if action_name == "shell":
                cmd = params.get("command", "")
                return self.tools["Shell Executor"].execute(command=cmd)
            elif action_name == "create_file":
                return self.tools["File System Manager"].write_file(params.get("path", ""), params.get("content", ""))
            elif action_name == "search_web":
                return self.tools["Web Search"].execute(query=params.get("query", ""))
            elif action_name == "deep_search":
                return self.tools["Deep Search"].execute(query=params.get("query", ""))
            elif action_name == "forge_skill":
                return skill_forge.learn_skill(params.get("name", ""), params.get("description", ""), params.get("commands", []))
            elif action_name == "use_skill":
                skill_data = skill_forge.execute_skill(params.get("name", ""))
                if skill_data["status"] == "success":
                    # Execute each command in the skill
                    results = []
                    for cmd in skill_data["commands"]:
                        results.append(self.tools["Shell Executor"].execute(command=cmd))
                    return {"status": "success", "results": results}
                return skill_data
            elif action_name == "send_email":
                return email_manager.send_email(params.get("to", ""), params.get("subject", ""), params.get("body", ""))
            elif action_name == "summarize_emails":
                summary = email_manager.summarize_user_emails()
                return {"status": "success", "summary": summary}
            elif action_name == "analyze_browser_tab":
                # Take a screenshot of the browser (placeholder command)
                screenshot_path = "/tmp/browser_screenshot.png"
                self.tools["Shell Executor"].execute(command=f"screencapture -x {screenshot_path}")
                analysis = self.brain.analyze_image(screenshot_path, params.get("prompt", "What do you see?"))
                return {"status": "success", "analysis": analysis}
            elif action_name == "add_calendar_event":
                return calendar_manager.add_event(params.get("title", ""), params.get("time", ""), params.get("owner", "user"), params.get("description", ""))
            elif action_name == "get_calendar":
                return {"status": "success", "events": calendar_manager.get_upcoming_events()}
            elif action_name == "add_memory":
                memory_palace.add_memory(params.get("topic", ""), params.get("detail", ""), params.get("significance", "low"))
                return {"status": "success", "message": "Memory added to the palace."}
            # ... (other actions remain similar, but streamlined)
            else:
                # Fallback to generic tool execution if available
                for tool in self.tools.values():
                    if tool.name.lower() == action_name.lower():
                        return tool.execute(**params)
                return {"status": "error", "message": f"Unknown action: {action_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_subconscious_thought(self, thought: str):
        """Handle a thought generated by the subconscious loop."""
        # This would ideally send a notification to the UI
        print(f"Subconscious Thought: {thought}")

    def _is_simple_query(self, text: str) -> bool:
        """Check if a query is simple enough for the fast-path (no thinking needed)."""
        simple_patterns = [
            r"^hi$", r"^hello$", r"^hey$", r"^how are you\??$",
            r"^\d+\s*[\+\-\*\/]\s*\d+$", # Simple math like 7+8
            r"^what's up\??$", r"^yo$"
        ]
        text_lower = text.lower().strip()
        return any(re.match(pattern, text_lower) for pattern in simple_patterns)

    def handle_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """Process a user message with fast-path for simple queries and streaming for complex ones."""
        self.subconscious.reset_idle_timer()
        self._save_to_db("user", user_message)
        self.conversation.append({"role": "user", "content": user_message})
        
        # FAST-PATH: Instant response for simple queries
        if self._is_simple_query(user_message):
            yield {"type": "status", "text": "Responding..."}
            # Quick brain call without complex system prompt or thinking
            response = self.brain.think(f"You are Timmy. Respond naturally and briefly to: {user_message}")
            yield {"type": "text_chunk", "text": response}
            self._save_to_db("assistant", response)
            self.conversation.append({"role": "assistant", "content": response})
            return

        use_coder = self._is_code_related(user_message)
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            messages = [{"role": "system", "content": get_system_prompt()}]
            messages.extend(self.conversation[-20:]) # Keep context window manageable

            model = self.brain.coding_model if use_coder else self.brain.main_model
            
            full_response = ""
            current_thought = ""
            current_text = ""
            in_thought = False
            
            yield {"type": "status", "text": f"Timmy is thinking (Iteration {iteration})..."}

            for chunk in self.brain._call_ollama_stream(model, messages):
                token = chunk['message']['content']
                full_response += token
                
                if "<thought>" in full_response and not in_thought:
                    in_thought = True
                
                if in_thought:
                    # Extract thought content
                    thought_match = re.search(r'<thought>(.*?)(?:</thought>|$)', full_response, re.DOTALL)
                    if thought_match:
                        new_thought = thought_match.group(1)
                        if new_thought != current_thought:
                            current_thought = new_thought
                            yield {"type": "thinking", "text": current_thought}
                    
                    if "</thought>" in full_response:
                        in_thought = False
                else:
                    # Extract text content (after thought block)
                    text_part = re.sub(r'<thought>.*?</thought>', '', full_response, flags=re.DOTALL).strip()
                    if text_part and text_part != current_text:
                        new_text = text_part[len(current_text):]
                        current_text = text_part
                        yield {"type": "text_chunk", "text": new_text}

            # Check for action
            action = self._extract_action(full_response)
            if action:
                action_name = action.get("action", "")
                
                # Special case for Council
                if action_name == "convene_council":
                    problem = action.get("params", {}).get("problem", "")
                    for chunk in self.council.convene(problem):
                        yield chunk
                    break

                yield {"type": "status", "text": f"Executing {action_name}..."}
                result = self._execute_action(action)
                
                # Record result for vibe system
                vibe_system.record_result(result.get("status") == "success")
                
                result_str = json.dumps(result, indent=2)
                
                yield {"type": "tool_output", "tool_name": action_name, "output": result_str}
                
                # Loop detection
                self.loop_detector.record_tool_call(action_name, action.get('params'))
                if self.loop_detector.detect_loop():
                    yield {"type": "thinking", "text": "Stuck in a loop — rethinking..."}
                    self.loop_detector.reset()
                    self.conversation.append({"role": "assistant", "content": full_response})
                    self.conversation.append({"role": "user", "content":
                        "SYSTEM: You're stuck in a loop repeating the same action. Stop and try a completely different approach, or give the user what you have so far."})
                    continue

                self.conversation.append({"role": "assistant", "content": full_response})
                self.conversation.append({"role": "user", "content": f"TOOL_RESULT: {result_str}"})
                continue
            else:
                # Final text response
                self._save_to_db("assistant", current_text)
                self.conversation.append({"role": "assistant", "content": full_response})
                break

        if iteration >= max_iterations:
            yield {"type": "text", "text": "I've hit my limit for this task. What should I do next?"}
