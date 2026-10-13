"""
Matrix Generator & Synthesis Agent for AegisAudit AI.
Aggregates findings, computes overall compliance statistics, and generates the executive report.
"""

from typing import List
import uuid
from datetime import datetime
from models.audit_schema import (
    AuditFinding,
    AuditSummary,
    FullAuditReport,
    ComplianceStatus,
    RiskLevel
)
from agents.base_agent import BaseAgent
from core.logger import logger

class MatrixGeneratorAgent(BaseAgent):
    def generate_report(
        self,
        standard_name: str,
        policy_name: str,
        findings: List[AuditFinding]
    ) -> FullAuditReport:
        """
        Synthesizes the entire audit, computes compliance rates, and generates an executive overview.
        """
        logger.info(f"MatrixGeneratorAgent: Generating full audit report for {standard_name} vs {policy_name}...")

        total = len(findings)
        compliant = sum(1 for f in findings if f.status == ComplianceStatus.COMPLIANT)
        partial = sum(1 for f in findings if f.status == ComplianceStatus.PARTIALLY_COMPLIANT)
        non_compliant = sum(1 for f in findings if f.status == ComplianceStatus.NON_COMPLIANT)

        percentage = round(((compliant + (0.5 * partial)) / max(1, total)) * 100.0, 1)

        risk_counts = {
            "Critical": sum(1 for f in findings if f.risk_level == RiskLevel.CRITICAL),
            "High": sum(1 for f in findings if f.risk_level == RiskLevel.HIGH),
            "Medium": sum(1 for f in findings if f.risk_level == RiskLevel.MEDIUM),
            "Low": sum(1 for f in findings if f.risk_level == RiskLevel.LOW)
        }

        # Prompt for concise Executive Overview
        prompt = f"""
You are the Chief Information Security Officer (CISO).
Draft a concise, high-level Executive Summary (2-3 paragraphs) based on these audit statistics:

Standard Audited: {standard_name}
Target Document: {policy_name}
Total Clauses: {total}
Compliant: {compliant}
Partially Compliant: {partial}
Non-Compliant: {non_compliant}
Overall Compliance Score: {percentage}%
Critical Risks: {risk_counts['Critical']}
High Risks: {risk_counts['High']}

Highlight key vulnerability areas, legal exposure, and recommended immediate next steps for leadership.
"""
        executive_text = self.call_llm(prompt)
        if not executive_text or len(executive_text) < 20:
            executive_text = (
                f"The compliance review for {policy_name} against {standard_name} concluded an overall "
                f"compliance posture of {percentage}%. Out of {total} examined clauses, {compliant} controls "
                f"fully satisfied requirements, while {non_compliant} presented critical/high security gaps. "
                f"Immediate priority should be directed toward rectifying high-risk non-compliance items."
            )

        summary = AuditSummary(
            total_clauses_audited=total,
            compliant_count=compliant,
            partially_compliant_count=partial,
            non_compliant_count=non_compliant,
            overall_compliance_percentage=percentage,
            risk_breakdown=risk_counts,
            executive_overview=executive_text
        )

        report = FullAuditReport(
            audit_id=f"AUDIT-{uuid.uuid4().hex[:8].upper()}",
            standard_name=standard_name,
            policy_name=policy_name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=summary,
            findings=findings
        )

        logger.info(f"MatrixGeneratorAgent: Report {report.audit_id} generated successfully.")
        return report
