"""
Interactive Findings Explorer View for AegisAudit AI.
Two-pane master-detail inspector for deep-dive compliance analysis and human-in-the-loop verification.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from db.storage import AuditDatabase
from models.audit_schema import FullAuditReport, ComplianceStatus, RiskLevel, AuditFinding
from utils.report_exporter import ReportExporter

def render_explorer_view():
    db = AuditDatabase()
    audits = db.list_audits()

    st.markdown("### 🔍 Interactive Findings Explorer & Inspector")
    st.caption("Inspect individual clause requirements, review evidence citations, and apply auditor overrides.")

    if not audits:
        st.info("No audit reports recorded yet. Please run an audit in the **Audit Studio**.")
        return

    # Top Selector Bar
    audit_map = {
        f"{a['audit_id']} — {a['standard_name']} ({a['compliance_pct']}%) — {a['timestamp'][:10]}": a["audit_id"]
        for a in audits
    }

    # Determine default index
    default_id = st.session_state.get("selected_audit_id", audits[0]["audit_id"])
    default_idx = 0
    for idx, (lbl, aid) in enumerate(audit_map.items()):
        if aid == default_id:
            default_idx = idx
            break

    c_sel, c_exp = st.columns([3, 2])
    with c_sel:
        selected_label = st.selectbox("Select Audit Engagement:", list(audit_map.keys()), index=default_idx)
        selected_audit_id = audit_map[selected_label]
        st.session_state["selected_audit_id"] = selected_audit_id

    report: Optional[FullAuditReport] = db.get_report(selected_audit_id)
    if not report:
        st.error(f"Could not load report for audit ID: {selected_audit_id}")
        return

    with c_exp:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        c_e1, c_e2, c_e3, c_e4 = st.columns(4)
        with c_e1:
            try:
                pdf_data = ReportExporter.to_pdf(report)
                st.download_button(
                    "📄 Official PDF",
                    data=pdf_data,
                    file_name=f"{report.audit_id}_certificate.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as pdf_err:
                st.caption(f"PDF unavailable: {pdf_err}")
        with c_e2:
            st.download_button(
                "🛠️ Task List (CSV)",
                data=ReportExporter.to_remediation_csv(report),
                file_name=f"{report.audit_id}_remediation_tasks.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_e3:
            st.download_button(
                "⬇️ Matrix CSV",
                data=ReportExporter.to_csv(report),
                file_name=f"{report.audit_id}_matrix.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_e4:
            st.download_button(
                "⬇️ Markdown",
                data=ReportExporter.to_markdown(report),
                file_name=f"{report.audit_id}_brief.md",
                mime="text/markdown",
                use_container_width=True
            )

    # --- TOP KPI SUMMARY CHIPS ---
    score = report.summary.overall_compliance_percentage
    score_color = "#10B981" if score >= 75 else "#F59E0B" if score >= 50 else "#EF4444"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Compliance Rate</div>
            <div class="metric-val" style="color: {score_color};">{score}%</div>
            <div class="metric-sub">{report.summary.total_clauses_audited} total clauses</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card compliant">
            <div class="metric-label">Compliant Controls</div>
            <div class="metric-val" style="color: #10B981;">{report.summary.compliant_count}</div>
            <div class="metric-sub">Fully satisfied</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card partial">
            <div class="metric-label">Partial Controls</div>
            <div class="metric-val" style="color: #F59E0B;">{report.summary.partially_compliant_count}</div>
            <div class="metric-sub">Ambiguous implementation</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card non-compliant">
            <div class="metric-label">Non-Compliant Gaps</div>
            <div class="metric-val" style="color: #EF4444;">{report.summary.non_compliant_count}</div>
            <div class="metric-sub">Violations & omissions</div>
        </div>
        """, unsafe_allow_html=True)

    # Collapsible CISO Executive Overview
    with st.expander("📌 Executive CISO Overview & Legal Exposure Assessment", expanded=False):
        st.markdown(report.summary.executive_overview)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TWO-PANE MASTER-DETAIL LAYOUT ---
    col_master, col_detail = st.columns([4, 6], gap="large")

    # Filter state
    with col_master:
        st.markdown("#### 📋 Clauses & Mandates")
        
        search_query = st.text_input("🔍 Search clauses or IDs...", key="clause_search", placeholder="e.g. A.8.5, access, encryption...")

        filter_option = st.radio(
            "Filter Status:",
            options=["All", "Non-Compliant", "Partially Compliant", "Compliant", "High/Critical Risk"],
            horizontal=True,
            key="clause_filter_radio"
        )

        # Filter findings
        filtered_findings: List[AuditFinding] = report.findings

        if search_query:
            q = search_query.lower()
            filtered_findings = [
                f for f in filtered_findings
                if q in f.clause_id.lower() or q in f.clause_title.lower() or q in f.requirement_summary.lower()
            ]

        if filter_option == "Non-Compliant":
            filtered_findings = [f for f in filtered_findings if f.status == ComplianceStatus.NON_COMPLIANT]
        elif filter_option == "Partially Compliant":
            filtered_findings = [f for f in filtered_findings if f.status == ComplianceStatus.PARTIALLY_COMPLIANT]
        elif filter_option == "Compliant":
            filtered_findings = [f for f in filtered_findings if f.status == ComplianceStatus.COMPLIANT]
        elif filter_option == "High/Critical Risk":
            filtered_findings = [f for f in filtered_findings if f.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]

        st.caption(f"Showing {len(filtered_findings)} of {len(report.findings)} clauses")

        if not filtered_findings:
            st.info("No clauses match your search or filter.")
            active_clause = None
        else:
            # Maintain active clause selection in session state
            active_clause_id = st.session_state.get("active_clause_id", filtered_findings[0].clause_id)
            
            # Ensure active_clause_id is in current filtered list
            if active_clause_id not in [f.clause_id for f in filtered_findings]:
                active_clause_id = filtered_findings[0].clause_id
                st.session_state["active_clause_id"] = active_clause_id

            # Render selectable cards
            for finding in filtered_findings:
                is_selected = finding.clause_id == active_clause_id

                badge_class = (
                    "badge-compliant" if finding.status == ComplianceStatus.COMPLIANT
                    else "badge-partial" if finding.status == ComplianceStatus.PARTIALLY_COMPLIANT
                    else "badge-non-compliant"
                )

                verified_chip = '<span class="badge-verified">✓ Reviewed</span>' if getattr(finding, "is_verified", False) else ''

                card_border = "#38BDF8" if is_selected else "#1F2937"
                card_bg = "rgba(14, 165, 233, 0.12)" if is_selected else "rgba(17, 24, 39, 0.85)"

                st.markdown(f"""
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-weight: 700; color: #F9FAFB; font-size: 0.9rem;">{finding.clause_id}</span>
                        <div>
                            <span class="{badge_class}">{finding.status.value}</span>
                            <span class="badge-risk">{finding.risk_level.value}</span>
                            {verified_chip}
                        </div>
                    </div>
                    <div style="font-size: 0.82rem; color: #94A3B8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {finding.clause_title}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Inspect {finding.clause_id}", key=f"btn_sel_{finding.clause_id}", use_container_width=True):
                    st.session_state["active_clause_id"] = finding.clause_id
                    st.rerun()

            active_clause = next((f for f in report.findings if f.clause_id == st.session_state.get("active_clause_id")), filtered_findings[0])

    # Detail Inspector Pane
    with col_detail:
        st.markdown("#### 🔎 Evidence & Audit Inspector")

        if not active_clause:
            st.info("Select a clause from the left list to view detailed audit telemetry.")
            return

        status_class = (
            "badge-compliant" if active_clause.status == ComplianceStatus.COMPLIANT
            else "badge-partial" if active_clause.status == ComplianceStatus.PARTIALLY_COMPLIANT
            else "badge-non-compliant"
        )

        st.markdown(f"""
        <div class="inspector-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; border-bottom: 1px solid #1F2937; padding-bottom: 14px;">
                <div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #38BDF8;">{active_clause.clause_id}: {active_clause.clause_title}</div>
                    <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 2px;">Standard: {report.standard_name}</div>
                </div>
                <div>
                    <span class="{status_class}" style="font-size: 0.85rem; padding: 4px 12px;">{active_clause.status.value}</span>
                    <span class="badge-risk" style="font-size: 0.85rem; padding: 4px 10px;">Risk: {active_clause.risk_level.value}</span>
                </div>
            </div>

            <!-- MANDATE -->
            <div class="inspector-section">
                <div class="inspector-title">📜 1. Regulatory Requirement Mandate</div>
                <div class="inspector-box-mandate">
                    {active_clause.requirement_summary}
                </div>
            </div>

            <!-- EVIDENCE -->
            <div class="inspector-section">
                <div class="inspector-title">🏢 2. Company Policy Evidence & Citations</div>
                <div class="inspector-box-evidence">
                    {active_clause.evidence_found}
                </div>
                <div style="margin-top: 8px;">
                    {' '.join([f'<span class="citation-chip">📄 Pg {c.page_number} ({c.document_name})</span>' for c in active_clause.citations]) or '<span class="citation-chip">No Citations Found</span>'}
                </div>
            </div>

            <!-- GAP ANALYSIS -->
            <div class="inspector-section">
                <div class="inspector-title">⚖️ 3. Adversarial Lead Auditor Gap Analysis</div>
                <div class="inspector-box-gap">
                    {active_clause.gap_analysis}
                </div>
            </div>

            <!-- REMEDIATION -->
            <div class="inspector-section">
                <div class="inspector-title">🛠️ 4. Actionable Remediation Guidance</div>
                <div class="inspector-box-remediation">
                    {active_clause.remediation_recommendation}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Human-in-the-Loop Auditor Review Form
        with st.expander("✍️ Human Auditor Review & Override", expanded=False):
            st.caption("As a certified compliance officer, you can verify findings, override statuses, and log audit notes.")

            current_verified = getattr(active_clause, "is_verified", False)
            current_notes = getattr(active_clause, "auditor_notes", "")

            c_rev1, c_rev2 = st.columns(2)
            with c_rev1:
                new_status = st.selectbox(
                    "Override Compliance Status:",
                    options=[ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT, ComplianceStatus.NON_COMPLIANT, ComplianceStatus.NOT_APPLICABLE],
                    index=[ComplianceStatus.COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT, ComplianceStatus.NON_COMPLIANT, ComplianceStatus.NOT_APPLICABLE].index(active_clause.status),
                    key=f"ov_status_{active_clause.clause_id}"
                )
            with c_rev2:
                is_verified = st.checkbox("Mark as Verified by Auditor", value=current_verified, key=f"ov_ver_{active_clause.clause_id}")

            current_owner = getattr(active_clause, "remediation_owner", "") or ""
            current_rem_status = getattr(active_clause, "remediation_status", "Open") or "Open"

            c_rem1, c_rem2 = st.columns(2)
            with c_rem1:
                rem_owner = st.selectbox(
                    "Assign Remediation Owner:",
                    options=["DevOps Lead", "Security Architect", "Engineering Team", "CISO Office", "Legal / Privacy Team", "External Vendor"],
                    index=["DevOps Lead", "Security Architect", "Engineering Team", "CISO Office", "Legal / Privacy Team", "External Vendor"].index(current_owner) if current_owner in ["DevOps Lead", "Security Architect", "Engineering Team", "CISO Office", "Legal / Privacy Team", "External Vendor"] else 0,
                    key=f"ov_owner_{active_clause.clause_id}"
                )
            with c_rem2:
                rem_status = st.selectbox(
                    "Remediation Task Status:",
                    options=["Open", "In Progress", "Resolved"],
                    index=["Open", "In Progress", "Resolved"].index(current_rem_status) if current_rem_status in ["Open", "In Progress", "Resolved"] else 0,
                    key=f"ov_rem_status_{active_clause.clause_id}"
                )

            auditor_note = st.text_area(
                "Auditor Review Commentary & Justification:",
                value=current_notes,
                placeholder="Log internal context, compensating controls, or audit exceptions...",
                key=f"ov_notes_{active_clause.clause_id}"
            )

            if st.button("💾 Save Review & Remediation Task", type="primary", use_container_width=True):
                # Update finding in memory
                active_clause.status = new_status
                active_clause.is_verified = is_verified
                active_clause.auditor_notes = auditor_note
                active_clause.remediation_owner = rem_owner
                active_clause.remediation_status = rem_status

                # Recompute summary statistics
                total = len(report.findings)
                comp = sum(1 for f in report.findings if f.status == ComplianceStatus.COMPLIANT)
                part = sum(1 for f in report.findings if f.status == ComplianceStatus.PARTIALLY_COMPLIANT)
                non = sum(1 for f in report.findings if f.status == ComplianceStatus.NON_COMPLIANT)
                new_pct = round(((comp + (0.5 * part)) / max(1, total)) * 100.0, 1)

                report.summary.compliant_count = comp
                report.summary.partially_compliant_count = part
                report.summary.non_compliant_count = non
                report.summary.overall_compliance_percentage = new_pct

                # Persist updated report to DB
                db.save_report(report)
                st.success(f"Review and task saved for clause {active_clause.clause_id}! Compliance score updated to {new_pct}%.")
                st.rerun()
