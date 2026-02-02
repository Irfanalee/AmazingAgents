from sentence_transformers import SentenceTransformer
import numpy as np
from config import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION

class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        """Initialize the embedder with a pre-trained model."""
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for the given text."""
        embedding = self.model.encode(text)
        return embedding #type: ignore

    def embed_chunks(self, chunks: list[dict]) -> list[dict]:
        """Generate embeddings for a list of text chunks."""
        for chunk in chunks:
            # Get original text
            original_text = chunk['chunk_text']

            # combine context with chunk text for contextal embedding
            contextual_text = f"{chunk['context']}\n\n{original_text}"

            chunk['embedding'] = self.embed_text(original_text)
            chunk['contextual_embedding'] = self.embed_text(contextual_text)
        return chunks
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a search query"""
        return self.embed_text(query)
    