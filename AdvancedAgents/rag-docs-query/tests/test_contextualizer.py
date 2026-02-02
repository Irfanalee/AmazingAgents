
"""
Test the contextualizer with Claude API
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chunker import chunk_text
from src.contextualizer import add_context_to_chunk

def test_contextualizer():
    print("=" * 50)
    print("TEST: Contextualizer (Claude API)")
    print("=" * 50)
    
    # Sample document
    test_doc = """
    Artificial Intelligence (AI) has revolutionized modern technology. 
    Machine learning algorithms can now process massive datasets to find patterns.
    Deep learning, a subset of machine learning, uses neural networks with multiple layers.
    Natural language processing enables computers to understand human language.
    """
    
    # Create one chunk
    chunks = chunk_text(test_doc, chunk_size_tokens=30, chunk_overlap=5)
    
    print(f"Testing with first chunk...")
    print(f"Chunk text: {chunks[0]['chunk_text'][:100]}...")
    print(f"\nCalling Claude API... (this may take a few seconds)")
    
    try:
        chunk_with_context = add_context_to_chunk(chunks[0], test_doc)
        
        print("\n✅ SUCCESS!")
        print(f"\nOriginal chunk:")
        print(f"  {chunk_with_context['chunk_text']}")
        print(f"\nGenerated context:")
        print(f"  {chunk_with_context['context']}")
        
        return chunk_with_context
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has ANTHROPIC_API_KEY")
        print("2. Verify API key is valid")
        print("3. Ensure anthropic package is installed")
        raise

if __name__ == "__main__":
    test_contextualizer()
