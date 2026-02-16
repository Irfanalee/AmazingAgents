#!/usr/bin/env python3
"""Quick test to verify GitHub token works."""

import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token or token == "your_github_personal_access_token_here":
    print("❌ GITHUB_TOKEN not set in .env file")
    print("\n📝 Steps to fix:")
    print("   1. Visit: https://github.com/settings/tokens")
    print("   2. Generate new token (classic) with 'public_repo' scope")
    print("   3. Copy the token (starts with ghp_)")
    print("   4. Replace GITHUB_TOKEN value in .env file")
    exit(1)

print(f"🔍 Testing GitHub token...")
print(f"   Token: {token[:10]}... (hidden)")

try:
    client = Github(token)
    user = client.get_user()
    print(f"✅ GitHub token is valid!")
    print(f"   Authenticated as: {user.login}")
    print(f"   Name: {user.name or 'Not set'}")
    
    # Test fetching a public repo
    repo = client.get_repo("facebook/react")
    print(f"✅ Can access public repositories")
    print(f"   Tested with: {repo.full_name}")
    
    print("\n✨ GitHub token is working correctly!")
    
except Exception as e:
    print(f"❌ GitHub token is invalid or expired")
    print(f"   Error: {e}")
    print("\n📝 Generate a new token:")
    print("   https://github.com/settings/tokens")
    exit(1)
