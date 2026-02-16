# Prompt: Add Custom Agent Configuration

## Context
You built the Shadow ARB system with hardcoded agent prompts in `prompts.py`. Currently, users cannot:
- Customize agent behavior for their team's standards
- Adjust severity thresholds
- Add custom review criteria
- Create team-specific agents
- Override prompts per repository

## Your Task
Implement a flexible configuration system that allows users to:
1. Customize agent prompts via YAML/JSON files
2. Configure severity levels and finding thresholds
3. Create custom agents without code changes
4. Override configurations per repository
5. Version and share configurations across teams

## Implementation Requirements

### 1. Define Configuration Schema (`shadow_arb/config_schema.py`)
Create Pydantic models for configuration:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    name: str = Field(..., description="Agent name (lowercase, underscores)")
    display_name: str = Field(..., description="Human-readable name")
    enabled: bool = Field(default=True, description="Whether agent is active")
    system_prompt: str = Field(..., description="LLM system prompt")
    model: Optional[str] = Field(None, description="Override default LLM model")
    temperature: float = Field(default=0.3, min=0.0, max=2.0)
    
class SeverityConfig(BaseModel):
    """Severity level configuration."""
    name: str  # 'critical', 'high', 'medium', 'low'
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to match in findings"
    )
    emoji: str = "⚠️"
    color: str = "#FFA500"  # For future UI

class ChairpersonConfig(BaseModel):
    """Chairperson synthesis configuration."""
    system_prompt: str
    approval_threshold: int = Field(
        default=0,
        description="Max findings before rejecting PR (0 = always synthesize)"
    )
    auto_approve_if_empty: bool = Field(
        default=True,
        description="Auto-approve if no findings"
    )

class ReviewConfig(BaseModel):
    """Complete Shadow ARB configuration."""
    version: str = Field(default="1.0", description="Config version")
    agents: List[AgentConfig] = Field(..., description="List of review agents")
    chairperson: ChairpersonConfig
    severities: List[SeverityConfig] = Field(default_factory=list)
    
    # Global settings
    max_concurrent_agents: int = Field(default=10, ge=1, le=20)
    timeout_per_agent_seconds: int = Field(default=120)
    
    # Repository overrides
    repo_overrides: Dict[str, "ReviewConfig"] = Field(
        default_factory=dict,
        description="Per-repo configurations (key: owner/repo)"
    )
```

### 2. Create Default Configuration (`configs/default.yaml`)
Ship with sensible defaults:

```yaml
version: "1.0"

agents:
  - name: security
    display_name: "Security Agent"
    enabled: true
    system_prompt: |
      You are a Security Architect reviewing code changes for security vulnerabilities.
      
      **Your Focus:**
      - SQL Injection, XSS, CSRF vulnerabilities
      - Hardcoded credentials, API keys, or secrets
      - Insecure authentication/authorization patterns
      
      **Output Format:**
      Return a JSON array of strings, where each string describes one security issue.
    temperature: 0.3
  
  - name: scale
    display_name: "Scalability Agent"
    enabled: true
    system_prompt: |
      You are a Scalability Architect reviewing for performance issues.
      ...
    temperature: 0.3
  
  - name: clean_code
    display_name: "Clean Code Agent"
    enabled: true
    system_prompt: |
      You are a Clean Code Architect reviewing for maintainability.
      ...
    temperature: 0.3

chairperson:
  system_prompt: |
    You are the Chairperson synthesizing findings from all agents.
    Provide a constructive, professional review in markdown format.
  approval_threshold: 0
  auto_approve_if_empty: true

severities:
  - name: critical
    keywords: ["sql injection", "xss", "hardcoded password", "remote code execution"]
    emoji: "🔴"
  - name: high
    keywords: ["n+1", "memory leak", "race condition"]
    emoji: "🟠"
  - name: medium
    keywords: ["code duplication", "missing tests", "complex function"]
    emoji: "🟡"
  - name: low
    keywords: ["naming convention", "missing docstring"]
    emoji: "🟢"

max_concurrent_agents: 10
timeout_per_agent_seconds: 120
```

### 3. Create Configuration Loader (`shadow_arb/config_loader.py`)
Load and validate configurations:

```python
import yaml
from pathlib import Path
from typing import Optional
from .config_schema import ReviewConfig, AgentConfig

