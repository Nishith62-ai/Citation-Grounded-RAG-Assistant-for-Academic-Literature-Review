"""Central settings. Edit the values here (or override via .env)."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
VECTORSTORE_DIR = BASE_DIR / "data" / "vectorstore"
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

# Chunking: easy to tune.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# Retrieval: how many chunks go to the LLM.
TOP_K = int(os.getenv("TOP_K", 5))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")