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


def _parse_set_count(value):
    try:
        text = str(value or "3").strip().replace("–","-").replace("—","-")
        return max(1, int(text.split("-")[0].strip()))
    except (TypeError, ValueError):
        return 3


def _divider():
    st.markdown("<div style='height:0.1rem;background:var(--border);margin:1.25rem 0;border-radius:1px;'></div>", unsafe_allow_html=True)


def athlete_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1.25rem 0.75rem 1rem;">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.25rem;">
                <div style="width:40px;height:40px;border-radius:12px;
                            background:linear-gradient(145deg,#e8cc7a,#a8782a);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.2rem;flex-shrink:0;">⚡</div>
                <div>
                    <div style="font-size:1rem;font-weight:900;letter-spacing:-0.03em;color:#eef2f8;">StrengthOS</div>
                    <div style="font-size:0.6rem;letter-spacing:0.15em;font-weight:800;color:#c9a84c;">ATHLETE PORTAL</div>
                </div>
            </div>
            <div style="padding:0.7rem 0.85rem;background:#0e1520;border:1px solid #1e2d42;border-radius:10px;">
                <div style="font-size:0.62rem;color:#5a7090;letter-spacing:0.1em;font-weight:800;text-transform:uppercase;">Signed in as</div>
                <div style="font-size:0.88rem;font-weight:750;color:#eef2f8;margin-top:0.15rem;">{user.get('name','Athlete')}</div>
                <div style="font-size:0.72rem;color:#5a7090;margin-top:0.1rem;">{user.get('sport','')} {('· ' + user.get('position','')) if user.get('position') else ''}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["Today's Workout", "My Week", "My History"],
            label_visibility="collapsed",
            key="athlete_nav",
        )
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        if st.button("↪  Sign Out", use_container_width=True, key="athlete_sign_out"):
            st.session_state.user = None
            st.rerun()

    if page == "Today's Workout":
        show_workout(user)
    elif page == "My Week":
        if athlete_calendar is None:
            st.markdown("""
            <div style="margin:0.25rem 0 1.75rem;">
                <div class="sos-page-kicker">WEEKLY VIEW</div>
                <div class="sos-page-title">My Week</div>
            </div>
            """, unsafe_allow_html=True)
            st.info("Calendar view coming soon. Your workout and history pages are available now.")
        else:
            athlete_calendar(user)
    elif page == "My History":
        show_history(user)


