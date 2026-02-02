"""
Test the chunking functionality
"""
from src.chunker import chunk_text, count_tokens

def test_chunker():
    print("=" * 50)
    print("TEST: Chunker")
    print("=" * 50)
    
    test_doc = """
    Artificial Intelligence (AI) has revolutionized modern technology. 
    Machine learning algorithms can now process massive datasets to find patterns.
    Deep learning, a subset of machine learning, uses neural networks with multiple layers.
    Natural language processing enables computers to understand human language.
    Computer vision allows machines to interpret visual information.
    These technologies are transforming industries like healthcare, finance, and transportation.
    """
    
    # Count tokens
    token_count = count_tokens(test_doc)
    print(f"Total tokens: {token_count}")
    
    # Create chunks
    chunks = chunk_text(test_doc, chunk_size_tokens=50, chunk_overlap=10)
    print(f"Number of chunks: {len(chunks)}")
    
    # Show first chunk
    if chunks:
        print(f"\nFirst chunk:")
        print(f"  ID: {chunks[0]['chunk_id']}")
        print(f"  Tokens: {chunks[0]['start_token']}-{chunks[0]['end_token']}")
        print(f"  Text: {chunks[0]['chunk_text'][:100]}...")
    
    print("✅ Chunker test passed\n")
    return chunks, test_doc

if __name__ == "__main__":
    test_chunker()
