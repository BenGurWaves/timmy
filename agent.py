"""
agent.py

Core Agent class for Timmy AI. The brain (qwen3:30b) decides what to do.
It sees the available tools and picks the right one, or just responds directly.
"""

import json
import datetime
import traceback
from typing import Dict, Any, List, Generator

from brain import Brain
from council import Council
from memory import Memory
from loop_detector import LoopDetector
from tools import ALL_TOOLS, Tool
from skills import ALL_SKILLS, Skill, CodeWriterSkill
from learning import YouTubeLearner, WebScraper


SYSTEM_PROMPT = """You are Timmy, a powerful AI agent running locally on Ben's Mac.
You are NOT just a chatbot. You have FULL control of this computer through your tools.

AVAILABLE TOOLS:
{tools_description}

IMPORTANT RULES:
1. When the user asks you to DO something (create files, search the web, run commands, open apps, etc.), you MUST use your tools. NEVER say "I can't do that" — you CAN.
2. To use a tool, respond with a JSON block like this:
```tool
{{"tool": "tool_name", "params": {{"param1": "value1"}}}}
```
3. You can chain multiple tool calls by responding with multiple ```tool blocks.
4. After using a tool, you will see the result. Then give the user a natural summary.
5. If you just need to chat/answer a question (no action needed), respond normally without any tool blocks.
6. You run on Ben's Mac at /Users/bengur/Desktop/timmy — the user's home is /Users/bengur and desktop is /Users/bengur/Desktop.
7. For web searches, use the "Web Search" tool. For creating files/folders, use "File System Manager". For terminal commands, use "Shell Executor".
8. You have access to a council of AI models for hard problems. If something is really complex, mention you can convene the council.
9. Be helpful, direct, and confident. You are Timmy — not qwen3, not an AI that "can't do things". You ARE the agent.

TOOL REFERENCE:
- "Shell Executor": params: {{"command": "any terminal command"}}
- "File System Manager": params: {{"operation": "read|write|create_dir|delete|list|search|append", "path": "/full/path", "content": "text" (for write/append)}}
- "Web Search": params: {{"query": "search terms"}}
- "Browser": params: {{"operation": "open_page|get_content|search_extract|fill_field|click", "url": "...", "selector": "..."}}
- "Application Control (macOS)": params: {{"operation": "open|close|send_keystrokes", "app_name": "AppName"}}
- "YouTube Learner": params: {{"url": "youtube_url"}}
- "Web Scraper": params: {{"url": "any_url"}}
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

        # Build tools description for the system prompt
        self.tools_description = self._build_tools_description()

        # Conversation messages for context
        self.conversation: List[Dict[str, str]] = []

        print("Agent initialized with Brain, Council, Memory, Loop Detector, Tools, Skills, and Learning modules.")

    def _build_tools_description(self) -> str:
        lines = []
        for tool in self.tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
        lines.append("- YouTube Learner: Extracts and learns from YouTube video transcripts")
        lines.append("- Web Scraper: Extracts and learns from any web page content")
        return "\n".join(lines)

    def _get_system_prompt(self) -> str:
        return SYSTEM_PROMPT.format(tools_description=self.tools_description)

    def _extract_tool_calls(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract tool call JSON blocks from the response."""
        tool_calls = []
        # Look for ```tool ... ``` blocks
        parts = response_text.split("```tool")
        for part in parts[1:]:  # Skip the first part (before any tool block)
            end_idx = part.find("```")
            if end_idx != -1:
                json_str = part[:end_idx].strip()
                try:
                    tool_call = json.loads(json_str)
                    tool_calls.append(tool_call)
                except json.JSONDecodeError:
                    # Try to find JSON within the text
                    try:
                        start = json_str.index("{")
                        end = json_str.rindex("}") + 1
                        tool_call = json.loads(json_str[start:end])
                        tool_calls.append(tool_call)
                    except (ValueError, json.JSONDecodeError):
                        pass

        # Also check for inline JSON tool calls (without code blocks)
        if not tool_calls and '"tool"' in response_text and '"params"' in response_text:
            try:
                start = response_text.index("{")
                end = response_text.rindex("}") + 1
                candidate = response_text[start:end]
                tool_call = json.loads(candidate)
                if "tool" in tool_call:
                    tool_calls.append(tool_call)
            except (ValueError, json.JSONDecodeError):
                pass

        return tool_calls

    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given params."""
        # Handle special tools
        if tool_name == "YouTube Learner":
            return self.youtube_learner.learn_from_youtube(params.get("url", ""))
        elif tool_name == "Web Scraper":
            return self.web_scraper.learn_from_webpage(params.get("url", ""))
        elif tool_name == "Council":
            return {"result": self.council.convene(params.get("problem", ""))}

        # Handle registered tools
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            return tool.execute(**params)

        # Try matching by partial name
        for name, tool in self.tools.items():
            if tool_name.lower() in name.lower() or name.lower() in tool_name.lower():
                return tool.execute(**params)

        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    def _strip_tool_blocks(self, text: str) -> str:
        """Remove tool call blocks from response text to get the natural language part."""
        result = text
        while "```tool" in result:
            start = result.index("```tool")
            end = result.find("```", start + 7)
            if end != -1:
                result = result[:start] + result[end + 3:]
            else:
                result = result[:start]
        return result.strip()

    def handle_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """Process a user message through the brain, execute tools if needed, respond."""
        # Store in memory
        ts = datetime.datetime.now().isoformat()
        self.memory.add_to_memory("conversation_history", f"User: {user_message}",
                                   metadata={"role": "user", "timestamp": ts})

        # Add to conversation context
        self.conversation.append({"role": "user", "content": user_message})
        # Keep last 20 messages for context
        if len(self.conversation) > 20:
            self.conversation = self.conversation[-20:]

        yield {"type": "status", "text": "Timmy is thinking..."}

        try:
            # Build messages for Ollama
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            messages.extend(self.conversation)

            # Get brain's response
            print(f"Thinking with model: {self.brain.main_model}")
            response = self.brain._call_ollama(self.brain.main_model, None, messages=messages)
            brain_response = response['message']['content']
            print(f"Brain response: {brain_response[:200]}...")

            # Check for tool calls
            tool_calls = self._extract_tool_calls(brain_response)

            if tool_calls:
                # Execute each tool call
                all_results = []
                for tc in tool_calls:
                    tool_name = tc.get("tool", "")
                    params = tc.get("params", {})
                    yield {"type": "status", "text": f"Using tool: {tool_name}..."}
                    print(f"Executing tool: {tool_name} with params: {params}")

                    try:
                        result = self._execute_tool(tool_name, params)
                        all_results.append({"tool": tool_name, "result": result})
                        yield {"type": "tool_output", "tool_name": tool_name,
                               "output": json.dumps(result, indent=2, default=str)}
                    except Exception as e:
                        error_result = {"status": "error", "message": str(e)}
                        all_results.append({"tool": tool_name, "result": error_result})
                        yield {"type": "tool_output", "tool_name": tool_name,
                               "output": json.dumps(error_result, indent=2)}

                # Now ask the brain to summarize the results for the user
                tool_results_text = json.dumps(all_results, indent=2, default=str)
                summary_messages = messages + [
                    {"role": "assistant", "content": brain_response},
                    {"role": "user", "content": f"Tool results:\n{tool_results_text}\n\nNow give the user a clear, natural summary of what happened. Do NOT include any tool blocks in this response."}
                ]

                summary_response = self.brain._call_ollama(self.brain.main_model, None, messages=summary_messages)
                summary_text = summary_response['message']['content']
                # Strip any accidental tool blocks from summary
                summary_text = self._strip_tool_blocks(summary_text)

                yield {"type": "text", "text": summary_text}

                # Store in conversation
                self.conversation.append({"role": "assistant", "content": summary_text})
                self.memory.add_to_memory("conversation_history", f"Timmy: {summary_text}",
                                           metadata={"role": "assistant", "timestamp": datetime.datetime.now().isoformat()})
            else:
                # No tool calls — just a direct response
                clean_response = self._strip_tool_blocks(brain_response)
                yield {"type": "text", "text": clean_response}

                self.conversation.append({"role": "assistant", "content": clean_response})
                self.memory.add_to_memory("conversation_history", f"Timmy: {clean_response}",
                                           metadata={"role": "assistant", "timestamp": datetime.datetime.now().isoformat()})

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Agent error: {traceback.format_exc()}")
            yield {"type": "error", "text": error_msg}
