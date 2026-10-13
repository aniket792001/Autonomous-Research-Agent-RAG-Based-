"""
Interactive Streamlit Dashboard for AegisAudit AI.
Includes Phase 1: Authentication, Session Management, and Role-Based Access Control (RBAC).
"""

import streamlit as st
from pathlib import Path
import os
import pandas as pd
from typing import Optional

from core.config import settings
from core.logger import logger
from core.security import PasswordHasher, TokenManager
from ui.styles import CUSTOM_CSS
from agents.orchestrator import AuditOrchestrator
from db.storage import AuditDatabase
from db.user_store import UserDatabase
from utils.report_exporter import ReportExporter
from models.audit_schema import ComplianceStatus, RiskLevel, FullAuditReport
from models.user_schema import UserRole, UserResponse

def render_dashboard():
    st.set_page_config(
        page_title="AegisAudit AI - Autonomous Compliance Platform",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    db = AuditDatabase()
    user_db = UserDatabase()

    # Session state initialization
    if "auth_user" not in st.session_state:
        # Default to pre-seeded admin for seamless instant testing if desired
        default_admin = user_db.get_user_by_email("admin@aegisaudit.com")
        if default_admin:
            st.session_state["auth_user"] = UserResponse(
                id=default_admin["id"],
                email=default_admin["email"],
                full_name=default_admin["full_name"],
                role=default_admin["role"],
                is_active=default_admin["is_active"],
                created_at=default_admin["created_at"]
            )
        else:
            st.session_state["auth_user"] = None

    # --- SIDEBAR CONFIGURATION ---
    with st.sidebar:
        # User Authentication Section
        st.markdown("### 🔐 User & Session")
        curr_user: Optional[UserResponse] = st.session_state.get("auth_user")

        if curr_user:
            role_color = "#10B981" if curr_user.role == UserRole.ADMIN else "#0EA5E9" if curr_user.role == UserRole.AUDITOR else "#F59E0B"
            st.markdown(f"""
            <div style="background: rgba(17, 24, 39, 0.8); border: 1px solid #1F2937; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                <div style="font-size: 0.8rem; color: #94A3B8;">AUTHENTICATED AS</div>
                <div style="font-weight: 700; color: #F9FAFB; font-size: 1rem;">{curr_user.full_name}</div>
                <div style="font-size: 0.8rem; color: #94A3B8;">{curr_user.email}</div>
                <div style="margin-top: 6px;">
                    <span style="background: rgba(255,255,255,0.08); border: 1px solid {role_color}; color: {role_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase;">
                        {curr_user.role.value}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state["auth_user"] = None
                st.rerun()
        else:
            with st.expander("🔑 Sign In or Register", expanded=True):
                auth_tab_login, auth_tab_reg = st.tabs(["Sign In", "Register"])
                with auth_tab_login:
                    login_email = st.text_input("Email", value="admin@aegisaudit.com", key="login_email")
                    login_pass = st.text_input("Password", value="AdminPass123!", type="password", key="login_pass")
                    if st.button("Sign In", type="primary", use_container_width=True):
                        user_rec = user_db.get_user_by_email(login_email)
                        if user_rec and PasswordHasher.verify_password(login_pass, user_rec["hashed_password"]):
                            st.session_state["auth_user"] = UserResponse(
                                id=user_rec["id"],
                                email=user_rec["email"],
                                full_name=user_rec["full_name"],
                                role=user_rec["role"],
                                is_active=user_rec["is_active"],
                                created_at=user_rec["created_at"]
                            )
                            st.success("Authenticated!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")

                with auth_tab_reg:
                    reg_name = st.text_input("Full Name", key="reg_name")
                    reg_email = st.text_input("Work Email", key="reg_email")
                    reg_pass = st.text_input("Password", type="password", key="reg_pass")
                    reg_role = st.selectbox("Role", ["auditor", "viewer", "admin"], key="reg_role")
                    if st.button("Create Account", use_container_width=True):
                        if reg_email and reg_pass and reg_name:
                            try:
                                new_u = user_db.create_user(
                                    email=reg_email,
                                    password=reg_pass,
                                    full_name=reg_name,
                                    role=UserRole(reg_role)
                                )
                                st.session_state["auth_user"] = new_u
                                st.success("Account created!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Registration error: {e}")
                        else:
                            st.warning("Please fill in all fields.")

        st.markdown("---")
        st.markdown("### ⚙️ Engine Settings")
        provider = st.selectbox(
            "AI Model Provider",
            options=["gemini", "openai", "huggingface"],
            index=0 if settings.LLM_PROVIDER == "gemini" else 1
        )
        settings.LLM_PROVIDER = provider

        if provider == "gemini":
            api_key = st.text_input("Gemini API Key", value=settings.GEMINI_API_KEY, type="password")
            if api_key:
                settings.GEMINI_API_KEY = api_key
                os.environ["GEMINI_API_KEY"] = api_key
            model_name = st.selectbox("Model", ["gemini-2.5-flash", "gemini-1.5-pro"], index=0)
            settings.GEMINI_MODEL = model_name
        elif provider == "openai":
            api_key = st.text_input("OpenAI API Key", value=settings.OPENAI_API_KEY, type="password")
            if api_key:
                settings.OPENAI_API_KEY = api_key
                os.environ["OPENAI_API_KEY"] = api_key
            model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
            settings.OPENAI_MODEL = model_name
        else:
            st.info("Running offline using local HuggingFace / Fallback Heuristics.")

        st.markdown("---")
        st.markdown("### 🎯 Audit Parameters")
        max_clauses = st.slider("Max Clauses to Audit", min_value=3, max_value=25, value=10)
        evidence_k = st.slider("Retrieval Depth (Chunks per Clause)", min_value=2, max_value=8, value=4)
        settings.EVIDENCE_TOP_K = evidence_k

        st.markdown("---")
        st.markdown("### 📜 Past Audit Runs")
        past_audits = db.list_audits()
        selected_past_id = None
        if past_audits:
            audit_options = {f"{a['audit_id']} ({a['compliance_pct']}%) - {a['timestamp'][:10]}": a["audit_id"] for a in past_audits}
            selected_label = st.selectbox("Load Previous Audit", options=["None"] + list(audit_options.keys()))
            if selected_label != "None":
                selected_past_id = audit_options[selected_label]
        else:
            st.caption("No past audits recorded yet.")

    # --- HEADER BANNER ---
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🛡️ AegisAudit AI</h1>
        <p class="header-subtitle">Autonomous Regulatory & Policy Compliance Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # If user selected past audit, display it
    if selected_past_id:
        report = db.get_report(selected_past_id)
        if report:
            render_audit_results(report)
            return

    curr_role = curr_user.role if curr_user else UserRole.VIEWER
    tabs_to_show = ["🚀 Execute New Audit", "📊 Audit History & Analytics"]
    if curr_role == UserRole.ADMIN:
        tabs_to_show.append("👥 User Management (Admin)")

    main_tabs = st.tabs(tabs_to_show)

    with main_tabs[0]:
        col_reg, col_pol = st.columns(2)

        with col_reg:
            st.markdown("#### 📜 1. Regulatory Standard / Framework")
            reg_upload = st.file_uploader("Upload Regulatory Standard (PDF)", type=["pdf", "txt"], key="reg_file")
            
            existing_sample = settings.DATA_DIR / "sample.pdf"
            use_existing_standard = False
            if existing_sample.exists() and not reg_upload:
                use_existing_standard = st.checkbox(f"Use benchmark document ({existing_sample.name}) as Standard", value=True)

        with col_pol:
            st.markdown("#### 🏢 2. Company Policy / Operational Document")
            pol_upload = st.file_uploader("Upload Company Policy (PDF)", type=["pdf", "txt"], key="pol_file")
            use_existing_policy = False
            if existing_sample.exists() and not pol_upload:
                use_existing_policy = st.checkbox(f"Use benchmark document ({existing_sample.name}) as Policy", value=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # RBAC Check for Audit Execution
        can_run = curr_role in [UserRole.ADMIN, UserRole.AUDITOR]
        if not can_run:
            st.warning("🔒 Your current role ('viewer') has read-only access. Sign in as an Auditor or Admin to launch new audits.")
        
        btn_start = st.button(
            "⚡ Initiate Autonomous Multi-Agent Audit",
            type="primary",
            use_container_width=True,
            disabled=not can_run
        )

        if btn_start:
            std_path = None
            if reg_upload:
                std_path = settings.DATA_DIR / reg_upload.name
                with open(std_path, "wb") as f:
                    f.write(reg_upload.getbuffer())
            elif use_existing_standard and existing_sample.exists():
                std_path = existing_sample

            pol_path = None
            if pol_upload:
                pol_path = settings.DATA_DIR / pol_upload.name
                with open(pol_path, "wb") as f:
                    f.write(pol_upload.getbuffer())
            elif use_existing_policy and existing_sample.exists():
                pol_path = existing_sample

            if not std_path or not pol_path:
                st.error("Please supply both a Regulatory Standard document and a Company Policy document.")
            else:
                progress_bar = st.progress(0.0)
                status_text = st.empty()

                def update_ui(msg: str, pct: float):
                    status_text.markdown(f"**Agent Status:** `{msg}`")
                    progress_bar.progress(pct)

                orchestrator = AuditOrchestrator()
                with st.spinner("Multi-Agent Collaborative Audit in Progress..."):
                    try:
                        report = orchestrator.run_audit(
                            standard_path=std_path,
                            policy_path=pol_path,
                            max_clauses=max_clauses,
                            progress_callback=update_ui
                        )
                        db.save_report(report)
                        st.success("✅ Audit Completed Successfully!")
                        render_audit_results(report)
                    except Exception as e:
                        st.error(f"Audit encountered an error: {e}")
                        logger.error(f"Audit error: {e}", exc_info=True)

    with main_tabs[1]:
        audits = db.list_audits()
        if not audits:
            st.info("No audit runs recorded yet. Execute an audit to see analytics.")
        else:
            df = pd.DataFrame(audits)
            st.dataframe(df, use_container_width=True)

    if curr_role == UserRole.ADMIN and len(main_tabs) > 2:
        with main_tabs[2]:
            st.markdown("### 👥 Organization User Directory")
            users = user_db.list_users()
            u_df = pd.DataFrame([u.model_dump() for u in users])
            st.dataframe(u_df, use_container_width=True)


def render_audit_results(report: FullAuditReport):
    st.markdown("---")
    st.markdown(f"### 📋 Audit Findings: `{report.audit_id}`")
    st.caption(f"Standard: **{report.standard_name}** | Policy: **{report.policy_name}** | Timestamp: {report.timestamp}")

    # Top KPI Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Overall Compliance</div>
            <div class="metric-val" style="color: {'#10B981' if report.summary.overall_compliance_percentage >= 75 else '#F59E0B' if report.summary.overall_compliance_percentage >= 50 else '#EF4444'}">
                {report.summary.overall_compliance_percentage}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Compliant Controls</div>
            <div class="metric-val" style="color: #10B981">{report.summary.compliant_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Partial / Ambiguous</div>
            <div class="metric-val" style="color: #F59E0B">{report.summary.partially_compliant_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Non-Compliant Gaps</div>
            <div class="metric-val" style="color: #EF4444">{report.summary.non_compliant_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive Overview
    with st.expander("📌 Executive CISO Overview", expanded=True):
        st.markdown(report.summary.executive_overview)

    # Filter Options
    st.markdown("### 🔍 Compliance Matrix Explorer")
    filter_choice = st.radio(
        "Filter by Status:",
        options=["All", "Non-Compliant Only", "Partially Compliant Only", "Compliant Only"],
        horizontal=True
    )

    filtered_findings = report.findings
    if filter_choice == "Non-Compliant Only":
        filtered_findings = [f for f in report.findings if f.status == ComplianceStatus.NON_COMPLIANT]
    elif filter_choice == "Partially Compliant Only":
        filtered_findings = [f for f in report.findings if f.status == ComplianceStatus.PARTIALLY_COMPLIANT]
    elif filter_choice == "Compliant Only":
        filtered_findings = [f for f in report.findings if f.status == ComplianceStatus.COMPLIANT]

    # Findings Cards
    for f in filtered_findings:
        if f.status == ComplianceStatus.COMPLIANT:
            badge_class = "badge-compliant"
        elif f.status == ComplianceStatus.PARTIALLY_COMPLIANT:
            badge_class = "badge-partial"
        else:
            badge_class = "badge-non-compliant"

        citations_html = "".join([f'<span class="citation-chip">📄 Pg {c.page_number}</span>' for c in f.citations]) or '<span class="citation-chip">No Citations</span>'

        st.markdown(f"""
        <div class="finding-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 1.1rem; color: #38BDF8;">{f.clause_id}: {f.clause_title}</span>
                <div>
                    <span class="{badge_class}">{f.status.value}</span>
                    <span class="badge-risk">Risk: {f.risk_level.value}</span>
                </div>
            </div>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 12px;"><strong>Requirement:</strong> {f.requirement_summary}</p>
            <div style="margin-bottom: 10px;">
                <strong style="font-size: 0.85rem; color: #CBD5E1;">Citations:</strong> {citations_html}
            </div>
            <div style="background: rgba(0,0,0,0.25); border-left: 3px solid #0EA5E9; padding: 10px 14px; border-radius: 4px; margin-bottom: 10px;">
                <span style="font-size: 0.85rem; color: #94A3B8;"><strong>Identified Gap:</strong> {f.gap_analysis}</span>
            </div>
            <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; padding: 10px 14px; border-radius: 4px;">
                <span style="font-size: 0.85rem; color: #D1FAE5;"><strong>Remediation Action:</strong> {f.remediation_recommendation}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Exporters
    st.markdown("### 📥 Export Executive Report")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "⬇️ Download Markdown Brief",
            data=ReportExporter.to_markdown(report),
            file_name=f"{report.audit_id}_report.md",
            mime="text/markdown",
            use_container_width=True
        )
    with c2:
        st.download_button(
            "⬇️ Download CSV Matrix",
            data=ReportExporter.to_csv(report),
            file_name=f"{report.audit_id}_matrix.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c3:
        st.download_button(
            "⬇️ Download JSON Data",
            data=ReportExporter.to_json(report),
            file_name=f"{report.audit_id}_data.json",
            mime="application/json",
            use_container_width=True
        )
