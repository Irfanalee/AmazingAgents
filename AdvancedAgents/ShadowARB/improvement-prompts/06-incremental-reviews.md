# Prompt: Implement Incremental Reviews (Only New Commits)

## Context
You built the Shadow ARB system that reviews entire PRs. Currently, when new commits are pushed to an existing PR, the system re-reviews ALL code changes from the beginning. This:
- Wastes API calls on already-reviewed code
- Slows down feedback for developers
- Duplicates findings from previous reviews
- Makes it hard to track which issues were introduced in new commits

## Your Task
Implement incremental review capability that:
1. Tracks the last reviewed commit SHA for each PR
2. Generates diffs for only new commits since last review
3. Aggregates findings across reviews
4. Handles force-pushes and rebases gracefully
5. Provides clear indication of new vs. existing issues

## Implementation Requirements

### 1. Create Review State Tracker (`shadow_arb/review_state.py`)
Track review history for PRs:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
import json
from pathlib import Path

@dataclass
class ReviewSnapshot:
    """Represents a single review execution."""
    commit_sha: str
    reviewed_at: datetime
    findings: Dict[str, List[str]]  # agent_name -> findings
    verdict: str
    
    def to_dict(self) -> dict:
        return {
            'commit_sha': self.commit_sha,
            'reviewed_at': self.reviewed_at.isoformat(),
            'findings': self.findings,
            'verdict': self.verdict
        }

