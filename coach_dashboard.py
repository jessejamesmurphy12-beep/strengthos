import streamlit as st
import pandas as pd

try:
    from calendar_view import coach_calendar
except ModuleNotFoundError as exc:
    if exc.name != "calendar_view":
        raise
    coach_calendar = None

from database import (
    get_athletes, get_programs, create_program, delete_athlete,
    update_athlete, update_athlete_password,
    get_phases, add_phase, get_days, add_day,
    get_exercises_for_day, add_exercise, delete_exercise,
    delete_day, delete_phase, delete_program, assign_program,
    get_exercise_library, get_coach_stats, create_user,
    get_athlete_logs, get_conn,
)

FOCUS_OPTIONS = ["Strength","Power","Stability","Recovery","Conditioning","Upper Body","Lower Body","Full Body"]
FOCUS_COLORS  = {
    "Strength":"#1B4F72","Power":"#6E2F0A","Stability":"#1D6A39",
    "Recovery":"#4a4a4a","Conditioning":"#7D3C0A",
    "Upper Body":"#2874A6","Lower Body":"#1A5276","Full Body":"#4A235A",
}


# ── helpers ────────────────────────────────────────────────────────────────────
def add_exercise_with_superset(day_id, name, sets, reps, notes, superset_group=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO exercises (day_id,name,sets,reps,notes,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",
        (day_id, name, sets, reps,
         f"[Superset {superset_group}] {notes}".strip() if superset_group else notes, 0),
    )
    conn.commit()
    conn.close()


def _page_header(title, subtitle, kicker="COACH WORKSPACE"):
    st.markdown(f"""
    <div style="margin: 0.25rem 0 1.75rem;">
        <div class="sos-page-kicker">{kicker}</div>
        <div class="sos-page-title">{title}</div>
        <div class="sos-page-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def _divider():
    st.markdown("<div style='height:0.1rem;background:var(--border);margin:1.5rem 0;border-radius:1px;'></div>", unsafe_allow_html=True)


# ── main router ────────────────────────────────────────────────────────────────
def coach_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1.25rem 0.75rem 1rem;">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.25rem;">
                <div style="width:40px;height:40px;border-radius:12px;
                            background:linear-gradient(145deg,#e8cc7a,#a8782a);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.2rem;flex-shrink:0;">⚡</div>
                <div>
                    <div style="font-size:1rem;font-weight:900;letter-spacing:-0.03em;color:#eef2f8;">StrengthOS</div>
                    <div style="font-size:0.6rem;letter-spacing:0.15em;font-weight:800;color:#c9a84c;">COACH WORKSPACE</div>
                </div>
            </div>
            <div style="padding:0.7rem 0.85rem;background:#0e1520;border:1px solid #1e2d42;border-radius:10px;">
                <div style="font-size:0.62rem;color:#5a7090;letter-spacing:0.1em;font-weight:800;text-transform:uppercase;">Signed in as</div>
                <div style="font-size:0.88rem;font-weight:750;color:#eef2f8;margin-top:0.15rem;">{user.get('name','Coach')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = ["Dashboard","Athletes","Programs","Build Workout","Calendar","Exercise Library"]
        target = st.session_state.pop("coach_nav_target", None)
        if target in pages:
            st.session_state["coach_nav"] = target
        default = st.session_state.get("coach_nav","Dashboard")
        if default not in pages:
            default = "Dashboard"

        page = st.radio("Navigation", pages, index=pages.index(default),
                        label_visibility="collapsed", key="coach_nav")

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        if st.button("↪  Sign Out", use_container_width=True, key="coach_sign_out"):
            st.session_state.user = None
            st.rerun()

    if page == "Dashboard":        show_coach_home(user)
    elif page == "Athletes":       show_athletes(user)
    elif page == "Programs":       show_programs(user)
    elif page == "Build Workout":  show_workout_builder(user)
    elif page == "Calendar":
        if coach_calendar is None:
            _page_header("Training Calendar", "Schedule and organize athlete training.")
            st.info("Add calendar_view.py to your repo to enable the calendar.")
        else:
            coach_calendar(user)
    elif page == "Exercise Library": show_library()


# ── Dashboard ──────────────────────────────────────────────────────────────────
def show_coach_home(user):
    first_name = user.get("name","Coach").split()[0]
    _page_header(f"Welcome back, {first_name}", "Your athlete development workspace at a glance.", "STRENGTHOS / OVERVIEW")

    stats    = get_coach_stats(user["id"])
    athletes = get_athletes(user["id"])
    programs = get_programs(user["id"])

    c1, c2, c3 = st.columns(3, gap="medium")
    specs = [
        ("ATHLETES",    stats.get("athletes", len(athletes)), "on your roster"),
        ("PROGRAMS",    stats.get("programs", len(programs)), "training plans built"),
        ("ASSIGNMENTS", stats.get("assigned", 0),            "active athlete plans"),
    ]
    for col, (kicker, value, foot) in zip([c1, c2, c3], specs):
        with col:
            st.markdown(f"""
            <div class="sos-stat">
                <div class="sos-stat-kicker">{kicker}</div>
                <div class="sos-stat-value">{value}</div>
                <div class="sos-stat-foot">{foot}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.3, 1], gap="medium")

    with left:
        st.markdown("""
        <div class="sos-panel">
            <div class="sos-panel-label">Quick actions</div>
            <div class="sos-panel-title">Keep your program moving</div>
            <div class="sos-panel-copy">Jump straight into the most common coaching tasks.</div>
        </div>
        """, unsafe_allow_html=True)
        qa1, qa2, qa3 = st.columns(3, gap="small")
        if qa1.button("＋ Athlete", use_container_width=True, key="qa_add"):
            st.session_state["coach_nav_target"] = "Athletes"; st.rerun()
        if qa2.button("▤ Programs", use_container_width=True, key="qa_prog"):
            st.session_state["coach_nav_target"] = "Programs"; st.rerun()
        if qa3.button("↗ Build", use_container_width=True, key="qa_build"):
            st.session_state["coach_nav_target"] = "Build Workout"; st.rerun()

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sos-panel-label" style="margin-bottom:0.5rem;">Recent roster</div>', unsafe_allow_html=True)

        if not athletes:
            st.info("Your roster is empty. Add your first athlete to get started.")
        else:
            for a in athletes[:8]:
                detail = " · ".join(str(x) for x in [a.get("sport",""), a.get("position",""), a.get("year","")] if x)
                st.markdown(f"""
                <div class="sos-list-row">
                    <div>
                        <div class="sos-list-name">{a.get('name','Athlete')}</div>
                        <div class="sos-list-meta">{detail or a.get('email','')}</div>
                    </div>
                    <span class="sos-pill">ATHLETE</span>
                </div>
                """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="sos-panel">
            <div class="sos-panel-label">Program library</div>
            <div class="sos-panel-title">Your training plans</div>
            <div class="sos-panel-copy">Programs available to assign and develop.</div>
        </div>
        """, unsafe_allow_html=True)

        if not programs:
            st.info("No programs yet. Create one in the Programs tab.")
        else:
            for p in programs[:6]:
                phases = get_phases(p["id"])
                st.markdown(f"""
                <div class="sos-program-card">
                    <div>
                        <div class="sos-program-name">{p['name']}</div>
                        <div class="sos-program-meta">{p.get('goal','Training plan')} · {len(phases)} phase{'s' if len(phases)!=1 else ''}</div>
                    </div>
                    <span class="sos-pill">PLAN</span>
                </div>
                """, unsafe_allow_html=True)


# ── Athletes ───────────────────────────────────────────────────────────────────
def show_athletes(user):
    _page_header("Athletes", "Manage your full roster, assign programs, and review individual progress.", "ROSTER MANAGEMENT")

    athletes = get_athletes(user["id"])
    programs = get_programs(user["id"])

    tab_roster, tab_add, tab_manage = st.tabs(["Roster", "Add Athlete", "Manage"])

    with tab_roster:
        if not athletes:
            st.info("No athletes yet. Use the Add Athlete tab to build your roster.")
        else:
            st.caption(f"{len(athletes)} athlete{'s' if len(athletes)!=1 else ''} on your roster")
            for a in athletes:
                detail = " · ".join(str(x) for x in [a.get("sport",""), a.get("position",""), a.get("year","")] if x)
                with st.expander(f"**{a.get('name','Athlete')}** — {detail or a.get('email','')}"):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.caption("ATHLETE INFO")
                        st.markdown(f"**Email:** {a.get('email','—')}")
                        st.markdown(f"**Sport:** {a.get('sport','—')}")
                        st.markdown(f"**Position:** {a.get('position','—')}")
                        st.markdown(f"**Year:** {a.get('year','—')}")
                    with c2:
                        st.caption("ASSIGN PROGRAM")
                        if programs:
                            prog_map = {p["name"]: p for p in programs}
                            sel = st.selectbox("Program", list(prog_map.keys()), key=f"prog_{a['id']}")
                            if st.button("Assign →", key=f"assign_{a['id']}", type="primary"):
                                assign_program(a["id"], prog_map[sel]["id"])
                                st.success(f"Assigned {sel} to {a.get('name','athlete')}")
                        else:
                            st.info("No programs to assign yet.")

                    _divider()
                    st.caption("TRAINING HISTORY")
                    try:
                        logs = get_athlete_logs(a["id"], limit=50)
                        if logs:
                            df = pd.DataFrame(logs)
                            cols = [c for c in ["logged_at","exercise_name","sets_done","reps_done","weight"] if c in df.columns]
                            st.dataframe(df[cols].rename(columns={
                                "logged_at":"Date","exercise_name":"Exercise",
                                "sets_done":"Set","reps_done":"Reps","weight":"Weight",
                            }), use_container_width=True, hide_index=True)
                        else:
                            st.info("No training data logged yet.")
                    except Exception:
                        st.warning("Couldn't load training history.")

    with tab_add:
        st.markdown("#### Add a new athlete to your roster")
        with st.form("add_athlete_form"):
            c1, c2 = st.columns(2)
            name  = c1.text_input("Full name", placeholder="Alex Rivera")
            email = c2.text_input("Email", placeholder="athlete@example.com").strip().lower()
            pw    = c1.text_input("Temporary password", type="password", placeholder="6+ characters")
            c1b, c2b, c3b = st.columns(3)
            sport    = c1b.text_input("Sport", placeholder="Baseball")
            position = c2b.text_input("Position", placeholder="Pitcher")
            year     = c3b.selectbox("Year", ["Freshman","Sophomore","Junior","Senior","Grad","Pro"])
            submitted = st.form_submit_button("Add Athlete →", type="primary", use_container_width=True)

        if submitted:
            if not all([name, email, pw]):
                st.error("Name, email, and password are required.")
            elif len(pw) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    ok, msg = create_user(name, email, pw, "athlete",
                                         coach_id=user["id"], sport=sport,
                                         position=position, year=year)
                    if ok:
                        st.success(f"✅ {name} added to your roster.")
                        st.rerun()
                    else:
                        st.error(msg)
                except Exception:
                    st.error("Couldn't add the athlete. Please try again.")

    with tab_manage:
        if not athletes:
            st.info("No athletes to manage yet.")
        else:
            sel_name = st.selectbox("Select athlete", [a["name"] for a in athletes], key="manage_sel")
            athlete  = next(a for a in athletes if a["name"] == sel_name)

            st.markdown(f"#### Managing: {athlete['name']}")
            m1, m2 = st.tabs(["Edit Profile", "Reset Password"])

            with m1:
                with st.form("edit_athlete"):
                    c1, c2 = st.columns(2)
                    new_name  = c1.text_input("Name",     value=athlete.get("name",""))
                    new_sport = c2.text_input("Sport",    value=athlete.get("sport",""))
                    new_pos   = c1.text_input("Position", value=athlete.get("position",""))
                    new_year  = c2.text_input("Year",     value=athlete.get("year",""))
                    new_notes = st.text_area("Notes",     value=athlete.get("notes",""), placeholder="Optional coaching notes")
                    if st.form_submit_button("Save Changes", type="primary"):
                        try:
                            update_athlete(athlete["id"], new_name, new_sport, new_pos, new_year, new_notes)
                            st.success("Profile updated.")
                            st.rerun()
                        except Exception:
                            st.error("Couldn't update profile.")

            with m2:
                with st.form("reset_pw"):
                    new_pw  = st.text_input("New password", type="password")
                    new_pw2 = st.text_input("Confirm password", type="password")
                    if st.form_submit_button("Reset Password", type="primary"):
                        if new_pw != new_pw2:
                            st.error("Passwords don't match.")
                        elif len(new_pw) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            try:
                                update_athlete_password(athlete["id"], new_pw)
                                st.success("Password reset successfully.")
                            except Exception:
                                st.error("Couldn't reset password.")

            _divider()
            if st.button(f"🗑 Remove {athlete['name']} from roster", key="del_athlete"):
                try:
                    delete_athlete(athlete["id"])
                    st.success("Athlete removed.")
                    st.rerun()
                except Exception:
                    st.error("Couldn't remove athlete.")


# ── Programs ───────────────────────────────────────────────────────────────────
def show_programs(user):
    _page_header("Programs", "Build and manage your training programs and phases.", "PROGRAM MANAGEMENT")

    programs = get_programs(user["id"])
    tab_list, tab_new = st.tabs(["My Programs", "Create Program"])

    with tab_list:
        if not programs:
            st.info("No programs yet. Use the Create Program tab to get started.")
        else:
            for p in programs:
                phases = get_phases(p["id"])
                with st.expander(f"**{p['name']}** — {len(phases)} phase{'s' if len(phases)!=1 else ''}"):
                    st.caption(f"Goal: {p.get('goal','—')}")

                    if phases:
                        for ph in phases:
                            days      = get_days(ph["id"])
                            week_range = f"Wk {ph.get('week_start','?')}–{ph.get('week_end','?')}"
                            st.markdown(f"""
                            <div class="sos-day-banner">
                                <div>
                                    <div class="sos-day-banner-title">{ph['name']}</div>
                                    <div class="sos-day-banner-meta">{week_range} · {len(days)} day{'s' if len(days)!=1 else ''}</div>
                                </div>
                                <span class="sos-day-banner-pill">{ph.get('sets','—')} sets · {ph.get('reps','—')} reps · RPE {ph.get('rpe','—')}</span>
                            </div>
                            """, unsafe_allow_html=True)

                    _divider()
                    st.caption("ADD PHASE")
                    with st.form(f"add_phase_{p['id']}"):
                        ph_name = st.text_input("Phase name", placeholder="e.g. Accumulation Block")
                        c1, c2 = st.columns(2)
                        ph_week_start = c1.number_input("Start week", min_value=1, max_value=52, value=1, key=f"ws_{p['id']}")
                        ph_week_end   = c2.number_input("End week",   min_value=1, max_value=52, value=4, key=f"we_{p['id']}")
                        c3, c4, c5 = st.columns(3)
                        ph_sets  = c3.text_input("Sets", placeholder="4")
                        ph_reps  = c4.text_input("Reps", placeholder="6–8")
                        ph_rpe   = c5.text_input("RPE",  placeholder="7–8")
                        ph_notes = st.text_input("Phase notes (optional)", placeholder="e.g. Deload week 4")
                        if st.form_submit_button("Add Phase →", type="primary"):
                            if ph_name:
                                add_phase(p["id"], ph_name, ph_week_start, ph_week_end, ph_sets, ph_reps, ph_rpe, ph_notes)
                                st.success(f"Phase '{ph_name}' added.")
                                st.rerun()

                    _divider()
                    if st.button(f"🗑 Delete program", key=f"del_prog_{p['id']}"):
                        delete_program(p["id"])
                        st.rerun()

    with tab_new:
        st.markdown("#### Create a new training program")
        with st.form("new_program"):
            name        = st.text_input("Program name", placeholder="e.g. Off-Season Power Block")
            description = st.text_input("Description (optional)", placeholder="e.g. 12-week off-season block")
            goal        = st.text_input("Training goal", placeholder="e.g. Max strength, velocity development")
            weeks       = st.number_input("Duration (weeks)", min_value=1, max_value=52, value=8)
            if st.form_submit_button("Create Program →", type="primary", use_container_width=True):
                if name:
                    create_program(user["id"], name, description, goal, weeks)
                    st.success(f"Program '{name}' created.")
                    st.rerun()
                else:
                    st.error("Program name is required.")


# ── Workout Builder ────────────────────────────────────────────────────────────
def show_workout_builder(user):
    _page_header("Build Workout", "Add exercises to your program days.", "WORKOUT BUILDER")

    programs = get_programs(user["id"])
    if not programs:
        st.info("Create a program first before building workouts.")
        if st.button("Go to Programs →", type="primary"):
            st.session_state["coach_nav_target"] = "Programs"; st.rerun()
        return

    prog_map = {p["name"]: p for p in programs}
    sel_prog = st.selectbox("Program", list(prog_map.keys()))
    prog     = prog_map[sel_prog]
    phases   = get_phases(prog["id"])

    if not phases:
        st.warning("This program has no phases yet. Add phases in the Programs tab.")
        return

    _divider()
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.markdown("#### Select Day")
        all_days = []
        for ph in phases:
            for d in get_days(ph["id"]):
                all_days.append({
                    "label": f"[{ph['name']}] Day {d['day_number']} — {d['title']}",
                    "day": d, "phase": ph,
                })
        if all_days:
            sel_label   = st.selectbox("Choose a day to edit", [x["label"] for x in all_days], key="sel_day")
            chosen      = next(x for x in all_days if x["label"] == sel_label)
            active_day  = chosen["day"]
            active_phase = chosen["phase"]
        else:
            st.info("No days yet — create one →")
            active_day = active_phase = None

    with col_right:
        st.markdown("#### Create New Day")
        with st.form("new_day_form"):
            phase_map     = {ph["name"]: ph for ph in phases}
            sel_phase_name = st.selectbox("Phase", list(phase_map.keys()))
            day_title     = st.text_input("Day title", placeholder="Lower Body — Posterior Chain")
            c1, c2        = st.columns(2)
            day_number    = c1.number_input("Day #", 1, 7, 1)
            day_focus     = c2.selectbox("Focus", FOCUS_OPTIONS)
            if st.form_submit_button("Create Day →", type="primary"):
                if day_title:
                    ph = phase_map[sel_phase_name]
                    add_day(ph["id"], day_number, day_title, day_focus)
                    st.success("Day created.")
                    st.rerun()

    if not active_day:
        return

    _divider()

    fc = FOCUS_COLORS.get(active_day.get("focus",""), "#1e2d42")
    st.markdown(f"""
    <div class="sos-day-banner" style="border-left-color:{fc};">
        <div>
            <div class="sos-day-banner-title">{active_phase['name']} · Day {active_day['day_number']} — {active_day['title']}</div>
            <div class="sos-day-banner-meta">Focus: {active_day.get('focus','—')}</div>
        </div>
        <span class="sos-day-banner-pill">{active_phase.get('sets','—')} sets · {active_phase.get('reps','—')} reps · RPE {active_phase.get('rpe','—')}</span>
    </div>
    """, unsafe_allow_html=True)

    exercises = get_exercises_for_day(active_day["id"])

    if exercises:
        st.markdown("**Current Exercises**")
        for ex in exercises:
            c1, c2, c3, c4, c5 = st.columns([3, 0.8, 0.8, 2, 0.6])
            c1.markdown(f"<div class='sos-exercise-name'>{ex['name']}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='sos-set-badge'>{ex.get('sets','—')}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='sos-set-badge'>{ex.get('reps','—')}</div>", unsafe_allow_html=True)
            c4.caption(ex.get("notes","") or "")
            if c5.button("🗑", key=f"del_ex_{ex['id']}"):
                delete_exercise(ex["id"]); st.rerun()
        _divider()
    else:
        st.info("No exercises yet — add them below.")

    tab_single, tab_superset = st.tabs(["Add Exercise", "Add Superset"])

    with tab_single:
        with st.form("add_single"):
            library  = get_exercise_library()
            lib_names = ["— type custom name below —"] + [e["name"] for e in library]
            picked   = st.selectbox("Pick from library (optional)", lib_names, key="lib_pick")
            name_val = "" if picked.startswith("—") else picked
            custom   = st.text_input("Exercise name", value=name_val, placeholder="e.g. Trap Bar Deadlift")
            c1, c2, c3 = st.columns(3)
            sets  = c1.text_input("Sets",  placeholder="4")
            reps  = c2.text_input("Reps",  placeholder="6–8")
            notes = c3.text_input("Notes", placeholder="Optional cue")
            if st.form_submit_button("Add Exercise →", type="primary"):
                final_name = custom if custom else picked
                if final_name and not final_name.startswith("—"):
                    add_exercise(active_day["id"], final_name, sets, reps, notes)
                    st.success(f"✅ {final_name} added.")
                    st.rerun()
                else:
                    st.error("Enter or pick an exercise name.")

    with tab_superset:
        st.caption("Add 2–3 exercises as a superset. They'll be grouped together for the athlete.")
        with st.form("add_superset"):
            ss_label = st.text_input("Superset label", value="A", placeholder="A, B, C…")
            for i, num in enumerate(["1","2","3 (optional)"], 1):
                st.caption(f"EXERCISE {num}")
                c1, c2, c3 = st.columns(3)
                locals()[f"n{i}"] = c1.text_input("Name",  key=f"ss_n{i}", placeholder=f"Exercise {i}")
                locals()[f"s{i}"] = c2.text_input("Sets",  key=f"ss_s{i}", placeholder="3")
                locals()[f"r{i}"] = c3.text_input("Reps",  key=f"ss_r{i}", placeholder="10")

            if st.form_submit_button("Add Superset →", type="primary"):
                added = 0
                for i in range(1, 4):
                    n = locals().get(f"n{i}", "")
                    if n and n.strip():
                        add_exercise_with_superset(
                            active_day["id"], n,
                            locals().get(f"s{i}",""),
                            locals().get(f"r{i}",""),
                            "", ss_label,
                        )
                        added += 1
                if added >= 2:
                    st.success(f"✅ Superset {ss_label} added ({added} exercises).")
                    st.rerun()
                else:
                    st.error("Enter at least 2 exercises for a superset.")

    _divider()
    if st.button("🗑 Delete this day", key="del_active_day"):
        delete_day(active_day["id"])
        st.success("Day deleted.")
        st.rerun()


# ── Exercise Library ───────────────────────────────────────────────────────────
def show_library():
    _page_header("Exercise Library", "Search and reference your movement database.", "MOVEMENT DATABASE")

    library = get_exercise_library()
    if not library:
        st.info("Library is empty.")
        return

    c1, c2 = st.columns([2, 1])
    search     = c1.text_input("Search", placeholder="e.g. deadlift, rotational, core…")
    categories = sorted(set(e["category"] for e in library))
    cat_filter = c2.multiselect("Category", categories, default=categories)

    filtered = [
        e for e in library
        if e["category"] in cat_filter
        and (not search or search.lower() in e["name"].lower()
             or search.lower() in (e.get("muscle_group","") or "").lower())
    ]

    st.caption(f"{len(filtered)} exercise{'s' if len(filtered)!=1 else ''}")

    for ex in filtered:
        with st.expander(f"**{ex['name']}** — {ex['category']} · {ex.get('muscle_group','')}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {ex.get('description','—')}")
            c2.markdown(f"**Coaching Cues:** {ex.get('coaching_cues','—')}")
