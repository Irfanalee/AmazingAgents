"""
GitHub integration for fetching PR diffs and posting review comments.
"""

from typing import Tuple
from github import Github, PullRequest
from .config import Config


class GitHubClient:
    """Client for interacting with GitHub Pull Requests."""
    
    def __init__(self, token: str = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token (defaults to Config.GITHUB_TOKEN)
        """
        self.token = token or Config.GITHUB_TOKEN
        self.client = Github(self.token)
    
    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, int]:
        """
        Parse GitHub PR URL to extract owner, repo, and PR number.
        
        Args:
            pr_url: Full GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)
            
        Returns:
            Tuple of (owner, repo_name, pr_number)
            
        Raises:
            ValueError: If URL format is invalid
        """
        try:
            # Expected format: https://github.com/{owner}/{repo}/pull/{number}
            parts = pr_url.rstrip('/').split('/')
            
            if 'github.com' not in pr_url or 'pull' not in parts:
                raise ValueError("Invalid GitHub PR URL format")
            
            pr_number = int(parts[-1])
            repo_name = parts[-3]
            owner = parts[-4]
            
            return owner, repo_name, pr_number
        except (IndexError, ValueError) as e:
            raise ValueError(
                f"Invalid PR URL format. Expected: https://github.com/owner/repo/pull/number. Error: {e}"
            )
    
    def get_pr_diff(self, pr_url: str) -> str:
        """
        Fetch the diff for a given Pull Request.
        
        Args:
            pr_url: Full GitHub PR URL
            
        Returns:
            Raw diff string containing all code changes
        """
        owner, repo_name, pr_number = self.parse_pr_url(pr_url)
        
        # Get repository and PR
        repo = self.client.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        # Fetch all files changed in the PR
        files = pr.get_files()
        
        # Construct a unified diff
        diff_parts = []
        for file in files:
            diff_parts.append(f"File: {file.filename}")
            diff_parts.append(f"Status: {file.status}")
            diff_parts.append(f"Additions: {file.additions} | Deletions: {file.deletions}")
            diff_parts.append("-" * 80)
            if file.patch:
                diff_parts.append(file.patch)
            diff_parts.append("\n")
        
        return "\n".join(diff_parts)
    
    def post_review_comment(self, pr_url: str, comment_body: str) -> None:
        """
        Post a review comment to the Pull Request.
        
        Args:
            pr_url: Full GitHub PR URL
            comment_body: Markdown-formatted review comment
        """
        owner, repo_name, pr_number = self.parse_pr_url(pr_url)
        
        # Get repository and PR
        repo = self.client.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        # Post the comment
        pr.create_issue_comment(comment_body)
        print(f"✅ Review comment posted to PR #{pr_number}")
