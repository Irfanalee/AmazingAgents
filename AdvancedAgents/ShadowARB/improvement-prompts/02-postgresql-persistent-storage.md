# Prompt: Implement PostgreSQL Persistent Storage

## Context
You previously built the Shadow ARB system that reviews GitHub PRs using AI agents. Currently, all state is stored in-memory only during workflow execution - there's no persistence, audit trail, or ability to resume from failures.

## Your Task
Implement PostgreSQL-backed persistent storage using LangGraph's built-in `PostgresSaver` checkpointer, plus custom tables for review history and analytics.

## Implementation Requirements

### 1. Create Database Schema (`migrations/001_initial_schema.sql`)
Create SQL migration with these tables:

**Checkpoints Table (LangGraph):**
```sql
CREATE TABLE checkpoints (
    thread_id VARCHAR(255) PRIMARY KEY,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_checkpoints_created ON checkpoints(created_at);
```

**Review History Table:**
```sql
CREATE TABLE review_history (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) REFERENCES checkpoints(thread_id),
    pr_url TEXT NOT NULL,
    repo VARCHAR(255) NOT NULL,
    pr_number INTEGER NOT NULL,
    pr_title TEXT,
    pr_author VARCHAR(255),
    review_verdict TEXT NOT NULL,
    security_findings_count INTEGER DEFAULT 0,
    scale_findings_count INTEGER DEFAULT 0,
    code_quality_findings_count INTEGER DEFAULT 0,
    architecture_findings_count INTEGER DEFAULT 0,
    total_findings INTEGER GENERATED ALWAYS AS (
        security_findings_count + scale_findings_count + 
        code_quality_findings_count + architecture_findings_count
    ) STORED,
    verdict_status VARCHAR(50), -- 'approved', 'approved_with_comments', 'changes_requested'
    reviewed_at TIMESTAMP DEFAULT NOW(),
    execution_time_ms INTEGER
);

CREATE INDEX idx_review_history_repo ON review_history(repo);
CREATE INDEX idx_review_history_date ON review_history(reviewed_at);
CREATE INDEX idx_review_history_status ON review_history(verdict_status);
```

**Agent Performance Table:**
```sql
CREATE TABLE agent_performance (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) REFERENCES checkpoints(thread_id),
    agent_name VARCHAR(100) NOT NULL,
    execution_time_ms INTEGER,
    findings_count INTEGER DEFAULT 0,
    executed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_performance_agent ON agent_performance(agent_name);
CREATE INDEX idx_agent_performance_date ON agent_performance(executed_at);
```

### 2. Create Database Module (`shadow_arb/database.py`)
Build database utilities:

```python
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

class DatabaseManager:
    """Manages PostgreSQL connections and sessions."""
    
    def __init__(self, connection_string: str):
        # Create engine with connection pooling
        # Add health check method
        # Implement session context manager
        
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        # Yield session with automatic commit/rollback
        
    def health_check(self) -> bool:
        # Test database connectivity
        
    def run_migrations(self):
        # Execute migration files
```

### 3. Create Migration Manager (`shadow_arb/migrations.py`)
Simple migration runner:
```python
def run_migrations(db_url: str, migrations_dir: str):
    # Read .sql files in order
    # Execute each migration
    # Track applied migrations (simple approach)
```

Alternative: Integrate Alembic for production-grade migrations.

### 4. Create Analytics Module (`shadow_arb/analytics.py`)
Build analytics queries:

```python
class ReviewAnalytics:
    """Provides analytics on review history."""
    
    def get_review_history(self, repo: str, limit: int = 50):
        # Return recent reviews for a repository
        
    def get_finding_trends(self, repo: str, days: int = 30):
        # Return time-series of findings by type
        
    def get_agent_performance(self, days: int = 30):
        # Return average execution time per agent
        
    def get_most_common_findings(self, repo: str, limit: int = 10):
        # Return most frequent finding patterns
        
    def get_verdict_distribution(self, repo: str):
        # Return breakdown of approved/rejected PRs
```

### 5. Update Configuration (`shadow_arb/config.py`)
Add database configuration:

```python
# PostgreSQL Configuration
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", 
    "postgresql://localhost:5432/shadow_arb"
)
ENABLE_CHECKPOINTING: bool = os.getenv(
    "ENABLE_CHECKPOINTING", 
    "false"
).lower() == "true"
ENABLE_ANALYTICS: bool = os.getenv(
    "ENABLE_ANALYTICS", 
    "true"
).lower() == "true"

# Connection Pool Settings
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
```

### 6. Update Workflow (`shadow_arb/workflow.py`)
Integrate PostgreSQL checkpointing:

