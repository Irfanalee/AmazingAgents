# Prompt: Add Support for GitLab and Bitbucket

## Context
You previously built the Shadow ARB system that reviews GitHub Pull Requests. Currently, it only supports GitHub via the `PyGithub` library. We need to extend support to GitLab and Bitbucket to make it platform-agnostic.

## Your Task
Refactor the VCS integration layer to support GitHub, GitLab, and Bitbucket using a common interface pattern.

## Implementation Requirements

### 1. Create VCS Interface (`shadow_arb/vcs/interface.py`)
Define abstract base class:

```python
from abc import ABC, abstractmethod
from typing import Tuple

class VCSClient(ABC):
    """Abstract interface for Version Control System clients."""
    
    @abstractmethod
    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, int]:
        """Parse PR URL into (owner, repo, pr_number)."""
        pass
    
    @abstractmethod
    def get_pr_diff(self, pr_url: str) -> str:
        """Fetch the diff for a Pull Request."""
        pass
    
    @abstractmethod
    def post_review_comment(self, pr_url: str, comment: str) -> None:
        """Post a review comment to the Pull Request."""
        pass
    
    @abstractmethod
    def get_pr_metadata(self, pr_url: str) -> dict:
        """Get PR metadata (title, author, branch, etc.)."""
        pass
```

### 2. Refactor GitHub Client (`shadow_arb/vcs/github.py`)
Move existing `GitHubClient` and make it implement `VCSClient`:

```python
from github import Github
from .interface import VCSClient

class GitHubClient(VCSClient):
    """GitHub implementation of VCS client."""
    
    def __init__(self, token: str = None):
        self.token = token or Config.GITHUB_TOKEN
        self.client = Github(self.token)
    
    # Implement all abstract methods
    # Keep existing logic from shadow_arb/github_client.py
```

### 3. Create GitLab Client (`shadow_arb/vcs/gitlab.py`)
Implement GitLab support:

```python
import gitlab
from .interface import VCSClient

class GitLabClient(VCSClient):
    """GitLab implementation of VCS client."""
    
    def __init__(self, token: str = None, url: str = None):
        self.token = token or Config.GITLAB_TOKEN
        self.url = url or Config.GITLAB_URL  # Default: https://gitlab.com
        self.client = gitlab.Gitlab(self.url, private_token=self.token)
    
    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, int]:
        # GitLab format: https://gitlab.com/owner/repo/-/merge_requests/123
        # Parse and return (owner, repo, mr_number)
        
    def get_pr_diff(self, pr_url: str) -> str:
        # Use GitLab API: project.mergerequests.get(mr_id).diffs()
        
    def post_review_comment(self, pr_url: str, comment: str) -> None:
        # Use GitLab API: mr.notes.create({'body': comment})
    
    def get_pr_metadata(self, pr_url: str) -> dict:
        # Return title, author, source_branch, target_branch, etc.
```

### 4. Create Bitbucket Client (`shadow_arb/vcs/bitbucket.py`)
Implement Bitbucket support:

```python
from atlassian import Bitbucket
from .interface import VCSClient

class BitbucketClient(VCSClient):
    """Bitbucket implementation of VCS client."""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username or Config.BITBUCKET_USERNAME
        self.password = password or Config.BITBUCKET_APP_PASSWORD
        self.client = Bitbucket(
            url='https://api.bitbucket.org',
            username=self.username,
            password=self.password
        )
    
    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, int]:
        # Bitbucket format: https://bitbucket.org/owner/repo/pull-requests/123
        # Parse and return (owner, repo, pr_number)
        
    def get_pr_diff(self, pr_url: str) -> str:
        # Use Bitbucket API: pullrequests endpoint with diff
        
    def post_review_comment(self, pr_url: str, comment: str) -> None:
        # Use Bitbucket API: POST to PR comments
    
    def get_pr_metadata(self, pr_url: str) -> dict:
        # Return title, author, source_branch, destination_branch
```

### 5. Create VCS Factory (`shadow_arb/vcs/factory.py`)
Auto-detect platform from URL:

```python
from .interface import VCSClient
from .github import GitHubClient
from .gitlab import GitLabClient
from .bitbucket import BitbucketClient

class VCSFactory:
    """Factory for creating appropriate VCS client based on URL."""
    
    @staticmethod
    def create_client(pr_url: str) -> VCSClient:
        """
        Detect platform from URL and return appropriate client.
        
        Raises:
            ValueError: If platform is not supported
        """
        if 'github.com' in pr_url:
            return GitHubClient()
        elif 'gitlab.com' in pr_url or 'gitlab' in pr_url:
            return GitLabClient()
        elif 'bitbucket.org' in pr_url:
            return BitbucketClient()
        else:
            raise ValueError(
                f"Unsupported VCS platform in URL: {pr_url}\n"
                f"Supported platforms: GitHub, GitLab, Bitbucket"
            )
    
    @staticmethod
    def get_supported_platforms() -> list:
        return ['GitHub', 'GitLab', 'Bitbucket']
```

