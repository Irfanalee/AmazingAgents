# Interactive Contextual Retrieval System - User Guide

## 🎯 Overview

`main.py` is an interactive command-line application that lets you ask questions about any PDF document using state-of-the-art contextual retrieval with hybrid search.

## 🚀 Quick Start

### Basic Usage

```bash
python main.py path/to/your/document.pdf
```

### With Real Context (Recommended for Production)

```bash
python main.py path/to/your/document.pdf --real-context
```

## 📋 Features

### 1. **Automatic Document Processing**
- Loads PDF and extracts text
- Chunks document intelligently (800 tokens, 200 overlap)
- Generates contextual descriptions for each chunk
- Creates dual embeddings (standard + contextual)
- Builds both vector (Qdrant) and BM25 indexes

### 2. **Hybrid Search**
- Combines semantic search (vector embeddings)
- With lexical search (BM25 keyword matching)
- Automatically ranks results by relevance

### 3. **Interactive Q&A Session**
- Ask unlimited questions about your document
- Get top 3 most relevant results
- See scoring breakdown (vector + BM25)
- View context and chunk text

## 🎮 How It Works

### Step-by-Step Process

```
1. Document Loading
   └─> Reads PDF and extracts text

2. Chunking
   └─> Splits into 800-token chunks with 200-token overlap

3. Context Generation
   ├─> Mock Mode: Fast, uses template context
   └─> Real Mode: Uses Claude API for intelligent context

4. Embedding Generation
   ├─> Standard embedding (chunk only)
   └─> Contextual embedding (context + chunk)

5. Dual Indexing
   ├─> Vector Store (Qdrant) for semantic search
   └─> BM25 Index for keyword search

6. Interactive Session
   └─> Ask questions → Hybrid search → Ranked results
```

## 💡 Usage Examples

### Example 1: Quick Test (Mock Context)

```bash
# Fast processing for testing
python main.py data/reference.docx
```

**Output:**
```
======================================================================
🔍 CONTEXTUAL RETRIEVAL SYSTEM
======================================================================
Powered by: Contextual Embeddings + Hybrid Search
======================================================================

📄 Loading document: data/reference.docx
✅ Loaded 15234 characters

📦 Chunking document (size=800, overlap=200)...
✅ Created 5 chunks

🧠 Adding context to chunks...
   Using MOCK context for speed (use --real-context for Claude API)
✅ Added context to all 5 chunks

🎯 Generating embeddings...
✅ Generated dual embeddings for 5 chunks

💾 Storing in vector database (Qdrant)...
✅ Stored in Qdrant with dual vectors

📇 Building BM25 index...
✅ Built BM25 index

🔗 Initializing hybrid retriever...
✅ Hybrid retriever ready (50% vector + 50% BM25)

======================================================================
✅ DOCUMENT LOADED AND INDEXED SUCCESSFULLY!
======================================================================

======================================================================
💡 INTERACTIVE SESSION STARTED
======================================================================
Ask questions about your document!
Commands:
  - Type your question and press Enter
  - 'quit' or 'exit' to end session
  - 'help' for more options
======================================================================

🔍 Your question:
```

### Example 2: Production Mode (Real Context)

```bash
# Best quality results using Claude API
python main.py data/reference.docx --real-context
```

**Benefits:**
- Claude generates intelligent, document-specific context
- Much better retrieval accuracy
- Takes longer to process (uses API calls)

### Example 3: Interactive Session

