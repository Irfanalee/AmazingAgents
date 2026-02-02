import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vector_store import QdrantStorage
from src.embedder import Embedder
import numpy as np

print('=' * 50)
print('TEST: Vector Store (Qdrant)')
print('=' * 50)

# Initialize
print('\n1. Initializing Qdrant storage...')
storage = QdrantStorage()

# Delete and recreate collection for clean test
print('   Recreating collection for clean test...')
storage.client.delete_collection(collection_name=storage.collection_name)
storage._create_collection()
print('✅ Qdrant client initialized with fresh collection')

# Initialize embedder
print('\n2. Initializing embedder...')
embedder = Embedder()
print('✅ Embedder initialized')

# Create test chunks with embeddings
print('\n3. Creating test chunks...')
test_chunks = [
    {
        'chunk_id': 1,
        'chunk_text': 'Artificial Intelligence is transforming technology.',
        'context': 'This discusses AI impact on modern tech industry.'
    },
    {
        'chunk_id': 2,
        'chunk_text': 'Machine learning algorithms process data efficiently.',
        'context': 'This covers ML algorithms and data processing.'
    }
]

# Add embeddings
enriched_chunks = embedder.embed_chunks(test_chunks)
print(f'✅ Created {len(enriched_chunks)} chunks with embeddings')

# Store chunks
print('\n4. Storing chunks in Qdrant...')
storage.add_chunks(enriched_chunks)
print('✅ Chunks stored successfully')

# Search test
print('\n5. Testing search...')
query = 'What is AI?'
query_embedding = embedder.embed_query(query)
print(f'Query: "{query}"')

# Search with contextual embeddings
results = storage.search(query_embedding, top_k=2, use_contextual=True)
print(f'\n✅ Found {len(results)} results (contextual)')
for i, result in enumerate(results, 1):
    print(f'\nResult {i}:')
    print(f'  Text: {result["chunk_text"]}')
    print(f'  Score: {result["score"]:.4f}')
    print(f'  Chunk ID: {result["chunk_id"]}')

print('\n' + '=' * 50)
print('✅ Vector store test passed!')
print('=' * 50)