```python
from langgraph.checkpoint.postgres import PostgresSaver
from .config import Config
from .database import DatabaseManager

def create_workflow(enable_checkpointing: bool = False) -> StateGraph:
    """Creates workflow with optional checkpointing."""
    
    workflow = StateGraph(AgentState)
    
    # ... add nodes and edges ...
    
    # Compile with checkpointer if enabled
    if enable_checkpointing and Config.ENABLE_CHECKPOINTING:
        checkpointer = PostgresSaver.from_conn_string(
            Config.DATABASE_URL
        )
        return workflow.compile(checkpointer=checkpointer)
    
    return workflow.compile()

def run_review(pr_diff: str, pr_url: str, thread_id: str = None):
    # Generate thread_id if not provided (use PR URL hash)
    # Track execution time
    # Save review history to database
    # Record agent performance metrics
```

### 7. Add Review History Tracking (`shadow_arb/review_tracker.py`)
Create module to save review results:

```python
class ReviewTracker:
    """Tracks and persists review results."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_review(
        self,
        thread_id: str,
        pr_url: str,
        state: AgentState,
        execution_time_ms: int
    ):
        # Parse PR URL to extract repo and number
        # Count findings by type
        # Determine verdict status from final_verdict
        # Insert into review_history table
        
    def save_agent_metrics(
        self,
        thread_id: str,
        agent_metrics: dict
    ):
        # Save execution time per agent
        # Insert into agent_performance table
```

### 8. Update Main Entry Point (`main.py`)
Add database initialization and review tracking:

```python
def main():
    # ... existing code ...
    
    # Initialize database if checkpointing enabled
    if Config.ENABLE_CHECKPOINTING:
        db_manager = DatabaseManager(Config.DATABASE_URL)
        db_manager.health_check()
        
        # Run migrations on first start
        run_migrations(Config.DATABASE_URL, "migrations")
    
    # Generate thread_id from PR URL
    thread_id = generate_thread_id(args.pr_url)
    
    # Run review with tracking
    start_time = time.time()
    final_verdict = run_review(pr_diff, args.pr_url, thread_id)
    execution_time = int((time.time() - start_time) * 1000)
    
    # Save to database if enabled
    if Config.ENABLE_ANALYTICS:
        tracker = ReviewTracker(db_manager)
        tracker.save_review(thread_id, args.pr_url, final_state, execution_time)
```

### 9. Add CLI Analytics Command (`main.py`)
Add subcommands for analytics:

```python
# Add argparse subparsers
parser.add_subparsers(dest='command')

# Review command (existing)
review_parser = subparsers.add_parser('review')
review_parser.add_argument('--pr_url', ...)

# Analytics command (new)
analytics_parser = subparsers.add_parser('analytics')
analytics_parser.add_argument('--repo', required=True)
analytics_parser.add_argument('--days', type=int, default=30)
analytics_parser.add_argument('--report', choices=['history', 'trends', 'performance'])
```

### 10. Update Dependencies (`requirements.txt`)
Add:
```
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.23
alembic>=1.13.1  # Optional, for production migrations
langgraph[postgres]>=0.2.45
```

### 11. Add Docker Compose for Development (`docker-compose.yml`)
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: shadow_arb
      POSTGRES_USER: shadow
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 12. Update Environment Template (`.env.example`)
Add:
```
# PostgreSQL Configuration
DATABASE_URL=postgresql://shadow:dev_password@localhost:5432/shadow_arb
ENABLE_CHECKPOINTING=true
ENABLE_ANALYTICS=true
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

## Technical Constraints
- Use SQLAlchemy for connection pooling (not raw psycopg2)
- Implement proper error handling for database failures
- Make checkpointing optional (feature flag)
- Use context managers for session management
- Implement database health checks
- Handle migration failures gracefully
- Use prepared statements (prevent SQL injection)
- Add retry logic for transient failures

## Expected Workflow
1. User runs: `python main.py review --pr_url <url>`
2. System checks if DATABASE_URL is configured
3. If yes: Initialize PostgresSaver, run migrations
4. Execute workflow with checkpointing enabled
5. Save review results to review_history table
6. Save agent metrics to agent_performance table
7. User can query: `python main.py analytics --repo owner/repo --report trends`

## Success Criteria
- [ ] Workflow state persisted to PostgreSQL
- [ ] Can resume interrupted workflows (LangGraph checkpointing)
- [ ] Review history stored with full metadata
- [ ] Analytics queries return meaningful insights
- [ ] Database migrations run automatically
- [ ] Connection pooling prevents resource exhaustion
- [ ] System works with/without database (graceful degradation)
- [ ] Docker Compose setup for local development

## Notes
- Start with simple migration runner, can add Alembic later
- Consider adding a `--resume` flag to continue from checkpoint
- Future: Add webhook endpoint to trigger reviews automatically
- Future: Build Grafana dashboard on top of these tables
