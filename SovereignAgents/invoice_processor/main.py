import uvicorn
import gradio as gr
from fastapi import FastAPI

from api import router
from database import init_db
from ui import demo  # Gradio Blocks

app = FastAPI(
    title="Invoice Processor",
    description="Automated invoice processing powered by doc-intel via Ollama",
    version="1.0.0",
)

app.include_router(router)

# Mount the Gradio UI at /ui
app = gr.mount_gradio_app(app, demo, path="/ui")


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Invoice Processor",
        "api_docs": "/docs",
        "ui": "/ui",
        "status": "running",
    }


if __name__ == "__main__":
    init_db()
    print("Invoice Processor starting...")
    print("  REST API : http://localhost:8000")
    print("  API Docs : http://localhost:8000/docs")
    print("  Web UI   : http://localhost:8000/ui")
    uvicorn.run(app, host="0.0.0.0", port=8000)
