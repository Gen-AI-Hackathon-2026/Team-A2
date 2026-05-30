"""
Login Page for Synapse AI Tutor.
Provides a premium login interface with hardcoded authentication.
"""

import streamlit as st
from backend.auth import authenticate


def render_login():
    """Render the login page."""

    # Center content
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # Logo and title
        st.markdown("""
        <div class="main-header animate-fade-in" style="margin-top: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">
                <span style="background: linear-gradient(135deg, #6C63FF, #00D2FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 4rem;">S</span>
            </div>
            <h1>Synapse</h1>
            <p style="font-size: 1.2rem; color: #A0A0C0; margin-bottom: 0.3rem;">Adaptive AI Tutor</p>
            <p style="font-size: 0.85rem; color: #6B6B8D;">Personalized learning powered by RAG &amp; GPT</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Login form
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <span class="gradient-text" style="font-size: 1.3rem;">Welcome Back</span>
            <p style="color: #A0A0C0; font-size: 0.85rem; margin-top: 0.3rem;">Sign in to continue learning</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True
            )

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.page = "topic_selection"
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        # Demo credentials hint
        st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem; padding: 1rem;
                    background: rgba(108, 99, 255, 0.05); border-radius: 12px;
                    border: 1px solid rgba(108, 99, 255, 0.1);">
            <p style="color: #6B6B8D; font-size: 0.8rem; margin-bottom: 0.3rem;">Demo Credentials</p>
            <p style="color: #A0A0C0; font-size: 0.85rem;">
                <code style="background: rgba(108, 99, 255, 0.1); padding: 2px 8px; border-radius: 4px; color: #8B83FF;">demo</code> /
                <code style="background: rgba(108, 99, 255, 0.1); padding: 2px 8px; border-radius: 4px; color: #8B83FF;">demo</code>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Features showcase
        st.markdown("<br>", unsafe_allow_html=True)

        feat_cols = st.columns(3)
        features = [
            ("Adaptive Learning", "Personalized to your level"),
            ("RAG-Powered", "Learn from real textbooks"),
            ("Track Progress", "Visualize your growth"),
        ]

        for col, (title, desc) in zip(feat_cols, features):
            with col:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: rgba(20, 20, 46, 0.5);
                            border-radius: 12px; border: 1px solid rgba(108, 99, 255, 0.08);">
                    <div style="color: #FFFFFF; font-weight: 600; font-size: 0.85rem;">{title}</div>
                    <div style="color: #6B6B8D; font-size: 0.75rem; margin-top: 0.2rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
