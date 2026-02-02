from qdrant_client import QdrantClient
from qdrant_client.models import NamedVector, Distance, VectorParams, PointStruct
from config import(
    QDRANT_URL,
    COLLECTION_NAME,
    EMBEDDING_DIMENSION,
    TOP_K_RETRIEVAL
)
import numpy as np
from typing import List, Dict
import uuid

class QdrantStorage:
    """
    Manage vector storage and retrieval using Qdrant.
    """

    def __init__(self, collection_name: str = COLLECTION_NAME) -> None:
        self.client = QdrantClient(url=QDRANT_URL)
        self.collection_name = collection_name
        self._create_collection()
    def _create_collection(self) -> None:
        """
        Create a new collection if it doesn't exist.
        """
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "embedding": VectorParams(
                        size=EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    ),
                    "contextual_embedding": VectorParams(
                        size=EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                }
            )
    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Add document chunks to the collection.

        Args:
            chunks (List[Dict]): List of document chunks with 'embedding', 'contextual_embedding', and 'metadata'.
        """
        points = []
        for chunk in chunks:
            point = PointStruct(
                id=str(uuid.uuid4()), # Generate a unique ID for each chunk
                vector={
                    "embedding": chunk["embedding"].tolist(),
                    "contextual_embedding": chunk["contextual_embedding"].tolist()
                },
                payload={
                    "chunk_text": chunk["chunk_text"],
                    "context": chunk["context"],
                    "chunk_id": chunk["chunk_id"]
                }
            )
            points.append(point)
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    def search(self, query_vector: np.ndarray, top_k: int = TOP_K_RETRIEVAL, use_contextual: bool = True) -> List[Dict]:
        """
        Docstring for search
        
        Search for similar chunks using vector similarity.
        
        Args:
            query_vector: The query embedding
            top_k: Number of results to return
            use_contextual: Whether to use contextual embeddings
            
        Returns:
            List of matching chunks with scores
        """
        vector_name = "contextual_embedding" if use_contextual else "embedding"

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            using=vector_name,
            limit=top_k
        ).points    
        return [
            {
                "chunk_text": hit.payload["chunk_text"],
                "context": hit.payload["context"],
                "chunk_id": hit.payload["chunk_id"],
                "score": hit.score  
            }
            for hit in results
            if hit.payload is not None
        ]