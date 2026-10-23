"""
Interactive Streamlit Dashboard for AegisAudit AI.
Multi-workspace architecture with executive analytics, audit wizard, two-pane findings inspector, and RBAC.
"""

import streamlit as st
from typing import Optional

from core.security import PasswordHasher
from core.logger import logger
from ui.styles import CUSTOM_CSS
from db.user_store import UserDatabase
from models.user_schema import UserRole, UserResponse

# Import modular views
from ui.views.dashboard_view import render_dashboard_view
from ui.views.studio_view import render_studio_view
from ui.views.explorer_view import render_explorer_view
from ui.views.standards_view import render_standards_view
from ui.views.settings_view import render_settings_view

def render_dashboard():
    st.set_page_config(
        page_title="AegisAudit AI - Autonomous Compliance Platform",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    user_db = UserDatabase()

    # Session state initialization
    if "auth_user" not in st.session_state:
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

    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "📊 Executive Dashboard"

    # --- SLEEK SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 18px;">
            <span style="font-size: 1.8rem;">🛡️</span>
            <div>
                <div style="font-weight: 800; font-size: 1.15rem; color: #F9FAFB; letter-spacing: -0.02em;">AegisAudit AI</div>
                <div style="font-size: 0.72rem; color: #0EA5E9; font-weight: 600; text-transform: uppercase;">Autonomous Compliance</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        curr_user: Optional[UserResponse] = st.session_state.get("auth_user")

        # User Profile or Auth Box
        if curr_user:
            role_color = (
                "#10B981" if curr_user.role == UserRole.ADMIN
                else "#0EA5E9" if curr_user.role == UserRole.AUDITOR
                else "#F59E0B"
            )

            st.markdown(f"""
            <div class="sidebar-profile-card">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">ACTIVE OPERATOR</div>
                <div style="font-weight: 700; color: #F9FAFB; font-size: 0.95rem; margin-top: 2px;">{curr_user.full_name}</div>
                <div style="font-size: 0.75rem; color: #94A3B8;">{curr_user.email}</div>
                <div style="margin-top: 8px;">
                    <span style="background: rgba(255,255,255,0.06); border: 1px solid {role_color}; color: {role_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">
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
                t_login, t_reg = st.tabs(["Sign In", "Register"])
                with t_login:
                    login_email = st.text_input("Email", value="admin@aegisaudit.com", key="sb_login_email")
                    login_pass = st.text_input("Password", value="AdminPass123!", type="password", key="sb_login_pass")
                    if st.button("Sign In", type="primary", use_container_width=True):
                        u_rec = user_db.get_user_by_email(login_email)
                        if u_rec and PasswordHasher.verify_password(login_pass, u_rec["hashed_password"]):
                            st.session_state["auth_user"] = UserResponse(
                                id=u_rec["id"],
                                email=u_rec["email"],
                                full_name=u_rec["full_name"],
                                role=u_rec["role"],
                                is_active=u_rec["is_active"],
                                created_at=u_rec["created_at"]
                            )
                            st.success("Authenticated!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")

                with t_reg:
                    reg_name = st.text_input("Name", key="sb_reg_name")
                    reg_email = st.text_input("Email", key="sb_reg_email")
                    reg_pass = st.text_input("Password", type="password", key="sb_reg_pass")
                    reg_role = st.selectbox("Role", ["auditor", "viewer", "admin"], key="sb_reg_role")
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
                                st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("<div style='font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>WORKSPACES</div>", unsafe_allow_html=True)

        # Workspace Navigation
        views = [
            "📊 Executive Dashboard",
            "⚡ Audit Studio",
            "🔍 Findings Explorer",
            "📚 Standards Library",
            "⚙️ Settings & Team"
        ]

        active_idx = views.index(st.session_state["active_view"]) if st.session_state["active_view"] in views else 0
        selected_view = st.radio("Navigation", views, index=active_idx, label_visibility="collapsed")
        
        if selected_view != st.session_state["active_view"]:
            st.session_state["active_view"] = selected_view
            st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.72rem; color: #475569; text-align: center; margin-top: 10px;">
            AegisAudit AI v1.2<br/>
            Multi-Agent Audit Engine
        </div>
        """, unsafe_allow_html=True)

    # --- TOP APP BANNER ---
    curr_view_name = st.session_state["active_view"].replace("📊 ", "").replace("⚡ ", "").replace("🔍 ", "").replace("📚 ", "").replace("⚙️ ", "")
    user_badge = curr_user.role.value.upper() if curr_user else "VIEWER"

    st.markdown(f"""
    <div class="app-header">
        <div class="header-brand">
            <span style="font-size: 2.2rem;">🛡️</span>
            <div>
                <h1 class="header-title">AegisAudit AI</h1>
                <p class="header-subtitle">Workspace: {curr_view_name} &bull; Enterprise Compliance & Governance Platform</p>
            </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span style="background: rgba(16, 185, 129, 0.12); border: 1px solid #10B981; color: #34D399; padding: 4px 10px; border-radius: 9999px; font-size: 0.72rem; font-weight: 600;">
                ● System Ready
            </span>
            <span class="header-badge">Role: {user_badge}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- WORKSPACE ROUTING ---
    active = st.session_state["active_view"]

    if active == "📊 Executive Dashboard":
        render_dashboard_view()
    elif active == "⚡ Audit Studio":
        render_studio_view()
    elif active == "🔍 Findings Explorer":
        render_explorer_view()
    elif active == "📚 Standards Library":
        render_standards_view()
    elif active == "⚙️ Settings & Team":
        render_settings_view()
    else:
        render_dashboard_view()
