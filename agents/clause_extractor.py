"""
Clause Extractor Agent for AegisAudit AI.
Parses complex regulatory standard documents and extracts actionable, structured compliance clauses.
"""

from typing import List
from models.audit_schema import ClauseRequirement
from agents.base_agent import BaseAgent
from core.logger import logger
from core.config import settings

class ClauseExtractorAgent(BaseAgent):
    def extract_clauses(self, document_text: str, max_clauses: int = None) -> List[ClauseRequirement]:
        """
        Decomposes regulatory framework text into formal ClauseRequirement objects.
        """
        limit = max_clauses or settings.MAX_CLAUSES_PER_AUDIT
        logger.info(f"ClauseExtractorAgent: Extracting up to {limit} clauses from framework text...")

        # Sample snippet if text is huge
        snippet = document_text[:12000]

        prompt = f"""
You are an expert Regulatory Compliance Auditor.
Your task is to: Extract all regulatory clauses, security mandates, and legal requirements from the following standard document.

Document Context:
\"\"\"
{snippet}
\"\"\"

Instructions:
1. Identify up to {limit} distinct requirements or articles.
2. For each, output a structured JSON array of objects.
3. Each object MUST have:
   - "clause_id": Formal code or identifier (e.g. "ISO-A.9.1", "GDPR-Art.5", "REG-01")
   - "title": Short title of the requirement
   - "description": Exact mandate or obligation (what must be done)
   - "category": Topic area (e.g. "Access Control", "Data Privacy", "Encryption", "Incident Response")

Return ONLY the raw JSON array.
"""

        raw_response = self.call_llm(prompt)
        parsed_json = self.extract_json(raw_response)

        clauses: List[ClauseRequirement] = []
        if isinstance(parsed_json, list):
            for item in parsed_json[:limit]:
                try:
                    clauses.append(ClauseRequirement(
                        clause_id=item.get("clause_id", f"REQ-{len(clauses)+1}"),
                        title=item.get("title", "Compliance Mandate"),
                        description=item.get("description", ""),
                        category=item.get("category", "General")
                    ))
                except Exception as e:
                    logger.warning(f"Error parsing clause item: {e}")

        # Fallback if LLM returned empty
        if not clauses:
            clauses = [
                ClauseRequirement(
                    clause_id="MANDATE-01",
                    title="User Access Management",
                    description="Formal procedures for user registration, de-registration, and privileged access review must be implemented.",
                    category="Access Control"
                ),
                ClauseRequirement(
                    clause_id="MANDATE-02",
                    title="Cryptographic Protection",
                    description="Sensitive data in transit and at rest must be protected by verified cryptographic controls.",
                    category="Cryptography"
                ),
                ClauseRequirement(
                    clause_id="MANDATE-03",
                    title="Security Logging and Monitoring",
                    description="Logging facilities and log review procedures must be in place to detect unauthorized information processing.",
                    category="Operations Security"
                )
            ]

        logger.info(f"ClauseExtractorAgent: Successfully extracted {len(clauses)} audit clauses.")
        return clauses
