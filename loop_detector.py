"""
loop_detector.py

Smart loop detection — only triggers when the agent is actually stuck
(same tool call failing repeatedly, or same error repeating).
Normal user messages do NOT count as loops.
"""

from collections import deque
from typing import Any, Dict, List
from config import LOOP_DETECTION_WINDOW, LOOP_DETECTION_THRESHOLD


class LoopDetector:
    def __init__(self):
        self.tool_history: deque = deque(maxlen=LOOP_DETECTION_WINDOW)
        self.error_history: deque = deque(maxlen=LOOP_DETECTION_WINDOW)
        print("LoopDetector initialized.")

    def record_tool_call(self, tool_name: str, params: Dict[str, Any] = None):
        """Record a tool execution (NOT user messages)."""
        self.tool_history.append((tool_name, str(params)))
        print(f"Tool call recorded: {tool_name}")

    def record_error(self, error_message: str, context: Dict[str, Any] = None):
        """Record an error."""
        self.error_history.append((error_message, str(context)))
        print(f"Error recorded: {error_message}")

    def detect_loop(self) -> bool:
        """
        Detect if the agent is stuck in a loop.
        Only triggers if the same tool+params combo repeats THRESHOLD times,
        or the same error repeats THRESHOLD times.
        """
        # Check for repeating tool calls with same params
        if len(self.tool_history) >= LOOP_DETECTION_THRESHOLD:
            recent = list(self.tool_history)[-LOOP_DETECTION_THRESHOLD:]
            if all(item == recent[0] for item in recent):
                print(f"Loop detected: Same tool call repeated {LOOP_DETECTION_THRESHOLD} times: {recent[0]}")
                return True

        # Check for repeating errors
        if len(self.error_history) >= LOOP_DETECTION_THRESHOLD:
            recent = list(self.error_history)[-LOOP_DETECTION_THRESHOLD:]
            if all(item[0] == recent[0][0] for item in recent):
                print(f"Loop detected: Same error repeated {LOOP_DETECTION_THRESHOLD} times: {recent[0][0]}")
                return True

        return False

    def get_loop_context(self) -> Dict[str, List[Any]]:
        return {
            "tool_history": list(self.tool_history),
            "error_history": list(self.error_history)
        }

    def reset(self):
        self.tool_history.clear()
        self.error_history.clear()
        print("LoopDetector reset.")
