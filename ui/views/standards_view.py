"""
Standards & Policy Library View for AegisAudit AI.
Displays pre-seeded regulatory frameworks and uploaded policy repositories.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any
from core.config import settings
from rag.standards_catalog import StandardsCatalogService, STANDARDS_CATALOG

def render_standards_view():
    st.markdown("### 📚 Regulatory Standards & Policy Document Library")
    st.caption("Browse pre-seeded compliance frameworks and manage organizational policy assets.")

    lib_tab1, lib_tab2 = st.tabs(["📜 Pre-Seeded Regulatory Standards", "🏢 Corporate Policy Repository"])

    with lib_tab1:
        st.markdown("#### Pre-Configured Global Frameworks")
        st.write("These frameworks are pre-indexed and ready for instant automated audits.")

        standards_list = StandardsCatalogService.list_standards()

        for std in standards_list:
            col_info, col_act = st.columns([4, 1])

            with col_info:
                st.markdown(f"""
                <div class="standard-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 1.15rem; font-weight: 700; color: #38BDF8;">{std['title']}</span>
                        <span style="background: rgba(14, 165, 233, 0.15); border: 1px solid #0EA5E9; color: #38BDF8; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">
                            {std['badge']}
                        </span>
                    </div>
                    <div style="font-size: 0.88rem; color: #E2E8F0; font-weight: 500; margin-bottom: 4px;">{std['full_name']}</div>
                    <div style="font-size: 0.82rem; color: #94A3B8; margin-bottom: 10px;">{std['description']}</div>
                    <div style="font-size: 0.78rem; color: #64748B;">
                        <strong>Key Domains:</strong> {', '.join(std['key_controls'][:3])} (+{len(std['key_controls']) - 3} more)
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_act:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button(f"Audit {std['title']}", key=f"btn_audit_std_{std['key']}", use_container_width=True):
                    st.session_state["active_view"] = "⚡ Audit Studio"
                    st.rerun()

    with lib_tab2:
        st.markdown("#### Uploaded Company Documents")
        st.caption(f"Documents currently indexed in `{settings.DATA_DIR}`:")

        files = list(settings.DATA_DIR.glob("*.pdf")) + list(settings.DATA_DIR.glob("*.txt"))

        if not files:
            st.info("No policy documents found in the local repository.")
        else:
            file_data = []
            for f in files:
                stat = f.stat()
                file_data.append({
                    "Document Name": f.name,
                    "Size (KB)": round(stat.st_size / 1024, 1),
                    "Last Modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "Type": f.suffix.upper()[1:]
                })

            import pandas as pd
            df_files = pd.DataFrame(file_data)
            st.dataframe(df_files, use_container_width=True, hide_index=True)
