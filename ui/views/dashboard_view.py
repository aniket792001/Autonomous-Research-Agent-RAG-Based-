"""
Executive Dashboard View for AegisAudit AI.
Displays enterprise compliance posture, KPI cards, framework coverage, and audit history.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from db.storage import AuditDatabase
from models.audit_schema import FullAuditReport
from utils.report_exporter import ReportExporter

def render_dashboard_view():
    db = AuditDatabase()
    audits: List[Dict[str, Any]] = db.list_audits()
    
    st.markdown("### 📊 Executive Compliance Dashboard")
    st.caption("Continuous Governance, Risk & Regulatory Compliance Posture Overview")

    if not audits:
        st.info("👋 No audits have been conducted yet. Navigate to **Audit Studio** to launch your first autonomous audit.")
        col_btn, _ = st.columns([2, 5])
        with col_btn:
            if st.button("🚀 Launch First Audit", type="primary", use_container_width=True):
                st.session_state["active_view"] = "⚡ Audit Studio"
                st.rerun()
        return

    # Calculate aggregate stats
    total_audits = len(audits)
    avg_score = round(sum(a.get("compliance_pct", 0) for a in audits) / max(1, total_audits), 1)
    total_clauses_evaluated = sum(a.get("total_clauses", 0) for a in audits)
    total_non_compliant = sum(a.get("non_compliant_count", 0) for a in audits)
    
    latest_audit = audits[0]
    latest_score = latest_audit.get("compliance_pct", 0)
    latest_id = latest_audit.get("audit_id", "N/A")

    # --- KPI METRICS GRID ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Compliance</div>
            <div class="metric-val" style="color: {'#10B981' if avg_score >= 75 else '#F59E0B' if avg_score >= 50 else '#EF4444'};">
                {avg_score}%
            </div>
            <div class="metric-sub">Across {total_audits} total audit runs</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card compliant">
            <div class="metric-label">Latest Audit Score</div>
            <div class="metric-val" style="color: #38BDF8;">
                {latest_score}%
            </div>
            <div class="metric-sub">{latest_id}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Clauses Evaluated</div>
            <div class="metric-val" style="color: #F9FAFB;">
                {total_clauses_evaluated}
            </div>
            <div class="metric-sub">Mandates cross-verified</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card non-compliant">
            <div class="metric-label">Active Gaps Identified</div>
            <div class="metric-val" style="color: #EF4444;">
                {total_non_compliant}
            </div>
            <div class="metric-sub">Non-compliant controls flagged</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- FRAMEWORK POSTURE & QUICK SUMMARY ---
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.markdown("#### 📜 Recent Audit Engagements")
        
        # Format table
        table_rows = []
        for a in audits[:8]:
            table_rows.append({
                "Audit ID": a.get("audit_id", "N/A"),
                "Regulatory Standard": a.get("standard_name", "N/A"),
                "Corporate Policy": a.get("policy_name", "N/A"),
                "Date": a.get("timestamp", "")[:10],
                "Score": f"{a.get('compliance_pct', 0)}%",
                "Clauses": a.get("total_clauses", 0),
                "Passed": a.get("compliant_count", 0),
                "Gaps": a.get("non_compliant_count", 0)
            })
            
        df = pd.DataFrame(table_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown("#### 🎯 Quick Actions")
        st.markdown("""
        <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid #1F2937; border-radius: 12px; padding: 18px; margin-bottom: 14px;">
            <div style="font-weight: 700; color: #38BDF8; font-size: 1rem; margin-bottom: 6px;">Initiate New Compliance Audit</div>
            <div style="color: #94A3B8; font-size: 0.85rem; margin-bottom: 12px;">Run our 4-agent autonomous pipeline against ISO 27001, SOC 2, or GDPR standards.</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Open Audit Studio", type="primary", use_container_width=True):
            st.session_state["active_view"] = "⚡ Audit Studio"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Select audit to inspect directly
        st.markdown("##### 🔍 Inspect an Audit in Findings Explorer")
        audit_choices = {f"{a['audit_id']} ({a['standard_name']} - {a['compliance_pct']}%)": a["audit_id"] for a in audits}
        selected_choice = st.selectbox("Choose Audit to Inspect:", list(audit_choices.keys()), index=0)
        
        if st.button("Inspect in Findings Explorer ➔", use_container_width=True):
            st.session_state["selected_audit_id"] = audit_choices[selected_choice]
            st.session_state["active_view"] = "🔍 Findings Explorer"
            st.rerun()

    # --- COMPLIANCE DIFF & DRIFT ANALYSIS ---
    st.markdown("---")
    st.markdown("### 🔄 Compliance Diff & Trend Analysis")
    st.caption("Compare two audit runs side-by-side to track remediation progress, closed security gaps, and control regressions over time.")

    if len(audits) < 2:
        st.info("💡 Run at least 2 audits to unlock automated historical diff analysis, gap resolution velocity, and control regression tracking.")
    else:
        diff_col1, diff_col2, diff_btn = st.columns([2, 2, 1])
        audit_lookup = {f"{a['audit_id']} ({a.get('standard_name', 'Framework')} - {a.get('compliance_pct', 0)}%)": a["audit_id"] for a in audits}
        options_list = list(audit_lookup.keys())

        with diff_col1:
            baseline_label = st.selectbox("Baseline Audit (Earlier):", options_list, index=min(1, len(options_list) - 1), key="diff_base_sel")
            base_id = audit_lookup[baseline_label]
        with diff_col2:
            current_label = st.selectbox("Target Audit (Recent / Remediated):", options_list, index=0, key="diff_curr_sel")
            curr_id = audit_lookup[current_label]
        with diff_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_diff = st.button("Run Diff Analysis", type="primary", use_container_width=True)

        if base_id == curr_id:
            st.warning("Please select two distinct audit runs to calculate historical diff metrics.")
        else:
            rep_base = db.get_report(base_id)
            rep_curr = db.get_report(curr_id)

            if rep_base and rep_curr:
                score_base = rep_base.summary.overall_compliance_percentage
                score_curr = rep_curr.summary.overall_compliance_percentage
                delta = round(score_curr - score_base, 1)
                delta_sign = "+" if delta > 0 else ""
                delta_color = "#10B981" if delta > 0 else "#EF4444" if delta < 0 else "#94A3B8"

                # Map findings by clause_id
                base_dict = {f.clause_id: f for f in rep_base.findings}
                curr_dict = {f.clause_id: f for f in rep_curr.findings}

                all_keys = list(dict.fromkeys(list(base_dict.keys()) + list(curr_dict.keys())))

                closed_gaps = []
                regressions = []
                unchanged = []

                diff_rows = []
                for cid in all_keys:
                    f_base = base_dict.get(cid)
                    f_curr = curr_dict.get(cid)

                    st_base = f_base.status.value if f_base else "Not Audited"
                    st_curr = f_curr.status.value if f_curr else "Not Audited"
                    title = f_curr.clause_title if f_curr else (f_base.clause_title if f_base else cid)

                    if st_base in ["Non-Compliant", "Partially Compliant"] and st_curr == "Compliant":
                        verdict = "🟢 Resolved Gap"
                        closed_gaps.append(cid)
                    elif st_base == "Compliant" and st_curr in ["Non-Compliant", "Partially Compliant"]:
                        verdict = "🔴 Regressed Control"
                        regressions.append(cid)
                    elif st_curr == "Compliant":
                        verdict = "⚪ Maintained Compliant"
                        unchanged.append(cid)
                    else:
                        verdict = "⚠️ Ongoing Gap"

                    diff_rows.append({
                        "Clause ID": cid,
                        "Title": title,
                        "Baseline Status": st_base,
                        "Target Status": st_curr,
                        "Remediation Verdict": verdict
                    })

                # Diff KPI scorecard
                d_c1, d_c2, d_c3, d_c4 = st.columns(4)
                with d_c1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Compliance Trend</div>
                        <div class="metric-val" style="color: {delta_color};">{delta_sign}{delta}%</div>
                        <div class="metric-sub">{score_base}% ➔ {score_curr}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                with d_c2:
                    st.markdown(f"""
                    <div class="metric-card compliant">
                        <div class="metric-label">Gaps Resolved</div>
                        <div class="metric-val" style="color: #10B981;">{len(closed_gaps)}</div>
                        <div class="metric-sub">Newly satisfied controls</div>
                    </div>
                    """, unsafe_allow_html=True)
                with d_c3:
                    st.markdown(f"""
                    <div class="metric-card non-compliant">
                        <div class="metric-label">Control Regressions</div>
                        <div class="metric-val" style="color: #EF4444;">{len(regressions)}</div>
                        <div class="metric-sub">Fell out of compliance</div>
                    </div>
                    """, unsafe_allow_html=True)
                with d_c4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Common Clauses</div>
                        <div class="metric-val" style="color: #38BDF8;">{len(all_keys)}</div>
                        <div class="metric-sub">Cross-referenced mandates</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(diff_rows), use_container_width=True, hide_index=True)
