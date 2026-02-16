#!/usr/bin/env python3
"""
Estimate cost for a specific GitHub PR before reviewing.
Usage: python estimate_pr_cost.py --pr_url <URL>
"""

import argparse
import os
from dotenv import load_dotenv
from shadow_arb.github_client import GitHubClient
from cost_estimator import estimate_review_cost, print_cost_report, compare_models

load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="Estimate API costs for reviewing a specific PR"
    )
    parser.add_argument(
        "--pr_url",
        type=str,
        required=True,
        help="GitHub PR URL"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to estimate for (default: gpt-4o)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare costs across all models"
    )
    
    args = parser.parse_args()
    
    try:
        print("🔍 Fetching PR data...")
        
        # Check if GitHub token is set
        if not os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN") == "your_github_personal_access_token_here":
            print("\n⚠️  Warning: GITHUB_TOKEN not configured")
            print("   Set it in .env to fetch real PR data")
            print("   For now, using example estimations...\n")
            
            # Show example costs
            from cost_estimator import estimate_from_pr_size
            print("\nExample cost estimations:")
            estimate_from_pr_size(10, args.model)
            estimate_from_pr_size(50, args.model)
            estimate_from_pr_size(200, args.model)
            return
        
        # Fetch PR diff
        github_client = GitHubClient()
        pr_diff = github_client.get_pr_diff(args.pr_url)
        
        print(f"✅ PR data fetched successfully")
        print(f"   Diff size: {len(pr_diff):,} characters\n")
        
        # Estimate cost
        cost_data = estimate_review_cost(pr_diff, args.model)
        print_cost_report(cost_data)
        
        # Compare models if requested
        if args.compare:
            compare_models(pr_diff)
        
        # Show approval message
        print(f"\n❓ Proceed with review?")
        print(f"   Estimated cost: ${cost_data['totals']['total_cost']:.4f}")
        print(f"   Run: python main.py --pr_url {args.pr_url} --dry-run")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
