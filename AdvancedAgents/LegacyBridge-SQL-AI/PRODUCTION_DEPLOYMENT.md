# Production Deployment Guide

This guide covers deploying LegacyBridge-SQL-AI as a containerized application with support for multiple database backends (PostgreSQL, MySQL, SQL Server, Oracle).

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Support](#database-support)
3. [Configuration Management](#configuration-management)
4. [Docker Deployment](#docker-deployment)
5. [Security Best Practices](#security-best-practices)
6. [Monitoring & Logging](#monitoring--logging)
7. [Scaling Considerations](#scaling-considerations)

---

## Architecture Overview

### Production Architecture

```
┌─────────────────┐
│   Load Balancer │
│   (optional)    │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬──────────┐
    │          │          │          │
┌───▼───┐  ┌──▼───┐  ┌───▼───┐  ┌───▼───┐
│ App   │  │ App  │  │ App   │  │ App   │
│ Pod 1 │  │ Pod 2│  │ Pod 3 │  │ Pod N │
└───┬───┘  └──┬───┘  └───┬───┘  └───┬───┘
    │         │          │          │
    └────────┬┴──────────┴──────────┘
             │
    ┌────────▼─────────┐
    │ Database Server  │
    │ (PostgreSQL/     │
    │  MySQL/Oracle/   │
    │  SQL Server)     │
    └──────────────────┘
```

### Key Components

- **Application Container**: Python app with connection pooling
- **Database**: External database server (not SQLite)
- **Configuration**: Environment variables and secrets
- **Logging**: Structured logging to stdout/stderr
- **Monitoring**: Health checks and metrics endpoints

---

## Database Support

### Supported Databases

| Database | Driver | Connection String Format |
|----------|--------|-------------------------|
| PostgreSQL | `psycopg2` | `postgresql://user:pass@host:5432/dbname` |
| MySQL | `mysql-connector-python` | `mysql://user:pass@host:3306/dbname` |
| SQL Server | `pyodbc` | `mssql+pyodbc://user:pass@host/dbname?driver=ODBC+Driver+17+for+SQL+Server` |
| Oracle | `cx_Oracle` | `oracle://user:pass@host:1521/service_name` |

### Implementation Guidelines

#### 1. Update Dependencies

Add database drivers to your requirements file:
- PostgreSQL: `psycopg2-binary` or `psycopg2`
- MySQL: `mysql-connector-python` or `pymysql`
- SQL Server: `pyodbc` with ODBC drivers
- Oracle: `cx_Oracle`
- ORM Layer: `sqlalchemy` for database abstraction

#### 2. Create Database Abstraction Layer

**File: `src/database_factory.py`**

Pseudocode:
```
FUNCTION create_database_manager(connection_string, pool_size, timeout):
    // Get connection string from environment if not provided
    IF connection_string is None THEN
        connection_string = ENVIRONMENT_VARIABLE("DATABASE_URL")
    END IF

    // Read pool configuration from environment
    pool_size = ENVIRONMENT_VARIABLE("DB_POOL_SIZE", default=pool_size)
    timeout = ENVIRONMENT_VARIABLE("DB_TIMEOUT", default=timeout)

    // Fallback to SQLite for development
    IF connection_string is empty THEN
        db_path = ENVIRONMENT_VARIABLE("SQLITE_PATH", default="data/chinook.db")
        RETURN new DatabaseManager(db_path, pool_size, timeout)
    END IF

    // Parse connection string to determine database type
    parsed_url = PARSE_URL(connection_string)
    database_type = EXTRACT_SCHEME(parsed_url)

    // Return appropriate database manager
    IF database_type == "sqlite" THEN
        RETURN new DatabaseManager(path, pool_size, timeout)
    ELSE IF database_type IN ["postgresql", "mysql", "mssql", "oracle"] THEN
        RETURN new SQLDatabaseManager(connection_string, pool_size, timeout)
    ELSE
        THROW ERROR("Unsupported database type")
    END IF
END FUNCTION
```

#### 3. Create SQL Database Manager

**File: `src/database_sql.py`**

Pseudocode:
```
CLASS SQLDatabaseManager:

    CONSTRUCTOR(connection_string, pool_size, timeout):
        // Initialize SQLAlchemy engine with connection pooling
        this.engine = CREATE_ENGINE(
            connection_string,
            pool_class = QueuePool,
            pool_size = pool_size,
            max_overflow = pool_size * 2,
            pool_timeout = timeout,
            pool_pre_ping = True  // Test connections before use
        )
        LOG("Database engine initialized")
    END CONSTRUCTOR

    METHOD get_connection():
        // Context manager for safe connection handling
        connection = this.engine.connect()
        TRY
            YIELD connection
        FINALLY
            connection.close()
        END TRY
    END METHOD

    METHOD execute_query(sql):
        // Validate that query is SELECT only
        sql_upper = UPPERCASE(TRIM(sql))
        IF NOT STARTS_WITH(sql_upper, "SELECT") THEN
            THROW ERROR("Only SELECT queries allowed")
        END IF

        // Check for dangerous keywords
        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]
        FOR EACH keyword IN dangerous_keywords DO
            IF CONTAINS(sql_upper, keyword) THEN
                THROW ERROR("Query contains forbidden keyword")
            END IF
        END FOR

        // Execute query using connection pool
        WITH this.get_connection() AS conn DO
            result = conn.execute(sql)
            rows = result.fetchall()
            RETURN CONVERT_TO_DICT_LIST(rows)
        END WITH
    END METHOD

    METHOD get_tables():
        // Use SQLAlchemy inspector to get table names
        inspector = INSPECT(this.engine)
        RETURN inspector.get_table_names()
    END METHOD

    METHOD get_table_schema(table_name):
        // Validate table exists
        IF table_name NOT IN this.get_tables() THEN
            THROW ERROR("Table not found")
        END IF

        // Get column information using inspector
        inspector = INSPECT(this.engine)
        columns = inspector.get_columns(table_name)

        // Convert to standard format
        schema = []
        FOR EACH column IN columns DO
            ADD TO schema {
                name: column.name,
                type: column.type,
                nullable: column.nullable,
                primary_key: column.primary_key
            }
        END FOR
        RETURN schema
    END METHOD

    METHOD close():
        // Dispose of all connections in pool
        this.engine.dispose()
        LOG("Database connections closed")
    END METHOD

END CLASS
```

#### 4. Update Server Initialization

**File: `src/server.py`**

Pseudocode:
```
CLASS LegacyBridgeServer:

    CONSTRUCTOR(connection_string = None, pool_size = 5):
        // Use factory to create appropriate database manager
        this.db = create_database_manager(connection_string, pool_size)
        this.server = CREATE_MCP_SERVER("legacy-bridge-sql-ai")
        this.register_handlers()

        LOG("Server initialized with pool size:", pool_size)
    END CONSTRUCTOR

    METHOD register_handlers():
        // Register MCP protocol handlers
        // (schema resources, query tools, etc.)
    END METHOD

    METHOD run():
        TRY
            // Start MCP server
            START_SERVER(this.server)
        FINALLY
            // Ensure cleanup on shutdown
            LOG("Shutting down database connections")
            this.db.close()
        END TRY
    END METHOD

END CLASS
```

---

## Configuration Management

### Environment Variables Structure

**Development (`.env.development`)**
```bash
# Database - SQLite for local development
SQLITE_PATH=data/chinook.db
DB_POOL_SIZE=1
DB_TIMEOUT=30

# Application
APP_ENV=development
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

**Production (`.env.production`)**
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@db-host:5432/production_db
DB_POOL_SIZE=10
DB_TIMEOUT=30
DB_POOL_RECYCLE=3600  # Recycle connections after 1 hour
DB_POOL_PRE_PING=true  # Verify connection health

# Application Configuration
APP_ENV=production
APP_PORT=8080
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
API_KEY_REQUIRED=true
ALLOWED_HOSTS=api.yourcompany.com,*.internal.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Monitoring
HEALTH_CHECK_ENABLED=true
METRICS_ENABLED=true
METRICS_PORT=9090
```

### Secrets Management Approaches

#### Option 1: Docker Secrets (Docker Swarm)
```bash
# Create secrets
echo "my_db_password" | docker secret create db_password -
echo "my_api_key" | docker secret create anthropic_api_key -

# Reference in docker-compose.yml
secrets:
  db_password:
    external: true
  anthropic_api_key:
    external: true
```

#### Option 2: Kubernetes Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: legacy-bridge-secrets
type: Opaque
stringData:
  database-url: postgresql://user:password@host:5432/db
  anthropic-api-key: sk-ant-xxxxx
```

#### Option 3: Cloud Provider Secrets
- **AWS**: Secrets Manager or Parameter Store
- **GCP**: Secret Manager
- **Azure**: Key Vault

**Implementation Approach:**
```
FUNCTION get_secret(secret_name):
    // Try cloud provider first
    IF CLOUD_PROVIDER_AVAILABLE THEN
        secret = FETCH_FROM_CLOUD_SECRETS(secret_name)
        RETURN secret
    END IF

    // Fallback to environment variables
    RETURN ENVIRONMENT_VARIABLE(secret_name)
END FUNCTION
```

---

## Docker Deployment

### Dockerfile Structure

**Multi-stage Dockerfile:**

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Install build dependencies for database drivers
RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production runtime
FROM python:3.11-slim

# Install runtime libraries only (not build tools)
RUN apt-get update && apt-get install -y \
    libpq5 unixodbc curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser run_server.py .

# Switch to non-root user
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose application port
EXPOSE 8080

# Run application
CMD ["python", "run_server.py"]
```

**Key Principles:**
- Use multi-stage builds to minimize image size
- Run as non-root user for security
- Include health checks
- Only copy necessary files
- Use `.dockerignore` to exclude unnecessary files

### Docker Compose for Local Testing

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/chinook
      - DB_POOL_SIZE=10
      - LOG_LEVEL=INFO
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=chinook
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:

networks:
  backend:
    driver: bridge
```

**Build and Run Commands:**
```bash
# Build the image
docker build -t legacy-bridge:latest .

# Tag for registry
docker tag legacy-bridge:latest registry.example.com/legacy-bridge:latest

# Push to registry
docker push registry.example.com/legacy-bridge:latest

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Remove volumes (caution: data loss)
docker-compose down -v
```

### Kubernetes Deployment

**Deployment Manifest Structure:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legacy-bridge
  labels:
    app: legacy-bridge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: legacy-bridge
  template:
    metadata:
      labels:
        app: legacy-bridge
    spec:
      containers:
      - name: legacy-bridge
        image: your-registry/legacy-bridge:latest
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: legacy-bridge-secrets
              key: database-url
        - name: DB_POOL_SIZE
          value: "10"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: legacy-bridge-service
spec:
  selector:
    app: legacy-bridge
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

**Auto-scaling Configuration:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: legacy-bridge-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: legacy-bridge
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Security Best Practices

### 1. Database Security

**Create Read-Only Database User:**

PostgreSQL:
```sql
-- Create read-only user
CREATE USER readonly_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE production_db TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;

-- Explicitly revoke dangerous permissions
REVOKE CREATE ON SCHEMA public FROM readonly_user;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM readonly_user;
```

MySQL:
```sql
-- Create read-only user
CREATE USER 'readonly_user'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT ON production_db.* TO 'readonly_user'@'%';
FLUSH PRIVILEGES;
```

### 2. Network Security

**Principles:**
- Use private networks for database connections
- Implement network policies in Kubernetes
- Use security groups in cloud environments
- Enable TLS/SSL for all database connections

**TLS/SSL Connection Strings:**
```bash
# PostgreSQL with SSL
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# MySQL with SSL
DATABASE_URL=mysql://user:pass@host:3306/db?ssl=true&ssl_ca=/path/to/ca.pem

# SQL Server with encryption
DATABASE_URL=mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes
```

### 3. Container Security

**Best Practices:**
- Run as non-root user (UID > 1000)
- Use read-only root filesystem where possible
- Scan images for vulnerabilities
- Keep base images updated
- Minimize image layers
- Use official base images

### 4. API Security

**Implementation Approach:**

Pseudocode for API authentication:
```
MIDDLEWARE authenticate_request(request):
    api_key = request.headers.get("X-API-Key")

    IF API_KEY_REQUIRED == true THEN
        IF api_key is None OR api_key != EXPECTED_API_KEY THEN
            RETURN ERROR(401, "Unauthorized")
        END IF
    END IF

    CONTINUE to next handler
END MIDDLEWARE
```

### 5. Secrets Management Rules

**Never do this:**
- ❌ Commit secrets to version control
- ❌ Hardcode passwords in code
- ❌ Log sensitive information
- ❌ Store secrets in environment variables in production (use secret managers)

**Always do this:**
- ✅ Use secret management systems
- ✅ Rotate secrets regularly
- ✅ Use least-privilege principle
- ✅ Encrypt secrets at rest and in transit

---

## Monitoring & Logging

### Health Check Endpoints

**Implementation Guidelines:**

**Endpoint: `/health` (Liveness Check)**
```
ENDPOINT /health:
    // Simple check - is the application running?
    RETURN {
        "status": "healthy",
        "service": "legacy-bridge-sql-ai",
        "timestamp": CURRENT_TIMESTAMP()
    }
END ENDPOINT
```

**Endpoint: `/ready` (Readiness Check)**
```
ENDPOINT /ready:
    TRY
        // Check database connectivity
        result = database.execute_query("SELECT 1")

        IF result is successful THEN
            RETURN STATUS 200 {
                "status": "ready",
                "database": "connected",
                "timestamp": CURRENT_TIMESTAMP()
            }
        END IF
    CATCH error
        LOG_ERROR("Readiness check failed:", error)
        RETURN STATUS 503 {
            "status": "not_ready",
            "database": "disconnected",
            "error": error.message
        }
    END TRY
END ENDPOINT
```

**Endpoint: `/metrics` (Prometheus)**
```
ENDPOINT /metrics:
    // Expose application metrics
    RETURN {
        "database_connection_pool_size": pool_size,
        "database_connection_pool_active": active_connections,
        "database_connection_pool_idle": idle_connections,
        "queries_total": total_queries_executed,
        "queries_failed": total_queries_failed,
        "query_duration_p50": median_query_time,
        "query_duration_p95": p95_query_time,
        "query_duration_p99": p99_query_time
    }
END ENDPOINT
```

### Structured Logging

**Logging Configuration Approach:**

```
CLASS JSONLogger:

    METHOD log(level, message, context):
        log_entry = {
            "timestamp": ISO8601_TIMESTAMP(),
            "level": level,
            "service": "legacy-bridge",
            "message": message,
            "context": context,
            "trace_id": CURRENT_TRACE_ID()
        }

        IF level == "ERROR" AND exception_present THEN
            log_entry["exception"] = {
                "type": exception.type,
                "message": exception.message,
                "stacktrace": exception.stacktrace
            }
        END IF

        PRINT_JSON(log_entry)
    END METHOD

END CLASS

CONFIGURE_LOGGING:
    log_level = ENVIRONMENT_VARIABLE("LOG_LEVEL", default="INFO")
    log_format = ENVIRONMENT_VARIABLE("LOG_FORMAT", default="json")

    IF log_format == "json" THEN
        USE JSONLogger
    ELSE
        USE StandardLogger
    END IF
END CONFIGURE
```

**What to Log:**
- ✅ Query execution (SQL, duration, result count)
- ✅ Connection pool metrics
- ✅ Error conditions with context
- ✅ Health check failures
- ✅ Configuration changes
- ✅ Startup and shutdown events

**What NOT to Log:**
- ❌ Sensitive data (passwords, API keys, PII)
- ❌ Full query results (only count)
- ❌ Stack traces in production (send to error tracking)

### Metrics Collection

**Key Metrics to Track:**

1. **Application Metrics:**
   - Request rate (requests/second)
   - Response time (p50, p95, p99)
   - Error rate (errors/minute)
   - Active connections

2. **Database Metrics:**
   - Query execution time
   - Connection pool utilization
   - Failed queries
   - Slow queries (> threshold)

3. **System Metrics:**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

**Prometheus Integration Approach:**
```
LIBRARY prometheus_client

METRICS:
    query_counter = Counter("db_queries_total", "Total database queries")
    query_errors = Counter("db_query_errors_total", "Failed queries")
    query_duration = Histogram("db_query_duration_seconds", "Query execution time")
    pool_connections = Gauge("db_pool_connections", "Active pool connections")

METHOD execute_query_with_metrics(sql):
    query_counter.increment()

    start_time = CURRENT_TIME()
    TRY
        result = database.execute_query(sql)
        duration = CURRENT_TIME() - start_time
        query_duration.observe(duration)
        RETURN result
    CATCH error
        query_errors.increment()
        THROW error
    END TRY
END METHOD
```

---

## Scaling Considerations

### Connection Pool Sizing

**Formula for Optimal Pool Size:**
```
Recommended pool_size = (number_of_cpu_cores * 2) + number_of_disks

For typical cloud applications:
- Small workload:  5-10 connections per instance
- Medium workload: 10-20 connections per instance
- Large workload:  20-50 connections per instance

Critical constraint:
(pool_size * number_of_instances) ≤ database_max_connections
```

**Example Calculation:**
```
Scenario:
- 10 application instances
- pool_size = 10 per instance
- Total connections needed = 10 * 10 = 100

Database max_connections must be ≥ 100 (+ buffer for admin)
Set database max_connections = 150
```

### Database Connection Limits

| Database | Default Max | Recommended Action |
|----------|-------------|-------------------|
| PostgreSQL | 100 | Increase to 200-500 for production |
| MySQL | 151 | Increase to 200-500 for production |
| SQL Server | 32,767 | Usually sufficient |
| Oracle | Dynamic | Configure based on workload |

**Increasing Connection Limits:**

PostgreSQL:
```sql
ALTER SYSTEM SET max_connections = 200;
-- Then restart database
```

MySQL:
```sql
SET GLOBAL max_connections = 200;
-- Add to my.cnf for persistence
```

### Horizontal Scaling Strategy

**Kubernetes Horizontal Pod Autoscaler:**

```
Scaling Logic:
    IF average_cpu_usage > 70% THEN
        IF current_replicas < max_replicas THEN
            scale_up()
        END IF
    ELSE IF average_cpu_usage < 30% THEN
        IF current_replicas > min_replicas THEN
            scale_down()
        END IF
    END IF

Configuration:
    min_replicas: 3
    max_replicas: 10
    target_cpu: 70%
    target_memory: 80%
```

### Caching Strategy

**Multi-Layer Caching Approach:**

**Layer 1: Application Memory Cache**
```
CACHE schema_cache (LRU, max_size=100):
    // Cache table schemas in memory

    METHOD get_table_schema(table_name):
        IF table_name IN schema_cache THEN
            RETURN schema_cache[table_name]
        END IF

        schema = database.get_table_schema(table_name)
        schema_cache[table_name] = schema
        RETURN schema
    END METHOD
END CACHE
```

**Layer 2: Distributed Cache (Redis)**
```
CACHE redis_cache (TTL=300 seconds):

    METHOD cached_query(sql):
        cache_key = HASH(sql)

        // Check cache first
        cached_result = redis.get(cache_key)
        IF cached_result is not None THEN
            RETURN DESERIALIZE(cached_result)
        END IF

        // Execute query if not cached
        result = database.execute_query(sql)

        // Store in cache with TTL
        redis.setex(cache_key, TTL=300, SERIALIZE(result))

        RETURN result
    END METHOD
END CACHE
```

**Cache Invalidation Strategy:**
- Set appropriate TTL based on data volatility
- Implement cache warming for frequently accessed data
- Use cache versioning for schema changes
- Monitor cache hit rate

### Load Balancing

**Distribution Strategies:**

1. **Round Robin**: Simple, equal distribution
2. **Least Connections**: Route to instance with fewest active connections
3. **IP Hash**: Consistent routing based on client IP
4. **Weighted**: Route based on instance capacity

**Health Check Integration:**
```
Load Balancer Configuration:
    - Health check endpoint: /ready
    - Health check interval: 10 seconds
    - Unhealthy threshold: 3 consecutive failures
    - Healthy threshold: 2 consecutive successes
    - Remove unhealthy instances from pool
    - Re-add when health checks pass
```

---

## Deployment Checklist

### Pre-Deployment

Configuration:
- [ ] Environment variables configured for production
- [ ] Secrets properly stored in secret manager (not in code/env files)
- [ ] Connection strings use appropriate credentials
- [ ] TLS/SSL enabled for database connections
- [ ] Connection pool sized appropriately for load

Security:
- [ ] Database user has read-only permissions only
- [ ] API authentication enabled (if applicable)
- [ ] Network policies/security groups configured
- [ ] Container runs as non-root user
- [ ] Secrets are encrypted at rest

Monitoring:
- [ ] Health check endpoints implemented
- [ ] Structured logging configured (JSON format)
- [ ] Metrics collection enabled
- [ ] Alerts configured for critical issues
- [ ] Log aggregation configured

Testing:
- [ ] Integration tests pass
- [ ] Load testing completed
- [ ] Failover testing done
- [ ] Database connection resilience tested

### Deployment

Infrastructure:
- [ ] Docker image built and scanned for vulnerabilities
- [ ] Image pushed to container registry
- [ ] Database connection tested from application
- [ ] DNS/Load balancer configured

Kubernetes:
- [ ] Secrets created in cluster
- [ ] ConfigMaps created
- [ ] Deployment manifest applied
- [ ] Service manifest applied
- [ ] Ingress configured (if needed)
- [ ] HPA configured

Validation:
- [ ] Health checks passing (`/health` returns 200)
- [ ] Readiness checks passing (`/ready` returns 200)
- [ ] Database queries executing successfully
- [ ] Logs flowing to monitoring system
- [ ] Metrics being collected

### Post-Deployment

Monitoring:
- [ ] Smoke tests executed and passed
- [ ] Connection pool metrics verified
- [ ] Database connection count within limits
- [ ] Response times meet SLA
- [ ] Error rates within acceptable range
- [ ] Resource utilization (CPU/memory) normal

Operations:
- [ ] Runbook created for common issues
- [ ] Escalation procedures documented
- [ ] Backup procedures verified
- [ ] Disaster recovery plan tested
- [ ] Documentation updated

---

## Troubleshooting

### Common Issues

#### Issue 1: Too Many Database Connections

**Symptoms:**
- Error: `FATAL: remaining connection slots are reserved`
- Application hangs waiting for connections

**Diagnosis:**
```
1. Check current database connections:
   SELECT count(*) FROM pg_stat_activity;  -- PostgreSQL
   SHOW PROCESSLIST;  -- MySQL

2. Check application pool settings:
   - Number of instances
   - Pool size per instance
   - Calculate: total = instances * pool_size

3. Check database max_connections setting
```

**Solutions:**
- Reduce pool size per instance
- Reduce number of application instances
- Increase database max_connections
- Implement connection recycling

#### Issue 2: Connection Pool Exhaustion

**Symptoms:**
- TimeoutError: Could not acquire database connection
- Slow response times during peak load

**Diagnosis:**
```
1. Check pool utilization metrics
2. Check query execution times
3. Look for slow queries blocking the pool
4. Check if connections are being properly released
```

**Solutions:**
- Increase pool size
- Increase pool timeout
- Optimize slow queries
- Ensure connections are released (use context managers)
- Enable connection recycling

#### Issue 3: Slow Query Performance

**Symptoms:**
- High query execution time (p95, p99)
- Database CPU high
- Application timeouts

**Diagnosis:**
```
1. Enable slow query logging
2. Analyze query execution plans
3. Check for missing indexes
4. Check database statistics
```

**Solutions:**
- Add appropriate indexes
- Optimize SQL queries
- Implement query result caching
- Set query timeout limits
- Consider read replicas for heavy read workloads

#### Issue 4: Memory Leaks

**Symptoms:**
- Gradual memory increase over time
- OOMKilled events in Kubernetes
- Container restarts

**Diagnosis:**
```
1. Monitor memory usage over time
2. Check for unclosed connections
3. Profile application memory
4. Check for large result sets
```

**Solutions:**
- Ensure proper connection cleanup
- Implement result set pagination
- Set memory limits appropriately
- Add connection recycling
- Restart pods periodically if needed

---

## Performance Tuning

### Database Connection Pool

**Key Parameters:**

```
pool_size:
  - Start with: (CPU cores * 2) + effective_spindles
  - Monitor and adjust based on metrics
  - Typical range: 5-20 per instance

pool_timeout:
  - How long to wait for an available connection
  - Default: 30 seconds
  - Adjust based on query complexity

pool_recycle:
  - Recycle connections after N seconds
  - Prevents stale connections
  - Typical: 1800-3600 seconds (30-60 minutes)

pool_pre_ping:
  - Test connection before use
  - Slightly slower but more reliable
  - Recommended: true for production
```

### Query Optimization

**Strategies:**

1. **Indexing**
   - Add indexes on frequently queried columns
   - Composite indexes for multi-column queries
   - Monitor index usage and remove unused indexes

2. **Query Optimization**
   - Use EXPLAIN/ANALYZE to understand query plans
   - Avoid SELECT *; specify needed columns only
   - Use appropriate JOINs
   - Add WHERE clauses to limit result sets

3. **Caching**
   - Cache static/semi-static data
   - Cache schema metadata
   - Set appropriate TTL based on data volatility

4. **Pagination**
   - Implement pagination for large result sets
   - Use LIMIT and OFFSET
   - Consider cursor-based pagination for better performance

---

## Additional Resources

### Documentation
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) - Database ORM and connection pooling
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/) - Container optimization
- [Kubernetes Production Guide](https://kubernetes.io/docs/setup/best-practices/) - K8s best practices
- [The Twelve-Factor App](https://12factor.net/) - Modern application methodology

### Database-Specific
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [MySQL Performance Tuning](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [SQL Server Best Practices](https://docs.microsoft.com/en-us/sql/relational-databases/best-practices-analyzer/)

### Monitoring & Observability
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [OpenTelemetry](https://opentelemetry.io/) - Distributed tracing

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Docker Benchmarks](https://www.cisecurity.org/benchmark/docker)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)

---

## Support

For implementation questions or issues:
1. Review the existing codebase in `src/database.py` for SQLite implementation patterns
2. Refer to SQLAlchemy documentation for multi-database support
3. Test thoroughly in development environment before production deployment
4. Monitor metrics closely during initial rollout

---

**Document Version:** 1.0
**Last Updated:** 2025-12-10
**Maintained By:** Development Team
