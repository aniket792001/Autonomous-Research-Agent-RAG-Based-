"""
Settings & User Management View for AegisAudit AI.
Engine hyperparameters, LLM credentials, and Role-Based Access Control directory.
"""

import streamlit as st
import os
import pandas as pd
from typing import Optional
from core.config import settings
from models.user_schema import UserRole, UserResponse
from db.user_store import UserDatabase

def render_settings_view():
    st.markdown("### ⚙️ Engine Settings & Administration")
    st.caption("Configure AI intelligence backends, API credentials, and enterprise user roles.")

    user_db = UserDatabase()
    curr_user: Optional[UserResponse] = st.session_state.get("auth_user")
    is_admin = curr_user and curr_user.role == UserRole.ADMIN

    tabs = ["🤖 AI Engine & Models", "⚙️ Retrieval & Hyperparameters"]
    if is_admin:
        tabs.append("👥 User Directory & RBAC (Admin)")

    set_tabs = st.tabs(tabs)

    with set_tabs[0]:
        st.markdown("#### LLM Provider Configuration")
        provider = st.selectbox(
            "Primary LLM Provider:",
            options=["gemini", "openai", "huggingface"],
            index=0 if settings.LLM_PROVIDER == "gemini" else 1 if settings.LLM_PROVIDER == "openai" else 2,
            key="set_provider_select"
        )
        settings.LLM_PROVIDER = provider

        col_k1, col_k2 = st.columns(2)

        if provider == "gemini":
            with col_k1:
                api_key = st.text_input("Google Gemini API Key:", value=settings.GEMINI_API_KEY, type="password", key="set_gemini_key")
                if api_key:
                    settings.GEMINI_API_KEY = api_key
                    os.environ["GEMINI_API_KEY"] = api_key
            with col_k2:
                model_name = st.selectbox("Gemini Model:", ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"], index=0, key="set_gemini_model")
                settings.GEMINI_MODEL = model_name

        elif provider == "openai":
            with col_k1:
                api_key = st.text_input("OpenAI API Key:", value=settings.OPENAI_API_KEY, type="password", key="set_openai_key")
                if api_key:
                    settings.OPENAI_API_KEY = api_key
                    os.environ["OPENAI_API_KEY"] = api_key
            with col_k2:
                model_name = st.selectbox("OpenAI Model:", ["gpt-4o-mini", "gpt-4o"], index=0, key="set_openai_model")
                settings.OPENAI_MODEL = model_name

        else:
            st.info("Running with offline local HuggingFace / Heuristic Fallbacks. Zero external API calls.")

        st.success(f"Configured: {provider.upper()} ({settings.GEMINI_MODEL if provider == 'gemini' else settings.OPENAI_MODEL if provider == 'openai' else 'Offline'})")

    with set_tabs[1]:
        st.markdown("#### RAG & Indexing Parameters")
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            settings.CHUNK_SIZE = st.number_input("Document Chunk Size (Tokens)", min_value=200, max_value=2000, value=settings.CHUNK_SIZE, step=100)
            settings.CHUNK_OVERLAP = st.number_input("Chunk Overlap (Tokens)", min_value=0, max_value=400, value=settings.CHUNK_OVERLAP, step=25)
        with c_r2:
            st.markdown(f"""
            <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid #1F2937; border-radius: 8px; padding: 14px; margin-top: 14px;">
                <div style="font-size: 0.8rem; color: #94A3B8;">EMBEDDINGS MODEL</div>
                <div style="font-weight: 600; color: #F9FAFB; font-size: 0.95rem;">{settings.HF_EMBEDDING_MODEL}</div>
                <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px;">Local Dense Vector Index (FAISS / NumPy)</div>
            </div>
            """, unsafe_allow_html=True)

    if is_admin and len(set_tabs) > 2:
        with set_tabs[2]:
            st.markdown("#### Organization User Directory")
            users = user_db.list_users()
            u_df = pd.DataFrame([u.model_dump() for u in users])
            st.dataframe(u_df, use_container_width=True, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("➕ Register New Team Member", expanded=False):
                with st.form("new_user_form"):
                    f_name = st.text_input("Full Name")
                    f_email = st.text_input("Work Email")
                    f_pass = st.text_input("Temporary Password", type="password")
                    f_role = st.selectbox("Role", ["auditor", "viewer", "admin"])
                    submitted = st.form_submit_button("Create User Account", type="primary")

                    if submitted:
                        if f_name and f_email and f_pass:
                            try:
                                user_db.create_user(
                                    email=f_email,
                                    password=f_pass,
                                    full_name=f_name,
                                    role=UserRole(f_role)
                                )
                                st.success(f"User {f_email} successfully registered!")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Error creating user: {err}")
                        else:
                            st.warning("All fields are required.")
