"""
memory.py

This module implements the memory system for the Timmy AI agent using ChromaDB.
It handles short-term (conversation history), long-term (task summaries, learned knowledge),
and episodic memory (past sessions), as well as semantic memory from learned content.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from config import MEMORY_PATH

class Memory:
    """
    Manages different types of memory for the Timmy AI agent using ChromaDB.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(path=MEMORY_PATH)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

        self.collections = {
            "conversation_history": self.client.get_or_create_collection(
                name="conversation_history",
                embedding_function=self.embedding_function
            ),
            "long_term_knowledge": self.client.get_or_create_collection(
                name="long_term_knowledge",
                embedding_function=self.embedding_function
            ),
            "episodic_memory": self.client.get_or_create_collection(
                name="episodic_memory",
                embedding_function=self.embedding_function
            ),
            "semantic_knowledge": self.client.get_or_create_collection(
                name="semantic_knowledge",
                embedding_function=self.embedding_function
            ),
        }
        print(f"Memory initialized. ChromaDB path: {MEMORY_PATH}")

    def add_to_memory(self, collection_name: str, document: str, metadata: Optional[Dict[str, Any]] = None, id: Optional[str] = None):
        """
        Adds a document to a specified memory collection.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' does not exist.")
        
        # Generate a simple ID if not provided
        if not id:
            id = f"{collection_name}_{self.collections[collection_name].count() + 1}"

        add_kwargs = {
            "documents": [document],
            "ids": [id]
        }
        if metadata:
            add_kwargs["metadatas"] = [metadata]
        self.collections[collection_name].add(**add_kwargs)
        print(f"Added to {collection_name}: {document[:50]}...")

    def retrieve_from_memory(self, collection_name: str, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant documents from a specified memory collection based on a query.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' does not exist.")

        # Don't query if collection is empty
        if self.collections[collection_name].count() == 0:
            return []
        actual_n = min(n_results, self.collections[collection_name].count())
        results = self.collections[collection_name].query(
            query_texts=[query_text],
            n_results=actual_n,
            include=["documents", "metadatas"]
        )
        # Flatten the nested list
        return results["documents"][0] if results["documents"] else []

    def get_conversation_history(self, n_messages: int = 10) -> List[str]:
        """
        Retrieves the most recent conversation history.
        """
        # ChromaDB doesn't inherently order by insertion, so we'll retrieve all and sort if metadata allows
        # For simplicity, let's assume we store a timestamp in metadata for ordering
        all_messages = self.collections["conversation_history"].get(include=["documents", "metadatas"])
        
        # If timestamps are available, sort by them. Otherwise, return in arbitrary order.
        if all_messages and "metadatas" in all_messages and all_messages["metadatas"] and "timestamp" in all_messages["metadatas"][0]:
            sorted_messages = sorted(
                zip(all_messages["documents"], all_messages["metadatas"]),
                key=lambda x: x[1].get("timestamp", 0), reverse=True
            )
            return [doc for doc, meta in sorted_messages[:n_messages]]
        else:
            return all_messages["documents"][-n_messages:] if all_messages and "documents" in all_messages else []

    def clear_memory(self, collection_name: str):
        """
        Clears all documents from a specified memory collection.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' does not exist.")
        
        self.client.delete_collection(name=collection_name)
        self.collections[collection_name] = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        print(f"Collection '{collection_name}' cleared.")