```
🔍 Your question: What is machine learning?

🔎 Searching...

📊 Found 3 results:

======================================================================
Result #1
======================================================================
📈 Combined Score: 0.8954
   ├─ Vector Score:  0.9234 (semantic similarity)
   └─ BM25 Score:    0.8674 (keyword matching)

💬 Context:
   This chunk discusses machine learning as a subset of artificial
   intelligence, focusing on algorithms and data processing.

📝 Text:
   Machine learning is a branch of artificial intelligence that
   enables computers to learn from data without being explicitly
   programmed. It uses algorithms to identify patterns...

======================================================================
Result #2
======================================================================
📈 Combined Score: 0.7821
   ├─ Vector Score:  0.8123 (semantic similarity)
   └─ BM25 Score:    0.7519 (keyword matching)

💬 Context:
   This section explains different types of machine learning
   approaches including supervised and unsupervised learning.

📝 Text:
   There are three main types of machine learning: supervised
   learning, unsupervised learning, and reinforcement learning...

📄 See full text of results? (y/n): n

🔍 Your question: stats

📊 Document Statistics:
   Total chunks: 5
   Total characters: 15234
   Average chunk size: 3046 chars

🔍 Your question: quit

👋 Goodbye! Thanks for using Contextual Retrieval System.
```

## 🎛️ Command Options

### During Interactive Session

| Command | Description |
|---------|-------------|
| `<question>` | Ask any question about the document |
| `stats` | Show document statistics (chunks, characters, etc.) |
| `help` | Display available commands |
| `quit` / `exit` / `q` | End the session |

### Command Line Options

| Option | Description |
|--------|-------------|
| `<pdf-path>` | **Required**. Path to your PDF document |
| `--real-context` | Use Claude API for context generation (recommended for production) |

## 📊 Understanding Results

### Result Components

```
======================================================================
Result #1
======================================================================
📈 Combined Score: 0.8954          ← Overall relevance (0-1 scale)
   ├─ Vector Score:  0.9234        ← Semantic similarity score
   └─ BM25 Score:    0.8674        ← Keyword matching score

💬 Context:                         ← AI-generated context description
   This chunk discusses...

📝 Text:                            ← Actual chunk content
   Machine learning is...
```

### Score Interpretation

- **Combined Score**: Weighted average (50% vector + 50% BM25)
  - 0.9 - 1.0: Excellent match
  - 0.7 - 0.9: Good match
  - 0.5 - 0.7: Moderate match
  - < 0.5: Weak match

- **Vector Score**: How semantically similar the chunk is to your question
  - High: Chunk discusses similar concepts
  - Uses contextual embeddings

- **BM25 Score**: How well keywords match
  - High: Chunk contains exact query terms
  - Uses lexical matching

## 🔧 Configuration

### Modify Search Behavior

Edit the code in `main.py`:

```python
# Change weights (line ~82)
hybrid_retriever = HybridRetriever(
    vector_store=storage,
    bm25_index=bm25_index,
    embedder=embedder,
    vector_weight=0.7,  # More weight on semantic search
    bm25_weight=0.3     # Less weight on keywords
)

# Change number of results (line ~163)
results = hybrid_retriever.retrieve(query, top_k=5)  # Get 5 results instead of 3

# Change chunk size (in config.py)
chunk_size = 1000          # Larger chunks
chunk_overlap = 250        # More overlap
```

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. "Qdrant connection error"**
```bash
# Solution: Start Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

**3. "File not found" error**
```bash
# Solution: Use correct path
python main.py data/reference.docx  # Correct
python main.py reference.docx       # Wrong (missing data/ prefix)
```

**4. "Claude API error" (with --real-context)**
```bash
# Solution: Check your API key in .env file
ANTHROPIC_API_KEY=your-key-here
```

## 🎓 Tips for Best Results

### 1. **Question Formulation**
```
✅ Good: "What are the main benefits of machine learning?"
✅ Good: "Explain neural networks"
✅ Good: "How does gradient descent work?"

