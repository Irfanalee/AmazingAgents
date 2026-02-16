# Prompt: Implement Caching for Repeated Reviews

## Context
You built the Shadow ARB system that reviews PRs using AI agents. Currently, every review re-analyzes the entire PR from scratch, even if the code hasn't changed. This wastes API calls, time, and money when:
- Re-reviewing the same commit after agent improvements
- Running multiple reviews on the same PR (e.g., after config changes)
- Analyzing unchanged files in incremental commits

## Your Task
Implement a smart caching layer that:
1. Caches agent findings by commit SHA + agent version
2. Reuses cached results for unchanged code
3. Invalidates cache when code or agent prompts change
4. Supports both Redis (fast) and local file cache (simple)

## Implementation Requirements

### 1. Create Cache Interface (`shadow_arb/cache/interface.py`)
Define abstract caching interface:

```python
from abc import ABC, abstractmethod
from typing import Optional, List
import hashlib

class CacheInterface(ABC):
    """Abstract interface for caching review results."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[dict]:
        """Retrieve cached value by key."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: dict, ttl: int = None) -> None:
        """Store value with optional TTL (seconds)."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete cached value."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @staticmethod
    def generate_cache_key(
        pr_diff: str,
        agent_name: str,
        agent_version: str,
        prompt_hash: str
    ) -> str:
        """
        Generate deterministic cache key.
        
        Format: shadow_arb:{agent_name}:{diff_hash}:{agent_version}:{prompt_hash}
        """
        diff_hash = hashlib.sha256(pr_diff.encode()).hexdigest()[:16]
        return f"shadow_arb:{agent_name}:{diff_hash}:{agent_version}:{prompt_hash}"
```

### 2. Implement File-Based Cache (`shadow_arb/cache/file_cache.py`)
Simple local file cache:

```python
import json
import os
import time
from pathlib import Path
from .interface import CacheInterface

class FileCache(CacheInterface):
    """File-based cache implementation for development/single-server."""
    
    def __init__(self, cache_dir: str = ".cache/shadow_arb"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[dict]:
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        # Read cache file
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        # Check TTL
        if 'expires_at' in data and data['expires_at'] < time.time():
            cache_file.unlink()  # Delete expired cache
            return None
        
        return data.get('value')
    
    def set(self, key: str, value: dict, ttl: int = None) -> None:
        cache_file = self.cache_dir / f"{key}.json"
        
        data = {
            'value': value,
            'created_at': time.time()
        }
        
        if ttl:
            data['expires_at'] = time.time() + ttl
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Implement delete() and exists()
```

### 3. Implement Redis Cache (`shadow_arb/cache/redis_cache.py`)
Production-ready Redis cache:

```python
import json
import redis
from typing import Optional
from .interface import CacheInterface

class RedisCache(CacheInterface):
    """Redis-based cache for production multi-instance deployments."""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or Config.REDIS_URL
        self.client = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=5
        )
    
    def get(self, key: str) -> Optional[dict]:
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(self, key: str, value: dict, ttl: int = None) -> None:
        serialized = json.dumps(value)
        if ttl:
            self.client.setex(key, ttl, serialized)
        else:
            self.client.set(key, serialized)
    
    def delete(self, key: str) -> None:
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0
    
    def health_check(self) -> bool:
        """Check Redis connectivity."""
        try:
            return self.client.ping()
        except:
            return False
```

### 4. Create Cache Factory (`shadow_arb/cache/factory.py`)
Auto-select cache backend:

```python
from .interface import CacheInterface
from .file_cache import FileCache
from .redis_cache import RedisCache
from ..config import Config

class CacheFactory:
    """Factory for creating appropriate cache backend."""
    
    @staticmethod
    def create_cache() -> CacheInterface:
        """
        Create cache based on configuration.
        
        Priority:
        1. Redis (if REDIS_URL configured)
        2. File cache (fallback)
        """
        if Config.REDIS_URL and Config.CACHE_BACKEND == 'redis':
            try:
                cache = RedisCache()
                if cache.health_check():
                    print("✅ Using Redis cache")
                    return cache
            except Exception as e:
                print(f"⚠️  Redis unavailable, falling back to file cache: {e}")
        
        print("✅ Using file-based cache")
        return FileCache()
```

### 5. Create Cacheable Agent Wrapper (`shadow_arb/cache/cacheable_agent.py`)
Decorator to add caching to agents:

```python
from functools import wraps
import hashlib
from typing import Callable
from ..state import AgentState
from .factory import CacheFactory

# Agent version - increment when changing prompts or logic
AGENT_VERSION = "1.0.0"

def get_prompt_hash(prompt: str) -> str:
    """Generate hash of agent prompt for cache invalidation."""
    return hashlib.sha256(prompt.encode()).hexdigest()[:8]

def cacheable_agent(agent_name: str, prompt: str):
    """
    Decorator to add caching to agent functions.
    
    Usage:
        @cacheable_agent("security", SECURITY_AGENT_PROMPT)
        def security_agent(state: AgentState) -> AgentState:
            ...
    """
    def decorator(agent_func: Callable) -> Callable:
        @wraps(agent_func)
        def wrapper(state: AgentState) -> AgentState:
            if not Config.ENABLE_CACHE:
                return agent_func(state)
            
            # Generate cache key
            cache = CacheFactory.create_cache()
            pr_diff = state.get("pr_diff", "")
            prompt_hash = get_prompt_hash(prompt)
            
            cache_key = cache.generate_cache_key(
                pr_diff=pr_diff,
                agent_name=agent_name,
                agent_version=AGENT_VERSION,
                prompt_hash=prompt_hash
            )
            
            # Check cache
            cached_result = cache.get(cache_key)
            if cached_result:
                print(f"💾 Cache HIT for {agent_name}_agent")
                state[f"{agent_name}_findings"] = cached_result['findings']
                return state
            
            print(f"🔄 Cache MISS for {agent_name}_agent")
            
            # Execute agent
            result_state = agent_func(state)
            
            # Cache result
            findings_key = f"{agent_name}_findings"
            cache.set(
                cache_key,
                {'findings': result_state[findings_key]},
                ttl=Config.CACHE_TTL
            )
            
            return result_state
        
        return wrapper
    return decorator
```

