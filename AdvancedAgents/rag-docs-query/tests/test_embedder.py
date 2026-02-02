import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.embedder import Embedder
import numpy as np
import sys


print('=' * 50)
print('TEST: Embedder')
print('=' * 50)

# Initialize embedder
print('Loading embedding model...')
embedder = Embedder()
print('✅ Model loaded successfully')

# Test single text embedding
test_text = 'Artificial Intelligence is transforming technology.'
embedding = embedder.embed_text(test_text)

print(f'\nText: {test_text}')
print(f'Embedding shape: {embedding.shape}')
print(f'Embedding type: {type(embedding)}')
print(f'First 5 values: {embedding[:5]}')

# Test with a chunk
test_chunk = {
    'chunk_id': 1,
    'chunk_text': 'Machine learning algorithms process data.',
    'context': 'This chunk discusses AI and ML capabilities in modern computing.'
}

print(f'\n--- Testing chunk embedding ---')
enriched_chunks = embedder.embed_chunks([test_chunk])

print(f'Chunk has embedding: {"embedding" in enriched_chunks[0]}')
print(f'Chunk has contextual_embedding: {"contextual_embedding" in enriched_chunks[0]}')
print(f'Embedding shape: {enriched_chunks[0]["embedding"].shape}')
print(f'Contextual embedding shape: {enriched_chunks[0]["contextual_embedding"].shape}')

print('\n✅ Embedder test passed!')
