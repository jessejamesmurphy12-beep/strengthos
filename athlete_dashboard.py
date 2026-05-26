import streamlit as st
import pandas as pd
from database import (get_assigned_program, get_phases, get_days,
                      get_exercises_for_day, get_athlete_logs, get_conn)

# ── Save individual sets ───────────────────────────────────────────────────────
def log_set(athlete_id, exercise_id, set_num, reps, weight, notes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO workout_logs (athlete_id, exercise_id, sets_done, reps_done, weight, rpe_actual, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (athlete_id, exercise_id, set_num, reps, weight, "", notes))
    conn.commit()
    conn.close()

# ── Main router ────────────────────────────────────────────────────────────────
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


# ── Workout page ───────────────────────────────────────────────────────────────
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

    phase_names = [p["name"] for p in phases]
    sel_phase_name = st.selectbox("Phase", phase_names)
    phase = next(p for p in phases if p["name"] == sel_phase_name)

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
                border-radius:8px; font-weight:700; margin-bottom:1.25rem;'>
        {sel_day_name} &nbsp;·&nbsp; {phase['sets']} sets · {phase['reps']} reps · RPE {phase['rpe']}
    </div>
    """, unsafe_allow_html=True)

    # ── Per-exercise set logger ────────────────────────────────────────────────
    for ex in exercises:
        raw_notes = ex.get("notes") or ""
        is_superset = raw_notes.startswith("[Superset")
        if is_superset:
            ss_tag      = raw_notes.split("]")[0] + "]"
            clean_notes = raw_notes.replace(ss_tag, "").strip()
            label       = f"🔗 {ss_tag} **{ex['name']}**"
            sub_label   = f"{ex['sets']} sets × {ex['reps']}" + (f" · *{clean_notes}*" if clean_notes else "")
        else:
            label     = f"**{ex['name']}**"
            sub_label = f"{ex['sets']} sets × {ex['reps']}" + (f" · *{raw_notes}*" if raw_notes else "")

        st.markdown(f"{label} — {sub_label}")

        # Figure out how many sets prescribed
        try:
            # handle ranges like "3–4" → use first number
            num_sets = int(str(ex.get("sets","3")).replace("–","-").split("-")[0])
        except:
            num_sets = 3

        # Column headers
        hc1, hc2, hc3, hc4, hc5 = st.columns([1, 2, 2, 3, 2])
        hc1.markdown("<small>**Set**</small>", unsafe_allow_html=True)
        hc2.markdown("<small>**Reps**</small>", unsafe_allow_html=True)
        hc3.markdown("<small>**Weight**</small>", unsafe_allow_html=True)
        hc4.markdown("<small>**Notes**</small>", unsafe_allow_html=True)
        hc5.markdown("<small></small>", unsafe_allow_html=True)

        for s in range(1, num_sets + 1):
            with st.form(key=f"set_{ex['id']}_{s}"):
                c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 3, 2])
                c1.markdown(f"**{s}**")
                reps   = c2.text_input("", placeholder=ex.get("reps",""), key=f"r_{ex['id']}_{s}", label_visibility="collapsed")
                weight = c3.text_input("", placeholder="lbs / kg",        key=f"w_{ex['id']}_{s}", label_visibility="collapsed")
                notes  = c4.text_input("", placeholder="notes...",         key=f"n_{ex['id']}_{s}", label_visibility="collapsed")
                save   = c5.form_submit_button("✅ Log", use_container_width=True)
                if save:
                    log_set(user["id"], ex["id"], s, reps, weight, notes)
                    st.success(f"Set {s} logged!", icon="✅")

        st.markdown("---")


# ── History page ───────────────────────────────────────────────────────────────
def show_history(user):
    st.markdown("## 📋 My History")
    logs = get_athlete_logs(user["id"], limit=200)
    if not logs:
        st.info("No workouts logged yet.")
        return

    df = pd.DataFrame(logs)

    c1, c2, c3 = st.columns(3)
    c1.metric("Sessions Logged",   len(df["logged_at"].str[:10].unique()))
    c2.metric("Exercises Tracked", df["exercise_name"].nunique())
    c3.metric("Last Logged",       df["logged_at"].iloc[0][:10])

    st.markdown("---")

    exercises = ["All"] + sorted(df["exercise_name"].dropna().unique().tolist())
    sel_ex    = st.selectbox("Filter by exercise", exercises)
    filtered  = df if sel_ex == "All" else df[df["exercise_name"] == sel_ex]

    display = filtered[["logged_at","exercise_name","sets_done","reps_done","weight","notes"]].copy()
    display.columns = ["Date","Exercise","Set #","Reps","Weight","Notes"]
    display["Date"] = display["Date"].str[:10]

    st.dataframe(display, use_container_width=True, hide_index=True)