class ReviewStateManager:
    """Manages review state across PR updates."""
    
    def __init__(self, storage_backend='file'):
        # Can be 'file' or 'database'
        self.backend = storage_backend
        self.state_dir = Path('.shadow-arb-state')
        self.state_dir.mkdir(exist_ok=True)
    
    def get_last_review(self, pr_url: str) -> Optional[ReviewSnapshot]:
        """Get the most recent review for a PR."""
        state_file = self._get_state_file(pr_url)
        if not state_file.exists():
            return None
        
        with open(state_file, 'r') as f:
            data = json.load(f)
        
        if not data.get('reviews'):
            return None
        
        last = data['reviews'][-1]
        return ReviewSnapshot(
            commit_sha=last['commit_sha'],
            reviewed_at=datetime.fromisoformat(last['reviewed_at']),
            findings=last['findings'],
            verdict=last['verdict']
        )
    
    def save_review(
        self, 
        pr_url: str, 
        snapshot: ReviewSnapshot
    ):
        """Save a new review snapshot."""
        state_file = self._get_state_file(pr_url)
        
        # Load existing state
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
        else:
            data = {'pr_url': pr_url, 'reviews': []}
        
        # Append new review
        data['reviews'].append(snapshot.to_dict())
        
        # Save
        with open(state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_all_reviews(self, pr_url: str) -> List[ReviewSnapshot]:
        """Get all review history for a PR."""
        # Return chronological list of reviews
        ...
    
    def _get_state_file(self, pr_url: str) -> Path:
        """Generate state file path from PR URL."""
        # Hash PR URL to filename
        import hashlib
        url_hash = hashlib.sha256(pr_url.encode()).hexdigest()[:16]
        return self.state_dir / f"{url_hash}.json"
```

### 2. Create Incremental Diff Generator (`shadow_arb/incremental_diff.py`)
Generate diffs for only new commits:

```python
from github import Github
from typing import Tuple, Optional

class IncrementalDiffGenerator:
    """Generates diffs for only new commits in a PR."""
    
    def __init__(self, vcs_client):
        self.vcs_client = vcs_client
    
    def get_incremental_diff(
        self,
        pr_url: str,
        last_reviewed_sha: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Get diff for new commits only.
        
        Args:
            pr_url: Pull request URL
            last_reviewed_sha: Last commit SHA that was reviewed
        
        Returns:
            Tuple of (incremental_diff, current_head_sha)
        """
        owner, repo_name, pr_number = self.vcs_client.parse_pr_url(pr_url)
        
        # Get PR details
        repo = self.vcs_client.client.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        current_head_sha = pr.head.sha
        
        # If no previous review, return full diff
        if not last_reviewed_sha:
            return self.vcs_client.get_pr_diff(pr_url), current_head_sha
        
        # Check if last_reviewed_sha still exists in PR history
        if not self._sha_in_pr_history(pr, last_reviewed_sha):
            # Force push or rebase detected - review full diff
            print("⚠️  Force push detected - reviewing full PR")
            return self.vcs_client.get_pr_diff(pr_url), current_head_sha
        
        # Generate diff from last_reviewed_sha to current HEAD
        comparison = repo.compare(last_reviewed_sha, current_head_sha)
        
        # Build incremental diff
        diff_parts = []
        for file in comparison.files:
            diff_parts.append(f"File: {file.filename}")
            diff_parts.append(f"Status: {file.status}")
            diff_parts.append(f"Changes: +{file.additions} -{file.deletions}")
            diff_parts.append("-" * 80)
            if file.patch:
                diff_parts.append(file.patch)
            diff_parts.append("\n")
        
        incremental_diff = "\n".join(diff_parts)
        
        if not incremental_diff.strip():
            print("ℹ️  No new changes since last review")
            return "", current_head_sha
        
        print(f"📊 Incremental diff: {len(comparison.files)} files changed")
        return incremental_diff, current_head_sha
    
    def _sha_in_pr_history(self, pr, sha: str) -> bool:
        """Check if commit SHA exists in PR's commit history."""
        try:
            commits = list(pr.get_commits())
            return any(commit.sha == sha for commit in commits)
        except:
            return False
```

### 3. Create Findings Aggregator (`shadow_arb/findings_aggregator.py`)
Combine findings across reviews:

```python
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class AggregatedFindings:
    """Findings aggregated across multiple reviews."""
    new_findings: Dict[str, List[str]]      # From current review
    existing_findings: Dict[str, List[str]]  # From previous reviews
    resolved_findings: Dict[str, List[str]]  # Were in previous, not in current
    
    def get_total_count(self) -> int:
        """Total unique findings across all reviews."""
        total = 0
        for findings in self.new_findings.values():
            total += len(findings)
        for findings in self.existing_findings.values():
            total += len(findings)
        return total

class FindingsAggregator:
    """Aggregates findings across incremental reviews."""
    
    @staticmethod
    def aggregate(
        current_findings: Dict[str, List[str]],
        previous_snapshots: List[ReviewSnapshot]
    ) -> AggregatedFindings:
        """
        Combine current findings with historical findings.
        
        Logic:
        - New: In current but not in any previous
        - Existing: In current AND in previous
        - Resolved: In previous but not in current
        """
        # Aggregate all previous findings
        all_previous = {}
        for snapshot in previous_snapshots:
            for agent, findings in snapshot.findings.items():
                if agent not in all_previous:
                    all_previous[agent] = set()
                all_previous[agent].update(findings)
        
        # Categorize current findings
        new_findings = {}
        existing_findings = {}
        
        for agent, findings in current_findings.items():
            new_findings[agent] = []
            existing_findings[agent] = []
            
            previous_set = all_previous.get(agent, set())
            
            for finding in findings:
                if finding in previous_set:
                    existing_findings[agent].append(finding)
                else:
                    new_findings[agent].append(finding)
        
        # Find resolved issues
        resolved_findings = {}
        current_all = {
            agent: set(findings) 
            for agent, findings in current_findings.items()
        }
        
        for agent, previous_set in all_previous.items():
            current_set = current_all.get(agent, set())
            resolved = list(previous_set - current_set)
            if resolved:
                resolved_findings[agent] = resolved
        
        return AggregatedFindings(
            new_findings=new_findings,
            existing_findings=existing_findings,
            resolved_findings=resolved_findings
        )
```

### 4. Update Chairperson Prompt (`shadow_arb/prompts.py`)
Add incremental review awareness:

```python
CHAIRPERSON_INCREMENTAL_PROMPT = """You are the Chairperson synthesizing an INCREMENTAL code review.

**Context:**
This PR was previously reviewed. You are now reviewing ONLY the new commits since the last review.

**Findings Breakdown:**
- **NEW Findings**: Issues introduced in new commits (prioritize these)
- **EXISTING Findings**: Issues from previous reviews that still exist
- **RESOLVED Findings**: Issues from previous reviews that have been fixed

**Instructions:**
1. Focus primarily on NEW findings from the incremental diff
2. Acknowledge RESOLVED findings positively (praise improvements)
3. Briefly mention EXISTING findings if still critical
4. Provide incremental verdict:
   - ✅ **Approved** - No new issues, or only minor new issues
   - 💬 **Approved with Comments** - Some new issues but not blocking
   - ❌ **Changes Requested** - Critical new issues introduced

**Output Format:**
```markdown
## 🔄 Incremental Review (Commit: {current_sha})

### 🆕 New Issues in This Update ({count})
[List new findings by agent]

### ✅ Resolved Issues ({count})
[Celebrate fixed issues]

### 📌 Existing Issues (Still Present)
[Brief reminder of previous findings]

---

### Verdict: [Approved | Approved with Comments | Changes Requested]
[Focus on the incremental changes]
```
"""
```

### 5. Update Workflow (`shadow_arb/workflow.py`)
Add incremental review mode:

```python
def run_review(
    pr_url: str,
    incremental: bool = True,
    vcs_client = None
) -> str:
    """Execute review with optional incremental mode."""
    
    # Get review state
    state_manager = ReviewStateManager()
    last_review = state_manager.get_last_review(pr_url)
    
    # Generate diff
    if incremental and last_review:
        diff_generator = IncrementalDiffGenerator(vcs_client)
        pr_diff, current_sha = diff_generator.get_incremental_diff(
            pr_url,
            last_review.commit_sha
        )
        
        if not pr_diff:
            return "No new changes since last review. Skipping."
        
        print(f"📊 Incremental review: {last_review.commit_sha[:7]} → {current_sha[:7]}")
    else:
        pr_diff = vcs_client.get_pr_diff(pr_url)
        current_sha = get_current_head_sha(pr_url, vcs_client)
        print("📊 Full PR review")
    
    # Run workflow
    initial_state = {
        "pr_diff": pr_diff,
        "security_findings": [],
        # ... other findings
    }
    
    app = create_workflow()
    final_state = app.invoke(initial_state)
    
    # Aggregate findings if incremental
    if incremental and last_review:
        all_previous = state_manager.get_all_reviews(pr_url)
        aggregated = FindingsAggregator.aggregate(
            current_findings={
                'security': final_state['security_findings'],
                'scale': final_state['scale_findings'],
                'clean_code': final_state['clean_code_findings'],
            },
            previous_snapshots=all_previous
        )
        
        # Generate incremental verdict
        final_verdict = generate_incremental_verdict(aggregated, current_sha)
    else:
        final_verdict = final_state['final_verdict']
    
    # Save review state
    snapshot = ReviewSnapshot(
        commit_sha=current_sha,
        reviewed_at=datetime.now(),
        findings={
            'security': final_state['security_findings'],
            'scale': final_state['scale_findings'],
            'clean_code': final_state['clean_code_findings'],
        },
        verdict=final_verdict
    )
    state_manager.save_review(pr_url, snapshot)
    
    return final_verdict
```

### 6. Update Main Entry Point (`main.py`)
Add incremental review flag:

```python
parser.add_argument(
    '--incremental',
    action='store_true',
    default=True,
    help='Only review new commits (default: True)'
)

parser.add_argument(
    '--full',
    action='store_true',
    help='Force full PR review, ignoring previous reviews'
)

def main():
    # ... existing code ...
    
    # Determine review mode
    incremental = args.incremental and not args.full
    
    # Run review
    final_verdict = run_review(
        pr_url=args.pr_url,
        incremental=incremental,
        vcs_client=vcs_client
    )
```

### 7. Add Review History CLI (`main.py`)
View review history for a PR:

```python
# Add to subparsers
history_parser = subparsers.add_parser('history')
history_parser.add_argument('--pr_url', required=True)
history_parser.add_argument('--format', choices=['table', 'json'], default='table')

def handle_history_command(args):
    state_manager = ReviewStateManager()
    reviews = state_manager.get_all_reviews(args.pr_url)
    
    if args.format == 'table':
        print(f"\n📜 Review History for PR: {args.pr_url}\n")
        for i, review in enumerate(reviews, 1):
            print(f"{i}. Commit: {review.commit_sha[:7]}")
            print(f"   Reviewed: {review.reviewed_at}")
            print(f"   Findings: {sum(len(f) for f in review.findings.values())}")
            print()
    else:
        print(json.dumps([r.to_dict() for r in reviews], indent=2))
```

### 8. Handle Force Pushes (`shadow_arb/incremental_diff.py`)
Detect and handle rebases:

```python
def detect_force_push(
    pr_url: str,
    last_reviewed_sha: str
) -> bool:
    """
    Detect if PR was force-pushed or rebased.
    
    Returns:
        True if force push detected
    """
    # Check if last_reviewed_sha exists in current PR history
    # If not, it was force-pushed
    ...
    
def handle_force_push(pr_url: str):
    """
    Handle force push scenario.
    
    Options:
    1. Review full PR again
    2. Prompt user for decision
    3. Try to map old commits to new commits (advanced)
    """
    print("⚠️  Force push detected!")
    print("    Previous review history may not apply to current commits.")
    print("    Running full PR review...")
```

### 9. Add Database Storage Option (`shadow_arb/review_state_db.py`)
Store review state in PostgreSQL:

```python
# If database is available, store review history there instead of files
class ReviewStateDatabase:
    """Database-backed review state storage."""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    # Implement same interface as ReviewStateManager
    # Store in review_history table with commit_sha tracking
```

### 10. Update Configuration (`shadow_arb/config.py`)
Add incremental review settings:

```python
# Incremental Review Settings
ENABLE_INCREMENTAL_REVIEW: bool = os.getenv(
    "ENABLE_INCREMENTAL_REVIEW", 
    "true"
).lower() == "true"

REVIEW_STATE_BACKEND: str = os.getenv(
    "REVIEW_STATE_BACKEND", 
    "file"
)  # 'file' or 'database'
```

## Technical Constraints
- Must handle force pushes gracefully (don't crash)
- Commit SHA tracking must be reliable
- Findings comparison should be fuzzy (minor text differences OK)
- Support both file-based and database storage
- Backward compatible (can still do full reviews)
- Clear indicators in review comment about incremental vs. full
- Preserve review history even after PR is merged

## Expected Workflow

**First Review:**
```bash
python main.py review --pr_url <url>
# Output: 📊 Full PR review (no previous review found)
```

**Subsequent Review (after new commits):**
```bash
python main.py review --pr_url <url>
# Output: 📊 Incremental review: abc1234 → def5678
#         🆕 2 new findings, ✅ 1 resolved
```

**Force Full Review:**
```bash
python main.py review --pr_url <url> --full
# Output: 📊 Full PR review (forced)
```

**View History:**
```bash
python main.py history --pr_url <url>
# Shows all previous reviews with commit SHAs
```

## Success Criteria
- [ ] Only new commits reviewed on subsequent runs
- [ ] Findings categorized as new/existing/resolved
- [ ] Force pushes detected and handled
- [ ] Review history persisted (file or DB)
- [ ] Clear indication of incremental vs. full review
- [ ] Performance improvement for large PRs
- [ ] CLI to view review history
- [ ] Backward compatible with existing workflow

## Notes
- Consider adding a "diff visualization" showing old vs. new findings
- Future: Smart commit mapping after rebase (git similarity detection)
- Future: Trend analysis (are findings increasing or decreasing?)
- Handle edge case: PR reverted to previous state (all findings resolved)
