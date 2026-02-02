#!/usr/bin/env python3
# This was generrated by AI - not by yours truly

"""
Interactive Contextual Retrieval System
Load a PDF and ask questions using hybrid search!
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.document_loader import load_document
from src.chunker import chunk_text
from src.contextualizer import add_context_to_chunk
from src.contextualizer_parallel import add_context_to_chunks_batch
from src.embedder import Embedder
from src.vector_store import QdrantStorage
from src.bm25_index import BM25Index
from src.retriever import HybridRetriever
from config import chunk_size, chunk_overlap

def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 70)
    print("🔍 CONTEXTUAL RETRIEVAL SYSTEM")
    print("=" * 70)
    print("Powered by: Contextual Embeddings + Hybrid Search")
    print("=" * 70 + "\n")

def load_and_process_document(pdf_path: str, use_mock_context: bool = False):
    """
    Load and process a PDF document through the entire pipeline.

    Args:
        pdf_path: Path to PDF file
        use_mock_context: If True, use mock context (fast). If False, use Claude API (slower but better)

    Returns:
        Tuple of (chunks, embedder, vector_store, bm25_index, hybrid_retriever)
    """
    print(f"📄 Loading document: {pdf_path}")
    document_text = load_document(pdf_path)
    print(f"✅ Loaded {len(document_text)} characters")

    # Step 1: Chunk the document
    print(f"\n📦 Chunking document (size={chunk_size}, overlap={chunk_overlap})...")
    chunks = chunk_text(document_text, chunk_size_tokens=chunk_size, chunk_overlap=chunk_overlap)
    print(f"✅ Created {len(chunks)} chunks")

    # Step 2: Add context to chunks
    print(f"\n🧠 Adding context to chunks...")
    if use_mock_context:
        print("   Using MOCK context for speed (use --real-context for Claude API)")
        for i, chunk in enumerate(chunks):
            chunk['context'] = f"This is chunk {i+1} from the document discussing various topics."
    else:
        print("   Using Claude API with PARALLEL processing + prompt caching...")
        print("   This is much faster and cheaper than sequential processing!")
        chunks = add_context_to_chunks_batch(chunks, document_text)
        print(f"✅ Added context to all {len(chunks)} chunks")

    # Step 3: Generate embeddings
    print(f"\n🎯 Generating embeddings...")
    embedder = Embedder()
    enriched_chunks = embedder.embed_chunks(chunks)
    print(f"✅ Generated dual embeddings for {len(enriched_chunks)} chunks")

    # Step 4: Store in Qdrant
    print(f"\n💾 Storing in vector database (Qdrant)...")
    storage = QdrantStorage(collection_name="interactive_session")
    # Clear existing data
    storage.client.delete_collection(collection_name=storage.collection_name)
    storage._create_collection()
    storage.add_chunks(enriched_chunks)
    print(f"✅ Stored in Qdrant with dual vectors")

    # Step 5: Build BM25 index
    print(f"\n📇 Building BM25 index...")
    bm25_index = BM25Index()
    bm25_index.add_documents(enriched_chunks)
    print(f"✅ Built BM25 index")

    # Step 6: Initialize hybrid retriever
    print(f"\n🔗 Initializing hybrid retriever...")
    hybrid_retriever = HybridRetriever(
        vector_store=storage,
        bm25_index=bm25_index,
        embedder=embedder,
        vector_weight=0.5,
        bm25_weight=0.5
    )
    print(f"✅ Hybrid retriever ready (50% vector + 50% BM25)")

    return enriched_chunks, embedder, storage, bm25_index, hybrid_retriever

def display_results(results, show_full_text: bool = False):
    """Display search results in a formatted way"""
    if not results:
        print("\n❌ No results found.")
        return

    print(f"\n📊 Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{'='*70}")
        print(f"Result #{i}")
        print(f"{'='*70}")
        print(f"📈 Combined Score: {result['combined_score']:.4f}")
        print(f"   ├─ Vector Score:  {result['vector_score']:.4f} (semantic similarity)")
        print(f"   └─ BM25 Score:    {result['bm25_score']:.4f} (keyword matching)")
        print(f"\n💬 Context:")
        print(f"   {result['context']}")
        print(f"\n📝 Text:")
        if show_full_text:
            print(f"   {result['chunk_text']}")
        else:
            # Show first 200 chars
            text = result['chunk_text']
            if len(text) > 200:
                print(f"   {text[:200]}...")
            else:
                print(f"   {text}")
        print()

def interactive_session(hybrid_retriever, chunks):
    """Run interactive Q&A session"""
    print("\n" + "=" * 70)
    print("💡 INTERACTIVE SESSION STARTED")
    print("=" * 70)
    print("Ask questions about your document!")
    print("Commands:")
    print("  - Type your question and press Enter")
    print("  - 'quit' or 'exit' to end session")
    print("  - 'help' for more options")
    print("=" * 70 + "\n")

    while True:
        try:
            # Get user input
            query = input("🔍 Your question: ").strip()

            if not query:
                continue

            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thanks for using Contextual Retrieval System.")
                break

            if query.lower() == 'help':
                print("\n📖 Available commands:")
                print("  - Ask any question about the document")
                print("  - 'stats' - Show document statistics")
                print("  - 'quit' or 'exit' - End session")
                print()
                continue

            if query.lower() == 'stats':
                print(f"\n📊 Document Statistics:")
                print(f"   Total chunks: {len(chunks)}")
                print(f"   Total characters: {sum(len(c['chunk_text']) for c in chunks)}")
                print(f"   Average chunk size: {sum(len(c['chunk_text']) for c in chunks) // len(chunks)} chars")
                print()
                continue

            # Perform hybrid search
            print(f"\n🔎 Searching...")
            results = hybrid_retriever.retrieve(query, top_k=3)

            # Display results
            display_results(results, show_full_text=False)

            # Ask if user wants to see full text
            see_more = input("📄 See full text of results? (y/n): ").strip().lower()
            if see_more == 'y':
                display_results(results, show_full_text=True)

            print()

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.\n")

def main():
    """Main entry point"""
    print_banner()

    # Check for PDF path argument
    if len(sys.argv) < 2:
        print("Usage: python main.py <path-to-pdf> [--real-context]")
        print("\nExample:")
        print("  python main.py data/mydocument.pdf")
        print("  python main.py data/mydocument.pdf --real-context")
        print("\nOptions:")
        print("  --real-context: Use Claude API for context generation (slower but better)")
        print("                  Default: Uses mock context for speed")
        return

    pdf_path = sys.argv[1]
    use_real_context = '--real-context' in sys.argv

    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"❌ Error: File not found: {pdf_path}")
        return

    try:
        # Process document
        chunks, embedder, storage, bm25_index, hybrid_retriever = load_and_process_document(
            pdf_path,
            use_mock_context=not use_real_context
        )

        print("\n" + "="*70)
        print("✅ DOCUMENT LOADED AND INDEXED SUCCESSFULLY!")
        print("="*70)

        # Start interactive session
        interactive_session(hybrid_retriever, chunks)

    except Exception as e:
        print(f"\n❌ Error processing document: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
