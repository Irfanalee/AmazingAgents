---
description: Invoke Agent Trond to process the latest analyzed job
---

1. Find the latest job ID from the backend logs or state (simulated here by checking logs or just assuming the user knows it, but for automation we'll grab the latest job ID from the API if possible, or just ask the user).
2. **Simpler approach for now:** We will list the active jobs and ask the user to pick one, OR just pick the latest one if we can query it.
3. Since we don't have a CLI to query jobs easily, we'll assume the user wants to process the *same* file we just analyzed.

**Better approach:**
The `/agent/trond` endpoint takes a `job_id`. We need to know the `job_id` that Qazi just finished.

For this workflow, we will:
1. List recent jobs from the API.
2. Extract the latest Job ID.
3. Trigger Trond.

```bash
# Get latest job ID (requires jq)
# If jq is not installed, we might need a simpler grep
# Assuming we are running this in the dev environment

echo "Fetching latest job..."
# This is a bit hacky without jq, but let's try to grep the ID from the jobs endpoint
# Note: In a real scenario, we'd use a proper script.
# For now, let's just tell the user how to call it if they know the ID, 
# OR we can try to automate it if we had a way to store the ID from the previous step.

# Let's try to get the latest job ID by hitting the debug endpoint if we had one.
# Actually, let's just list the jobs and let the user see.
# Wait, the user wants to just type /trond.

# Let's assume the user just ran /qazi and we want to continue.
# We can't easily share state between these bash blocks across different turns.
# BUT, we can look at the backend logs to find the latest job ID!

# Grep the latest "Agent Qazi Summoned" job ID from logs
JOB_ID=$(docker-compose logs backend | grep "Agent Qazi Summoned" | tail -n 1 | grep -oE "jobs/[a-f0-9-]+" | cut -d'/' -f2)

if [ -z "$JOB_ID" ]; then
  echo "Could not find a recent Qazi job to process."
  exit 1
fi

echo "Invoking Agent Trond for Job ID: $JOB_ID"
curl -X POST "http://localhost:8000/agent/trond/$JOB_ID"
```
