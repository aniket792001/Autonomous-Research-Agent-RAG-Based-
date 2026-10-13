"""
Report Exporter for AegisAudit AI.
Exports audit reports to Markdown, CSV, and JSON formats for enterprise distribution.
"""

import io
import csv
import json
from models.audit_schema import FullAuditReport

class ReportExporter:
    @staticmethod
    def to_markdown(report: FullAuditReport) -> str:
        md = []
        md.append(f"# 🛡️ AegisAudit AI - Executive Compliance Report")
        md.append(f"**Audit ID:** `{report.audit_id}` | **Date:** {report.timestamp}")
        md.append(f"**Standard:** {report.standard_name} | **Target Document:** {report.policy_name}\n")
        
        md.append("## 📈 Executive Summary")
        md.append(f"- **Overall Compliance:** **{report.summary.overall_compliance_percentage}%**")
        md.append(f"- **Total Clauses Audited:** {report.summary.total_clauses_audited}")
        md.append(f"- **Compliant:** {report.summary.compliant_count}")
        md.append(f"- **Partially Compliant:** {report.summary.partially_compliant_count}")
        md.append(f"- **Non-Compliant:** {report.summary.non_compliant_count}\n")
        md.append(report.summary.executive_overview)
        md.append("\n---\n")

        md.append("## 📋 Detailed Compliance Audit Matrix\n")
        md.append("| Clause ID | Title | Status | Risk Level | Evidence Citations | Key Gap / Remediations |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

        for f in report.findings:
            citation_str = ", ".join([f"Page {c.page_number}" for c in f.citations]) or "None"
            status_badge = f"**{f.status.value}**"
            md.append(
                f"| `{f.clause_id}` | {f.clause_title} | {status_badge} | {f.risk_level.value} | {citation_str} | **Gap:** {f.gap_analysis}<br>**Fix:** {f.remediation_recommendation} |"
            )

        return "\n".join(md)

    @staticmethod
    def to_csv(report: FullAuditReport) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Clause ID", "Title", "Requirement", "Status", "Risk Level",
            "Citations", "Evidence Found", "Gap Analysis", "Remediation Recommendation"
        ])
        for f in report.findings:
            citations_str = "; ".join([f"Page {c.page_number} ({c.document_name})" for c in f.citations])
            writer.writerow([
                f.clause_id,
                f.clause_title,
                f.requirement_summary,
                f.status.value,
                f.risk_level.value,
                citations_str,
                f.evidence_found,
                f.gap_analysis,
                f.remediation_recommendation
            ])
        return output.getvalue()

    @staticmethod
    def to_json(report: FullAuditReport) -> str:
        return report.model_dump_json(indent=2)
