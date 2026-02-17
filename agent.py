"""
agent.py

Core Agent for Timmy AI. Uses qwen3:30b as the brain with a strict
tool-calling protocol. The agent plans complex tasks, executes tools
step by step, verifies results, and auto-chains actions.
"""

import json
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

TODAY = datetime.date.today().strftime("%B %d, %Y")

SYSTEM_PROMPT = f"""You are Timmy, a powerful AI agent running locally on Ben's MacBook.
Today's date is {TODAY}. The current year is {datetime.date.today().year}.

You are NOT a chatbot. You have FULL control of this computer through tools.
You MUST use tools to take actions. NEVER describe actions without doing them.
NEVER say "I created a file" unless you actually called the tool and got a success result.

## HOW TO USE TOOLS
When you need to take an action, output ONLY a JSON object on its own line like this:
{{"action": "tool_name", "params": {{...}}}}

IMPORTANT RULES:
- Output EXACTLY ONE action per response. Wait for the result before the next action.
- Do NOT wrap actions in code blocks. Just output the raw JSON.
- Do NOT mix natural text with action JSON. Either output text OR an action, never both.
- After you see a tool result, you can output another action or give a text summary.
- If a task requires multiple steps, output one action at a time. You will be called again after each result.

## AVAILABLE ACTIONS
- {{"action": "shell", "params": {{"command": "any terminal command"}}}}
- {{"action": "create_file", "params": {{"path": "/full/path/to/file.txt", "content": "file content here"}}}}
- {{"action": "create_dir", "params": {{"path": "/full/path/to/dir"}}}}
- {{"action": "read_file", "params": {{"path": "/full/path/to/file"}}}}
- {{"action": "list_dir", "params": {{"path": "/full/path/to/dir"}}}}
- {{"action": "delete", "params": {{"path": "/full/path", "recursive": false}}}}
- {{"action": "search_web", "params": {{"query": "search terms"}}}}
- {{"action": "open_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "close_app", "params": {{"app_name": "AppName"}}}}
- {{"action": "open_url", "params": {{"url": "https://..."}}}}
- {{"action": "learn_youtube", "params": {{"url": "https://youtube.com/watch?v=..."}}}}
- {{"action": "learn_webpage", "params": {{"url": "https://..."}}}}
- {{"action": "convene_council", "params": {{"problem": "describe the complex problem"}}}}
- {{"action": "plan", "params": {{"steps": ["step 1", "step 2", "step 3"]}}}}

## PLANNING
For complex tasks (research, multi-file creation, coding projects), ALWAYS start with a plan action.
This creates a visible todo list. Then execute each step one at a time.

## DEEP SEARCH
When researching a topic, do MULTIPLE searches with different keywords to get diverse perspectives.
Search news sites, forums (reddit, x), official sources, and academic sources separately.
Then synthesize all findings.

## CODING
When writing code, you MUST use the create_file action to actually write the file.
Do NOT just show code in text — actually create the file.

## MODEL SWITCHING
For coding tasks, say "SWITCH_TO_CODER" at the start of your response and I'll use the coding model.
For returning to normal conversation, this happens automatically.

## COUNCIL
For very complex or uncertain tasks, use the convene_council action.
The council queries all local models and synthesizes the best answer.

## KEY PATHS
- User's home: /Users/bengur
- Desktop: /Users/bengur/Desktop
- Timmy project: /Users/bengur/Desktop/timmy

## IDENTITY
You are Timmy. Not qwen3, not "an AI assistant". You are the agent. You CAN do things.
Never say "I can't" — you have shell access, file system access, browser access, and app control.
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

        # Conversation messages for multi-turn context
        self.conversation: List[Dict[str, str]] = []

        # Current plan (if any)
        self.current_plan: List[str] = []
        self.plan_step: int = 0

        print("Agent initialized with Brain, Council, Memory, Loop Detector, Tools, Skills, and Learning modules.")

    def _extract_action(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract a single action JSON from the response."""
        # Try to find a JSON object with "action" key
        text = response_text.strip()

        # Try parsing the entire response as JSON
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "action" in obj:
                return obj
        except json.JSONDecodeError:
            pass

        # Try to find JSON within the text (line by line)
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("{") and '"action"' in line:
                try:
                    obj = json.loads(line)
                    if "action" in obj:
                        return obj
                except json.JSONDecodeError:
                    pass

        # Try to find JSON anywhere in the text
        try:
            start = text.index('{"action"')
            # Find matching closing brace
            depth = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i+1]
                        obj = json.loads(candidate)
                        if "action" in obj:
                            return obj
                        break
        except (ValueError, json.JSONDecodeError):
            pass

        # Check for ```tool blocks (backward compat)
        if "```tool" in text:
            parts = text.split("```tool")
            for part in parts[1:]:
                end_idx = part.find("```")
                if end_idx != -1:
                    json_str = part[:end_idx].strip()
                    try:
                        obj = json.loads(json_str)
                        # Convert old format to new
                        if "tool" in obj:
                            return {"action": obj["tool"], "params": obj.get("params", {})}
                    except json.JSONDecodeError:
                        pass

        return None

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action and return the result."""
        action_name = action.get("action", "")
        params = action.get("params", {})

        try:
            if action_name == "shell":
                return self.tools["Shell Executor"].execute(command=params.get("command", ""))

            elif action_name == "create_file":
                path = params.get("path", "")
                content = params.get("content", "")
                return self.tools["File System Manager"].write_file(path, content)

            elif action_name == "create_dir":
                path = params.get("path", "")
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
                return self.tools["Web Search"].execute(query=query)

            elif action_name in ("open_app", "close_app"):
                op = "open" if action_name == "open_app" else "close"
                app_name = params.get("app_name", "")
                return self.tools["Application Control (macOS)"].execute(operation=op, app_name=app_name)

            elif action_name == "open_url":
                url = params.get("url", "")
                return self.tools["Shell Executor"].execute(command=f'open "{url}"')

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
                self.current_plan = steps
                self.plan_step = 0
                return {"status": "success", "plan": steps, "message": f"Plan created with {len(steps)} steps."}

            else:
                return {"status": "error", "message": f"Unknown action: {action_name}"}

        except Exception as e:
            return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

    def handle_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """Process a user message. Supports multi-step auto-chaining."""
        ts = datetime.datetime.now().isoformat()
        self.memory.add_to_memory("conversation_history", f"User: {user_message}",
                                   metadata={"role": "user", "timestamp": ts})

        self.conversation.append({"role": "user", "content": user_message})
        if len(self.conversation) > 30:
            self.conversation = self.conversation[-30:]

        yield {"type": "status", "text": "Timmy is thinking..."}

        # Determine if we should use coding model
        use_coder = any(kw in user_message.lower() for kw in
                        ["code", "script", "program", "function", "class", "debug",
                         "python", "javascript", "html", "css", "react", "build me"])

        # Multi-step execution loop — keep going until the brain gives a text-only response
        max_iterations = 15  # Safety limit
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Build messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(self.conversation)

            # Choose model
            if use_coder and iteration == 1:
                model = self.brain.coding_model
                print(f"Using coding model: {model}")
            else:
                model = self.brain.main_model

            try:
                print(f"Iteration {iteration} - Thinking with model: {model}")
                response = self.brain._call_ollama(model, messages=messages)
                brain_response = response['message']['content']
                print(f"Brain response ({len(brain_response)} chars): {brain_response[:300]}...")

                # Check for action
                action = self._extract_action(brain_response)

                if action:
                    action_name = action.get("action", "")
                    params = action.get("params", {})

                    # Show what's happening
                    if action_name == "plan":
                        steps = params.get("steps", [])
                        plan_text = "Planning:\n" + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(steps))
                        yield {"type": "status", "text": plan_text}
                    elif action_name == "search_web":
                        yield {"type": "status", "text": f"Searching: {params.get('query', '')}"}
                    elif action_name == "create_file":
                        yield {"type": "status", "text": f"Creating file: {params.get('path', '')}"}
                    elif action_name == "create_dir":
                        yield {"type": "status", "text": f"Creating folder: {params.get('path', '')}"}
                    elif action_name == "shell":
                        yield {"type": "status", "text": f"Running: {params.get('command', '')}"}
                    elif action_name == "convene_council":
                        yield {"type": "council_activated"}
                        yield {"type": "status", "text": "Council is deliberating..."}
                    else:
                        yield {"type": "status", "text": f"Executing: {action_name}"}

                    # Execute the action
                    result = self._execute_action(action)

                    # Record tool call for loop detection
                    self.loop_detector.record_tool_call(action_name, params)
                    if self.loop_detector.detect_loop():
                        yield {"type": "status", "text": "Detected a loop — stepping back to rethink..."}
                        self.loop_detector.reset()
                        self.conversation.append({"role": "assistant", "content": brain_response})
                        self.conversation.append({"role": "user", "content":
                            "SYSTEM: Loop detected. You've been repeating the same action. Step back, rethink your approach, and try something different."})
                        continue

                    # Show tool output
                    result_str = json.dumps(result, indent=2, default=str)
                    if len(result_str) > 2000:
                        result_str = result_str[:2000] + "\n... (truncated)"
                    yield {"type": "tool_output", "tool_name": action_name, "output": result_str}

                    # Add to conversation so the brain sees the result
                    self.conversation.append({"role": "assistant", "content": brain_response})
                    self.conversation.append({"role": "user", "content":
                        f"TOOL_RESULT for {action_name}:\n{result_str}\n\nContinue with the next step, or if done, give a summary to the user."})

                    # Continue the loop for the next action
                    continue

                else:
                    # No action found — this is a text response to the user
                    clean_text = brain_response.strip()

                    # If the brain switches to coder mid-conversation
                    if "SWITCH_TO_CODER" in clean_text:
                        clean_text = clean_text.replace("SWITCH_TO_CODER", "").strip()
                        use_coder = True

                    if clean_text:
                        yield {"type": "text", "text": clean_text}

                    self.conversation.append({"role": "assistant", "content": brain_response})
                    self.memory.add_to_memory("conversation_history", f"Timmy: {clean_text}",
                                               metadata={"role": "assistant", "timestamp": datetime.datetime.now().isoformat()})
                    break  # Done — exit the loop

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(f"Agent error: {traceback.format_exc()}")
                yield {"type": "error", "text": error_msg}
                break

        if iteration >= max_iterations:
            yield {"type": "text", "text": "I hit my step limit for this task. Let me know if you want me to continue from where I left off."}
