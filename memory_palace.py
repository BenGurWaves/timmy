"""
memory_palace.py

Implements Timmy's "Memory Palace" (Fun Upgrade). 
Instead of just a list of facts, Timmy maintains a "mental map" of 
shared history, allowing him to make callbacks to things you said 
weeks ago in a way that feels genuinely human.
"""

import json
import os
from typing import List, Dict, Any
from config import PROJECT_ROOT

MEMORY_PALACE_FILE = os.path.join(PROJECT_ROOT, "data", "memory_palace.json")

class MemoryPalace:
    def __init__(self):
        self.memories: List[Dict[str, Any]] = self._load_memories()
        
    def _load_memories(self) -> List[Dict[str, Any]]:
        """Load memories from disk."""
        try:
            if os.path.exists(MEMORY_PALACE_FILE):
                with open(MEMORY_PALACE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading memory palace: {e}")
        return []
        
    def _save_memories(self):
        """Save memories to disk."""
        try:
            os.makedirs(os.path.dirname(MEMORY_PALACE_FILE), exist_ok=True)
            with open(MEMORY_PALACE_FILE, 'w') as f:
                json.dump(self.memories, f, indent=2)
        except Exception as e:
            print(f"Error saving memory palace: {e}")
            
    def add_memory(self, topic: str, detail: str, significance: str = "low"):
        """Add a new memory to the palace."""
        memory = {
            "topic": topic,
            "detail": detail,
            "significance": significance,
            "timestamp": os.path.getmtime(MEMORY_PALACE_FILE) if os.path.exists(MEMORY_PALACE_FILE) else 0
        }
        self.memories.append(memory)
        self._save_memories()
        
    def get_random_callback(self) -> Optional[str]:
        """Get a random memory to use as a callback in conversation."""
        import random
        if not self.memories:
            return None
        memory = random.choice(self.memories)
        return f"Remember when we talked about {memory['topic']}? {memory['detail']}"

    def get_palace_summary(self) -> str:
        """Get a summary of the memory palace for the system prompt."""
        if not self.memories:
            return "The memory palace is empty."
        
        summary = "## MEMORY PALACE (SHARED HISTORY)\n"
        for m in self.memories[-5:]: # Just the last 5 for context
            summary += f"- {m['topic']}: {m['detail']} (Significance: {m['significance']})\n"
        return summary
