import streamlit as st
from database import get_user_by_email, create_user, verify_password


def login_page():
    # Centered sign-in experience. Global styling is inherited from app.py.
    left, center, right = st.columns([1, 1.5, 1], gap="large")

    with center:
        st.markdown(
            """
            <div class="sos-auth-brand">
                <div class="sos-auth-mark">⚡</div>
                <div class="sos-auth-title">StrengthOS</div>
                <div class="sos-auth-subtitle">ATHLETE PERFORMANCE PLATFORM</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("### Welcome back")
            st.caption("Sign in to access your training workspace.")

            with st.form("strengthos_login_form", clear_on_submit=False):
                email = st.text_input(
                    "Email",
                    key="login_email",
                    placeholder="you@example.com",
                ).strip()
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_pw",
                    placeholder="Enter your password",
                )
                submitted = st.form_submit_button(
                    "Sign In",
                    use_container_width=True,
                    type="primary",
                )

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
                        st.error(
                            "We couldn't sign you in right now. Please try again. "
                            "If the problem continues, contact your coach or administrator."
                        )

            st.markdown(
                """
                <div class="sos-auth-note">
                    <strong>Welcome to StrengthOS</strong>
                    <span>Use your coach-provided account to sign in, or create an account below.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with tab_register:
            st.markdown("### Create your account")
            st.caption("Set up your profile to get started.")

            with st.form("strengthos_register_form", clear_on_submit=False):
                role_label = st.selectbox(
                    "Account type",
                    ["Athlete", "Coach"],
                    key="reg_role",
                )
                name = st.text_input(
                    "Full name",
                    key="reg_name",
                    placeholder="Your full name",
                ).strip()
                reg_email = st.text_input(
                    "Email",
                    key="reg_email",
                    placeholder="you@example.com",
                ).strip().lower()
                reg_pw = st.text_input(
                    "Password",
                    type="password",
                    key="reg_pw",
                    placeholder="At least 6 characters",
                )
                reg_pw2 = st.text_input(
                    "Confirm password",
                    type="password",
                    key="reg_pw2",
                    placeholder="Re-enter your password",
                )

                sport = ""
                position = ""
                year = ""
                coach_email = ""
                if role_label == "Athlete":
                    st.markdown("#### Athlete profile")
                    sport = st.text_input("Sport", key="reg_sport", placeholder="e.g. Baseball")
                    position = st.text_input(
                        "Position",
                        key="reg_position",
                        placeholder="e.g. Pitcher, Infielder",
                    )
                    year = st.selectbox(
                        "Year",
                        ["Freshman", "Sophomore", "Junior", "Senior", "Grad"],
                        key="reg_year",
                    )
                    coach_email = st.text_input(
                        "Coach email (optional)",
                        key="reg_coach_email",
                        placeholder="coach@example.com",
                    ).strip().lower()

                submitted_registration = st.form_submit_button(
                    "Create Account",
                    use_container_width=True,
                    type="primary",
                )

            if submitted_registration:
                if not all([name, reg_email, reg_pw, reg_pw2]):
                    st.error("Please complete all required fields.")
                elif "@" not in reg_email or "." not in reg_email.rsplit("@", 1)[-1]:
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
                            st.error("We couldn't find a coach with that email. Check it and try again.")
                            st.stop()

                    try:
                        ok, message = create_user(
                            name,
                            reg_email,
                            reg_pw,
                            role_label.lower(),
                            coach_id=coach_id,
                            sport=sport,
                            position=position,
                            year=year,
                        )
                        if ok:
                            st.success("Account created. You can now sign in.")
                        else:
                            st.error(message)
                    except Exception:
                        st.error(
                            "We couldn't create the account right now. "
                            "Please try again or contact your administrator."
                        )


# Login-specific visual refinements; safe if app.py's global CSS is also present.
st.markdown(
    """
    <style>
    .sos-auth-brand {
        text-align: center;
        padding: 1.25rem 0 1.5rem;
    }
    .sos-auth-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 1.1rem;
        background: linear-gradient(145deg, #d9bd6a, #b18c34);
        color: #101827;
        font-size: 2rem;
        box-shadow: 0 8px 24px rgba(210, 177, 92, .18);
        margin-bottom: .8rem;
    }
    .sos-auth-title {
        color: #f3f6fb;
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -.045em;
        line-height: 1.15;
    }
    .sos-auth-subtitle {
        color: #d2b15c;
        font-size: .7rem;
        font-weight: 750;
        letter-spacing: .16em;
        margin-top: .55rem;
    }
    .sos-auth-note {
        display: flex;
        flex-direction: column;
        gap: .25rem;
        background: #101d30;
        border: 1px solid #263852;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        color: #f3f6fb;
        font-size: .88rem;
    }
    .sos-auth-note strong {
        color: #f0d98d;
    }
    .sos-auth-note span {
        color: #a7b4c7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
