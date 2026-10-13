"""
Autonomous Multi-Agent Core for AegisAudit AI.
"""

from agents.base_agent import BaseAgent
from agents.clause_extractor import ClauseExtractorAgent
from agents.evidence_hunter import EvidenceHunterAgent
from agents.compliance_auditor import ComplianceAuditorAgent
from agents.matrix_generator import MatrixGeneratorAgent
from agents.orchestrator import AuditOrchestrator

__all__ = [
    "BaseAgent",
    "ClauseExtractorAgent",
    "EvidenceHunterAgent",
    "ComplianceAuditorAgent",
    "MatrixGeneratorAgent",
    "AuditOrchestrator",
]
