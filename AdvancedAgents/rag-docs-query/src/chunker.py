import tiktoken 
from config import chunk_size, chunk_overlap

def count_tokens(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    """Count the number of tokens in a given text using tiktoken."""
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    return len(tokens)


def chunk_text(text: str, chunk_size_tokens: int = chunk_size, chunk_overlap: int = chunk_overlap, model_name: str = "gpt-3.5-turbo") -> list[dict]:
    """Chunk the input text into smaller pieces based on token count."""
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    text_length = len(tokens)
    
    while start < text_length:
        end = min(start + chunk_size_tokens, text_length)
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        
        chunks.append({
            "chunk_text": chunk_text,
            "start_token": start,
            "end_token": end,
            "chunk_id": len(chunks) + 1
        })
        
        start += chunk_size_tokens - chunk_overlap
    
    return chunks