# Prompt: Implement Architecture Context Awareness (Hybrid Approach)

## Context
You previously built the Shadow ARB system - an AI-powered Architecture Review Board that uses three specialized agents (security, scale, clean code) to review GitHub Pull Requests in parallel, then synthesizes findings via a chairperson agent.

## Current Problem
The existing implementation only reviews PR diffs in isolation without understanding the broader codebase architecture. The agents cannot:
- Detect architectural pattern violations
- Identify breaking changes to existing APIs
- Spot circular dependency introduction
- Validate module boundary violations
- Check consistency with existing design patterns

## Your Task
Implement the **Hybrid Architecture Context Awareness** system as described in IMPROVEMENTS.md.

## Implementation Requirements

### 1. Create Static Analyzer (`shadow_arb/static_analyzer.py`)
Build a module that:
- Accepts a GitHub PR URL and extracts repo URL and PR number
- Clones the repository to a temporary directory
- Checks out the PR branch
- Runs static analysis tools:
  - `radon` for complexity metrics
  - `bandit` for security scanning
  - `pylint` for code quality
  - Custom AST parsing for dependency extraction
- Extracts:
  - Module structure and layers
  - Import dependency graph
  - API endpoints/contracts
  - Class hierarchies
  - Function complexity metrics
- Returns a structured dict with all findings
- Cleans up temporary directory after analysis

### 2. Create Architecture Graph (`shadow_arb/architecture_graph.py`)
Build a knowledge graph system that:
- Takes the static analysis results as input
- Builds a graph representation with:
  - Nodes: Modules, Classes, Functions, APIs
  - Edges: Dependencies, Calls, Implements, Inherits
- Provides methods:
  - `analyze_impact(pr_diff)` - Shows which modules are affected
  - `detect_violations(pr_diff)` - Finds architectural pattern violations
  - `check_boundaries(pr_diff)` - Validates layer separation
  - `find_breaking_changes(pr_diff)` - Identifies API contract violations
- Returns structured findings for the architecture agent

### 3. Add 4th Agent: Architecture Agent (`shadow_arb/agents.py`)
Create a new agent function `architecture_agent(state: AgentState)` that:
- Uses the ARCHITECTURE_AGENT_PROMPT from prompts.py (you'll create this)
- Receives both `pr_diff` and `codebase_context` from state
- Analyzes:
  - Architectural fit with existing patterns
  - Consistency with current design
  - Module coupling impact
  - Potential for architectural drift
  - Bounded context violations
- Returns structured findings list (like other agents)
- Uses the same `_call_llm_with_structured_output` pattern

### 4. Update State Definition (`shadow_arb/state.py`)
Extend `AgentState` TypedDict with:
```python
codebase_analysis: dict      # Static analysis results
impact_analysis: dict         # Architecture impact analysis
architecture_findings: List[str]  # Architecture agent findings
```

### 5. Add Architecture Agent Prompt (`shadow_arb/prompts.py`)
Create `ARCHITECTURE_AGENT_PROMPT` with focus on:
- Design pattern consistency
- SOLID principle adherence
- Layer/module boundary violations
- API contract stability
- Architectural drift detection
- Bounded context violations (if microservices)

### 6. Update Workflow (`shadow_arb/workflow.py`)
Modify the workflow to:
- Add `architecture_agent` as a 4th node
- Run it in parallel with the other three agents
- Connect its output to the chairperson
- Update `run_review()` function to:
  - Accept `pr_url` instead of just `pr_diff`
  - Call `StaticAnalyzer` to get codebase analysis
  - Call `ArchitectureGraph` to get impact analysis
  - Include context in initial state
  - Pass enriched state to all agents

### 7. Update Main Entry Point (`main.py`)
Modify to pass the full PR URL to workflow instead of just the diff.

### 8. Update Chairperson (`shadow_arb/prompts.py` and `shadow_arb/agents.py`)
Update the chairperson to:
- Include architecture findings in the synthesis
- Add an "Architecture Findings" section to the review
- Consider architecture violations in the final verdict

### 9. Add Dependencies (`requirements.txt`)
Add:
```
radon>=6.0.1
bandit>=1.7.5
pylint>=3.0.0
gitpython>=3.1.40
networkx>=3.2  # For graph operations
```

### 10. Update Configuration (`shadow_arb/config.py`)
Add:
```python
ENABLE_ARCHITECTURE_ANALYSIS: bool = os.getenv("ENABLE_ARCHITECTURE_ANALYSIS", "true").lower() == "true"
TEMP_REPO_DIR: str = os.getenv("TEMP_REPO_DIR", "/tmp/shadow_arb_repos")
```

## Technical Constraints
- Use type hints throughout
- Follow existing code patterns (Pydantic models, structured output)
- Handle errors gracefully (repo clone failures, analysis timeouts)
- Clean up temporary files
- Make architecture analysis optional via feature flag
- Cache static analysis results (same repo + commit SHA)
- Limit analysis to changed files + their dependencies (not entire codebase)

## Expected Output Structure

**Static Analysis Result:**
```python
{
    "complexity": {"file.py": {"function_name": 12}},
    "dependencies": {"module_a": ["module_b", "module_c"]},
    "security_scans": [{"file": "auth.py", "issue": "..."}],
    "architecture": {
        "layers": ["controllers", "services", "models"],
        "patterns": ["MVC", "Repository"],
        "api_contracts": [...]
    }
}
```

**Architecture Findings:**
```python
[
    "Violation: New controller directly imports model layer, bypassing service layer",
    "Breaking Change: Modified UserService.create() signature - impacts 5 callers",
    "Pattern Inconsistency: Using direct DB queries instead of repository pattern"
]
```

## Success Criteria
- [ ] Agents receive full codebase context, not just PR diff
- [ ] Architecture violations are detected and reported
- [ ] Breaking changes identified before merge
- [ ] System works with feature flag (can be disabled)
- [ ] No impact on performance (parallel execution maintained)
- [ ] Works with both public and private repositories
- [ ] Proper cleanup of cloned repositories

## Notes
- Start with MVP: basic static analysis + simple architecture agent
- Can enhance later with ML-based pattern detection
- Consider adding caching to avoid re-analyzing same commits
- May need GitHub token with repo clone permissions for private repos
