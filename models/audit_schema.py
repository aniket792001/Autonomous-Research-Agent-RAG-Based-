"""
Pydantic schemas and data contracts for audit entities.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ComplianceStatus(str, Enum):
    COMPLIANT = "Compliant"
    PARTIALLY_COMPLIANT = "Partially Compliant"
    NON_COMPLIANT = "Non-Compliant"
    NOT_APPLICABLE = "Not Applicable"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ClauseRequirement(BaseModel):
    clause_id: str = Field(description="Unique regulatory identifier, e.g., 'ISO-27001:A.9.2.1' or 'GDPR-Art.32'")
    title: str = Field(description="Short title or clause category")
    description: str = Field(description="Exact mandate or obligation stated in the standard")
    category: Optional[str] = Field(default="General", description="Security Domain or Compliance Topic")

class Citation(BaseModel):
    document_name: str
    page_number: int
    matched_snippet: str

class AuditFinding(BaseModel):
    clause_id: str = Field(description="Referenced clause ID")
    clause_title: str = Field(description="Referenced clause title")
    requirement_summary: str = Field(description="Summary of the requirement")
    evidence_found: str = Field(description="Exact factual evidence found in policy, or 'None found'")
    citations: List[Citation] = Field(default_factory=list, description="Document page and snippet citations")
    status: ComplianceStatus = Field(description="Compliance determination")
    risk_level: RiskLevel = Field(description="Risk if not compliant")
    gap_analysis: str = Field(description="Detailed explanation of compliance gaps or ambiguities")
    remediation_recommendation: str = Field(description="Actionable steps the organization must take to achieve compliance")

class AuditSummary(BaseModel):
    total_clauses_audited: int
    compliant_count: int
    partially_compliant_count: int
    non_compliant_count: int
    overall_compliance_percentage: float
    risk_breakdown: dict
    executive_overview: str

class FullAuditReport(BaseModel):
    audit_id: str
    standard_name: str
    policy_name: str
    timestamp: str
    summary: AuditSummary
    findings: List[AuditFinding]
