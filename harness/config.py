"""Paths and settings shared by every part of the harness.

Everything can be overridden with environment variables so the README can
document one place to change the model, host, or retrieval sizes.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The Obsidian vault. Only raw/ (unchanged originals), wiki/ (generated,
# reviewed notes) and index.md live here. Machine files stay outside it.
VAULT = Path(os.environ.get("WIKI_VAULT", ROOT / "vault"))
RAW = VAULT / "raw"
WIKI = VAULT / "wiki"
INDEX_MD = VAULT / "index.md"
SOURCES_MD = VAULT / "Source Catalog.md"

# Instructions the harness loads explicitly for each mode.
PROMPTS = ROOT / "prompts"
PERSONA = PROMPTS / "persona.md"             # chat voice + real capabilities
RESEARCH_RULES = PROMPTS / "wiki-instructions.md"  # ask-mode evidence rules
INGEST_RULES = PROMPTS / "ingest-instructions.md"  # how to write wiki notes
ROUTER_RULES = PROMPTS / "router.md"         # chat: should this turn retrieve?

# Machine files: retrieval chunks, source catalog, run logs. Never in vault/.
DATA = Path(os.environ.get("WIKI_DATA", ROOT / "data"))
CHUNKS = DATA / "chunks.jsonl"
CATALOG = DATA / "catalog.json"
EVIDENCE = Path(os.environ.get("WIKI_EVIDENCE", ROOT / "evidence"))
RUN_LOG_DIR = EVIDENCE / "runs"
DRAFTS = ROOT / "outputs" / "drafts"         # /save in chat writes here

# Model + runtime. Local Ollama is the only (and default) execution mode.
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
MODEL = os.environ.get("WIKI_MODEL", "gemma4:e4b")
NUM_CTX = int(os.environ.get("WIKI_NUM_CTX", "8192"))

# Retrieval sizes. ~900 characters is roughly 200 tokens, so 5 passages plus
# instructions stay far below the context window.
CHUNK_TARGET = int(os.environ.get("WIKI_CHUNK_CHARS", "900"))
CHUNK_MAX = int(CHUNK_TARGET * 1.6)
TOP_K = int(os.environ.get("WIKI_TOP_K", "5"))
CHAT_HISTORY_MESSAGES = 10   # last 5 exchanges are sent back to the model

# How much of one source ingestion sends to Gemma in a single call.
INGEST_MAX_CHARS = int(os.environ.get("WIKI_INGEST_CHARS", "12000"))
