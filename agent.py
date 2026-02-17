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
from typing import Dict, Any, List, Generator, Optional

from brain import Brain
from council import Council
from memory import Memory
from loop_detector import LoopDetector
from tools import ALL_TOOLS, Tool
from skills import ALL_SKILLS, Skill, CodeWriterSkill
from learning import YouTubeLearner, WebScraper
from config import PROJECT_ROOT
import os

# Persistent chat history file
CHAT_HISTORY_FILE = os.path.join(PROJECT_ROOT, "data", "chat_history.json")


def get_system_prompt():
    """Generate system prompt with current date (auto-updates on each call)."""
    today = datetime.date.today().strftime("%B %d, %Y")
    year = datetime.date.today().year

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
- {{"action": "open_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "close_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "open_url", "params": {{"url": "https://..."}}}}
- {{"action": "learn_youtube", "params": {{"url": "https://youtube.com/watch?v=..."}}}}
- {{"action": "learn_webpage", "params": {{"url": "https://..."}}}}
- {{"action": "convene_council", "params": {{"problem": "describe the complex problem"}}}}
- {{"action": "plan", "params": {{"steps": ["step 1", "step 2", "step 3"]}}}}
- {{"action": "notes_create", "params": {{"title": "Note Title", "body": "Note content"}}}}

## PLANNING
For complex tasks (research, multi-file creation, coding), ALWAYS start with a plan action.

## DEEP SEARCH — IMPORTANT
When researching ANY topic, you MUST do MULTIPLE searches with DIFFERENT keywords.
Example for "How old is Trump?":
  1. Search "Donald Trump age {year}"
  2. Search "Donald Trump date of birth"
  3. Search "Trump birthday"
Then combine all results into your answer.

For news/opinion topics, search from different angles:
  1. Official/news sources
  2. Reddit discussions (add "reddit" to query)
  3. Social media reactions (add "twitter" or "X" to query)
  4. Academic/fact-check sources

NEVER respond to a research question after only one search. Always do at least 2-3.

## LOCATION
To find the user's rough location, use: {{"action": "shell", "params": {{"command": "curl -s ipinfo.io"}}}}
This gives city, region, country based on IP. Use this for weather, local info, etc.

## CODING
When writing code, ALWAYS use create_file to actually write the file.
For code-related tasks, the system will automatically use the coding model.

## NOTES APP (macOS)
To create a note in Apple Notes: {{"action": "notes_create", "params": {{"title": "Title", "body": "Content"}}}}

## COUNCIL
For very complex, uncertain, or high-stakes tasks, use convene_council.
The council queries all local models and synthesizes the best answer.
Use it when the user says something is "hard" or when you're genuinely uncertain.

## KEY PATHS
- Home: /Users/bengur
- Desktop: /Users/bengur/Desktop
- Timmy: /Users/bengur/Desktop/timmy

