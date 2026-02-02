from rank_bm25 import BM25Okapi
from typing import List, Dict
import numpy as np

class BM25Index:
    def __init__(self) -> None:
        self.bm25 = None            # The BM25 index Object.
        self.documents = []         # Store original chunks
        self.tokenized_corpus =[]   # Store Tokenized versions

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization by splitting on whitespace and converting to lowercase.
    
        Args:
            text: Text to tokenize
        
        Returns:
            List of tokens
        """
        return text.lower().split()
    
    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Add document chunks to the BM25 index.
        
        Args:
            chunks: List of chunks with 'chunk_text' and 'chunk_id' fields
        """
        self.documents = chunks

        # Tokenize corpus - combine context and chunk_text for better matching
        self.tokenized_corpus = []
        for chunk in chunks:
            # Combine context and chunk_text (similar to contextual embedding!)
            combined_text = f"{chunk.get('context','')} {chunk['chunk_text']}"
            tokens = self._tokenize(combined_text)
            self.tokenized_corpus.append(tokens)
        # Create BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search the BM25 index for the most relevant document chunks.
            
        Args:
            query: The search query string
            top_k: Number of top results to return
            
        Returns:
            List of top_k most relevant document chunks
            """
        if self.bm25 is None:
            raise ValueError("BM25 index is not initialized. Add documents first.")
            
        # Tokenize the query
        tokenized_query = self._tokenize(query)

        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
            
        # Get top_k indices sorted descending by score
        top_indices = np.argsort(scores)[::-1][:top_k]
            
        results = []
        for idx in top_indices:
            if scores[idx] > 0: # Only return results with positive scores
                results.append({
                    'chunk_id': self.documents[idx]['chunk_id'],
                    'chunk_text': self.documents[idx]['chunk_text'],
                    'context': self.documents[idx].get('context',''),
                    'score': float(scores[idx])
                })
        return results
