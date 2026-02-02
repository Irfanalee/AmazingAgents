import anthropic
from config import API_KEY, CLAUDE_MODEL, CONTEXT_PROMPT
from anthropic.types import Message, TextBlock

def generate_context_for_chunk(chunk_text: str, document_text:str) -> str:
    """
    Use Claude API to generate contextual description for a chunk.
    
    Args:
        chunk_text: The text of the chunk
        document_text: The full document text
        
    Returns:
        str: The contextual description
    """


    client = anthropic.Anthropic(api_key=API_KEY)
    
    prompt = CONTEXT_PROMPT.format(
        doc_content=document_text,
        chunk_content=chunk_text

    )
    
    response =  client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=200, # short context
        messages= [
            {"role": "user", "content": prompt}
        ]
    )

    context = response.content[0].text if isinstance(response.content[0], TextBlock) else str(response.content[0])
    return context


def add_context_to_chunk(chunk: dict, document_text: str) -> dict:
    """
    Add contextual description to a chunk.
    
    Args:
        chunk: The chunk dictionary
        document_text: The full document text
        
    Returns:
        dict: The chunk dictionary with added context
    """
    context = generate_context_for_chunk(chunk["chunk_text"], document_text)
    chunk["context"] = context
    return chunk    