### 6. Update Configuration (`shadow_arb/config.py`)
Add tokens for all platforms:

```python
# GitHub Configuration
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

# GitLab Configuration
GITLAB_TOKEN: str = os.getenv("GITLAB_TOKEN", "")
GITLAB_URL: str = os.getenv("GITLAB_URL", "https://gitlab.com")

# Bitbucket Configuration
BITBUCKET_USERNAME: str = os.getenv("BITBUCKET_USERNAME", "")
BITBUCKET_APP_PASSWORD: str = os.getenv("BITBUCKET_APP_PASSWORD", "")

@classmethod
def validate(cls) -> None:
    # Update validation to check for at least one VCS token
    if not any([cls.GITHUB_TOKEN, cls.GITLAB_TOKEN, cls.BITBUCKET_USERNAME]):
        raise ValueError(
            "At least one VCS token must be configured: "
            "GITHUB_TOKEN, GITLAB_TOKEN, or BITBUCKET_USERNAME"
        )
```

### 7. Update Main Entry Point (`main.py`)
Replace direct GitHubClient usage with factory:

```python
from shadow_arb.vcs.factory import VCSFactory

def main():
    # ... existing code ...
    
    # Auto-detect and create appropriate VCS client
    print(f"🔍 Detecting VCS platform from URL...")
    vcs_client = VCSFactory.create_client(args.pr_url)
    print(f"✅ Using {vcs_client.__class__.__name__}")
    
    # Rest of the code remains the same
    pr_diff = vcs_client.get_pr_diff(args.pr_url)
    # ...
    vcs_client.post_review_comment(args.pr_url, final_verdict)
```

### 8. Update Package Structure
Reorganize to:
```
shadow_arb/
├── vcs/
│   ├── __init__.py         # Export VCSFactory, VCSClient
│   ├── interface.py        # Abstract base class
│   ├── github.py           # GitHub implementation
│   ├── gitlab.py           # GitLab implementation
│   ├── bitbucket.py        # Bitbucket implementation
│   └── factory.py          # Platform detection
```

### 9. Update Dependencies (`requirements.txt`)
Add:
```
# VCS Integrations
PyGithub==2.4.0              # Existing
python-gitlab==4.4.0         # GitLab
atlassian-python-api==3.41.0 # Bitbucket
```

### 10. Update Environment Template (`.env.example`)
Add:
```
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here

# GitLab Configuration (optional)
GITLAB_TOKEN=your_gitlab_token_here
GITLAB_URL=https://gitlab.com  # Or self-hosted URL

# Bitbucket Configuration (optional)
BITBUCKET_USERNAME=your_username
BITBUCKET_APP_PASSWORD=your_app_password
```

### 11. Update Workflow (`shadow_arb/workflow.py`)
Pass VCS client to workflow if needed for repo cloning:

```python
def run_review(
    pr_diff: str, 
    pr_url: str, 
    vcs_client: VCSClient = None
) -> str:
    # If architecture analysis is enabled, may need to clone repo
    # VCS client provides authentication for private repos
```

## Technical Constraints
- Maintain backward compatibility (existing GitHub-only setups should work)
- Use same authentication patterns for all platforms
- Normalize diff format across platforms (unified diff)
- Handle platform-specific rate limits
- Support self-hosted instances (GitLab, Bitbucket Server)
- Graceful error messages if token is missing for detected platform

## URL Format Examples
```
GitHub:    https://github.com/owner/repo/pull/123
GitLab:    https://gitlab.com/owner/repo/-/merge_requests/123
Bitbucket: https://bitbucket.org/owner/repo/pull-requests/123
```

## Expected Behavior
```bash
# GitHub PR
python main.py review --pr_url https://github.com/owner/repo/pull/123
# Output: ✅ Using GitHubClient

# GitLab MR
python main.py review --pr_url https://gitlab.com/owner/repo/-/merge_requests/456
# Output: ✅ Using GitLabClient

# Bitbucket PR
python main.py review --pr_url https://bitbucket.org/owner/repo/pull-requests/789
# Output: ✅ Using BitbucketClient
```

## Success Criteria
- [ ] Single interface for all VCS platforms
- [ ] Auto-detection from URL works correctly
- [ ] GitHub functionality unchanged (backward compatible)
- [ ] GitLab MRs can be reviewed and commented
- [ ] Bitbucket PRs can be reviewed and commented
- [ ] Clear error messages for unsupported platforms
- [ ] Supports self-hosted GitLab instances
- [ ] All three platforms return normalized diff format

## Notes
- GitLab calls them "Merge Requests" (MR) not "Pull Requests"
- Bitbucket uses "App Passwords" for API authentication
- Consider adding platform-specific features later (e.g., GitLab CI integration)
- May need to handle different diff formats (normalize to unified diff)
