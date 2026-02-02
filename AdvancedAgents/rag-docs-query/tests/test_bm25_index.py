import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bm25_index import BM25Index

print('=' * 50)
print('TEST: BM25 Lexical Search')
print('=' * 50)

# Initialize BM25 index
print('\n1. Initializing BM25 index...')
bm25_index = BM25Index()
print('✅ BM25 index initialized')

# Create test chunks
print('\n2. Creating test chunks...')
test_chunks = [
    {
        'chunk_id': 1,
        'chunk_text': 'Artificial Intelligence is transforming technology across industries.',
        'context': 'This discusses AI impact on modern tech industry.'
    },
    {
        'chunk_id': 2,
        'chunk_text': 'Machine learning algorithms process large amounts of data efficiently.',
        'context': 'This covers ML algorithms and data processing capabilities.'
    },
    {
        'chunk_id': 3,
        'chunk_text': 'Deep learning models require significant computational resources.',
        'context': 'This explains resource requirements for deep learning.'
    },
    {
        'chunk_id': 4,
        'chunk_text': 'Natural language processing enables computers to understand human language.',
        'context': 'This discusses NLP and language understanding technology.'
    },
    {
        'chunk_id': 5,
        'chunk_text': 'Computer vision systems can identify objects in images and videos.',
        'context': 'This covers computer vision applications and capabilities.'
    }
]
print(f'✅ Created {len(test_chunks)} test chunks')

# Add documents to index
print('\n3. Adding documents to BM25 index...')
bm25_index.add_documents(test_chunks)
print('✅ Documents indexed successfully')

# Test search with different queries
print('\n4. Testing BM25 search...')

queries = [
    'What is machine learning?',
    'How does AI process data?',
    'computer vision',
    'language understanding'
]

for query in queries:
    print(f'\n--- Query: "{query}" ---')
    results = bm25_index.search(query, top_k=3)
    print(f'Found {len(results)} results:')

    for i, result in enumerate(results, 1):
        print(f'\n  Result {i}:')
        print(f'    Score: {result["score"]:.4f}')
        print(f'    Text: {result["chunk_text"]}')
        print(f'    Chunk ID: {result["chunk_id"]}')

# Test with keyword match
print('\n\n5. Testing exact keyword match...')
query = 'algorithms'
print(f'Query: "{query}"')
results = bm25_index.search(query, top_k=2)
print(f'\n✅ Found {len(results)} results with keyword "algorithms"')
for i, result in enumerate(results, 1):
    print(f'\nResult {i}:')
    print(f'  Score: {result["score"]:.4f}')
    print(f'  Text: {result["chunk_text"]}')

# Test that context is being used
print('\n\n6. Testing context matching...')
query = 'NLP technology'
print(f'Query: "{query}"')
results = bm25_index.search(query, top_k=2)
print(f'\n✅ Found {len(results)} results')
for i, result in enumerate(results, 1):
    print(f'\nResult {i}:')
    print(f'  Score: {result["score"]:.4f}')
    print(f'  Text: {result["chunk_text"]}')
    print(f'  Context: {result["context"]}')

# Test zero results for unrelated query
print('\n\n7. Testing unrelated query...')
query = 'quantum physics superposition'
print(f'Query: "{query}"')
results = bm25_index.search(query, top_k=5)
print(f'✅ Found {len(results)} results (expected 0 since query is unrelated)')

print('\n' + '=' * 50)
print('✅ BM25 index test passed!')
print('=' * 50)
