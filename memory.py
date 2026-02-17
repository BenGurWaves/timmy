import chromadb
import logging
from chromadb.utils import embedding_functions
from config import config

logger = logging.getLogger(__name__)

class Memory:
    def __init__(self, persist_directory: str = config.CHROMA_PATH):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        # Collections for different types of memory
        self.episodic_collection = self.client.get_or_create_collection(
            name="episodic_memory",
            embedding_function=self.embedding_function
        )
        self.semantic_collection = self.client.get_or_create_collection(
            name="semantic_memory",
            embedding_function=self.embedding_function
        )
        logger.info(f"Memory initialized with ChromaDB at: {persist_directory}")

    def add_episodic_memory(self, user_input: str, agent_response: str):
        content = f"User: {user_input}\nAgent: {agent_response}"
        self.episodic_collection.add(
            documents=[content],
            metadatas=[{"type": "conversation"}],
            ids=[f"episodic-{self.episodic_collection.count()}"]
        )
        logger.info("Added episodic memory.")

    def add_semantic_memory(self, content: str, source: str = "unknown"):
        self.semantic_collection.add(
            documents=[content],
            metadatas=[{"type": "knowledge", "source": source}],
            ids=[f"semantic-{self.semantic_collection.count()}"]
        )
        logger.info(f"Added semantic memory from source: {source}")

    def retrieve_relevant_memories(self, query: str, n_results: int = 3) -> list:
        # Retrieve from both episodic and semantic memory
        episodic_results = self.episodic_collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents']
        )
        semantic_results = self.semantic_collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents']
        )
        
        all_results = []
        if episodic_results and episodic_results['documents']:
            all_results.extend(episodic_results['documents'][0])
        if semantic_results and semantic_results['documents']:
            all_results.extend(semantic_results['documents'][0])
            
        logger.info(f"Retrieved {len(all_results)} relevant memories for query: {query}")
        return all_results

    def clear_memory(self):
        self.client.delete_collection(name="episodic_memory")
        self.client.delete_collection(name="semantic_memory")
        self.episodic_collection = self.client.get_or_create_collection(
            name="episodic_memory",
            embedding_function=self.embedding_function
        )
        self.semantic_collection = self.client.get_or_create_collection(
            name="semantic_memory",
            embedding_function=self.embedding_function
        )
        logger.info("All memories cleared.")
