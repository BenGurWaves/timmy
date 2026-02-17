"""
note_taking.py

This skill allows the Timmy AI agent to take and retrieve notes, leveraging the memory system.
"""

from typing import Any, Dict
from skills.base import Skill
from memory import Memory # Assuming Memory class is accessible
import datetime

class NoteTakingSkill(Skill):
    """
    A skill for taking and retrieving notes.
    """

    def __init__(self):
        super().__init__(
            name="Note Taking",
            description="Allows taking and retrieving notes, storing them in long-term memory."
        )
        self.memory = Memory()

    def execute(self, operation: str, content: str = "", query: str = "") -> Dict[str, Any]:
        """
        Executes a note-taking operation.

        Args:
            operation (str): The type of note operation ("take" or "retrieve").
            content (str): The content of the note to take (for "take" operation).
            query (str): The query to retrieve notes (for "retrieve" operation).

        Returns:
            Dict[str, Any]: The result of the note-taking operation.
        """
        print(f"Executing Note Taking Skill for operation: {operation}")
        if operation == "take":
            if not content:
                return {"status": "error", "message": "Note content cannot be empty."}
            timestamp = datetime.datetime.now().isoformat()
            metadata = {"type": "note", "timestamp": timestamp}
            self.memory.add_to_memory("long_term_knowledge", content, metadata=metadata)
            return {"status": "success", "message": "Note taken successfully.", "timestamp": timestamp}
        elif operation == "retrieve":
            if not query:
                return {"status": "error", "message": "Query for note retrieval cannot be empty."}
            results = self.memory.retrieve_from_memory("long_term_knowledge", query)
            return {"status": "success", "query": query, "notes": results}
        else:
            return {"status": "error", "message": f"Unknown note operation: {operation}"}
