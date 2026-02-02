########################
#
#centralized configuration file that stores all the settings 
#and parameters for your entire project in one place.
#
############################

import os 
from dotenv import load_dotenv


# Load environment variables from a .env file if it exists
load_dotenv()

# API key for accessing the language model service
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")  

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None) 
COLLECTION_NAME ="contextual_retrieval"

# Chunking config
chunk_size = 800  # token per chunk
chunk_overlap = 200  # token overlap between chunks

# Embedding model configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Example embedding model name
EMBEDDING_DIMENSION = 384  # Dimension for the chosen embedding model

# Retrieval configuration
TOP_K_RETRIEVAL = 20  # Number of top similar chunks to retrieve
TOP_K_FINAL = 5 # After re-ranking


# Claude model configuration  
CLAUDE_MODEL = "claude-3-5-haiku-20241022"

CONTEXT_PROMPT = """<document>
{doc_content}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else."""
