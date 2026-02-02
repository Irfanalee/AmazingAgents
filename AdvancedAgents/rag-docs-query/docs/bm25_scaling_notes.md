# BM25 Scaling and Future Improvements

This document contains notes on how to scale the BM25 implementation for larger datasets and production use cases.

## Current Implementation

The current BM25Index implementation stores everything in memory:
- **Storage**: All documents and tokenized corpus stored in RAM
- **Scalability**: Good for up to 100K-1M documents
- **Persistence**: None - index rebuilt on each restart
- **Speed**: Very fast (no I/O overhead)

## Scaling Options

### Option 1: Persist to Disk with Pickle

For medium-sized datasets where you want to avoid rebuilding the index on every restart, you can serialize the BM25 index to disk.

**Implementation:**

```python
import pickle

def save_index(self, filepath: str):
    """Save the BM25 index to disk."""
    with open(filepath, 'wb') as f:
        pickle.dump({
            'bm25': self.bm25,
            'documents': self.documents,
            'tokenized_corpus': self.tokenized_corpus
        }, f)

def load_index(self, filepath: str):
    """Load a previously saved BM25 index from disk."""
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
        self.bm25 = data['bm25']
        self.documents = data['documents']
        self.tokenized_corpus = data['tokenized_corpus']
```

**Usage:**

```python
# Save after building
bm25 = BM25Index()
bm25.add_documents(chunks)
bm25.save_index('data/bm25_index.pkl')

# Load on restart
bm25 = BM25Index()
bm25.load_index('data/bm25_index.pkl')
results = bm25.search("query")
```

**Pros:**
- Fast startup (no need to rebuild)
- Simple implementation
- No additional dependencies

**Cons:**
- Still limited by available RAM
- File can be large (GBs for big datasets)
- Not suitable for distributed systems

---

### Option 2: Use Elasticsearch

For production systems with millions of documents, consider Elasticsearch which uses BM25 under the hood.

**Why Elasticsearch:**
- Uses BM25 algorithm natively
- Scales to billions of documents
- Distributed across multiple servers
- Built-in persistence and replication
- RESTful API
- Advanced features (filtering, aggregations, etc.)

**Implementation Example:**

```python
from elasticsearch import Elasticsearch

class ElasticsearchBM25:
    def __init__(self, index_name: str = "documents"):
        self.client = Elasticsearch(['http://localhost:9200'])
        self.index_name = index_name
        self._create_index()

    def _create_index(self):
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(
                index=self.index_name,
                body={
                    "settings": {
                        "number_of_shards": 2,
                        "number_of_replicas": 1,
                        "similarity": {
                            "default": {
                                "type": "BM25"
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "chunk_text": {"type": "text"},
                            "context": {"type": "text"},
                            "chunk_id": {"type": "keyword"}
                        }
                    }
                }
            )

    def add_documents(self, chunks: List[Dict]):
        """Bulk index documents."""
        actions = []
        for chunk in chunks:
            action = {
                "_index": self.index_name,
                "_source": {
                    "chunk_text": chunk["chunk_text"],
                    "context": chunk.get("context", ""),
                    "chunk_id": chunk["chunk_id"]
                }
            }
            actions.append(action)

        from elasticsearch.helpers import bulk
        bulk(self.client, actions)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search using BM25."""
        response = self.client.search(
            index=self.index_name,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["chunk_text", "context"]
                    }
                },
                "size": top_k
            }
        )

        results = []
        for hit in response['hits']['hits']:
            results.append({
                "chunk_text": hit["_source"]["chunk_text"],
                "context": hit["_source"]["context"],
                "chunk_id": hit["_source"]["chunk_id"],
                "score": hit["_score"]
            })
        return results
```

**Setup:**

```bash
# Install Elasticsearch locally (via Docker)
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0

# Install Python client
pip install elasticsearch
```

**Pros:**
- Massive scalability (billions of documents)
- Distributed and fault-tolerant
- Production-ready with monitoring
- Advanced search features
- Horizontal scaling

**Cons:**
- More complex infrastructure
- Higher operational overhead
- Requires dedicated server/cluster
- Overkill for small datasets

---

### Option 3: Hybrid Approach

Use in-memory BM25 for development and small deployments, with easy migration to Elasticsearch for production:

```python
# Create a common interface
class BM25SearchInterface:
    def add_documents(self, chunks: List[Dict]) -> None:
        raise NotImplementedError

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        raise NotImplementedError

# Both implementations inherit from interface
class BM25Index(BM25SearchInterface):
    # Current in-memory implementation
    pass

class ElasticsearchBM25(BM25SearchInterface):
    # Elasticsearch implementation
    pass

# Use environment variable to switch
import os
if os.getenv('USE_ELASTICSEARCH') == 'true':
    bm25_search = ElasticsearchBM25()
else:
    bm25_search = BM25Index()
```

---

## Recommendations

| Dataset Size | Recommended Approach |
|--------------|---------------------|
| < 10K documents | In-memory BM25Index (current) |
| 10K - 100K | In-memory + Pickle persistence |
| 100K - 1M | In-memory or Elasticsearch |
| > 1M documents | Elasticsearch or similar |

## Additional Considerations

### Memory Usage Estimates
- 10K chunks × 500 chars = ~5MB text
- With tokenization + BM25 stats = ~15-20MB total
- 100K chunks = ~150-200MB
- 1M chunks = ~1.5-2GB

### Alternative Solutions
- **Apache Solr**: Similar to Elasticsearch, also uses BM25
- **Typesense**: Lightweight alternative, faster but less scalable
- **Meilisearch**: Great for smaller datasets, simpler than ES
- **OpenSearch**: AWS fork of Elasticsearch

### Performance Considerations
- In-memory BM25: Sub-millisecond query times
- Elasticsearch: 10-50ms query times (network + processing)
- Pickle load time: Proportional to index size (~1-5 seconds for 100K docs)
