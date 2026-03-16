import hashlib
import json
import asyncio
import uuid
from typing import AsyncGenerator, Optional
from datetime import datetime, timedelta

import anthropic
from sqlalchemy.orm import Session as DBSession

from .database import Cache, Analysis, FeedbackMessage
from .models import estimate_cost

CACHE_TTL_DAYS = 7


def make_cache_key(model: str, prompt_id: str, inputs: dict) -> str:
    payload = json.dumps(
        {"model": model, "prompt_id": prompt_id, "inputs": inputs}, sort_keys=True
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def get_cached_response(db: DBSession, cache_key: str) -> Optional[Cache]:
    cutoff = datetime.utcnow() - timedelta(days=CACHE_TTL_DAYS)
    entry = (
        db.query(Cache)
        .filter(Cache.cache_key == cache_key, Cache.created_at >= cutoff)
        .first()
    )
    if entry:
        entry.hit_count = (entry.hit_count or 0) + 1
        db.commit()
    return entry


def store_cache(
    db: DBSession,
    cache_key: str,
    prompt_id: str,
    model: str,
    response: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
):
    existing = db.query(Cache).filter(Cache.cache_key == cache_key).first()
    if existing:
        existing.response = response
        existing.input_tokens = input_tokens
        existing.output_tokens = output_tokens
        existing.cost_usd = cost_usd
        existing.created_at = datetime.utcnow()
    else:
        entry = Cache(
            cache_key=cache_key,
            prompt_id=prompt_id,
            model=model,
            response=response,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
        db.add(entry)
    db.commit()


def save_analysis(
    db: DBSession,
    session_id: Optional[str],
    prompt_id: str,
    inputs_dict: dict,
    output: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    from_cache: bool,
) -> str:
    analysis_id = str(uuid.uuid4())
    analysis = Analysis(
        id=analysis_id,
        session_id=session_id,
        prompt_id=prompt_id,
        inputs=json.dumps(inputs_dict),
        output=output,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
        from_cache=from_cache,
    )
    db.add(analysis)
    db.commit()
    return analysis_id


async def stream_analysis(
    api_key: str,
    model: str,
    prompt_id: str,
    filled_prompt: str,
    inputs_dict: dict,
    db: DBSession,
    session_id: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    cache_key = make_cache_key(model, prompt_id, inputs_dict)

    # --- Cache hit ---
    cached = get_cached_response(db, cache_key)
    if cached:
        yield f"data: {json.dumps({'type': 'cache_hit', 'input_tokens': cached.input_tokens, 'output_tokens': cached.output_tokens, 'cost_usd': cached.cost_usd})}\n\n"

        # Stream cached content in small chunks for a live feel
        text = cached.response
        chunk_size = 120
        for i in range(0, len(text), chunk_size):
            yield f"data: {json.dumps({'type': 'text', 'text': text[i : i + chunk_size]})}\n\n"
            await asyncio.sleep(0.005)

        analysis_id = save_analysis(
            db, session_id, prompt_id, inputs_dict,
            cached.response, model,
            cached.input_tokens, cached.output_tokens, cached.cost_usd,
            from_cache=True,
        )
        yield f"data: {json.dumps({'type': 'done', 'analysis_id': analysis_id, 'from_cache': True, 'input_tokens': cached.input_tokens, 'output_tokens': cached.output_tokens, 'cost_usd': cached.cost_usd})}\n\n"
        return

    # --- Live stream from Claude ---
    full_response = ""
    input_tokens = 0
    output_tokens = 0

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        async with client.messages.stream(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": filled_prompt}],
        ) as stream:
            async for text in stream.text_stream:
                full_response += text
                yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"

            final_msg = await stream.get_final_message()
            input_tokens = final_msg.usage.input_tokens
            output_tokens = final_msg.usage.output_tokens

        cost_usd = estimate_cost(model, input_tokens, output_tokens)

        store_cache(
            db, cache_key, prompt_id, model,
            full_response, input_tokens, output_tokens, cost_usd,
        )

        analysis_id = save_analysis(
            db, session_id, prompt_id, inputs_dict,
            full_response, model,
            input_tokens, output_tokens, cost_usd,
            from_cache=False,
        )

        yield f"data: {json.dumps({'type': 'done', 'analysis_id': analysis_id, 'from_cache': False, 'input_tokens': input_tokens, 'output_tokens': output_tokens, 'cost_usd': cost_usd})}\n\n"

    except anthropic.AuthenticationError:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Invalid API key. Please check your Anthropic API key.'})}\n\n"
    except anthropic.RateLimitError:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Rate limit exceeded. Please wait a moment and try again.'})}\n\n"
    except anthropic.APIError as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Anthropic API error: {str(e)}'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Unexpected error: {str(e)}'})}\n\n"


