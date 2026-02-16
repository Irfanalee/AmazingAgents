---
description: Invoke Agent Qazi to analyze the latest uploaded video
---

1. Find the latest uploaded file in `backend/uploads`.
2. Extract the file ID from the filename.
3. Call the backend API to trigger Agent Qazi.

```bash
# Find latest file
LATEST_FILE=$(ls -t backend/uploads | head -n 1)
FILE_ID=$(echo $LATEST_FILE | cut -d'_' -f 1)

echo "Invoking Agent Qazi for file: $LATEST_FILE (ID: $FILE_ID)"

# Trigger Qazi
curl -X POST "http://localhost:8000/agent/qazi/$FILE_ID"
```
