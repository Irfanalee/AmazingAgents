#!/usr/bin/env python3
"""
Shadow ARB - AI-Powered Architecture Review Board
Main entry point for executing PR reviews.

Usage:
    python main.py --pr_url https://github.com/owner/repo/pull/123
    python main.py --pr_url https://github.com/owner/repo/pull/123 --dry-run
"""

import argparse
import sys
from shadow_arb.config import Config
from shadow_arb.github_client import GitHubClient
from shadow_arb.workflow import run_review


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Shadow ARB - Automated AI Code Review for Pull Requests"
    )
    parser.add_argument(
        "--pr_url",
        type=str,
        required=True,
        help="Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run review without posting comment to GitHub"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        print("🔧 Validating configuration...")
        Config.validate()
        print("✅ Configuration valid")
        
        # Initialize GitHub client
        print(f"🔍 Fetching PR diff from: {args.pr_url}")
        github_client = GitHubClient()
        pr_diff = github_client.get_pr_diff(args.pr_url)
        
        if not pr_diff.strip():
            print("⚠️  Warning: PR diff is empty. Nothing to review.")
            sys.exit(0)
        
        print(f"📄 Fetched diff ({len(pr_diff)} characters)")
        
        # Execute the review workflow
        print("🤖 Starting Shadow ARB review workflow...")
        print("   ├─ Security Agent (parallel)")
        print("   ├─ Scale Agent (parallel)")
        print("   ├─ Clean Code Agent (parallel)")
        print("   └─ Chairperson Agent (synthesis)")
        print()
        
        final_verdict = run_review(pr_diff)
        
        print("=" * 80)
        print("REVIEW COMPLETE")
        print("=" * 80)
        print(final_verdict)
        print("=" * 80)
        
        # Post comment to GitHub (unless dry-run)
        if args.dry_run:
            print("\n🏃 Dry-run mode: Skipping GitHub comment posting")
        else:
            print("\n📤 Posting review to GitHub...")
            github_client.post_review_comment(args.pr_url, final_verdict)
        
        print("\n✨ Shadow ARB review completed successfully")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
