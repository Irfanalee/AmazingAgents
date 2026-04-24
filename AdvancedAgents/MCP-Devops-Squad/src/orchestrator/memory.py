import datetime
import json
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from src.utils.logger import setup_logger
from src.mcp.mcp_config import get_mcp_config
from src.agents.monitor import MetricUpdate

class IncidentMemory(BaseModel):
    """Represents a resolved incident stored in the Chroma vector database."""
    symptoms_description: str
    incident_id: str
    timestamp: str
    resource_id: str
    root_cause: str
    remediation_action: str
    resolution_summary: str

class MemoryManager:
    """Manages long-term incident memory using ChromaDB."""
    
    def __init__(self):
        self.logger = setup_logger("Memory-Manager")
        self.config = get_mcp_config()
        self.vectorstore = self._init_vectorstore()

    def _init_vectorstore(self) -> Optional[Chroma]:
        """Initialize ChromaDB with a provider-agnostic embedding model."""
        try:
            embeddings = self._init_embeddings()
            if not embeddings:
                return None
                
            return Chroma(
                collection_name="sre_incident_memory",
                embedding_function=embeddings,
                persist_directory=self.config.CHROMA_PERSIST_DIR
            )
        except Exception as e:
            self.logger.warning("chroma_init_failed", error=str(e), fallback="memory_disabled")
            return None

    def _init_embeddings(self):
        """Initialize embeddings based on AI provider."""
        provider = self.config.AI_PROVIDER.lower()
        try:
            if provider == "google":
                from langchain_google_vertexai import VertexAIEmbeddings
                return VertexAIEmbeddings(model_name="text-embedding-004")
            elif provider == "openai":
                from langchain_openai import OpenAIEmbeddings
                return OpenAIEmbeddings(model="text-embedding-3-small", api_key=self.config.AI_API_KEY)
            elif provider == "ollama":
                from langchain_ollama import OllamaEmbeddings
                return OllamaEmbeddings(model=self.config.AI_MODEL, base_url=self.config.AI_BASE_URL)
            else:
                return None
        except Exception as e:
            self.logger.error("embeddings_init_failed", provider=provider, error=str(e))
            return None

    def save_resolved_incident(self, context: Any):
        """Extract learning from a resolved context and save to Chroma."""
        if not self.vectorstore or not hasattr(context, "is_resolved") or not context.is_resolved or not context.history:
            return

        self.logger.info("saving_incident_to_memory", resource=context.initial_trigger.resource_id)
        
        # 1. Create Symptoms Description (the document to embed)
        symptoms = f"Incident on {context.initial_trigger.resource_id}: CPU={context.initial_trigger.cpu_percent}%, MEM={context.initial_trigger.memory_percent}%"
        
        # 2. Extract Root Cause (usually from the first or second action)
        # For mock/simplicity, we take the result of the Debugger or Sargent
        root_cause = "Unknown"
        for entry in context.history:
            if entry.agent_name in ["Debugger-Agent", "Sargent-Agent"]:
                root_cause = entry.result
                break
        
        # 3. Extract Remediation (from the Janitor action)
        remediation = "No fix recorded"
        for entry in context.history:
            if entry.agent_name == "Janitor-Agent":
                remediation = json.dumps(entry.task_kwargs)
                break
        
        # 4. Create Metadata
        metadata = {
            "incident_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "resource_id": context.initial_trigger.resource_id,
            "root_cause": root_cause,
            "remediation_action": remediation,
            "resolution_summary": f"Resolved {symptoms} by applying {remediation}"
        }
        
        # 5. Save to Chroma
        self.vectorstore.add_texts(
            texts=[symptoms],
            metadatas=[metadata],
            ids=[metadata["incident_id"]]
        )
        self.logger.info("incident_memory_saved", id=metadata["incident_id"])

    def search_similar_incidents(self, metrics: MetricUpdate, k: int = 2) -> List[IncidentMemory]:
        """Search for past incidents with similar symptoms."""
        if not self.vectorstore:
            return []
            
        symptoms = f"Incident on {metrics.resource_id}: CPU={metrics.cpu_percent}%, MEM={metrics.memory_percent}%"
        self.logger.info("searching_memory", symptoms=symptoms)
        
        try:
            results = self.vectorstore.similarity_search(symptoms, k=k)
            memories = []
            for doc in results:
                m = doc.metadata
                memories.append(IncidentMemory(
                    symptoms_description=doc.page_content,
                    incident_id=m.get("incident_id", ""),
                    timestamp=m.get("timestamp", ""),
                    resource_id=m.get("resource_id", ""),
                    root_cause=m.get("root_cause", ""),
                    remediation_action=m.get("remediation_action", ""),
                    resolution_summary=m.get("resolution_summary", "")
                ))
            return memories
        except Exception as e:
            self.logger.warning("memory_search_failed", error=str(e))
            return []

if __name__ == "__main__":
    # Basic test (will fail if no provider keys set, but verifies imports/logic)
    mgr = MemoryManager()
    print("Memory Manager Initialized.")
