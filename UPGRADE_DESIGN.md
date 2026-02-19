# Timmy Upgrade Design Document

This document outlines the planned upgrades for Timmy to address hallucinations, memory limitations, and lack of transparency in reasoning.

## 1. Memory System Overhaul
The current memory system uses a simple JSON file for chat history and ChromaDB for semantic search. We will move to a more robust tiered memory system.

### Tiered Memory Architecture:
- **Working Memory (Context Window):** The immediate conversation history (last 10-15 turns).
- **Short-Term Memory (Episodic):** Recent interactions and task-specific data, stored in a structured format (SQLite) for fast retrieval and filtering.
- **Long-Term Memory (Semantic):** Core knowledge, user preferences, and learned skills, stored in ChromaDB for vector search.
- **Memory Consolidation:** A background process (or triggered action) that summarizes old conversations and moves key insights from short-term to long-term memory.

### Implementation:
- Replace `chat_history.json` with a SQLite database (`memory.db`) to handle larger histories and complex queries.
- Enhance `Memory` class to support "Entity Memory" (remembering facts about people, places, things).

## 2. Thinking & Reasoning System
To address hallucinations and provide transparency, we will implement a dedicated "Thinking" phase.

### Visible Thinking:
- **Streaming Thinking:** Modify `Brain` and `Agent` to support streaming responses. Thinking will be captured in a `<thought>` block.
- **Frontend Update:** Update `script.js` to render `<thought>` blocks in a dedicated, collapsible UI element.
- **Reasoning Protocol:** Update the system prompt to require Timmy to think before acting or responding.

### Model Consistency:
- Implement a stricter "Identity Guard" in the system prompt to prevent "Qwen-leaks."
- Use a "Self-Correction" loop where Timmy reviews his own plan before execution.

## 3. Web Search & Action Enhancements
- **Search Refinement:** Implement a multi-step search tool that first generates search queries, then evaluates results, and performs follow-up searches if needed.
- **Uncertainty Handling:** If search results are ambiguous, Timmy will be instructed to ask the user for clarification rather than guessing.
- **Skill Building:** Create a framework for Timmy to "save" successful shell command sequences as new "Skills."

## 4. Technical Changes
- **Streaming:** Switch from `ollama.chat` to `ollama.chat(stream=True)`.
- **Database:** Integrate `sqlalchemy` or use raw `sqlite3` for episodic memory.
- **Frontend:** Enhance the WebSocket handler to distinguish between `thought` and `text` chunks.