async def stream_feedback(
    api_key: str,
    model: str,
    analysis_id: str,
    current_analysis: str,
    new_message: str,
    db: DBSession,
) -> AsyncGenerator[str, None]:
    """Stream a revised analysis based on user feedback, then persist both messages."""
    system_prompt = (
        "You are a McKinsey-grade strategic analyst. "
        "The user is providing feedback or corrections to their analysis. "
        "Incorporate all feedback and return a complete, professionally revised analysis "
        "in exactly the same format and structure as the original. "
        "If numbers or assumptions are corrected, update all dependent calculations and projections."
    )

    messages = [{
        "role": "user",
        "content": (
            f"Here is my current analysis:\n\n{current_analysis}\n\n"
            f"---\n\n"
            f"Feedback/Corrections: {new_message}\n\n"
            f"Please revise the analysis to incorporate this feedback. "
            f"Return the complete revised analysis."
        ),
    }]

    full_response = ""
    input_tokens = 0
    output_tokens = 0

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        async with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                full_response += text
                yield f"data: {json.dumps({'type': 'text', 'text': text})}\n\n"

            final_msg = await stream.get_final_message()
            input_tokens = final_msg.usage.input_tokens
            output_tokens = final_msg.usage.output_tokens

        cost_usd = estimate_cost(model, input_tokens, output_tokens)

        # Persist user feedback message
        db.add(FeedbackMessage(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            role="user",
            content=new_message,
        ))

        # Persist assistant revision
        db.add(FeedbackMessage(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            role="assistant",
            content=full_response,
        ))

        # Update the analysis record with the revised output
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.output = full_response

        db.commit()

        yield f"data: {json.dumps({'type': 'done', 'input_tokens': input_tokens, 'output_tokens': output_tokens, 'cost_usd': cost_usd})}\n\n"

    except anthropic.AuthenticationError:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Invalid API key. Please check your Anthropic API key.'})}\n\n"
    except anthropic.RateLimitError:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Rate limit exceeded. Please wait a moment and try again.'})}\n\n"
    except anthropic.APIError as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Anthropic API error: {str(e)}'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Unexpected error: {str(e)}'})}\n\n"


async def analyze_single(
    api_key: str,
    model: str,
    prompt_id: str,
    filled_prompt: str,
    inputs_dict: dict,
    db: DBSession,
    session_id: Optional[str] = None,
) -> dict:
    cache_key = make_cache_key(model, prompt_id, inputs_dict)

    cached = get_cached_response(db, cache_key)
    if cached:
        analysis_id = save_analysis(
            db, session_id, prompt_id, inputs_dict,
            cached.response, model,
            cached.input_tokens, cached.output_tokens, cached.cost_usd,
            from_cache=True,
        )
        return {
            "prompt_id": prompt_id, "output": cached.response,
            "from_cache": True, "analysis_id": analysis_id,
            "input_tokens": cached.input_tokens, "output_tokens": cached.output_tokens,
            "cost_usd": cached.cost_usd,
        }

    client = anthropic.AsyncAnthropic(api_key=api_key)
    msg = await client.messages.create(
        model=model, max_tokens=4096,
        messages=[{"role": "user", "content": filled_prompt}],
    )
    full_response = msg.content[0].text
    input_tokens = msg.usage.input_tokens
    output_tokens = msg.usage.output_tokens
    cost_usd = estimate_cost(model, input_tokens, output_tokens)

    store_cache(db, cache_key, prompt_id, model, full_response, input_tokens, output_tokens, cost_usd)
    analysis_id = save_analysis(
        db, session_id, prompt_id, inputs_dict,
        full_response, model, input_tokens, output_tokens, cost_usd, from_cache=False,
    )
    return {
        "prompt_id": prompt_id, "output": full_response,
        "from_cache": False, "analysis_id": analysis_id,
        "input_tokens": input_tokens, "output_tokens": output_tokens, "cost_usd": cost_usd,
    }
