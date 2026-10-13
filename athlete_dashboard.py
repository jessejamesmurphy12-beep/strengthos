import streamlit as st
import pandas as pd

try:
    from calendar_view import athlete_calendar
except ModuleNotFoundError as exc:
    if exc.name != "calendar_view":
        raise
    athlete_calendar = None

from database import (
    get_assigned_program,
    get_phases,
    get_days,
    get_exercises_for_day,
    get_athlete_logs,
    get_conn,
)


def log_set(athlete_id, exercise_id, set_num, reps, weight, notes):
    """Save one completed set to the existing workout_logs table."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO workout_logs
                (athlete_id, exercise_id, sets_done, reps_done, weight, rpe_actual, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (athlete_id, exercise_id, set_num, reps, weight, "", notes),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def athlete_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding:1rem 0 .75rem;">
                <div style="font-size:1.7rem;">⚡</div>
                <div style="font-size:1.15rem;font-weight:800;letter-spacing:-.02em;">StrengthOS</div>
                <div style="font-size:.78rem;color:#a7b4c7;margin-top:.2rem;">ATHLETE PORTAL</div>
                <div style="height:1px;background:#263852;margin:1rem 0;"></div>
                <div style="font-size:.9rem;">Welcome, {user.get("name", "Athlete")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = st.radio(
            "Navigation",
            ["Today's Workout", "My Week", "My History"],
            label_visibility="collapsed",
            key="athlete_navigation",
        )

        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="athlete_sign_out"):
            st.session_state.user = None
            st.rerun()

    if page == "Today's Workout":
        show_workout(user)
    elif page == "My Week":
        if athlete_calendar is None:
            st.markdown("## My Week")
            st.info(
                "The calendar view is not installed yet. Your workout and history "
                "pages are still available."
            )
        else:
            athlete_calendar(user)
    elif page == "My History":
        show_history(user)


def _parse_set_count(value):
    """Parse prescribed sets such as '3', '3-4', or '3–4' safely."""
    try:
        text = str(value or "3").strip().replace("–", "-").replace("—", "-")
        return max(1, int(text.split("-")[0].strip()))
    except (TypeError, ValueError):
        return 3


def show_workout(user):
    st.markdown("## Today's Workout")
    st.caption("Your assigned training plan, one set at a time.")

    try:
        program = get_assigned_program(user["id"])
    except Exception:
        st.error("We couldn't load your assigned program. Please refresh and try again.")
        return

    if not program:
        st.info("You haven't been assigned a program yet. Ask your coach to assign one.")
        return

    st.markdown(
        f"""
        <div style="padding:1.1rem 1.25rem;border-radius:14px;
                    background:linear-gradient(120deg,#172d4a,#101d30);
                    border:1px solid #30435d;margin:.5rem 0 1.2rem;">
            <div style="font-size:.72rem;letter-spacing:.12em;font-weight:750;color:#d2b15c;">
                YOUR TRAINING PROGRAM
            </div>
            <div style="font-size:1.35rem;font-weight:800;color:#f3f6fb;margin-top:.25rem;">
                {program.get("name", "Assigned Program")}
            </div>
            <div style="color:#a7b4c7;font-size:.9rem;margin-top:.3rem;">
                {program.get("goal", "Training plan")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    phases = get_phases(program["id"])
    if not phases:
        st.info("Your program doesn't have any phases yet.")
        return

    phase_names = [phase["name"] for phase in phases]
    selected_phase_name = st.selectbox(
        "Training phase",
        phase_names,
        key="athlete_selected_phase",
    )
    phase = next(p for p in phases if p["name"] == selected_phase_name)

    days = get_days(phase["id"])
    if not days:
        st.info("There are no workout days in this phase yet.")
        return

    day_labels = [f"Day {day['day_number']} — {day['title']}" for day in days]
    selected_day_label = st.selectbox(
        "Workout day",
        day_labels,
        key=f"athlete_day_{phase['id']}",
    )
    day = days[day_labels.index(selected_day_label)]

    exercises = get_exercises_for_day(day["id"])
    if not exercises:
        st.info("No exercises have been added to this workout yet.")
        return

    st.markdown(
        f"""
        <div style="display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;
                    padding:.8rem 1rem;border-radius:12px;background:#101d30;
                    border:1px solid #263852;margin:1rem 0;">
            <span style="font-weight:750;color:#f3f6fb;">{selected_day_label}</span>
            <span style="color:#a7b4c7;">{phase.get('sets','')} sets</span>
            <span style="color:#a7b4c7;">{phase.get('reps','')} reps</span>
            <span style="color:#d2b15c;">RPE {phase.get('rpe','')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Exercises")
    st.caption("Log each set after you complete it. Your entries are saved to your workout history.")

    for exercise in exercises:
        raw_notes = exercise.get("notes") or ""
        is_superset = raw_notes.startswith("[Superset")
        if is_superset:
            superset_tag = raw_notes.split("]")[0] + "]"
            clean_notes = raw_notes.replace(superset_tag, "", 1).strip()
            title = f"🔗 {superset_tag} · {exercise['name']}"
        else:
            clean_notes = raw_notes
            title = exercise["name"]

        with st.container(border=True):
            st.markdown(f"#### {title}")
            meta_left, meta_right = st.columns([1, 2])
            meta_left.caption(
                f"{exercise.get('sets', '—')} sets × {exercise.get('reps', '—')} reps"
            )
            if clean_notes:
                meta_right.caption(clean_notes)

            number_of_sets = _parse_set_count(exercise.get("sets", "3"))
            header = st.columns([0.55, 1.1, 1.2, 2.0, 1.0])
            for column, heading in zip(header, ["Set", "Reps", "Weight", "Notes", "Save"]):
                column.caption(heading)

            for set_number in range(1, number_of_sets + 1):
                with st.form(
                    key=f"athlete_set_form_{exercise['id']}_{set_number}",
                    clear_on_submit=False,
                    border=False,
                ):
                    c_set, c_reps, c_weight, c_notes, c_save = st.columns(
                        [0.55, 1.1, 1.2, 2.0, 1.0]
                    )
                    c_set.markdown(f"**{set_number}**")
                    reps = c_reps.text_input(
                        "Reps",
                        placeholder=str(exercise.get("reps", "")),
                        key=f"athlete_reps_{exercise['id']}_{set_number}",
                        label_visibility="collapsed",
                    )
                    weight = c_weight.text_input(
                        "Weight",
                        placeholder="lbs / kg",
                        key=f"athlete_weight_{exercise['id']}_{set_number}",
                        label_visibility="collapsed",
                    )
                    notes = c_notes.text_input(
                        "Notes",
                        placeholder="Optional",
                        key=f"athlete_notes_{exercise['id']}_{set_number}",
                        label_visibility="collapsed",
                    )
                    save = c_save.form_submit_button(
                        "Log set",
                        use_container_width=True,
                        type="primary",
                    )

                if save:
                    try:
                        log_set(user["id"], exercise["id"], set_number, reps, weight, notes)
                        st.success(f"Set {set_number} saved.", icon="✅")
                    except Exception:
                        st.error("Couldn't save this set. Please try again.")

        st.markdown("")


def show_history(user):
    st.markdown("## My Training History")
    st.caption("Review your logged sets and recent training progress.")

    try:
        logs = get_athlete_logs(user["id"], limit=200)
    except Exception:
        st.error("We couldn't load your training history. Please refresh and try again.")
        return

    if not logs:
        st.info("No workouts logged yet. Your completed sets will appear here.")
        return

    df = pd.DataFrame(logs)

    col1, col2, col3 = st.columns(3)
    if "logged_at" in df.columns:
        dates = df["logged_at"].astype(str).str[:10]
        col1.metric("Training Days", dates.nunique())
        col3.metric("Last Logged", dates.iloc[0] if not dates.empty else "—")
    else:
        col1.metric("Training Days", "—")
        col3.metric("Last Logged", "—")

    col2.metric(
        "Exercises Tracked",
        int(df["exercise_name"].nunique()) if "exercise_name" in df.columns else 0,
    )

    st.divider()

    if "exercise_name" not in df.columns:
        st.warning("Your workout log data doesn't include exercise names.")
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    exercise_options = ["All exercises"] + sorted(
        df["exercise_name"].dropna().astype(str).unique().tolist()
    )
    selected_exercise = st.selectbox(
        "Filter exercises",
        exercise_options,
        key="athlete_history_filter",
    )
    filtered = df if selected_exercise == "All exercises" else df[
        df["exercise_name"] == selected_exercise
    ]

    wanted_columns = [
        "logged_at", "exercise_name", "sets_done", "reps_done", "weight", "notes"
    ]
    available_columns = [column for column in wanted_columns if column in filtered.columns]
    display = filtered[available_columns].copy()
    display = display.rename(
        columns={
            "logged_at": "Date",
            "exercise_name": "Exercise",
            "sets_done": "Set #",
            "reps_done": "Reps",
            "weight": "Weight",
            "notes": "Notes",
        }
    )
    if "Date" in display.columns:
        display["Date"] = display["Date"].astype(str).str[:10]

    st.dataframe(display, use_container_width=True, hide_index=True)
