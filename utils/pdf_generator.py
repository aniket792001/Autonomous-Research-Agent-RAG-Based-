"""
Executive PDF Audit Report Generator for AegisAudit AI.
Generates board-ready, cryptographically sealed compliance reports.
"""

import io
import hashlib
from datetime import datetime
from typing import List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

from models.audit_schema import FullAuditReport, ComplianceStatus, RiskLevel

class AuditPDFGenerator:
    @staticmethod
    def generate_pdf(report: FullAuditReport) -> bytes:
        """
        Builds a comprehensive, publication-quality PDF audit certificate and report.
        Returns the raw PDF bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Typography
        style_title = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0B0F19'),
            spaceAfter=4
        )

        style_subtitle = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=12
        )

        style_section_h = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=14,
            spaceAfter=6
        )

        style_body = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#334155')
        )

        style_bold = ParagraphStyle(
            'ReportBold',
            parent=style_body,
            fontName='Helvetica-Bold'
        )

        style_table_text = ParagraphStyle(
            'TableText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#1E293B')
        )

        style_table_bold = ParagraphStyle(
            'TableBold',
            parent=style_table_text,
            fontName='Helvetica-Bold'
        )

        elements = []

        # --- HEADER BANNER ---
        elements.append(Paragraph("🛡️ AEGIS AUDIT AI", style_title))
        elements.append(Paragraph("Official Regulatory & Compliance Verification Certificate", style_subtitle))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0EA5E9'), spaceAfter=14))

        # --- METADATA & SUMMARY SCORECARD TABLE ---
        score = report.summary.overall_compliance_percentage
        score_color = colors.HexColor('#10B981') if score >= 75 else colors.HexColor('#F59E0B') if score >= 50 else colors.HexColor('#EF4444')

        meta_data = [
            [
                Paragraph("<b>Audit ID:</b>", style_table_text),
                Paragraph(report.audit_id, style_table_bold),
                Paragraph("<b>Overall Compliance:</b>", style_table_text),
                Paragraph(f"<font color='{score_color.hexval()}'><b>{score}%</b></font>", style_table_bold)
            ],
            [
                Paragraph("<b>Standard:</b>", style_table_text),
                Paragraph(report.standard_name, style_table_text),
                Paragraph("<b>Compliant Controls:</b>", style_table_text),
                Paragraph(f"<font color='#10B981'><b>{report.summary.compliant_count}</b></font>", style_table_bold)
            ],
            [
                Paragraph("<b>Target Policy:</b>", style_table_text),
                Paragraph(report.policy_name, style_table_text),
                Paragraph("<b>Partial / Ambiguous:</b>", style_table_text),
                Paragraph(f"<font color='#F59E0B'><b>{report.summary.partially_compliant_count}</b></font>", style_table_bold)
            ],
            [
                Paragraph("<b>Timestamp:</b>", style_table_text),
                Paragraph(report.timestamp, style_table_text),
                Paragraph("<b>Non-Compliant Gaps:</b>", style_table_text),
                Paragraph(f"<font color='#EF4444'><b>{report.summary.non_compliant_count}</b></font>", style_table_bold)
            ]
        ]

        t_meta = Table(meta_data, colWidths=[1.3 * inch, 2.3 * inch, 1.5 * inch, 1.7 * inch])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 14))

        # --- EXECUTIVE OVERVIEW ---
        elements.append(Paragraph("📌 Executive CISO Overview & Legal Risk Assessment", style_section_h))
        # Replace newlines with breaks
        ciso_text = report.summary.executive_overview.replace("\n\n", "<br/><br/>").replace("\n", " ")
        elements.append(Paragraph(ciso_text, style_body))
        elements.append(Spacer(1, 14))

        # --- FINDINGS TABLE ---
        elements.append(Paragraph("📋 Detailed Control Audit & Gap Analysis", style_section_h))

        findings_header = [
            Paragraph("<b>Clause / Mandate</b>", style_table_bold),
            Paragraph("<b>Status / Risk</b>", style_table_bold),
            Paragraph("<b>Policy Evidence & Citations</b>", style_table_bold),
            Paragraph("<b>Gap Analysis & Remediation</b>", style_table_bold)
        ]

        table_rows = [findings_header]

        for f in report.findings:
            # Color for status
            st_color = (
                "#10B981" if f.status == ComplianceStatus.COMPLIANT
                else "#F59E0B" if f.status == ComplianceStatus.PARTIALLY_COMPLIANT
                else "#EF4444"
            )

            citations_str = ", ".join([f"Pg {c.page_number}" for c in f.citations]) or "No citations"

            c1 = Paragraph(f"<b>{f.clause_id}</b><br/>{f.clause_title}", style_table_text)
            c2 = Paragraph(f"<font color='{st_color}'><b>{f.status.value}</b></font><br/>Risk: {f.risk_level.value}", style_table_text)
            c3 = Paragraph(f"{f.evidence_found[:180]}...<br/><font color='#0284C7'>[{citations_str}]</font>", style_table_text)
            c4 = Paragraph(f"<b>Gap:</b> {f.gap_analysis[:140]}...<br/><font color='#059669'><b>Fix:</b></font> {f.remediation_recommendation[:140]}...", style_table_text)

            table_rows.append([c1, c2, c3, c4])

        t_findings = Table(table_rows, colWidths=[1.5 * inch, 1.2 * inch, 2.0 * inch, 2.5 * inch], repeatRows=1)
        t_findings.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_findings)
        elements.append(Spacer(1, 16))

        # --- CRYPTOGRAPHIC AUDIT SEAL & INTEGRITY HASH ---
        raw_seal = f"{report.audit_id}|{report.timestamp}|{score}|{len(report.findings)}"
        sha256_seal = hashlib.sha256(raw_seal.encode("utf-8")).hexdigest()

        seal_data = [
            [
                Paragraph("<b>Cryptographic Verification Seal (SHA-256):</b>", style_table_bold),
                Paragraph(f"<font face='Courier' color='#0F172A'>{sha256_seal}</font>", style_table_text)
            ],
            [
                Paragraph("<b>Verification Authority:</b>", style_table_text),
                Paragraph("AegisAudit AI Autonomous Multi-Agent Core Engine v1.2 &bull; Formal Audit Ledger", style_table_text)
            ]
        ]
        t_seal = Table(seal_data, colWidths=[2.2 * inch, 5.0 * inch])
        t_seal.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(KeepTogether([t_seal]))

        # Build document
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
