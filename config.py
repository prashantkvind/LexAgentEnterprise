import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
# Folder Configuration (Update folder name here for primary search)
PRIVATE_DOCS_DIR_NAME = os.environ.get("PRIVATE_DOCS_DIR_NAME", "private_docs")
PRIVATE_DOCS_DIR = BASE_DIR / PRIVATE_DOCS_DIR_NAME
GENERATED_DOCS_DIR = BASE_DIR / "generated_docs"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# Ensure required directories exist
PRIVATE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# LLM & Model Configuration for Search & Legal Reasoning
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")  # Options: llama3, mistral, gemma2, legal-llama
SEARCH_MODEL_PROVIDER = os.environ.get("SEARCH_MODEL_PROVIDER", "auto") # Options: auto, tavily, duckduckgo, offline

# Vector Store & Embeddings Configuration
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_COLLECTION_NAME = "lexagent_private_docs"
RAG_TOP_K = 3
RAG_DISTANCE_THRESHOLD = 0.75  # Distance threshold for relevant facts

# Search Configuration
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
ENABLE_DUCKDUCKGO_FALLBACK = True

# Legal Drafting Defaults
DEFAULT_JURISDICTION = "RERA Tribunal / State High Court"

# Enterprise Microservice & Security Configuration
ENABLE_ENTERPRISE_SECURITY = os.environ.get("ENABLE_ENTERPRISE_SECURITY", "true").lower() == "true"
ENTERPRISE_TENANT_ID = os.environ.get("ENTERPRISE_TENANT_ID", "tenant_law_firm_alpha")
FASTAPI_PORT = int(os.environ.get("FASTAPI_PORT", 8000))
AUDIT_LOG_FILE = BASE_DIR / "logs" / "enterprise_audit.jsonl"

