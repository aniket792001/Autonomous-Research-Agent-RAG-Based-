"""
AegisAudit AI - Unified Application Launcher.
Defaults to launching the Production-Grade Pure React UI on FastAPI (http://127.0.0.1:8000).
Supports legacy Streamlit mode via: streamlit run app.py -- --streamlit
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

def main():
    if "--streamlit" in sys.argv:
        from ui.dashboard import render_dashboard
        render_dashboard()
    else:
        print("\n" + "=" * 65)
        print("  [AegisAudit AI] Production-Grade Pure React Single Page App")
        print("  Backend API & Real-time SSE Stream Server Online")
        print("  Open in Browser: http://127.0.0.1:8000")
        print("=" * 65 + "\n")
        uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
