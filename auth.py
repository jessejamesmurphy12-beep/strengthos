import streamlit as st
from database import get_user_by_email, create_user, verify_password, get_athletes

def login_page():
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 2rem 0 1rem;'>
            <span style='font-size:2.8rem;'>⚡</span>
            <h1 style='font-size:2rem; font-weight:800; color:#0f172a; margin:0;'>StrengthOS</h1>
            <p style='color:#64748b; margin-top:0.25rem;'>Online Strength & Conditioning Platform</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    user = get_user_by_email(email)
                    if user and verify_password(password, user["password_hash"]):
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
            st.markdown("""
            <div style='background:#f0f9ff; border-radius:8px; padding:0.75rem 1rem; margin-top:1rem;
                        font-size:0.82rem; color:#0369a1;'>
            <b>Demo login:</b> coach@demo.com / coach123
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            role = st.selectbox("Account type", ["Athlete", "Coach"], key="reg_role")
            name = st.text_input("Full name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pw = st.text_input("Password", type="password", key="reg_pw")
            reg_pw2 = st.text_input("Confirm password", type="password", key="reg_pw2")

            coach_id = None
            sport = position = year = ""
            if role == "Athlete":
                st.markdown("##### Athlete Info")
                sport = st.text_input("Sport", key="reg_sport")
                position = st.text_input("Position", key="reg_position")
                year = st.selectbox("Year", ["Freshman","Sophomore","Junior","Senior","Grad"], key="reg_year")
                coach_email = st.text_input("Coach email (to link your account)", key="reg_coach_email")
                if coach_email:
                    coach = get_user_by_email(coach_email)
                    if coach and coach["role"] == "coach":
                        coach_id = coach["id"]
                        st.success(f"✓ Linked to coach: {coach['name']}")
                    elif coach_email:
                        st.warning("No coach found with that email.")

            if st.button("Create Account", use_container_width=True, type="primary", key="reg_btn"):
                if not all([name, reg_email, reg_pw, reg_pw2]):
                    st.error("Please fill all fields.")
                elif reg_pw != reg_pw2:
                    st.error("Passwords don't match.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, msg = create_user(name, reg_email, reg_pw, role.lower(),
                                          coach_id=coach_id, sport=sport,
                                          position=position, year=year)
                    if ok:
                        st.success(f"Account created! Sign in above.")
                    else:
                        st.error(msg)