def show_workout(user):
    st.markdown("""
    <div style="margin:0.25rem 0 1.75rem;">
        <div class="sos-page-kicker">TRAINING SESSION</div>
        <div class="sos-page-title">Today's Workout</div>
        <div class="sos-page-subtitle">Your assigned training plan, one set at a time.</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        program = get_assigned_program(user["id"])
    except Exception:
        st.error("Couldn't load your program. Please refresh and try again.")
        return

    if not program:
        st.markdown("""
        <div style="background:#0e1520;border:1px solid #1e2d42;border-radius:14px;
                    padding:2rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.75rem;">🏋️</div>
            <div style="font-size:1rem;font-weight:700;color:#eef2f8;margin-bottom:0.35rem;">No program assigned yet</div>
            <div style="font-size:0.85rem;color:#8fa3bc;">Ask your coach to assign a training program to get started.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Program banner
    st.markdown(f"""
    <div style="padding:1.1rem 1.35rem;border-radius:14px;
                background:#0e1520;border:1px solid #1e2d42;
                border-top:2px solid #c9a84c;margin-bottom:1.25rem;">
        <div style="font-size:0.62rem;letter-spacing:0.14em;font-weight:800;color:#c9a84c;text-transform:uppercase;margin-bottom:0.3rem;">
            YOUR PROGRAM
        </div>
        <div style="font-size:1.3rem;font-weight:900;color:#eef2f8;letter-spacing:-0.03em;">
            {program.get('name','Training Program')}
        </div>
        <div style="font-size:0.85rem;color:#8fa3bc;margin-top:0.25rem;">
            {program.get('goal','Training plan')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    phases = get_phases(program["id"])
    if not phases:
        st.info("Your program doesn't have any phases yet.")
        return

    c1, c2 = st.columns(2)
    sel_phase_name = c1.selectbox("Phase", [p["name"] for p in phases], key="athlete_phase")
    phase = next(p for p in phases if p["name"] == sel_phase_name)

    days = get_days(phase["id"])
    if not days:
        st.info("No workout days in this phase yet.")
        return

    day_labels = [f"Day {d['day_number']} — {d['title']}" for d in days]
    sel_day_label = c2.selectbox("Day", day_labels, key=f"athlete_day_{phase['id']}")
    day = days[day_labels.index(sel_day_label)]

    exercises = get_exercises_for_day(day["id"])
    if not exercises:
        st.info("No exercises in this workout yet.")
        return

    # Day banner
    st.markdown(f"""
    <div class="sos-day-banner">
        <div>
            <div class="sos-day-banner-title">{sel_day_label}</div>
            <div class="sos-day-banner-meta">{phase['name']}</div>
        </div>
        <span class="sos-day-banner-pill">{phase.get('sets','')} sets · {phase.get('reps','')} reps · RPE {phase.get('rpe','')}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Exercises")
    st.caption("Log each set after you complete it. Entries are saved to your history.")

    for exercise in exercises:
        raw_notes = exercise.get("notes") or ""
        is_superset = raw_notes.startswith("[Superset")
        if is_superset:
            tag = raw_notes.split("]")[0] + "]"
            clean_notes = raw_notes.replace(tag,"",1).strip()
            title = f"🔗 {tag} · {exercise['name']}"
        else:
            clean_notes = raw_notes
            title = exercise["name"]

        with st.container(border=True):
            hc1, hc2 = st.columns([2,1])
            hc1.markdown(f"**{title}**")
            hc2.caption(f"{exercise.get('sets','—')} sets × {exercise.get('reps','—')} reps")
            if clean_notes:
                st.caption(f"📌 {clean_notes}")

            # Column headers
            h1, h2, h3, h4, h5 = st.columns([0.5, 1, 1.1, 2, 1])
            h1.caption("SET")
            h2.caption("REPS")
            h3.caption("WEIGHT")
            h4.caption("NOTES")
            h5.caption("SAVE")

            num_sets = _parse_set_count(exercise.get("sets","3"))
            for set_num in range(1, num_sets + 1):
                with st.form(key=f"set_{exercise['id']}_{set_num}", clear_on_submit=False, border=False):
                    s1, s2, s3, s4, s5 = st.columns([0.5, 1, 1.1, 2, 1])
                    s1.markdown(f"<div style='text-align:center;font-weight:800;color:#c9a84c;padding-top:0.6rem;'>{set_num}</div>", unsafe_allow_html=True)
                    reps   = s2.text_input("Reps",   placeholder=str(exercise.get("reps","")), key=f"r_{exercise['id']}_{set_num}", label_visibility="collapsed")
                    weight = s3.text_input("Weight", placeholder="lbs / kg",                  key=f"w_{exercise['id']}_{set_num}", label_visibility="collapsed")
                    notes  = s4.text_input("Notes",  placeholder="Optional",                  key=f"n_{exercise['id']}_{set_num}", label_visibility="collapsed")
                    save   = s5.form_submit_button("Log", use_container_width=True, type="primary")

                if save:
                    try:
                        log_set(user["id"], exercise["id"], set_num, reps, weight, notes)
                        st.success(f"Set {set_num} saved ✅", icon=None)
                    except Exception:
                        st.error("Couldn't save this set. Please try again.")

        st.markdown("")


def show_history(user):
    st.markdown("""
    <div style="margin:0.25rem 0 1.75rem;">
        <div class="sos-page-kicker">ATHLETE HISTORY</div>
        <div class="sos-page-title">My Training History</div>
        <div class="sos-page-subtitle">Review your logged sets and progress over time.</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        logs = get_athlete_logs(user["id"], limit=200)
    except Exception:
        st.error("Couldn't load your training history. Please refresh.")
        return

    if not logs:
        st.markdown("""
        <div style="background:#0e1520;border:1px solid #1e2d42;border-radius:14px;
                    padding:2rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.75rem;">📋</div>
            <div style="font-size:1rem;font-weight:700;color:#eef2f8;margin-bottom:0.35rem;">No workouts logged yet</div>
            <div style="font-size:0.85rem;color:#8fa3bc;">Complete sets in Today's Workout and they'll appear here.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(logs)

    # Summary stats
    c1, c2, c3 = st.columns(3)
    if "logged_at" in df.columns:
        dates = df["logged_at"].astype(str).str[:10]
        c1.metric("Training Days", dates.nunique())
        c3.metric("Last Session", dates.iloc[0] if not dates.empty else "—")
    else:
        c1.metric("Training Days", "—")
        c3.metric("Last Session", "—")
    c2.metric("Exercises Tracked", int(df["exercise_name"].nunique()) if "exercise_name" in df.columns else 0)

    _divider()

    if "exercise_name" not in df.columns:
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    exercise_options = ["All exercises"] + sorted(df["exercise_name"].dropna().astype(str).unique().tolist())
    selected = st.selectbox("Filter by exercise", exercise_options, key="history_filter")
    filtered = df if selected == "All exercises" else df[df["exercise_name"] == selected]

    wanted = ["logged_at","exercise_name","sets_done","reps_done","weight","notes"]
    available = [c for c in wanted if c in filtered.columns]
    display = filtered[available].copy().rename(columns={
        "logged_at":"Date","exercise_name":"Exercise",
        "sets_done":"Set #","reps_done":"Reps",
        "weight":"Weight","notes":"Notes",
    })
    if "Date" in display.columns:
        display["Date"] = display["Date"].astype(str).str[:10]

    st.dataframe(display, use_container_width=True, hide_index=True)