❌ Avoid: Single words like "ML" or "AI"
❌ Avoid: Too vague like "Tell me everything"
```

### 2. **Mock vs Real Context**

**Use Mock Context When:**
- Testing the system
- Quick iterations
- Document structure matters more than semantics

**Use Real Context When:**
- Production use
- Maximum accuracy needed
- Document has complex topics

### 3. **Document Types**

**Works Best With:**
- Technical documentation
- Research papers
- Reports and articles
- Educational materials

**May Need Tuning For:**
- Very short documents (< 1000 words)
- Heavily formatted documents
- Documents with lots of tables/figures

## 📈 Performance

### Processing Time

| Document Size | Mock Context | Real Context |
|---------------|--------------|--------------|
| 5 pages | ~10 seconds | ~30 seconds |
| 20 pages | ~30 seconds | ~2 minutes |
| 50 pages | ~1 minute | ~5 minutes |

**Note**: Real context time depends on Claude API response time

### Memory Usage

- Small doc (5 pages): ~100MB RAM
- Medium doc (20 pages): ~300MB RAM
- Large doc (50 pages): ~700MB RAM

## 🚀 Advanced Usage

### Batch Processing Multiple Documents

```bash
# Process multiple PDFs
for pdf in data/*.pdf; do
    echo "Processing $pdf"
    python main.py "$pdf" --real-context
done
```

### Integration with Scripts

```python
# Use as a library
from main import load_and_process_document

chunks, embedder, storage, bm25, retriever = load_and_process_document(
    "data/mydoc.pdf",
    use_mock_context=False
)

# Query programmatically
results = retriever.retrieve("your question", top_k=5)
for result in results:
    print(f"Score: {result['combined_score']}")
    print(f"Text: {result['chunk_text']}")
```

## 📚 Architecture

### System Components

```
main.py
   │
   ├─> Document Loader (src/document_loader.py)
   ├─> Chunker (src/chunker.py)
   ├─> Contextualizer (src/contextualizer.py)
   ├─> Embedder (src/embedder.py)
   ├─> Vector Store (src/vector_store.py)
   ├─> BM25 Index (src/bm25_index.py)
   └─> Hybrid Retriever (src/retriever.py)
```

### Data Flow

```
PDF Input
   ↓
Text Extraction
   ↓
Chunking (800 tokens)
   ↓
Context Generation (Claude API or Mock)
   ↓
Dual Embeddings (Standard + Contextual)
   ↓
   ├─> Qdrant (Vector Search)
   └─> BM25 (Keyword Search)
   ↓
Hybrid Retriever (Merge Results)
   ↓
Interactive Q&A
```

## 🎯 Use Cases

### 1. **Research Assistant**
- Load research papers
- Ask specific questions about methodology
- Find relevant sections quickly

### 2. **Document Q&A**
- Company policies and procedures
- Technical documentation
- Training materials

### 3. **Study Aid**
- Load textbook chapters
- Ask questions to test understanding
- Get relevant explanations

### 4. **Content Discovery**
- Explore large documents
- Find specific information
- Understand document structure

## 📝 Example Workflows

### Workflow 1: Academic Research

```bash
# 1. Load research paper
python main.py research/paper.pdf --real-context

# 2. Ask about methodology
🔍 Your question: What methodology was used in this study?

# 3. Find specific results
🔍 Your question: What were the main findings?

# 4. Understand implications
🔍 Your question: What are the practical applications?
```

### Workflow 2: Technical Documentation

```bash
# 1. Load API documentation
python main.py docs/api-reference.pdf

# 2. Quick queries (mock context is fine)
🔍 Your question: How do I authenticate?

# 3. Find examples
🔍 Your question: Show me an example of error handling

# 4. Get statistics
🔍 Your question: stats
```

## 🔗 Related Files

- `README.md` - Main project documentation
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
- `.env` - API keys and secrets
- `tests/test_end_to_end.py` - Full pipeline test

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review `README.md` for system architecture
3. Run tests: `python tests/test_end_to_end.py`
4. Check GitHub issues

## 🎉 Success Indicators

You know it's working when:
- ✅ Document loads without errors
- ✅ Search returns relevant results
- ✅ Scores make sense (higher for better matches)
- ✅ Results contain expected information
- ✅ Both vector and BM25 scores are > 0

---

**Happy Searching! 🚀**

*Built with Anthropic's Contextual Retrieval + Hybrid Search*
