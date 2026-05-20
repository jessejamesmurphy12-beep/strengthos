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

        page = st.radio("Navigation", ["Today's Workout", "My History"],
                        label_visibility="collapsed")
        st.markdown("<br>" * 8, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if page == "Today's Workout":
        show_workout(user)
    elif page == "My History":
        show_history(user)


def show_workout(user):
    st.markdown("## 🏋️ Today's Workout")

    prog = get_assigned_program(user["id"])
    if not prog:
        st.info("You haven't been assigned a program yet. Ask your coach!")
        return

    phases = get_phases(prog["id"])
    if not phases:
        st.info("Your program has no phases yet.")
        return

    # Pick phase
    phase_names = [p["name"] for p in phases]
    sel_phase_name = st.selectbox("Phase", phase_names)
    phase = next(p for p in phases if p["name"] == sel_phase_name)

    # Pick day
    days = get_days(phase["id"])
    if not days:
        st.info("No days in this phase yet.")
        return

    day_names = [f"Day {d['day_number']} — {d['title']}" for d in days]
    sel_day_name = st.selectbox("Day", day_names)
    day = days[day_names.index(sel_day_name)]

    exercises = get_exercises_for_day(day["id"])
    if not exercises:
        st.info("No exercises in this day yet.")
        return

    st.markdown("---")
    st.markdown(f"""
    <div style='background:#1B4F72; color:white; padding:0.6rem 1rem;
                border-radius:8px; font-weight:700; margin-bottom:1rem;'>
        {sel_day_name} &nbsp;·&nbsp; {phase['sets']} sets · {phase['reps']} reps · RPE {phase['rpe']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Log Your Weights")
    st.markdown("Fill in the weight you used for each exercise, then hit **Save Workout**.")

    # One form for the whole day
    with st.form("log_day"):
        weights = {}
        for ex in exercises:
            raw_notes = ex.get("notes") or ""
            is_superset = raw_notes.startswith("[Superset")
            if is_superset:
                ss_tag = raw_notes.split("]")[0] + "]"
                clean_notes = raw_notes.replace(ss_tag, "").strip()
                st.markdown(f"🔗 **{ss_tag} {ex['name']}** — {ex['sets']} sets × {ex['reps']}" +
                            (f" · *{clean_notes}*" if clean_notes else ""))
            else:
                st.markdown(f"**{ex['name']}** — {ex['sets']} sets × {ex['reps']}" +
                            (f" · *{raw_notes}*" if raw_notes else ""))
            c1, c2 = st.columns([2, 3])
            weight = c1.text_input("Weight used", key=f"w_{ex['id']}", placeholder="e.g. 135 lbs")
            notes  = c2.text_input("Notes (optional)", key=f"n_{ex['id']}", placeholder="How it felt...")
            weights[ex["id"]] = {"weight": weight, "notes": notes,
                                  "sets": ex["sets"], "reps": ex["reps"]}
            st.markdown("---")

        submitted = st.form_submit_button("💾 Save Workout", type="primary", use_container_width=True)
        if submitted:
            for ex_id, data in weights.items():
                log_workout(user["id"], ex_id,
                            data["sets"], data["reps"],
                            data["weight"], "", data["notes"])
            st.success("✅ Workout saved!")
            st.balloons()


def show_history(user):
    st.markdown("## 📋 My History")
    logs = get_athlete_logs(user["id"], limit=200)
    if not logs:
        st.info("No workouts logged yet.")
        return

    import pandas as pd
    df = pd.DataFrame(logs)

    # Summary
    c1, c2, c3 = st.columns(3)
    c1.metric("Sessions Logged", len(df["logged_at"].str[:10].unique()))
    c2.metric("Exercises Tracked", df["exercise_name"].nunique())
    c3.metric("Last Logged", df["logged_at"].iloc[0][:10])

    st.markdown("---")

    # Filter by exercise
    exercises = ["All"] + sorted(df["exercise_name"].dropna().unique().tolist())
    sel_ex = st.selectbox("Filter by exercise", exercises)

    filtered = df if sel_ex == "All" else df[df["exercise_name"] == sel_ex]

    display = filtered[["logged_at", "exercise_name", "sets_done", "reps_done", "weight", "notes"]].copy()
    display.columns = ["Date", "Exercise", "Sets", "Reps", "Weight", "Notes"]
    display["Date"] = display["Date"].str[:10]

    st.dataframe(display, use_container_width=True, hide_index=True)
