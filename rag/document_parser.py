"""
Document Parser for AegisAudit AI.
Handles multi-page PDFs and text documents with strict page and section metadata tracking.
"""

from pathlib import Path
from typing import List, Dict, Any
from core.logger import logger

class DocumentParser:
    @staticmethod
    def parse_pdf(file_path: Path) -> List[Dict[str, Any]]:
        """
        Parses a PDF file and extracts text page-by-page.
        Returns a list of dicts: [{"page": 1, "text": "...", "source": "sample.pdf"}]
        """
        pages_data = []
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path_obj))
            for i, page in enumerate(reader.pages):
                extracted = page.extract_text() or ""
                pages_data.append({
                    "page": i + 1,
                    "text": extracted.strip(),
                    "source": path_obj.name,
                    "total_pages": len(reader.pages)
                })
            logger.info(f"Parsed {len(pages_data)} pages from {path_obj.name}")
        except Exception as e:
            logger.warning(f"pypdf failed on {path_obj.name}: {e}. Attempting fallback...")
            # Fallback text reading if applicable
            try:
                with open(path_obj, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                pages_data.append({
                    "page": 1,
                    "text": content,
                    "source": path_obj.name,
                    "total_pages": 1
                })
            except Exception as read_err:
                logger.error(f"Failed to parse document {file_path}: {read_err}")
                raise read_err

        return pages_data

    @staticmethod
    def parse_text(file_path: Path) -> List[Dict[str, Any]]:
        """Parses plain text or markdown files."""
        path_obj = Path(file_path)
        with open(path_obj, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return [{
            "page": 1,
            "text": content,
            "source": path_obj.name,
            "total_pages": 1
        }]
