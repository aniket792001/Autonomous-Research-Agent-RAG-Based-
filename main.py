"""
Server launcher for AegisAudit AI FastAPI backend.
"""

import uvicorn
from core.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.APP_NAME} Backend on http://127.0.0.1:8000 ...")
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
