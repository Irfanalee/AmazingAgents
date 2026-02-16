#!/usr/bin/env python3
"""
Cost estimator for Shadow ARB reviews.
Analyzes token usage and API costs before running reviews.
"""

import tiktoken
from shadow_arb.prompts import (
    SECURITY_AGENT_PROMPT,
    SCALE_AGENT_PROMPT,
    CLEAN_CODE_AGENT_PROMPT,
    CHAIRPERSON_PROMPT,
)

# Pricing as of Jan 2026 (per 1M tokens)
PRICING = {
    "gpt-4o": {
        "input": 2.50,   # $2.50 per 1M input tokens
        "output": 10.00,  # $10.00 per 1M output tokens
    },
    "gpt-4o-mini": {
        "input": 0.15,   # $0.15 per 1M input tokens
        "output": 0.60,  # $0.60 per 1M output tokens
    },
    "claude-3-5-sonnet-20241022": {
        "input": 3.00,   # $3.00 per 1M input tokens
        "output": 15.00, # $15.00 per 1M output tokens
    },
    "claude-3-haiku-20240307": {
        "input": 0.25,   # $0.25 per 1M input tokens
        "output": 1.25,  # $1.25 per 1M output tokens
    },
}


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in text using tiktoken."""
    try:
        # Use cl100k_base encoding (used by GPT-4, GPT-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except:
        # Fallback: rough approximation (1 token ≈ 4 characters)
        return len(text) // 4


def estimate_review_cost(pr_diff: str, model: str = "gpt-4o") -> dict:
    """
    Estimate the cost of reviewing a PR.
    
    Args:
        pr_diff: The code changes to review
        model: LLM model to use
        
    Returns:
        Dictionary with cost breakdown
    """
    
    # Count tokens in PR diff
    diff_tokens = count_tokens(pr_diff)
    
    # Count tokens in system prompts
    security_prompt_tokens = count_tokens(SECURITY_AGENT_PROMPT)
    scale_prompt_tokens = count_tokens(SCALE_AGENT_PROMPT)
    clean_code_prompt_tokens = count_tokens(CLEAN_CODE_AGENT_PROMPT)
    chairperson_prompt_tokens = count_tokens(CHAIRPERSON_PROMPT)
    
    # Calculate input tokens per agent (prompt + diff)
    security_input = security_prompt_tokens + diff_tokens
    scale_input = scale_prompt_tokens + diff_tokens
    clean_code_input = clean_code_prompt_tokens + diff_tokens
    
    # Chairperson gets findings (estimate ~500 tokens for all findings)
    estimated_findings_tokens = 500
    chairperson_input = chairperson_prompt_tokens + estimated_findings_tokens
    
    # Total input tokens
    total_input_tokens = (
        security_input + scale_input + clean_code_input + chairperson_input
    )
    
    # Estimate output tokens (conservative estimate)
    # Each agent typically returns 100-500 tokens of findings
    security_output = 300
    scale_output = 300
    clean_code_output = 300
    chairperson_output = 800  # Longer synthesis
    
    total_output_tokens = (
        security_output + scale_output + clean_code_output + chairperson_output
    )
    
    # Get pricing for model
    if model not in PRICING:
        model = "gpt-4o"  # Default fallback
    
    pricing = PRICING[model]
    
    # Calculate costs (convert from per-1M to actual cost)
    input_cost = (total_input_tokens / 1_000_000) * pricing["input"]
    output_cost = (total_output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "model": model,
        "pr_diff_size": len(pr_diff),
        "pr_diff_tokens": diff_tokens,
        "breakdown": {
            "security_agent": {
                "input_tokens": security_input,
                "output_tokens": security_output,
                "cost": (security_input / 1_000_000 * pricing["input"]) +
                        (security_output / 1_000_000 * pricing["output"])
            },
            "scale_agent": {
                "input_tokens": scale_input,
                "output_tokens": scale_output,
                "cost": (scale_input / 1_000_000 * pricing["input"]) +
                        (scale_output / 1_000_000 * pricing["output"])
            },
            "clean_code_agent": {
                "input_tokens": clean_code_input,
                "output_tokens": clean_code_output,
                "cost": (clean_code_input / 1_000_000 * pricing["input"]) +
                        (clean_code_output / 1_000_000 * pricing["output"])
            },
            "chairperson_agent": {
                "input_tokens": chairperson_input,
                "output_tokens": chairperson_output,
                "cost": (chairperson_input / 1_000_000 * pricing["input"]) +
                        (chairperson_output / 1_000_000 * pricing["output"])
            },
        },
        "totals": {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        },
        "pricing": pricing,
    }


def print_cost_report(cost_data: dict):
    """Print a formatted cost report."""
    
    print("=" * 80)
    print("💰 SHADOW ARB COST ESTIMATION")
    print("=" * 80)
    
    print(f"\n📊 PR Diff Analysis:")
    print(f"   Size: {cost_data['pr_diff_size']:,} characters")
    print(f"   Tokens: {cost_data['pr_diff_tokens']:,} tokens")
    print(f"   Model: {cost_data['model']}")
    
    print(f"\n🤖 Per-Agent Breakdown:")
    for agent_name, agent_data in cost_data['breakdown'].items():
        print(f"\n   {agent_name.replace('_', ' ').title()}:")
        print(f"      Input:  {agent_data['input_tokens']:,} tokens")
        print(f"      Output: {agent_data['output_tokens']:,} tokens")
        print(f"      Cost:   ${agent_data['cost']:.4f}")
    
    totals = cost_data['totals']
    print(f"\n💵 Total Cost:")
    print(f"   Input:  {totals['input_tokens']:,} tokens → ${totals['input_cost']:.4f}")
    print(f"   Output: {totals['output_tokens']:,} tokens → ${totals['output_cost']:.4f}")
    print(f"   ─────────────────────────────────────")
    print(f"   TOTAL:  {totals['total_tokens']:,} tokens → ${totals['total_cost']:.4f}")
    
    print(f"\n📈 Cost Projections:")
    reviews_per_dollar = 1 / totals['total_cost'] if totals['total_cost'] > 0 else 0
    print(f"   10 reviews:   ${totals['total_cost'] * 10:.2f}")
    print(f"   100 reviews:  ${totals['total_cost'] * 100:.2f}")
    print(f"   1000 reviews: ${totals['total_cost'] * 1000:.2f}")
    print(f"   You can do ~{reviews_per_dollar:.0f} reviews per $1")
    
    print("\n" + "=" * 80)


def compare_models(pr_diff: str):
    """Compare costs across different models."""
    
    print("\n🔄 MODEL COMPARISON")
    print("=" * 80)
    
    results = []
    for model in PRICING.keys():
        cost_data = estimate_review_cost(pr_diff, model)
        results.append((model, cost_data['totals']['total_cost']))
    
    # Sort by cost
    results.sort(key=lambda x: x[1])
    
    print(f"{'Model':<40} {'Cost per Review':<20} {'Savings'}")
    print("-" * 80)
    
    baseline_cost = results[-1][1]  # Most expensive
    
    for model, cost in results:
        savings = ((baseline_cost - cost) / baseline_cost * 100) if baseline_cost > 0 else 0
        savings_str = f"(-{savings:.0f}%)" if savings > 0 else ""
        print(f"{model:<40} ${cost:.4f}              {savings_str}")
    
    print("=" * 80)
    
    # Recommendations
    cheapest = results[0]
    print(f"\n💡 Recommendation:")
    print(f"   Cheapest: {cheapest[0]} at ${cheapest[1]:.4f} per review")
    print(f"   That's ${cheapest[1] * 100:.2f} for 100 reviews")


def estimate_from_pr_size(lines_changed: int, model: str = "gpt-4o"):
    """Quick estimation based on lines changed."""
    
    # Rough estimate: 1 line of code ≈ 10 tokens (with context)
    estimated_diff_tokens = lines_changed * 10
    
    # Average system prompt size
    avg_prompt_tokens = 500
    
    # Estimate per agent
    per_agent_input = avg_prompt_tokens + estimated_diff_tokens
    total_input = per_agent_input * 3 + 500  # 3 agents + chairperson
    
    # Output estimate
    total_output = 1700  # Conservative estimate
    
    pricing = PRICING.get(model, PRICING["gpt-4o"])
    
    input_cost = (total_input / 1_000_000) * pricing["input"]
    output_cost = (total_output / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    print("\n📏 QUICK ESTIMATION (Based on Lines Changed)")
    print("=" * 80)
    print(f"   Lines changed: {lines_changed}")
    print(f"   Estimated tokens: ~{total_input + total_output:,}")
    print(f"   Estimated cost: ${total_cost:.4f}")
    print(f"   For 100 PRs: ${total_cost * 100:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    # Example PR diff sizes
    print("\n" + "=" * 80)
    print("SHADOW ARB COST CALCULATOR")
    print("=" * 80)
    
    # Small PR (10 lines)
    print("\n📦 Small PR (10 lines changed):")
    estimate_from_pr_size(10, "gpt-4o")
    
    # Medium PR (50 lines)
    print("\n📦 Medium PR (50 lines changed):")
    estimate_from_pr_size(50, "gpt-4o")
    
    # Large PR (200 lines)
    print("\n📦 Large PR (200 lines changed):")
    estimate_from_pr_size(200, "gpt-4o")
    
    # Model comparison for medium PR
    mock_diff = "+" + ("x" * 50 + "\n") * 50  # ~50 lines
    compare_models(mock_diff)
    
    print("\n💡 Cost Optimization Tips:")
    print("   1. Use gpt-4o-mini for development/testing (10x cheaper)")
    print("   2. Enable caching (future feature) to reduce repeated analysis")
    print("   3. Review only changed files, not entire codebase")
    print("   4. Use incremental reviews for subsequent commits")
    print("   5. Batch reviews during off-peak hours")
    
    print("\n📊 Real-world scenario (50 PRs/month, average 50 lines each):")
    medium_cost_gpt4o = estimate_review_cost(mock_diff, "gpt-4o")['totals']['total_cost']
    medium_cost_mini = estimate_review_cost(mock_diff, "gpt-4o-mini")['totals']['total_cost']
    
    print(f"   GPT-4o:      50 reviews × ${medium_cost_gpt4o:.4f} = ${medium_cost_gpt4o * 50:.2f}/month")
    print(f"   GPT-4o-mini: 50 reviews × ${medium_cost_mini:.4f} = ${medium_cost_mini * 50:.2f}/month")
    print(f"   Savings with mini: ${(medium_cost_gpt4o - medium_cost_mini) * 50:.2f}/month")