### 6. Update Agents (`shadow_arb/agents.py`)
Add caching decorator to all agents:

```python
from .cache.cacheable_agent import cacheable_agent
from .prompts import (
    SECURITY_AGENT_PROMPT,
    SCALE_AGENT_PROMPT,
    CLEAN_CODE_AGENT_PROMPT,
)

@cacheable_agent("security", SECURITY_AGENT_PROMPT)
def security_agent(state: AgentState) -> AgentState:
    # Existing implementation
    ...

@cacheable_agent("scale", SCALE_AGENT_PROMPT)
def scale_agent(state: AgentState) -> AgentState:
    # Existing implementation
    ...

@cacheable_agent("clean_code", CLEAN_CODE_AGENT_PROMPT)
def clean_code_agent(state: AgentState) -> AgentState:
    # Existing implementation
    ...

# Chairperson not cached (synthesis changes based on other findings)
```

### 7. Update Configuration (`shadow_arb/config.py`)
Add cache configuration:

```python
# Cache Configuration
ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
CACHE_BACKEND: str = os.getenv("CACHE_BACKEND", "file")  # 'file' or 'redis'
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "86400"))  # 24 hours default
REDIS_URL: str = os.getenv("REDIS_URL", "")

# File cache settings
FILE_CACHE_DIR: str = os.getenv("FILE_CACHE_DIR", ".cache/shadow_arb")
```

### 8. Add Cache Management CLI (`main.py`)
Add cache management commands:

```python
# Add to argparse subcommands
cache_parser = subparsers.add_parser('cache', help='Manage review cache')
cache_subparsers = cache_parser.add_subparsers(dest='cache_command')

# Clear cache
clear_parser = cache_subparsers.add_parser('clear', help='Clear all cached reviews')
clear_parser.add_argument('--agent', help='Clear specific agent cache only')

# Stats
stats_parser = cache_subparsers.add_parser('stats', help='Show cache statistics')

# Implementation
def handle_cache_command(args):
    cache = CacheFactory.create_cache()
    
    if args.cache_command == 'clear':
        # Implement cache clearing
        ...
    elif args.cache_command == 'stats':
        # Show cache hit/miss rates, size, etc.
        ...
```

### 9. Add Cache Metrics (`shadow_arb/cache/metrics.py`)
Track cache performance:

```python
class CacheMetrics:
    """Track cache hit/miss statistics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
    
    def record_hit(self):
        self.hits += 1
    
    def record_miss(self):
        self.misses += 1
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def print_stats(self):
        print(f"\n📊 Cache Statistics:")
        print(f"   Hits: {self.hits}")
        print(f"   Misses: {self.misses}")
        print(f"   Hit Rate: {self.get_hit_rate():.1%}")
```

### 10. Update Dependencies (`requirements.txt`)
Add:
```
redis>=5.0.1
hiredis>=2.3.2  # C parser for faster Redis
```

### 11. Update Environment Template (`.env.example`)
Add:
```
# Cache Configuration
ENABLE_CACHE=true
CACHE_BACKEND=file  # Options: file, redis
CACHE_TTL=86400     # 24 hours in seconds
FILE_CACHE_DIR=.cache/shadow_arb

# Redis Cache (optional, for production)
REDIS_URL=redis://localhost:6379/0
```

### 12. Add Docker Compose Redis Service (`docker-compose.yml`)
Update existing file:
```yaml
services:
  postgres:
    # ... existing ...
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  redis_data:
```

## Technical Constraints
- Cache keys must be deterministic (same input = same key)
- Invalidate cache when agent prompts change (use prompt hash)
- Include agent version in cache key
- Handle cache backend failures gracefully (fall back to no cache)
- Don't cache chairperson (synthesis may change based on context)
- Add cache warming option for frequently reviewed repos
- Implement cache size limits to prevent disk/memory overflow

## Cache Invalidation Strategy

**Automatic Invalidation:**
- Agent prompt changes → prompt_hash changes → new cache key
- Agent version update → AGENT_VERSION changes → new cache key
- PR diff changes → diff_hash changes → new cache key

**Manual Invalidation:**
```bash
# Clear all cache
python main.py cache clear

# Clear specific agent cache
python main.py cache clear --agent security
```

## Expected Performance Improvement
```
Without Cache:
- 3 agents × 2000 tokens × $0.01/1k = $0.06 per review
- ~30s execution time

With Cache (80% hit rate):
- 0.2 × $0.06 = $0.012 per review (80% savings)
- ~5s execution time (6x faster)
```

## Success Criteria
- [ ] Cache reduces API calls for unchanged code
- [ ] Cache hit rate > 70% for repeated reviews
- [ ] Cache invalidates correctly when agents change
- [ ] Both file and Redis backends work
- [ ] Graceful degradation if cache unavailable
- [ ] CLI commands to manage cache
- [ ] Metrics show cache hit/miss rates
- [ ] TTL prevents stale cache accumulation

## Notes
- Consider using cache warming for popular repositories
- Future: Add distributed cache for multi-region deployments
- Future: Cache architecture analysis results (expensive)
- Monitor cache size - add cleanup job if needed
