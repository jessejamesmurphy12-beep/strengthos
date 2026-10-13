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
