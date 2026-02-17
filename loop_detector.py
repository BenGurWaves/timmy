"""
loop_detector.py

This module implements a smart loop detection system for the Timmy AI agent.
It tracks recent actions and errors, and if a repeating pattern is detected,
it triggers a 'rethink mode' to prevent the agent from getting stuck.
"""

from collections import deque
from typing import Any, Dict, List
from config import LOOP_DETECTION_WINDOW, LOOP_DETECTION_THRESHOLD

class LoopDetector:
    """
    Detects repetitive actions or errors to prevent the agent from getting stuck in loops.
    """

    def __init__(self):
        self.action_history: deque = deque(maxlen=LOOP_DETECTION_WINDOW)
        self.error_history: deque = deque(maxlen=LOOP_DETECTION_WINDOW)
        print("LoopDetector initialized.")

    def record_action(self, action: str, details: Dict[str, Any] = None):
        """
        Records an action taken by the agent.
        """
        self.action_history.append((action, details))
        print(f"Action recorded: {action}")

    def record_error(self, error_message: str, action_context: Dict[str, Any] = None):
        """
        Records an error encountered by the agent.
        """
        self.error_history.append((error_message, action_context))
        print(f"Error recorded: {error_message}")

    def detect_loop(self) -> bool:
        """
        Checks if a loop is detected based on repeating actions or errors.
        """
        if len(self.action_history) < LOOP_DETECTION_WINDOW and len(self.error_history) < LOOP_DETECTION_WINDOW:
            return False

        # Check for repeating actions
        if len(self.action_history) == LOOP_DETECTION_WINDOW:
            first_action = self.action_history[0][0]
            if all(item[0] == first_action for item in self.action_history):
                print(f"Loop detected: Same action '{first_action}' repeated {LOOP_DETECTION_WINDOW} times.")
                return True

        # Check for repeating errors
        if len(self.error_history) == LOOP_DETECTION_WINDOW:
            first_error = self.error_history[0][0]
            if all(item[0] == first_error for item in self.error_history):
                print(f"Loop detected: Same error '{first_error}' repeated {LOOP_DETECTION_WINDOW} times.")
                return True

        return False

    def get_loop_context(self) -> Dict[str, List[Any]]:
        """
        Returns the context of the detected loop (action and error history).
        """
        return {
            "action_history": list(self.action_history),
            "error_history": list(self.error_history)
        }

    def reset(self):
        """
        Resets the loop detector history.
        """
        self.action_history.clear()
        self.error_history.clear()
        print("LoopDetector reset.")

