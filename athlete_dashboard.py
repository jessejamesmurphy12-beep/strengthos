import streamlit as st
from database import (get_assigned_program, get_phases, get_days,
                      get_exercises_for_day, log_workout, get_athlete_logs)

def athlete_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"""
        <div style='padding:1rem 0 0.5rem;'>
            <div style='font-size:1.5rem;'>⚡</div>
            <div style='font-weight:700; font-size:1rem;'>StrengthOS</div>
            <div style='font-size:0.8rem; color:#94a3b8; margin-top:2px;'>Athlete Portal</div>
        </div>
        <hr style='border-color:#1e293b; margin:0.5rem 0;'>
        <div style='font-size:0.85rem; padding:0.5rem 0;'>👋 {user["name"]}</div>
        """, unsafe_allow_html=True)

        page = st.radio("Navigation", ["My Program", "Log Workout", "My Progress"],
                        label_visibility="collapsed")
        st.markdown("<br>" * 8, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if page == "My Program":
        show_my_program(user)
    elif page == "Log Workout":
        show_log_workout(user)
    elif page == "My Progress":
        show_progress(user)


def show_my_program(user):
    st.markdown(f"## 🏋️ My Program")
    prog = get_assigned_program(user["id"])
    if not prog:
        st.info("You haven't been assigned a program yet. Ask your coach!")
        return

    st.markdown(f"### {prog['name']}")
    st.markdown(f"*{prog.get('description','') or ''}*")
    c1, c2 = st.columns(2)
    c1.metric("Total Weeks", prog["weeks"])
    c2.metric("Goal", prog["goal"])

    st.markdown("---")
    phases = get_phases(prog["id"])
    for phase in phases:
        st.markdown(f"""
        <div style='background:#1B4F72; color:white; padding:0.6rem 1rem;
                    border-radius:8px; font-weight:700; margin:1rem 0 0.5rem;'>
            {phase['name']} &nbsp;·&nbsp; Weeks {phase['week_start']}–{phase['week_end']}
            &nbsp;·&nbsp; {phase['sets']} sets · {phase['reps']} reps · RPE {phase['rpe']}
        </div>
        """, unsafe_allow_html=True)
        if phase.get("notes"):
            st.markdown(f"> 📝 {phase['notes']}")

        days = get_days(phase["id"])
        cols = st.columns(min(len(days), 2))
        for i, day in enumerate(days):
            with cols[i % 2]:
                st.markdown(f"""
                <div style='background:#f8fafc; border-radius:8px; padding:0.75rem 1rem;
                            border-left:4px solid #3b82f6; margin-bottom:0.75rem;'>
                    <div style='font-weight:700; margin-bottom:6px;'>
                        Day {day['day_number']} — {day['title']}
                    </div>
                """, unsafe_allow_html=True)
                exercises = get_exercises_for_day(day["id"])
                for ex in exercises:
                    st.markdown(f"• **{ex['name']}** — {ex['sets']} sets × {ex['reps']}" +
                                (f" · *{ex['notes']}*" if ex.get("notes") else ""))
                st.markdown("</div>", unsafe_allow_html=True)


def show_log_workout(user):
    st.markdown("## 📝 Log Workout")
    prog = get_assigned_program(user["id"])
    if not prog:
        st.info("No program assigned yet.")
        return

    phases = get_phases(prog["id"])
    if not phases:
        st.info("Program has no phases yet.")
        return

    phase_map = {p["name"]: p for p in phases}
    sel_phase = st.selectbox("Phase", list(phase_map.keys()))
    phase = phase_map[sel_phase]

    days = get_days(phase["id"])
    if not days:
        st.info("No days in this phase yet.")
        return

    day_map = {f"Day {d['day_number']} — {d['title']}": d for d in days}
    sel_day = st.selectbox("Day", list(day_map.keys()))
    day = day_map[sel_day]

    exercises = get_exercises_for_day(day["id"])
    if not exercises:
        st.info("No exercises in this day.")
        return

    st.markdown("---")
    st.markdown(f"**Logging: {sel_day}**")
    st.markdown(f"*Phase params: {phase['sets']} sets · {phase['reps']} reps · RPE {phase['rpe']}*")

    for ex in exercises:
        with st.expander(f"**{ex['name']}** — {ex['sets']} × {ex['reps']}"):
            with st.form(f"log_{ex['id']}"):
                c1,c2,c3,c4 = st.columns(4)
                sets_done = c1.number_input("Sets Done", min_value=0, max_value=20,
                                             value=int(ex["sets"]) if ex["sets"] and ex["sets"].isdigit() else 3,
                                             key=f"sd_{ex['id']}")
                reps_done = c2.text_input("Reps Done", value=ex["reps"] or "", key=f"rd_{ex['id']}")
                weight = c3.text_input("Weight (lbs/kg)", key=f"wt_{ex['id']}", placeholder="135 lbs")
                rpe = c4.text_input("RPE", key=f"rpe_{ex['id']}", placeholder="7")
                notes = st.text_input("Notes", key=f"n_{ex['id']}", placeholder="How it felt...")
                if st.form_submit_button("✅ Log Set", type="primary"):
                    log_workout(user["id"], ex["id"], sets_done, reps_done, weight, rpe, notes)
                    st.success("Logged!")


def show_progress(user):
    st.markdown("## 📈 My Progress")
    logs = get_athlete_logs(user["id"], limit=100)
    if not logs:
        st.info("No workouts logged yet.")
        return

    import pandas as pd
    df = pd.DataFrame(logs)

    st.markdown(f"**{len(df)} total entries logged**")

    # Summary metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sessions Logged", len(df["logged_at"].str[:10].unique()))
    c2.metric("Exercises Tracked", df["exercise_name"].nunique())
    c3.metric("Most Recent", df["logged_at"].iloc[0][:10])

    st.markdown("---")
    st.markdown("### Recent Logs")
    display = df[["logged_at","exercise_name","sets_done","reps_done","weight","rpe_actual","notes"]].head(30)
    display.columns = ["Date","Exercise","Sets","Reps","Weight","RPE","Notes"]
    display["Date"] = display["Date"].str[:10]
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.markdown("### Exercise History")
    exercises = df["exercise_name"].dropna().unique().tolist()
    if exercises:
        sel_ex = st.selectbox("Select Exercise", exercises)
        ex_df = df[df["exercise_name"] == sel_ex][["logged_at","sets_done","reps_done","weight","rpe_actual","notes"]]
        ex_df.columns = ["Date","Sets","Reps","Weight","RPE","Notes"]
        ex_df["Date"] = ex_df["Date"].str[:10]
        st.dataframe(ex_df, use_container_width=True, hide_index=True)
