import logging
from typing import List
from ..memory import Memory

logger = logging.getLogger(__name__)

class KnowledgeProcessor:
    def __init__(self, memory: Memory):
        self.memory = memory

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        # A simple chunking mechanism. More advanced methods might use NLTK or spaCy.
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        logger.info(f"Chunked text into {len(chunks)} chunks.")
        return chunks

    def process_and_store(self, content: str, source: str = "unknown"):
        chunks = self.chunk_text(content)
        for i, chunk in enumerate(chunks):
            self.memory.add_semantic_memory(chunk, f"{source}-chunk-{i}")
        logger.info(f"Processed and stored {len(chunks)} chunks from source: {source}")
