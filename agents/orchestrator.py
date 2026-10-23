"""
Audit Orchestrator for AegisAudit AI.
Coordinates the multi-agent execution pipeline, emits telemetry, and returns the full audit report.
"""

from typing import Callable, Optional, List, Union
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
        policy_path: Union[Path, List[Path]],
        max_clauses: int = 15,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> FullAuditReport:
        """
        Executes end-to-end autonomous audit between a standard framework and one or more company policy documents.
        """
        def update_progress(message: str, pct: float):
            logger.info(f"Progress ({int(pct*100)}%): {message}")
            if progress_callback:
                progress_callback(message, pct)

        update_progress("Parsing regulatory framework and policy documents...", 0.05)
        
        # 1. Parse standard framework
        standard_pages = DocumentParser.parse_pdf(standard_path)
        standard_full_text = "\n\n".join([p["text"] for p in standard_pages])

        # 2. Parse and index company policy (supports single or multi-document corpus)
        update_progress("Indexing company policy corpus into vector store...", 0.15)
        policy_files = policy_path if isinstance(policy_path, list) else [policy_path]
        
        all_policy_chunks = []
        splitter = AuditTextSplitter()
        for p_file in policy_files:
            try:
                pages = DocumentParser.parse_pdf(p_file)
                chunks = splitter.split_pages(pages)
                all_policy_chunks.extend(chunks)
            except Exception as parse_err:
                logger.warning(f"AuditOrchestrator: Error parsing policy {p_file}: {parse_err}")

        vector_store = AuditVectorStore()
        vector_store.add_chunks(all_policy_chunks)

        # 3. Extract regulatory clauses
        update_progress("ClauseExtractorAgent: Decomposing regulation into mandates...", 0.30)
        clauses: List[ClauseRequirement] = self.clause_extractor.extract_clauses(
            standard_full_text,
            max_clauses=max_clauses
        )

        evidence_hunter = EvidenceHunterAgent(vector_store)
        findings: List[AuditFinding] = []

        # 4. Audit clauses in parallel with Evidence Hunter and Compliance Auditor (3x-4x speedup)
        total_clauses = len(clauses)
        update_progress(f"Launching parallel multi-agent evaluation for {total_clauses} clauses...", 0.35)

        def audit_single_clause(clause_idx, clause):
            try:
                evidence_text, citations = evidence_hunter.gather_evidence(clause)
                finding = self.compliance_auditor.audit_clause(clause, evidence_text, citations)
                return clause_idx, finding
            except Exception as err:
                logger.error(f"AuditOrchestrator: Error auditing clause {clause.clause_id}: {err}")
                from models.audit_schema import ComplianceStatus, RiskLevel
                fallback_finding = AuditFinding(
                    clause_id=clause.clause_id,
                    clause_title=clause.title,
                    requirement_summary=clause.description,
                    evidence_found="Evidence extraction error or timeout",
                    citations=[],
                    status=ComplianceStatus.NON_COMPLIANT,
                    risk_level=RiskLevel.HIGH,
                    gap_analysis=f"Automated evaluation failed: {err}",
                    remediation_recommendation="Verify connectivity or review policy manually."
                )
                return clause_idx, fallback_finding

        import concurrent.futures
        results = [None] * total_clauses
        completed = 0
        workers = min(4, max(1, total_clauses))

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_idx = {
                executor.submit(audit_single_clause, i, c): i
                for i, c in enumerate(clauses)
            }
            for future in concurrent.futures.as_completed(future_to_idx):
                idx, finding = future.result()
                results[idx] = finding
                completed += 1
                progress_ratio = 0.35 + (0.50 * (completed / max(1, total_clauses)))
                update_progress(f"Audited {completed}/{total_clauses}: {finding.clause_id} ({finding.status.value})", progress_ratio)

        findings: List[AuditFinding] = results

        # 5. Compile Executive Matrix & Report
        update_progress("MatrixGeneratorAgent: Compiling executive report & compliance matrix...", 0.90)
        
        if isinstance(policy_path, list):
            if len(policy_path) == 1:
                display_policy_name = policy_path[0].name
            elif len(policy_path) <= 3:
                display_policy_name = ", ".join([p.name for p in policy_path])
            else:
                display_policy_name = f"{len(policy_path)} Policy Documents ({policy_path[0].name}, {policy_path[1].name}...)"
        else:
            display_policy_name = policy_path.name

        report = self.matrix_generator.generate_report(
            standard_name=standard_path.name,
            policy_name=display_policy_name,
            findings=findings
        )

        update_progress("Audit Complete! Executive Report ready.", 1.0)
        return report
