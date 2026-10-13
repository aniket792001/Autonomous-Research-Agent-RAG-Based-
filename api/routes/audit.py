"""
Audit REST API routes for AegisAudit AI.
Includes Phase 1 RBAC and Phase 2 Async Job Execution & SSE Event Streaming.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List, Dict, Any

from models.audit_schema import FullAuditReport
from models.user_schema import UserResponse, UserRole
from models.job_schema import AuditJobResponse
from agents.orchestrator import AuditOrchestrator
from db.storage import AuditDatabase
from core.config import settings
from core.job_manager import job_manager
from api.deps import get_current_user, require_roles

router = APIRouter(prefix="/api/audit", tags=["Audit"])
db = AuditDatabase()

class RunAuditRequest(BaseModel):
    standard_filename: str
    policy_filename: str
    max_clauses: Optional[int] = 15

# --- SYNCHRONOUS RUN (Direct execution) ---
@router.post("/run", response_model=FullAuditReport)
def run_compliance_audit_sync(
    req: RunAuditRequest,
    current_user: UserResponse = Depends(require_roles([UserRole.ADMIN, UserRole.AUDITOR]))
):
    """
    Executes a multi-agent audit synchronously.
    Requires 'admin' or 'auditor' role.
    """
    standard_path = settings.DATA_DIR / req.standard_filename
    policy_path = settings.DATA_DIR / req.policy_filename

    if not standard_path.exists():
        raise HTTPException(status_code=404, detail=f"Standard file not found: {req.standard_filename}")
    if not policy_path.exists():
        raise HTTPException(status_code=404, detail=f"Policy file not found: {req.policy_filename}")

    orchestrator = AuditOrchestrator()
    try:
        report = orchestrator.run_audit(
            standard_path=standard_path,
            policy_path=policy_path,
            max_clauses=req.max_clauses or 15
        )
        db.save_report(report)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

# --- ASYNC JOB QUEUE (Phase 2) ---
@router.post("/jobs/submit", response_model=AuditJobResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_async_audit_job(
    req: RunAuditRequest,
    current_user: UserResponse = Depends(require_roles([UserRole.ADMIN, UserRole.AUDITOR]))
):
    """
    Submits a background audit job. Returns 202 Accepted with job_id.
    """
    standard_path = settings.DATA_DIR / req.standard_filename
    policy_path = settings.DATA_DIR / req.policy_filename

    if not standard_path.exists():
        raise HTTPException(status_code=404, detail=f"Standard file not found: {req.standard_filename}")
    if not policy_path.exists():
        raise HTTPException(status_code=404, detail=f"Policy file not found: {req.policy_filename}")

    job_id = job_manager.create_job(req.standard_filename, req.policy_filename)
    job_manager.start_job(job_id, max_clauses=req.max_clauses or 15)
    return job_manager.get_job(job_id)

@router.get("/jobs/{job_id}/status", response_model=AuditJobResponse)
def get_job_status(job_id: str, current_user: UserResponse = Depends(get_current_user)):
    """
    Polls the progress status of an asynchronous audit job.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

@router.get("/jobs/{job_id}/stream")
def stream_job_agent_events(job_id: str):
    """
    Streams live Agent execution logs via Server-Sent Events (SSE).
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return StreamingResponse(
        job_manager.stream_job_events(job_id),
        media_type="text/event-stream"
    )

# --- AUDIT HISTORY ---
@router.get("/history", response_model=List[Dict[str, Any]])
def get_audit_history(current_user: UserResponse = Depends(get_current_user)):
    """Retrieves metadata of all past compliance audits. Requires authenticated user."""
    return db.list_audits()

@router.get("/{audit_id}", response_model=FullAuditReport)
def get_audit_report(audit_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Retrieves a full audit report by ID. Requires authenticated user."""
    report = db.get_report(audit_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Audit {audit_id} not found")
    return report
