"""
Audit Orchestrator for AegisAudit AI.
Coordinates the multi-agent execution pipeline, emits telemetry, and returns the full audit report.
"""

from typing import Callable, Optional, List
from pathlib import Path

from models.audit_schema import FullAuditReport, AuditFinding, ClauseRequirement
from rag.document_parser import DocumentParser
from rag.text_splitter import AuditTextSplitter
from rag.vector_store import AuditVectorStore
from agents.clause_extractor import ClauseExtractorAgent
from agents.evidence_hunter import EvidenceHunterAgent
from agents.compliance_auditor import ComplianceAuditorAgent
from agents.matrix_generator import MatrixGeneratorAgent
from core.logger import logger

class AuditOrchestrator:
    def __init__(self):
        self.clause_extractor = ClauseExtractorAgent()
        self.compliance_auditor = ComplianceAuditorAgent()
        self.matrix_generator = MatrixGeneratorAgent()

    def run_audit(
        self,
        standard_path: Path,
        policy_path: Path,
        max_clauses: int = 15,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> FullAuditReport:
        """
        Executes end-to-end autonomous audit between a standard framework and a company policy document.
        """
        def update_progress(message: str, pct: float):
            logger.info(f"Progress ({int(pct*100)}%): {message}")
            if progress_callback:
                progress_callback(message, pct)

        update_progress("Parsing regulatory framework and policy documents...", 0.05)
        
        # 1. Parse standard framework
        standard_pages = DocumentParser.parse_pdf(standard_path)
        standard_full_text = "\n\n".join([p["text"] for p in standard_pages])

        # 2. Parse and index company policy
        update_progress("Indexing company policy into vector store...", 0.15)
        policy_pages = DocumentParser.parse_pdf(policy_path)
        splitter = AuditTextSplitter()
        policy_chunks = splitter.split_pages(policy_pages)

        vector_store = AuditVectorStore()
        vector_store.add_chunks(policy_chunks)

        # 3. Extract regulatory clauses
        update_progress("ClauseExtractorAgent: Decomposing regulation into mandates...", 0.30)
        clauses: List[ClauseRequirement] = self.clause_extractor.extract_clauses(
            standard_full_text,
            max_clauses=max_clauses
        )

        evidence_hunter = EvidenceHunterAgent(vector_store)
        findings: List[AuditFinding] = []

        # 4. Audit each clause iteratively with Evidence Hunter and Compliance Auditor
        total_clauses = len(clauses)
        for i, clause in enumerate(clauses):
            progress_ratio = 0.35 + (0.50 * (i / max(1, total_clauses)))
            update_progress(f"Auditing Clause {i+1}/{total_clauses}: {clause.clause_id} - {clause.title}", progress_ratio)

            # Step A: Gather evidence & citations
            evidence_text, citations = evidence_hunter.gather_evidence(clause)

            # Step B: Adversarial Audit
            finding = self.compliance_auditor.audit_clause(clause, evidence_text, citations)
            findings.append(finding)

        # 5. Compile Executive Matrix & Report
        update_progress("MatrixGeneratorAgent: Compiling executive report & compliance matrix...", 0.90)
        report = self.matrix_generator.generate_report(
            standard_name=standard_path.name,
            policy_name=policy_path.name,
            findings=findings
        )

        update_progress("Audit Complete! Executive Report ready.", 1.0)
        return report
