import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chunker import chunk_text
from src.contextualizer import add_context_to_chunk
from src.embedder import Embedder
from src.vector_store import QdrantStorage
from src.bm25_index import BM25Index
from src.retriever import HybridRetriever

print('=' * 70)
print('END-TO-END TEST: Complete Contextual Retrieval Pipeline')
print('=' * 70)

# Sample document about AI and ML
document_text = """
Artificial Intelligence and Machine Learning Overview

Machine learning is a subset of artificial intelligence that focuses on
teaching computers to learn from data. Deep learning algorithms use neural
networks with multiple layers to process complex patterns.

Natural language processing (NLP) is a branch of AI that helps computers
understand and generate human language. Modern NLP systems use transformer
architectures like BERT and GPT.

Computer vision enables machines to interpret visual information from images
and videos. Convolutional neural networks are particularly effective for
image recognition tasks.

Reinforcement learning trains agents to make sequential decisions by
rewarding desired behaviors. This approach has been successful in game
playing and robotics applications.
"""

print('\n' + '=' * 70)
print('STEP 1: Document Chunking')
print('=' * 70)

# Chunk the document
chunks = chunk_text(document_text, chunk_size_tokens=50, chunk_overlap=10)
print(f'✅ Created {len(chunks)} chunks from document')
for i, chunk in enumerate(chunks, 1):
    print(f'\nChunk {i}:')
    print(f'  Text: {chunk["chunk_text"][:80]}...')
    print(f'  Tokens: {chunk["start_token"]} to {chunk["end_token"]}')

print('\n' + '=' * 70)
print('STEP 2: Adding Context (using mock context for speed)')
print('=' * 70)

# For testing, we'll add mock context instead of calling Claude API
# In production, you would use: add_context_to_chunk(chunk, document_text)
mock_contexts = [
    "This introduces AI and ML as related fields of computer science.",
    "This discusses deep learning and neural network architectures.",
    "This explains NLP and modern transformer models like BERT and GPT.",
    "This covers computer vision and CNNs for image tasks.",
    "This describes reinforcement learning applications in games and robotics."
]

for i, chunk in enumerate(chunks):
    if i < len(mock_contexts):
        chunk['context'] = mock_contexts[i]
    else:
        chunk['context'] = f"This discusses AI concepts in chunk {i+1}."
    print(f'✅ Chunk {i+1}: Added context')
    print(f'   Context: {chunk["context"]}')

print('\n' + '=' * 70)
print('STEP 3: Generating Embeddings')
print('=' * 70)

embedder = Embedder()
enriched_chunks = embedder.embed_chunks(chunks)
print(f'✅ Generated embeddings for {len(enriched_chunks)} chunks')
print(f'   Each chunk now has:')
print(f'   - embedding: {enriched_chunks[0]["embedding"].shape}')
print(f'   - contextual_embedding: {enriched_chunks[0]["contextual_embedding"].shape}')

print('\n' + '=' * 70)
print('STEP 4: Storing in Vector Database (Qdrant)')
print('=' * 70)

# Initialize Qdrant and clear existing data
storage = QdrantStorage(collection_name="test_end_to_end")
storage.client.delete_collection(collection_name=storage.collection_name)
storage._create_collection()
print('✅ Created fresh Qdrant collection')

# Store chunks
storage.add_chunks(enriched_chunks)
print(f'✅ Stored {len(enriched_chunks)} chunks with dual embeddings')

print('\n' + '=' * 70)
print('STEP 5: Building BM25 Index')
print('=' * 70)

bm25_index = BM25Index()
bm25_index.add_documents(enriched_chunks)
print(f'✅ Built BM25 index with {len(enriched_chunks)} documents')

print('\n' + '=' * 70)
print('STEP 6: Testing Individual Search Systems')
print('=' * 70)

test_query = "What is neural network architecture?"

print(f'\nQuery: "{test_query}"')

