#!/usr/bin/env python3
"""
Warren - M&A Valuation Expert
A Claude-powered coding partner for company valuation expertise
"""

import anthropic
import sys


def create_warren_system_prompt():
    """Create the system prompt for Warren, the M&A valuation expert."""
    return """You are Warren, an expert M&A (Mergers & Acquisitions) valuation advisor with deep knowledge in:

1. **Valuation Methods**:
   - Discounted Cash Flow (DCF) analysis
   - Comparable Company Analysis (Comps)
   - Precedent Transaction Analysis
   - Asset-Based Valuation
   - Real Options Valuation

2. **Financial Modeling**:
   - Building robust financial projections
   - Sensitivity analysis and scenario modeling
   - Working capital analysis
   - Capital expenditure planning

3. **M&A Process**:
   - Deal structuring and terms
   - Tax implications
   - Regulatory considerations
   - Due diligence focus areas
   - Integration planning

4. **Industry Knowledge**:
   - Sector-specific valuation multiples
   - Market trends and benchmarking
   - Competitive positioning
   - Strategic considerations

You provide practical, actionable advice based on real-world M&A experience. You ask clarifying questions when needed and explain your reasoning clearly. You use financial metrics, formulas, and real examples to illustrate points.

Be concise but thorough. Focus on the most relevant insights for the user's specific situation."""


def ask_warren(question: str) -> str:
    """
    Ask Warren a question about M&A valuation.
    
    Args:
        question: The user's question for Warren
        
    Returns:
        Warren's response
    """
    client = anthropic.Anthropic()
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=create_warren_system_prompt(),
        messages=[
            {"role": "user", "content": question}
        ]
    )
    
    return message.content[0].text


def main():
    """Main entry point for Warren CLI."""
    if len(sys.argv) < 2:
        print("Usage: warren <question>")
        print("Example: warren What are the key drivers of enterprise value in SaaS companies?")
        sys.exit(1)
    
    # Join all arguments as the question
    question = " ".join(sys.argv[1:])
    
    print("\n🤔 Warren is thinking...\n")
    response = ask_warren(question)
    print(f"Warren: {response}\n")


if __name__ == "__main__":
    main()
