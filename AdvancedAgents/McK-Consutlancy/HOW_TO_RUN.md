# NPI Strategy Suite — How to Run

## What you need

| Requirement | Where to get it |
|-------------|-----------------|
| Python 3.9 or newer | https://python.org/downloads |
| An Anthropic API key | https://console.anthropic.com |

You do **not** need Node.js. The UI is pre-built and shipped with the repo.

---

## First-time setup (one minute)

1. Open **Terminal** (Mac) or **Command Prompt / PowerShell** (Windows).
2. `cd` into this folder.
3. Create a virtual environment and install dependencies:

**Mac / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows**
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Starting the app

### Mac — double-click launcher
Double-click **`Start App.command`** in Finder.
A Terminal window opens, the server starts, and your browser opens automatically.

### Windows — double-click launcher
Double-click **`Start App.bat`**.
A Command Prompt window opens, the server starts, and your browser opens automatically.

### Manual start (any OS)
```bash
# activate the venv first (see above), then:
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
Open **http://localhost:8000** in your browser.

---

## Using the app

1. The browser opens to the home page.
2. Paste your **Anthropic API key** into the key field (it stays in your browser only — never sent to us).
3. Fill in your business context (company name, product, market, etc.).
4. Pick any of the 12 strategic frameworks and click **Analyse**.
5. Results stream in real time. Export to **DOCX** or **PDF** when done.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "python not found" | Use `python3` instead of `python`, or reinstall Python and tick "Add to PATH" |
| "No module named fastapi" | Run `pip install -r requirements.txt` inside the activated venv |
| Port 8000 already in use | Change `--port 8000` to `--port 8001` (and open http://localhost:8001) |
| API key error | Double-check you pasted the full key starting with `sk-ant-` |
