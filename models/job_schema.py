"""
Job Schemas and Event Streaming models for Phase 2 Async Audits.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from models.audit_schema import FullAuditReport

class AuditJobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentLogEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    agent_name: str
    message: str
    progress_pct: float

class AuditJobResponse(BaseModel):
    job_id: str
    status: AuditJobStatus
    progress_pct: float
    current_step: str
    created_at: str
    updated_at: str
    standard_filename: str
    policy_filename: str
    result: Optional[FullAuditReport] = None
    error: Optional[str] = None
