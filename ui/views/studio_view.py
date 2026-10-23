"""
Audit Studio View for AegisAudit AI.
Step-by-step wizard to launch autonomous multi-agent compliance audits.
"""

import streamlit as st
from pathlib import Path
from typing import List, Optional
from core.config import settings
from core.logger import logger
from models.user_schema import UserRole, UserResponse
from rag.standards_catalog import StandardsCatalogService, STANDARDS_CATALOG
from agents.orchestrator import AuditOrchestrator
from db.storage import AuditDatabase

def render_studio_view():
    st.markdown("### ⚡ Autonomous Audit Studio")
    st.caption("Configure regulatory scope, load corporate policy files, and launch multi-agent verification.")

    db = AuditDatabase()
    curr_user: Optional[UserResponse] = st.session_state.get("auth_user")
    curr_role = curr_user.role if curr_user else UserRole.VIEWER

    # RBAC Access Guard
    if curr_role not in [UserRole.ADMIN, UserRole.AUDITOR]:
        st.warning("🔒 Read-Only Access: Your role ('viewer') is authorized to inspect audit reports but cannot initiate new audits. Sign in as an Auditor or Admin to launch.")
        return

    # --- STEP 1: REGULATORY STANDARD ---
    st.markdown("""
    <div class="wizard-step-card">
        <div class="wizard-step-header">
            <div class="wizard-step-num">1</div>
            <div class="wizard-step-title">Select Regulatory Standard / Framework</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    source_type = st.radio(
        "Standard Source:",
        options=["Pre-Seeded Industry Standard (Recommended)", "Upload Custom Standard Document (PDF/TXT)"],
        horizontal=True,
        key="std_source_type"
    )

    std_path: Optional[Path] = None

    if source_type == "Pre-Seeded Industry Standard (Recommended)":
        std_options = {
            f"{s['title']} — {s['badge']} ({s['category']})": k
            for k, s in STANDARDS_CATALOG.items()
        }
        selected_std_label = st.selectbox("Choose Framework:", list(std_options.keys()), index=0)
        selected_std_key = std_options[selected_std_label]
        selected_meta = StandardsCatalogService.get_standard_meta(selected_std_key)

        # Standard Info Card
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid #1F2937; border-radius: 8px; padding: 14px; margin-top: 8px; margin-bottom: 12px;">
            <div style="font-weight: 700; color: #38BDF8; font-size: 0.95rem;">{selected_meta['full_name']}</div>
            <div style="font-size: 0.85rem; color: #94A3B8; margin-top: 4px;">{selected_meta['description']}</div>
            <div style="font-size: 0.8rem; color: #64748B; margin-top: 8px;"><strong>Sample Controls:</strong> {', '.join(selected_meta['key_controls'][:4])}...</div>
        </div>
        """, unsafe_allow_html=True)

        std_path = StandardsCatalogService.get_standard_file_path(selected_std_key)

    else:
        uploaded_std = st.file_uploader("Upload Regulatory Standard Document (PDF or TXT)", type=["pdf", "txt"], key="custom_std_file")
        if uploaded_std:
            save_path = settings.DATA_DIR / uploaded_std.name
            with open(save_path, "wb") as f:
                f.write(uploaded_std.getbuffer())
            std_path = save_path
            st.success(f"Loaded: `{uploaded_std.name}` ({len(uploaded_std.getbuffer()) // 1024} KB)")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- STEP 2: CORPORATE POLICIES ---
    st.markdown("""
    <div class="wizard-step-card">
        <div class="wizard-step-header">
            <div class="wizard-step-num">2</div>
            <div class="wizard-step-title">Select Corporate Policy Document(s) to Audit</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    policy_source = st.radio(
        "Policy Source:",
        options=["Upload Policy File(s)", "Use Benchmark Sample Document (sample.pdf)"],
        horizontal=True,
        key="policy_source_type"
    )

    policy_paths: List[Path] = []

    if policy_source == "Upload Policy File(s)":
        uploaded_policies = st.file_uploader(
            "Upload One or More Company Policy Documents (PDF / TXT)",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="custom_policy_files"
        )
        if uploaded_policies:
            for p_file in uploaded_policies:
                target_p = settings.DATA_DIR / p_file.name
                with open(target_p, "wb") as f:
                    f.write(p_file.getbuffer())
                policy_paths.append(target_p)
            st.success(f"Loaded {len(policy_paths)} policy document(s) into audit queue.")
    else:
        sample_file = settings.DATA_DIR / "sample.pdf"
        if sample_file.exists():
            policy_paths = [sample_file]
            st.info(f"Using benchmark document: `{sample_file.name}` ({sample_file.stat().st_size // 1024} KB)")
        else:
            st.warning("Benchmark sample.pdf not found in data/. Please upload policy files above.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- STEP 3: SCOPE & EXECUTION ---
    st.markdown("""
    <div class="wizard-step-card">
        <div class="wizard-step-header">
            <div class="wizard-step-num">3</div>
            <div class="wizard-step-title">Audit Tuning & Launch</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_tune1, c_tune2, c_tune3 = st.columns(3)
    with c_tune1:
        max_clauses = st.slider("Max Clauses to Audit", min_value=3, max_value=25, value=10, help="Controls how many regulatory mandates are evaluated.")
    with c_tune2:
        evidence_k = st.slider("Retrieval Depth per Clause", min_value=2, max_value=8, value=4, help="Number of hybrid semantic chunks retrieved for each clause.")
        settings.EVIDENCE_TOP_K = evidence_k
    with c_tune3:
        st.markdown(f"""
        <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid #1F2937; border-radius: 8px; padding: 12px; margin-top: 10px;">
            <div style="font-size: 0.75rem; color: #94A3B8;">ACTIVE AI PROVIDER</div>
            <div style="font-weight: 700; color: #38BDF8; font-size: 0.95rem; text-transform: uppercase;">{settings.LLM_PROVIDER}</div>
            <div style="font-size: 0.75rem; color: #64748B;">Model: {settings.GEMINI_MODEL if settings.LLM_PROVIDER == 'gemini' else settings.OPENAI_MODEL}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    btn_launch = st.button("🚀 Launch Autonomous Multi-Agent Audit", type="primary", use_container_width=True)

    if btn_launch:
        if not std_path:
            st.error("Missing Regulatory Standard: Please select or upload a standard in Step 1.")
            return
        if not policy_paths:
            st.error("Missing Company Policies: Please select or upload at least one policy document in Step 2.")
            return

        # Execution telemetry container
        st.markdown("---")
        st.markdown("#### 🤖 Real-Time Multi-Agent Execution Telemetry")
        progress_bar = st.progress(0.0)
        status_box = st.empty()

        def update_telemetry(msg: str, pct: float):
            status_box.markdown(f"**Current Agent Action:** `{msg}`")
            progress_bar.progress(pct)

        orchestrator = AuditOrchestrator()
        try:
            with st.spinner("Multi-Agent Collaborative Audit in Progress..."):
                report = orchestrator.run_audit(
                    standard_path=std_path,
                    policy_path=policy_paths,
                    max_clauses=max_clauses,
                    progress_callback=update_telemetry
                )
                db.save_report(report)

            st.success(f"✅ Audit Successfully Completed! Audit ID: `{report.audit_id}`")
            
            # Save selected audit and provide quick redirect
            st.session_state["selected_audit_id"] = report.audit_id
            
            col_inspect, col_stay = st.columns([2, 3])
            with col_inspect:
                if st.button("Inspect Findings in Explorer ➔", type="primary", use_container_width=True):
                    st.session_state["active_view"] = "🔍 Findings Explorer"
                    st.rerun()

        except Exception as e:
            st.error(f"Audit execution encountered an error: {e}")
            logger.error(f"Audit Studio error: {e}", exc_info=True)
