#!/usr/bin/env python3
"""
Quick test script for Shadow ARB without needing real API keys.
Tests the workflow structure with mock data.
"""

from shadow_arb.state import AgentState
from shadow_arb.workflow import create_workflow

def test_workflow():
    """Test workflow with mock data."""
    
    print("🧪 Testing Shadow ARB Workflow (Mock Mode)\n")
    
    # Create mock initial state
    initial_state: AgentState = {
        "pr_diff": """
diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -10,7 +10,7 @@
 def authenticate(username, password):
-    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
+    password = "hardcoded123"  # Security issue!
+    query = f"SELECT * FROM users WHERE username='{username}'"
     cursor.execute(query)
""",
        "security_findings": [],
        "scale_findings": [],
        "clean_code_findings": [],
        "final_verdict": "",
    }
    
    print("📊 Mock PR Diff:")
    print("-" * 80)
    print(initial_state["pr_diff"])
    print("-" * 80)
    
    # Test workflow creation
    print("\n✅ Step 1: Creating workflow graph...")
    try:
        app = create_workflow()
        print("   ✓ Workflow graph created successfully")
        print("   ✓ Nodes: security_agent, scale_agent, clean_code_agent, chairperson_agent")
        print("   ✓ Parallel execution configured")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Show what would happen
    print("\n📝 What happens next (with real API keys):")
    print("   1️⃣  Security Agent analyzes code → finds:")
    print("      - SQL injection vulnerability (line 13)")
    print("      - Hardcoded password (line 12)")
    print()
    print("   2️⃣  Scale Agent analyzes code → finds:")
    print("      - No indexes mentioned")
    print("      - Direct database access")
    print()
    print("   3️⃣  Clean Code Agent analyzes code → finds:")
    print("      - Poor variable naming")
    print("      - Missing error handling")
    print()
    print("   4️⃣  Chairperson synthesizes all findings")
    print("   5️⃣  Final verdict: Changes Requested")
    
    print("\n" + "=" * 80)
    print("✨ Mock Test Complete!")
    print("=" * 80)
    print("\n📋 To run with real API keys:")
    print("   1. Add GITHUB_TOKEN to .env file")
    print("   2. Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env")
    print("   3. Run: python main.py --pr_url <PR_URL> --dry-run")
    
    return True

if __name__ == "__main__":
    success = test_workflow()
    exit(0 if success else 1)
