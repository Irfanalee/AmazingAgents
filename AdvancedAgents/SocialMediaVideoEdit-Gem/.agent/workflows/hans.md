---
description: Invoke Agent Hans to check frontend health and configuration
---

1. Check if the frontend container is running.
2. Verify environment variables.
3. Run linting/type checking if available.

```bash
echo "Agent Hans: Starting Frontend Health Check..."

# 1. Check Container
if docker-compose ps | grep -q "frontend"; then
    echo "✅ Frontend container is running."
else
    echo "❌ Frontend container is NOT running."
fi

# 2. Check API Connection
echo "Checking API connectivity..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Backend API is reachable (Status: 200)."
else
    echo "❌ Backend API is unreachable (Status: $STATUS_CODE)."
fi

# 3. Run Lint (inside container)
echo "Running frontend diagnostics..."
docker-compose exec frontend npm run lint || echo "⚠️ Linting found issues (or failed to run)."

echo "Agent Hans: Health Check Complete."
```
