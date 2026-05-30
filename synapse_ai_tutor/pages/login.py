"""
Login Page for Synapse AI Tutor.
"""

import streamlit as st
from backend.auth import authenticate


def render_login():
    """Render the login page (used when not authenticated)."""

    # Centre the form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            """
<div style="text-align:center;margin-top:3rem;margin-bottom:1.5rem;">
    <div style="font-size:2.8rem;font-weight:900;
                background:linear-gradient(135deg,#6C63FF,#00D2FF);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                letter-spacing:-2px;margin-bottom:0.4rem;">SYN</div>
    <h1 style="font-size:1.8rem;font-weight:800;color:#FFFFFF;margin:0;">Synapse AI Tutor</h1>
    <p style="color:#A0A0C0;font-size:0.9rem;margin-top:0.3rem;">Adaptive AI Learning Platform</p>
    <p style="color:#6B6B8D;font-size:0.78rem;">Powered by RAG and GPT</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
<div style="text-align:center;margin-bottom:1.2rem;">
    <span style="font-size:1.1rem;font-weight:700;color:#FFFFFF;">Welcome Back</span>
    <p style="color:#A0A0C0;font-size:0.82rem;margin-top:0.2rem;">Sign in to continue learning</p>
</div>
""",
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.page = "Home"
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        st.markdown(
            """
<div style="text-align:center;margin-top:1.2rem;padding:0.9rem;
            background:rgba(108,99,255,0.05);border-radius:10px;
            border:1px solid rgba(108,99,255,0.1);">
    <p style="color:#6B6B8D;font-size:0.75rem;margin-bottom:0.3rem;">Demo Credentials</p>
    <p style="color:#A0A0C0;font-size:0.82rem;margin:0;">
        <code style="background:rgba(108,99,255,0.1);padding:2px 7px;border-radius:4px;color:#8B83FF;">demo</code>
        &nbsp;/&nbsp;
        <code style="background:rgba(108,99,255,0.1);padding:2px 7px;border-radius:4px;color:#8B83FF;">demo</code>
    </p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(3)
        for col2, (title, desc) in zip(
            cols,
            [
                ("Adaptive Learning", "Personalised to your level"),
                ("RAG-Powered", "Learn from real textbooks"),
                ("Track Progress", "Visualise your growth"),
            ],
        ):
            with col2:
                st.markdown(
                    f"""
<div style="text-align:center;padding:0.8rem;background:rgba(20,20,46,0.5);
            border-radius:10px;border:1px solid rgba(108,99,255,0.08);">
    <div style="color:#FFFFFF;font-weight:600;font-size:0.82rem;">{title}</div>
    <div style="color:#6B6B8D;font-size:0.72rem;margin-top:0.15rem;">{desc}</div>
</div>
""",
                    unsafe_allow_html=True,
                )