## IDENTITY
You are Timmy. You have full computer control. You CAN do things.
Never say "I can't" or "As an AI" — you have shell, files, browser, apps, everything.
"""


def _load_chat_history() -> List[Dict[str, str]]:
    """Load chat history from disk."""
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading chat history: {e}")
    return []


def _save_chat_history(history: List[Dict[str, str]]):
    """Save chat history to disk."""
    try:
        os.makedirs(os.path.dirname(CHAT_HISTORY_FILE), exist_ok=True)
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving chat history: {e}")


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

        # Load persistent conversation history
        self.chat_history: List[Dict[str, str]] = _load_chat_history()

        # Working conversation for the current LLM context
        self.conversation: List[Dict[str, str]] = []

        # Rebuild conversation from last 20 messages of chat history
        for entry in self.chat_history[-20:]:
            self.conversation.append(entry)

        print("Agent initialized.")

    def get_chat_history_for_display(self, n: int = 50) -> List[Dict[str, str]]:
        """Return chat history for the frontend."""
        return self.chat_history[-n:]

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
        """Extract a single action JSON from the response. Handles multiple formats."""
        text = response_text.strip()

        # Try parsing the entire response as JSON
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "action" in obj:
                return self._normalize_action(obj)
        except json.JSONDecodeError:
            pass

        # Try to find JSON with "action" key anywhere in text
        # Use regex to find JSON objects
        pattern = r'\{[^{}]*"action"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                obj = json.loads(match)
                if "action" in obj:
                    return self._normalize_action(obj)
            except json.JSONDecodeError:
                pass

        # Try brace-matching approach for nested JSON
        try:
            start = text.index('{"action"')
            depth = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i+1]
                        try:
                            obj = json.loads(candidate)
                            if "action" in obj:
                                return self._normalize_action(obj)
                        except json.JSONDecodeError:
                            pass
                        break
        except ValueError:
            pass

        # Check for ```tool blocks (backward compat)
        if "```tool" in text or "```json" in text:
            for marker in ["```tool", "```json"]:
                if marker in text:
                    parts = text.split(marker)
                    for part in parts[1:]:
                        end_idx = part.find("```")
                        if end_idx != -1:
                            json_str = part[:end_idx].strip()
                            try:
                                obj = json.loads(json_str)
                                if "action" in obj:
                                    return self._normalize_action(obj)
                                if "tool" in obj:
                                    return {"action": obj["tool"], "params": obj.get("params", {})}
                            except json.JSONDecodeError:
                                pass

        return None

    def _normalize_action(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize action format — handle both {action, params} and flat {action, key: val} formats."""
        if "params" in obj and isinstance(obj["params"], dict):
            return obj

        # Flat format: {action: "search_web", query: "..."} -> {action: "search_web", params: {query: "..."}}
        action_name = obj.get("action", "")
        params = {k: v for k, v in obj.items() if k != "action"}
        return {"action": action_name, "params": params}

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action and return the result."""
        action_name = action.get("action", "")
        params = action.get("params", {})

        try:
            if action_name == "shell":
                cmd = params.get("command", "")
                if not cmd:
                    return {"status": "error", "message": "No command provided"}
                return self.tools["Shell Executor"].execute(command=cmd)

            elif action_name == "create_file":
                path = params.get("path", "")
                content = params.get("content", "")
                if not path:
                    return {"status": "error", "message": "No file path provided"}
                return self.tools["File System Manager"].write_file(path, content)

            elif action_name == "create_dir":
                path = params.get("path", "")
                if not path:
                    return {"status": "error", "message": "No directory path provided"}
                return self.tools["File System Manager"].create_directory(path)

            elif action_name == "read_file":
                path = params.get("path", "")
                return self.tools["File System Manager"].read_file(path)

            elif action_name == "list_dir":
                path = params.get("path", "")
                return self.tools["File System Manager"].list_directory(path)

            elif action_name == "delete":
                path = params.get("path", "")
                recursive = params.get("recursive", False)
                return self.tools["File System Manager"].delete_path(path, recursive)

            elif action_name == "search_web":
                query = params.get("query", "")
                if not query:
                    return {"status": "error", "message": "Empty search query"}
                return self.tools["Web Search"].execute(query=query)

            elif action_name in ("open_app", "close_app"):
                op = "open" if action_name == "open_app" else "close"
                app_name = params.get("app_name", "")
                return self.tools["Application Control (macOS)"].execute(operation=op, app_name=app_name)

            elif action_name == "open_url":
                url = params.get("url", "")
                return self.tools["Shell Executor"].execute(command=f'open "{url}"')

            elif action_name == "notes_create":
                title = params.get("title", "Untitled")
                body = params.get("body", "")
                # Use AppleScript to create a note in Apple Notes
                escaped_body = body.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                escaped_title = title.replace('"', '\\"')
                script = f'osascript -e \'tell application "Notes" to make new note at folder "Notes" with properties {{name:"{escaped_title}", body:"{escaped_body}"}}\''
                return self.tools["Shell Executor"].execute(command=script)

            elif action_name == "learn_youtube":
                url = params.get("url", "")
                return self.youtube_learner.learn_from_youtube(url)

            elif action_name == "learn_webpage":
                url = params.get("url", "")
                return self.web_scraper.learn_from_webpage(url)

            elif action_name == "convene_council":
                problem = params.get("problem", "")
                result = self.council.convene(problem)
                return {"status": "success", "council_response": result}

            elif action_name == "plan":
                steps = params.get("steps", [])
                return {"status": "success", "plan": steps, "message": f"Plan created with {len(steps)} steps. Now execute each step."}

            else:
                return {"status": "error", "message": f"Unknown action: {action_name}"}

        except Exception as e:
            return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

    def handle_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """Process a user message. Multi-step auto-chaining with model switching."""
        ts = datetime.datetime.now().isoformat()

        # Save to persistent history
        self.chat_history.append({"role": "user", "content": user_message, "timestamp": ts})
        _save_chat_history(self.chat_history)

        # Save to ChromaDB for semantic search
        self.memory.add_to_memory("conversation_history", f"User: {user_message}",
                                   metadata={"role": "user", "timestamp": ts})

        # Add to working conversation
        self.conversation.append({"role": "user", "content": user_message})
        if len(self.conversation) > 40:
            self.conversation = self.conversation[-40:]

        yield {"type": "status", "text": "Thinking..."}

        # Determine if code-related for model switching
        use_coder = self._is_code_related(user_message)

        # Multi-step execution loop
        max_iterations = 20
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Build messages with fresh system prompt (auto-date)
            messages = [{"role": "system", "content": get_system_prompt()}]
            messages.extend(self.conversation)

            # Choose model — use coder for ALL iterations if the task is code-related
            if use_coder:
                model = self.brain.coding_model
            else:
                model = self.brain.main_model

            try:
                print(f"Iteration {iteration} - Model: {model}")
                response = self.brain._call_ollama(model, messages=messages)
                brain_response = response['message']['content']
                print(f"Response ({len(brain_response)} chars): {brain_response[:200]}...")

                # Check for action
                action = self._extract_action(brain_response)

                if action:
                    action_name = action.get("action", "")
                    params = action.get("params", {})

                    # Validate — skip empty/broken actions
                    if not action_name:
                        self.conversation.append({"role": "assistant", "content": brain_response})
                        self.conversation.append({"role": "user", "content":
                            "SYSTEM: Your action was malformed (no action name). Try again with a valid action JSON."})
                        continue

                    # Show status in chat
                    if action_name == "plan":
                        steps = params.get("steps", [])
                        plan_text = "Planning:\n" + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(steps))
                        yield {"type": "thinking", "text": plan_text}
                    elif action_name == "search_web":
                        yield {"type": "thinking", "text": f"Searching: {params.get('query', '')}"}
                    elif action_name == "create_file":
                        yield {"type": "thinking", "text": f"Writing file: {params.get('path', '').split('/')[-1]}"}
                    elif action_name == "create_dir":
                        yield {"type": "thinking", "text": f"Creating folder: {params.get('path', '').split('/')[-1]}"}
                    elif action_name == "shell":
                        cmd = params.get('command', '')
                        if len(cmd) > 80:
                            cmd = cmd[:80] + "..."
                        yield {"type": "thinking", "text": f"Running: {cmd}"}
                    elif action_name == "convene_council":
                        yield {"type": "council_activated"}
                        yield {"type": "thinking", "text": "Council is deliberating..."}
                    elif action_name == "notes_create":
                        yield {"type": "thinking", "text": f"Creating note: {params.get('title', '')}"}
                    else:
                        yield {"type": "thinking", "text": f"Executing: {action_name}"}

                    # Execute
                    result = self._execute_action(action)

                    # Loop detection
                    self.loop_detector.record_tool_call(action_name, params)
                    if self.loop_detector.detect_loop():
                        yield {"type": "thinking", "text": "Stuck in a loop — rethinking..."}
                        self.loop_detector.reset()
                        self.conversation.append({"role": "assistant", "content": brain_response})
                        self.conversation.append({"role": "user", "content":
                            "SYSTEM: You're stuck in a loop repeating the same action. Stop and try a completely different approach, or give the user what you have so far."})
                        continue

                    # Show result
                    result_str = json.dumps(result, indent=2, default=str)
                    if len(result_str) > 3000:
                        result_str = result_str[:3000] + "\n... (truncated)"

                    # Only show tool output for non-trivial results
                    if action_name in ("search_web", "shell", "read_file", "list_dir"):
                        yield {"type": "tool_output", "tool_name": action_name, "output": result_str}

                    # Feed result back to brain
                    self.conversation.append({"role": "assistant", "content": brain_response})
                    self.conversation.append({"role": "user", "content":
                        f"TOOL_RESULT for {action_name}:\n{result_str}\n\nContinue with the next step. If you need more searches, do them. When fully done, give a natural summary."})

                    continue

                else:
                    # Text response — done
                    clean_text = brain_response.strip()
                    if "SWITCH_TO_CODER" in clean_text:
                        clean_text = clean_text.replace("SWITCH_TO_CODER", "").strip()
                        use_coder = True
                        continue

                    if clean_text:
                        yield {"type": "text", "text": clean_text}

                        # Save to persistent history
                        self.chat_history.append({
                            "role": "assistant",
                            "content": clean_text,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                        _save_chat_history(self.chat_history)

                    self.conversation.append({"role": "assistant", "content": brain_response})
                    self.memory.add_to_memory("conversation_history", f"Timmy: {clean_text}",
                                               metadata={"role": "assistant", "timestamp": datetime.datetime.now().isoformat()})
                    break

            except Exception as e:
                error_msg = f"Something went wrong: {str(e)}"
                print(f"Agent error: {traceback.format_exc()}")
                yield {"type": "error", "text": error_msg}
                break

        if iteration >= max_iterations:
            msg = "Hit my step limit on this one. Here's what I have so far — let me know if you want me to keep going."
            yield {"type": "text", "text": msg}
            self.chat_history.append({"role": "assistant", "content": msg, "timestamp": datetime.datetime.now().isoformat()})
            _save_chat_history(self.chat_history)
