from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class SharedContext(BaseModel):
    business_name: str = ""
    product_description: str = ""
    industry: str = ""
    stage: str = ""  # Idea / MVP / Growth / Scale / Enterprise
    target_customer: str = ""
    geography: str = ""
    revenue: str = ""
    team_size: str = ""
    main_challenge: str = ""


class AnalyzeRequest(BaseModel):
    prompt_id: str
    shared_context: SharedContext
    extra_inputs: Dict[str, str] = {}
    model: str = "claude-sonnet-4-6"
    session_id: Optional[str] = None


class SessionCreate(BaseModel):
    name: str
    shared_context: Optional[SharedContext] = None
    theme: str = "mckinsey-dark"


class SessionUpdate(BaseModel):
    name: Optional[str] = None
    shared_context: Optional[SharedContext] = None
    theme: Optional[str] = None


class ExportRequest(BaseModel):
    session_id: str
    format: str = "docx"  # "docx" or "pdf"
    selected_analyses: Optional[List[str]] = None  # prompt_ids to include


# Model pricing per million tokens (input, output)
MODEL_PRICING = {
    "claude-opus-4-6": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5-20251001": (0.25, 1.25),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    prices = MODEL_PRICING.get(model, (3.0, 15.0))
    return (input_tokens / 1_000_000) * prices[0] + (output_tokens / 1_000_000) * prices[1]
