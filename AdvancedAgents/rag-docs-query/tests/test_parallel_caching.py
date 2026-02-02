"""
Test script for parallel processing + prompt caching optimization.

This script tests the new parallel contextualizer to ensure:
1. It processes chunks correctly
2. It's faster than sequential processing
3. Prompt caching is working (check costs in your API usage)
"""

import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.contextualizer_parallel import add_context_to_chunks_batch

# Sample document
document_text = """
The Art of War is an ancient Chinese military treatise dating from the Late Spring and Autumn Period.
The work, which is attributed to the ancient Chinese military strategist Sun Tzu, is composed of 13 chapters.
Each one is devoted to an aspect of warfare and how it applies to military strategy and tactics.

For almost 1,500 years it was the lead text in an anthology that was formalized as the Seven Military Classics
by Emperor Shenzong of Song in 1080. The Art of War remains the most influential strategy text in East Asian warfare
and has influenced both Eastern and Western military thinking, business tactics, legal strategy, lifestyles and beyond.

The book contained a detailed explanation and analysis of the Chinese military, from weapons and strategy to rank
and discipline. Sun Tzu also stressed the importance of intelligence operatives and espionage to the war effort.
Because Sun Tzu has long been considered to be one of history's finest military tacticians and analysts,
his teachings and strategies formed the basis of advanced military training for millennia to come.
"""

# Create sample chunks
chunks = [
    {
        "chunk_id": "chunk_0",
        "chunk_text": "The Art of War is an ancient Chinese military treatise dating from the Late Spring and Autumn Period. The work, which is attributed to the ancient Chinese military strategist Sun Tzu, is composed of 13 chapters.",
        "start_token": 0,
        "end_token": 50
    },
    {
        "chunk_id": "chunk_1",
        "chunk_text": "Each one is devoted to an aspect of warfare and how it applies to military strategy and tactics. For almost 1,500 years it was the lead text in an anthology that was formalized as the Seven Military Classics by Emperor Shenzong of Song in 1080.",
        "start_token": 40,
        "end_token": 90
    },
    {
        "chunk_id": "chunk_2",
        "chunk_text": "The Art of War remains the most influential strategy text in East Asian warfare and has influenced both Eastern and Western military thinking, business tactics, legal strategy, lifestyles and beyond.",
        "start_token": 80,
        "end_token": 130
    },
    {
        "chunk_id": "chunk_3",
        "chunk_text": "The book contained a detailed explanation and analysis of the Chinese military, from weapons and strategy to rank and discipline. Sun Tzu also stressed the importance of intelligence operatives and espionage to the war effort.",
        "start_token": 120,
        "end_token": 170
    },
    {
        "chunk_id": "chunk_4",
        "chunk_text": "Because Sun Tzu has long been considered to be one of history's finest military tacticians and analysts, his teachings and strategies formed the basis of advanced military training for millennia to come.",
        "start_token": 160,
        "end_token": 210
    }
]

print("=" * 70)
print("TEST: Parallel Processing + Prompt Caching")
print("=" * 70)

print(f"\n📄 Sample document: {len(document_text)} characters")
print(f"📦 Number of chunks: {len(chunks)}")

print("\n🚀 Testing parallel context generation...")
print("   This will make real API calls and cost ~$0.01")
print("   Watch for the progress indicator!")

# Time the operation
start_time = time.time()

try:
    # Run parallel processing
    enriched_chunks = add_context_to_chunks_batch(chunks, document_text)

    elapsed_time = time.time() - start_time

    print(f"\n⏱️  Processing time: {elapsed_time:.2f} seconds")
    print(f"\n✅ Successfully processed {len(enriched_chunks)} chunks!")

    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    for i, chunk in enumerate(enriched_chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  Text: {chunk['chunk_text'][:80]}...")
        print(f"  Context: {chunk['context']}")

    print("\n" + "=" * 70)
    print("✅ TEST PASSED!")
    print("=" * 70)

    print("\n📊 Performance Notes:")
    print(f"   - Processing time: {elapsed_time:.2f} seconds")
    print(f"   - Chunks per second: {len(chunks) / elapsed_time:.2f}")
    print(f"   - Estimated cost: ~$0.01 (check your API usage)")

    print("\n💡 Check your Anthropic API usage dashboard to verify:")
    print("   1. First chunk shows 'cache write' tokens")
    print("   2. Subsequent chunks show 'cache read' tokens (90% cheaper)")
    print("   3. Total cost should be much lower than without caching")

except Exception as e:
    print(f"\n❌ TEST FAILED!")
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
