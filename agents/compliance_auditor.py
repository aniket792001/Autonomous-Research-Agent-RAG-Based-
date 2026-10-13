"""
Compliance Auditor Agent (Adversarial Critic) for AegisAudit AI.
Evaluates evidence against regulatory requirements, checks for loopholes/omissions, and determines compliance status.
"""

from typing import List
from models.audit_schema import (
    ClauseRequirement,
    Citation,
    AuditFinding,
    ComplianceStatus,
    RiskLevel
)
from agents.base_agent import BaseAgent
from core.logger import logger

class ComplianceAuditorAgent(BaseAgent):
    def audit_clause(
        self,
        clause: ClauseRequirement,
        evidence_text: str,
        citations: List[Citation]
    ) -> AuditFinding:
        """
        Adversarially evaluates if the found policy evidence genuinely satisfies the regulatory mandate.
        """
        logger.info(f"ComplianceAuditorAgent: Auditing clause {clause.clause_id}...")

        prompt = f"""
You are an uncompromising Lead Information Security & Regulatory Compliance Auditor.
Your objective: Evaluate compliance strictly based ONLY on the evidence provided.

MANDATE REQUIREMENT:
Clause ID: {clause.clause_id}
Title: {clause.title}
Mandate Description: {clause.description}

COMPANY POLICY EVIDENCE FOUND:
\"\"\"
{evidence_text}
\"\"\"

CRITICAL EVALUATION RULES:
1. If the company evidence specifically, verifiably implements the mandate, mark as "Compliant", risk "Low".
2. If the policy mentions the concept vaguely or incompletely without formal procedures, mark as "Partially Compliant", risk "Medium".
3. If no evidence is found or the requirement is ignored, mark as "Non-Compliant", risk "High" or "Critical".
4. Point out exact loopholes, ambiguities, or missing controls in "gap_analysis".
5. Provide actionable, practical engineering/operational fixes in "remediation_recommendation".

Return ONLY a JSON object:
{{
  "status": "Compliant" | "Partially Compliant" | "Non-Compliant",
  "risk_level": "Low" | "Medium" | "High" | "Critical",
  "gap_analysis": "string explaining the gap or why it satisfies",
  "remediation_recommendation": "string describing steps to become compliant"
}}
"""

        raw_response = self.call_llm(prompt)
        parsed = self.extract_json(raw_response)

        status = ComplianceStatus.NON_COMPLIANT
        risk = RiskLevel.HIGH
        gap_analysis = "Evidence does not satisfy formal regulatory criteria."
        remediation = "Establish operational policy chapters and automated technical verification controls."

        if isinstance(parsed, dict):
            status_str = parsed.get("status", "").strip()
            if "partially" in status_str.lower():
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            elif "compliant" in status_str.lower() and "non" not in status_str.lower():
                status = ComplianceStatus.COMPLIANT
            elif "non" in status_str.lower():
                status = ComplianceStatus.NON_COMPLIANT

            risk_str = parsed.get("risk_level", "").strip()
            if "critical" in risk_str.lower():
                risk = RiskLevel.CRITICAL
            elif "high" in risk_str.lower():
                risk = RiskLevel.HIGH
            elif "medium" in risk_str.lower():
                risk = RiskLevel.MEDIUM
            elif "low" in risk_str.lower():
                risk = RiskLevel.LOW

            gap_analysis = parsed.get("gap_analysis", gap_analysis)
            remediation = parsed.get("remediation_recommendation", remediation)

        # Build AuditFinding
        finding = AuditFinding(
            clause_id=clause.clause_id,
            clause_title=clause.title,
            requirement_summary=clause.description,
            evidence_found=evidence_text[:400] + ("..." if len(evidence_text) > 400 else ""),
            citations=citations,
            status=status,
            risk_level=risk,
            gap_analysis=gap_analysis,
            remediation_recommendation=remediation
        )

        logger.info(f"ComplianceAuditorAgent: Clause {clause.clause_id} determination: {status.value} (Risk: {risk.value})")
        return finding
