import streamlit as st
from database import get_user_by_email, create_user, verify_password


def login_page():
    # Inject auth-specific styles
    st.markdown("""
    <style>
    .sos-auth-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 3rem 0 2rem;
    }
    .sos-brand-icon {
        width: 56px; height: 56px;
        border-radius: 18px;
        background: linear-gradient(145deg, #e8cc7a, #a8782a);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.75rem;
        box-shadow: 0 10px 30px rgba(201,168,76,0.25);
        margin: 0 auto 1rem;
    }
    .sos-brand-name {
        font-size: 2.4rem;
        font-weight: 900;
        color: #eef2f8;
        letter-spacing: -0.05em;
        text-align: center;
        line-height: 1;
        margin-bottom: 0.35rem;
    }
    .sos-brand-tag {
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 0.2em;
        color: #c9a84c;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sos-auth-card {
        background: #0e1520;
        border: 1px solid #1e2d42;
        border-radius: 18px;
        padding: 1.75rem;
        width: 100%;
    }
    .sos-auth-note {
        background: #0e1520;
        border: 1px solid #1e2d42;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-top: 1rem;
        font-size: 0.82rem;
        color: #8fa3bc;
        line-height: 1.5;
    }
    .sos-auth-note strong { color: #e8cc7a; }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.4, 1], gap="large")

    with center:
        st.markdown("""
        <div class="sos-auth-wrap">
            <div class="sos-brand-icon">⚡</div>
            <div class="sos-brand-name">StrengthOS</div>
            <div class="sos-brand-tag">ATHLETE PERFORMANCE PLATFORM</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        # ── Sign in ──────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("#### Welcome back")
            st.caption("Sign in to access your training workspace.")

            with st.form("sos_login", clear_on_submit=False):
                email = st.text_input("Email", placeholder="you@example.com", key="login_email").strip()
                password = st.text_input("Password", type="password", placeholder="Your password", key="login_pw")
                submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
                    try:
                        user = get_user_by_email(email)
                        if user and verify_password(password, user["password_hash"]):
                            st.session_state.user = user
                            st.rerun()
                        else:
                            st.error("Email or password is incorrect.")
                    except Exception:
                        st.error("Couldn't sign you in right now. Please try again.")

            st.markdown("""
            <div class="sos-auth-note">
                <strong>New here?</strong> Use the Create Account tab to register,
                or ask your coach for login details.
            </div>
            """, unsafe_allow_html=True)

        # ── Register ─────────────────────────────────────────────────────────
        with tab_register:
            st.markdown("#### Create your account")
            st.caption("Set up your profile to get started.")

            with st.form("sos_register", clear_on_submit=False):
                role_label = st.selectbox("Account type", ["Athlete", "Coach"], key="reg_role")
                name = st.text_input("Full name", placeholder="Your full name", key="reg_name").strip()
                reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email").strip().lower()
                c1, c2 = st.columns(2)
                reg_pw  = c1.text_input("Password", type="password", placeholder="6+ characters", key="reg_pw")
                reg_pw2 = c2.text_input("Confirm password", type="password", placeholder="Re-enter", key="reg_pw2")

                sport = position = year = coach_email = ""
                if role_label == "Athlete":
                    st.markdown("---")
                    st.caption("ATHLETE PROFILE")
                    ca, cb = st.columns(2)
                    sport    = ca.text_input("Sport", placeholder="e.g. Baseball", key="reg_sport")
                    position = cb.text_input("Position", placeholder="e.g. Pitcher", key="reg_position")
                    year     = st.selectbox("Year", ["Freshman","Sophomore","Junior","Senior","Grad","Pro"], key="reg_year")
                    coach_email = st.text_input("Coach email (optional)", placeholder="coach@example.com", key="reg_coach_email").strip().lower()

                submitted_reg = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

            if submitted_reg:
                if not all([name, reg_email, reg_pw, reg_pw2]):
                    st.error("Please complete all required fields.")
                elif "@" not in reg_email:
                    st.error("Enter a valid email address.")
                elif reg_pw != reg_pw2:
                    st.error("Passwords do not match.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    coach_id = None
                    if role_label == "Athlete" and coach_email:
                        try:
                            coach = get_user_by_email(coach_email)
                        except Exception:
                            coach = None
                        if coach and coach.get("role") == "coach":
                            coach_id = coach["id"]
                        elif coach_email:
                            st.error("No coach found with that email. Double-check and try again.")
                            st.stop()

                    try:
                        ok, message = create_user(
                            name, reg_email, reg_pw, role_label.lower(),
                            coach_id=coach_id, sport=sport, position=position, year=year,
                        )
                        if ok:
                            st.success("Account created — you can now sign in.")
                        else:
                            st.error(message)
                    except Exception:
                        st.error("Couldn't create the account right now. Please try again.")
