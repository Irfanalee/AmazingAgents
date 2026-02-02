from typing import List, Dict
import numpy as np
from src.vector_store import QdrantStorage
from src.bm25_index import BM25Index
from src.embedder import Embedder

class HybridRetriever:
    def __init__(
        self,
        vector_store: QdrantStorage,
        bm25_index: BM25Index,
        embedder: Embedder,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.5
    ):
        """
        Initialize hybrid retriever with both search systems.
        
        Args:
            vector_store: QdrantStorage instance
            bm25_index: BM25Index instance
            embedder: Embedder instance for query embedding
            vector_weight: Weight for vector search scores (default 0.5)
            bm25_weight: Weight for BM25 scores (default 0.5)
        """
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.embedder = embedder
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight

    def _normalize_scores(self, results: List[Dict]) -> List[Dict]:
        """
        Normalize scores to 0-1 range using min-max normalization.

        Args:
            results: List of result dictionaries with 'score' field
            
        Returns:
            List of results with normalized scores
        """
        if not results:
            return results
        scores=[r['score'] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        # Avoid division by zero
        score_range = max_score - min_score

        if score_range == 0:
            # All scores are the same 
            for result in results:
                result['normalized_score'] = 1.0
            return results
        
        # Min-max normalization: (score - min) / (max - min)
        for result in results: 
            result['normalized_score'] = (result['score'] - min_score) / score_range
        
        return results

    def retrieve(
            self, 
            query: str, 
            top_k: int = 10,
            use_contextual: bool = True
        ) -> List[Dict]:
        """
        Perform hybrid retrieval combining vector and BM25 search.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            use_contextual: Use contextual embeddings for vector search
            
        Returns:
            List of top_k results sorted by combined score
        """
        # Step 1: Vector search
        query_embedding = self.embedder.embed_query(query)
        vector_results = self.vector_store.search(
            query_embedding, 
            top_k=top_k * 2 , 
            use_contextual=use_contextual
        )

        # Query BM25 index
        bm25_results = self.bm25_index.search(query, top_k=top_k * 2)

        # Normalize scores
        vector_results = self._normalize_scores(vector_results)
        bm25_results = self._normalize_scores(bm25_results)

        # Step 3: Merge results by Chunk_id
        merged_results = {}

        # Add vector results
        for result in vector_results:
            chunk_id = result['chunk_id']
            merged_results[chunk_id] = {
                'chunk_id': chunk_id,
                'chunk_text': result['chunk_text'],
                'context': result['context'],
                'vector_score': result['normalized_score'],
                'bm25_score': 0.0  # Default if not found in BM25
            }

        # Add/update BM25 results
        for result in bm25_results:
            chunk_id = result['chunk_id']
            if chunk_id in merged_results:
                merged_results[chunk_id]['bm25_score'] = result['normalized_score']
            else:
                # Add new entry 
                merged_results[chunk_id] = {
                    'chunk_id': chunk_id,
                    'chunk_text': result['chunk_text'],
                    'context': result.get('context', ''),
                    'vector_score': 0.0,  # Default if not found in vector search
                    'bm25_score': result['normalized_score']
                }
        
        # Step 4: Compute combined score 
        for chunk_id, result in merged_results.items():
            combined_score = (
                self.vector_weight * result['vector_score'] +
                self.bm25_weight * result['bm25_score']
            )
            result['combined_score'] = combined_score

        # Step 5: Sort by combined score and return top_k
        final_results = sorted(
            merged_results.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )[:top_k]

        return final_results