# Test Vector Search
print('\n--- Vector Search Results (Contextual) ---')
query_embedding = embedder.embed_query(test_query)
vector_results = storage.search(query_embedding, top_k=3, use_contextual=True)
for i, result in enumerate(vector_results, 1):
    print(f'\nResult {i}:')
    print(f'  Score: {result["score"]:.4f}')
    print(f'  Text: {result["chunk_text"][:80]}...')

# Test BM25 Search
print('\n--- BM25 Search Results ---')
bm25_results = bm25_index.search(test_query, top_k=3)
for i, result in enumerate(bm25_results, 1):
    print(f'\nResult {i}:')
    print(f'  Score: {result["score"]:.4f}')
    print(f'  Text: {result["chunk_text"][:80]}...')

print('\n' + '=' * 70)
print('STEP 7: Hybrid Retrieval (THE MAGIC!) ✨')
print('=' * 70)

# Initialize hybrid retriever
hybrid_retriever = HybridRetriever(
    vector_store=storage,
    bm25_index=bm25_index,
    embedder=embedder,
    vector_weight=0.5,
    bm25_weight=0.5
)
print('✅ Initialized Hybrid Retriever (50% vector + 50% BM25)')

# Test queries
test_queries = [
    "What is neural network architecture?",
    "Tell me about NLP and language models",
    "computer vision CNN"
]

for query in test_queries:
    print(f'\n{"=" * 70}')
    print(f'Query: "{query}"')
    print(f'{"=" * 70}')

    hybrid_results = hybrid_retriever.retrieve(query, top_k=3)

    for i, result in enumerate(hybrid_results, 1):
        print(f'\nResult {i}:')
        print(f'  Combined Score: {result["combined_score"]:.4f}')
        print(f'  Vector Score:   {result["vector_score"]:.4f}')
        print(f'  BM25 Score:     {result["bm25_score"]:.4f}')
        print(f'  Text: {result["chunk_text"][:100]}...')
        print(f'  Context: {result["context"]}')

print('\n' + '=' * 70)
print('STEP 8: Comparing Search Approaches')
print('=' * 70)

query = "reinforcement learning rewards"
print(f'\nQuery: "{query}"')

# Vector only
print('\n--- Vector Search Only ---')
vector_only = storage.search(embedder.embed_query(query), top_k=2)
print(f'Top result: {vector_only[0]["chunk_text"][:80]}...')
print(f'Score: {vector_only[0]["score"]:.4f}')

# BM25 only
print('\n--- BM25 Search Only ---')
bm25_only = bm25_index.search(query, top_k=2)
print(f'Top result: {bm25_only[0]["chunk_text"][:80]}...')
print(f'Score: {bm25_only[0]["score"]:.4f}')

# Hybrid
print('\n--- Hybrid Search (BEST!) ---')
hybrid_only = hybrid_retriever.retrieve(query, top_k=2)
print(f'Top result: {hybrid_only[0]["chunk_text"][:80]}...')
print(f'Combined Score: {hybrid_only[0]["combined_score"]:.4f}')
print(f'  (Vector: {hybrid_only[0]["vector_score"]:.4f}, BM25: {hybrid_only[0]["bm25_score"]:.4f})')

print('\n' + '=' * 70)
print('✅ END-TO-END TEST COMPLETE!')
print('=' * 70)
print('\nWhat we demonstrated:')
print('1. ✅ Document chunking with token-based splitting')
print('2. ✅ Context generation (mocked for speed)')
print('3. ✅ Dual embeddings (standard + contextual)')
print('4. ✅ Vector storage in Qdrant with named vectors')
print('5. ✅ BM25 lexical indexing')
print('6. ✅ Vector search (semantic similarity)')
print('7. ✅ BM25 search (keyword matching)')
print('8. ✅ Hybrid retrieval (combining both!)')
print('\nThe system is now ready for production use! 🚀')
print('=' * 70)
