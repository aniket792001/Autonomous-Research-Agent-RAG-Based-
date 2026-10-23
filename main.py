"""
Server launcher for AegisAudit AI FastAPI backend.
"""

import sys

# Ensure UTF-8 output on Windows consoles to prevent cp1252 charmap encoding errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import uvicorn
from core.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} Backend on http://127.0.0.1:8000 ...")
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