class ConfigLoader:
    """Loads and manages Shadow ARB configurations."""
    
    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "configs" / "default.yaml"
    
    @staticmethod
    def load_config(config_path: Optional[str] = None) -> ReviewConfig:
        """
        Load configuration from file or use default.
        
        Priority:
        1. Provided config_path
        2. Environment variable CONFIG_PATH
        3. .shadow-arb.yaml in current directory
        4. Default config
        """
        if config_path:
            path = Path(config_path)
        elif os.getenv("SHADOW_ARB_CONFIG"):
            path = Path(os.getenv("SHADOW_ARB_CONFIG"))
        elif Path(".shadow-arb.yaml").exists():
            path = Path(".shadow-arb.yaml")
        else:
            path = ConfigLoader.DEFAULT_CONFIG_PATH
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Validate and parse with Pydantic
        config = ReviewConfig(**data)
        
        print(f"✅ Loaded configuration from: {path}")
        return config
    
    @staticmethod
    def get_repo_config(config: ReviewConfig, repo: str) -> ReviewConfig:
        """
        Get configuration for specific repository.
        Falls back to default if no override exists.
        """
        if repo in config.repo_overrides:
            print(f"📋 Using custom config for {repo}")
            return config.repo_overrides[repo]
        return config
    
    @staticmethod
    def save_config(config: ReviewConfig, path: str):
        """Save configuration to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(config.dict(), f, sort_keys=False)
```

### 4. Create Dynamic Agent Factory (`shadow_arb/agent_factory.py`)
Generate agents from configuration:

```python
from typing import Callable
from .state import AgentState
from .config_schema import AgentConfig
from .agents import _call_llm_with_structured_output

class AgentFactory:
    """Creates agent functions dynamically from configuration."""
    
    @staticmethod
    def create_agent(agent_config: AgentConfig) -> Callable:
        """
        Generate an agent function from configuration.
        
        Returns:
            Function matching signature: (state: AgentState) -> AgentState
        """
        def dynamic_agent(state: AgentState) -> AgentState:
            if not agent_config.enabled:
                print(f"⏭️  Skipping disabled agent: {agent_config.display_name}")
                state[f"{agent_config.name}_findings"] = []
                return state
            
            pr_diff = state.get("pr_diff", "")
            if not pr_diff:
                state[f"{agent_config.name}_findings"] = []
                return state
            
            user_message = f"Review the following code changes:\n\n{pr_diff}"
            
            response = _call_llm_with_structured_output(
                system_prompt=agent_config.system_prompt,
                user_message=user_message,
                model=agent_config.model,  # Override model if specified
                temperature=agent_config.temperature
            )
            
            state[f"{agent_config.name}_findings"] = response.findings
            return state
        
        # Set function name for debugging
        dynamic_agent.__name__ = f"{agent_config.name}_agent"
        
        return dynamic_agent
    
    @staticmethod
    def create_all_agents(config: ReviewConfig) -> dict:
        """
        Create all agents from configuration.
        
        Returns:
            Dict mapping agent names to agent functions
        """
        agents = {}
        for agent_config in config.agents:
            if agent_config.enabled:
                agents[agent_config.name] = AgentFactory.create_agent(agent_config)
        
        return agents
```

### 5. Update Workflow (`shadow_arb/workflow.py`)
Make workflow configuration-driven:

```python
from .config_loader import ConfigLoader
from .agent_factory import AgentFactory

def create_workflow(config: ReviewConfig) -> StateGraph:
    """Creates workflow from configuration."""
    
    workflow = StateGraph(AgentState)
    
    # Dynamically create and add agent nodes
    agents = AgentFactory.create_all_agents(config)
    
    for agent_name, agent_func in agents.items():
        workflow.add_node(f"{agent_name}_agent", agent_func)
    
    # Create chairperson from config
    chairperson = create_chairperson(config.chairperson)
    workflow.add_node("chairperson_agent", chairperson)
    
    # Set entry points (parallel execution)
    for agent_name in agents.keys():
        workflow.set_entry_point(f"{agent_name}_agent")
    
    # All agents feed into chairperson
    for agent_name in agents.keys():
        workflow.add_edge(f"{agent_name}_agent", "chairperson_agent")
    
    workflow.add_edge("chairperson_agent", END)
    
    return workflow.compile()
```

### 6. Add Repository-Specific Config (`configs/repo-overrides.yaml`)
Example override configuration:

```yaml
# configs/repo-overrides.yaml
version: "1.0"

repo_overrides:
  "mycompany/frontend":
    agents:
      - name: security
        enabled: true
        system_prompt: |
          Focus on XSS and CSRF in React components.
          Check for dangerouslySetInnerHTML usage.
      
      - name: accessibility
        display_name: "Accessibility Agent"
        enabled: true
        system_prompt: |
          Review for WCAG 2.1 AA compliance.
          Check ARIA labels, keyboard navigation, color contrast.
    
    severities:
      - name: critical
        keywords: ["accessibility violation", "wcag"]
  
  "mycompany/backend":
    agents:
      - name: database
        display_name: "Database Agent"
        enabled: true
        system_prompt: |
          Review database migrations and query performance.
          Check for missing indexes, N+1 queries.
```

### 7. Add Configuration Validation CLI (`main.py`)
Add command to validate configs:

```python
# Add to subparsers
config_parser = subparsers.add_parser('config', help='Manage configuration')
config_subparsers = config_parser.add_subparsers(dest='config_command')

# Validate config
validate_parser = config_subparsers.add_parser('validate')
validate_parser.add_argument('--config', help='Path to config file')

# Show config
show_parser = config_subparsers.add_parser('show')
show_parser.add_argument('--repo', help='Show config for specific repo')

# Generate template
init_parser = config_subparsers.add_parser('init')
init_parser.add_argument('--output', default='.shadow-arb.yaml')

def handle_config_command(args):
    if args.config_command == 'validate':
        config = ConfigLoader.load_config(args.config)
        print("✅ Configuration is valid")
        print(f"   Agents: {len(config.agents)}")
        print(f"   Severities: {len(config.severities)}")
    
    elif args.config_command == 'show':
        config = ConfigLoader.load_config()
        if args.repo:
            config = ConfigLoader.get_repo_config(config, args.repo)
        print(yaml.dump(config.dict()))
    
    elif args.config_command == 'init':
        # Copy default config to current directory
        ...
```

### 8. Update Main Execution (`main.py`)
Load configuration before review:

```python
def main():
    args = parser.parse_args()
    
    # Load configuration
    config_path = getattr(args, 'config', None)
    config = ConfigLoader.load_config(config_path)
    
    # Get repo-specific config if overrides exist
    owner, repo_name, _ = parse_pr_url(args.pr_url)
    repo = f"{owner}/{repo_name}"
    config = ConfigLoader.get_repo_config(config, repo)
    
    # Run review with configuration
    final_verdict = run_review(pr_diff, config)
```

### 9. Update Configuration (`shadow_arb/config.py`)
Add config path setting:

```python
# Configuration File Path
SHADOW_ARB_CONFIG: str = os.getenv("SHADOW_ARB_CONFIG", "")
```

### 10. Update Dependencies (`requirements.txt`)
Add:
```
pyyaml>=6.0.1
pydantic>=2.9.2  # Already exists
```

### 11. Create Example Custom Agent (`configs/examples/custom-agents.yaml`)
Show how to add custom agents:

```yaml
version: "1.0"

agents:
  # Standard agents
  - name: security
    display_name: "Security Agent"
    enabled: true
    system_prompt: "..."
  
  # Custom agent example
  - name: performance
    display_name: "Performance Agent"
    enabled: true
    system_prompt: |
      You are a Performance Optimization Expert.
      
      Focus:
      - Unnecessary re-renders in React
      - Bundle size increases
      - Unoptimized images
      - Slow database queries
      
      Output: JSON array of performance issues found.
    temperature: 0.4
  
  - name: documentation
    display_name: "Documentation Agent"
    enabled: true
    system_prompt: |
      You are a Documentation Specialist.
      
      Check:
      - Missing API documentation
      - Outdated README changes
      - Missing inline comments for complex logic
      - Changelog updates
      
      Output: JSON array of documentation issues.
```

## Technical Constraints
- Configuration must be version-controlled (YAML)
- Validate configs with Pydantic before use
- Support environment variable substitution in configs
- Backward compatible (old hardcoded prompts still work)
- Allow model override per agent
- Validate agent names (lowercase, underscores only)
- Prevent duplicate agent names
- Handle missing configuration files gracefully

## Expected Usage

**Basic:**
```bash
# Use default config
python main.py review --pr_url <url>

# Use custom config
python main.py review --pr_url <url> --config my-config.yaml
```

**Configuration Management:**
```bash
# Validate custom config
python main.py config validate --config team-config.yaml

# Generate template
python main.py config init --output .shadow-arb.yaml

# Show effective config for a repo
python main.py config show --repo mycompany/backend
```

## Success Criteria
- [ ] Custom agent prompts via YAML/JSON
- [ ] Per-repository configuration overrides
- [ ] Dynamic agent creation without code changes
- [ ] Configuration validation catches errors
- [ ] CLI commands to manage configurations
- [ ] Example configs for common use cases
- [ ] Backward compatible with hardcoded prompts
- [ ] Support environment variable substitution

## Notes
- Consider adding configuration hot-reloading for long-running processes
- Future: Web UI for configuration management
- Future: Marketplace for sharing agent configurations
- Document best practices for writing effective agent prompts
