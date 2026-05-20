import streamlit as st
from database import (get_athletes, get_programs, create_program, get_program,
                      get_phases, add_phase, get_days, add_day,
                      get_exercises_for_day, add_exercise, delete_exercise,
                      delete_day, delete_phase, delete_program, assign_program,
                      get_exercise_library, get_coach_stats, create_user, get_athlete_logs)

FOCUS_OPTIONS = ["Strength", "Power", "Stability", "Recovery", "Conditioning", "Upper Body", "Lower Body", "Full Body"]
FOCUS_COLORS  = {"Strength":"#1B4F72","Power":"#6E2F0A","Stability":"#1D6A39",
                 "Recovery":"#555555","Conditioning":"#7D3C0A","Upper Body":"#2874A6",
                 "Lower Body":"#1A5276","Full Body":"#4A235A"}

def coach_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"""
        <div style='padding:1rem 0 0.5rem;'>
            <div style='font-size:1.5rem;'>⚡</div>
            <div style='font-weight:700; font-size:1rem;'>StrengthOS</div>
            <div style='font-size:0.8rem; color:#94a3b8; margin-top:2px;'>Coach Portal</div>
        </div>
        <hr style='border-color:#1e293b; margin:0.5rem 0;'>
        <div style='font-size:0.85rem; padding:0.5rem 0;'>👋 {user["name"]}</div>
        """, unsafe_allow_html=True)

        page = st.radio("Navigation", ["Dashboard", "Athletes", "Programs", "Exercise Library"],
                        label_visibility="collapsed")
        st.markdown("<br>" * 8, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if page == "Dashboard":
        show_coach_home(user)
    elif page == "Athletes":
        show_athletes(user)
    elif page == "Programs":
        show_programs(user)
    elif page == "Exercise Library":
        show_library()


# ── Home ───────────────────────────────────────────────────────────────────────
def show_coach_home(user):
    st.markdown(f"## 👋 Welcome back, {user['name'].split()[0]}")
    stats = get_coach_stats(user["id"])

    c1, c2, c3 = st.columns(3)
    for col, label, val, icon in [
        (c1, "Total Athletes", stats["athletes"], "🏃"),
        (c2, "Programs Built", stats["programs"], "📋"),
        (c3, "Active Assignments", stats["assigned"], "✅"),
    ]:
        col.markdown(f"""
        <div class='metric-card'>
            <div style='font-size:1.8rem;'>{icon}</div>
            <div style='font-size:2rem; font-weight:800; margin:4px 0;'>{val}</div>
            <div style='font-size:0.85rem; color:#94a3b8;'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='section-header'>Recent Athletes</div>", unsafe_allow_html=True)
        athletes = get_athletes(user["id"])[:8]
        if athletes:
            for a in athletes:
                with st.container():
                    st.markdown(f"""
                    <div style='padding:0.6rem 0.8rem; background:#f8fafc; border-radius:8px;
                                margin-bottom:6px; border-left:3px solid #3b82f6;'>
                        <b>{a['name']}</b>
                        <span style='color:#64748b; font-size:0.8rem; margin-left:8px;'>
                            {a.get('sport','')} · {a.get('position','')} · {a.get('year','')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No athletes yet. Add them in the Athletes tab.")

    with col_b:
        st.markdown("<div class='section-header'>Recent Programs</div>", unsafe_allow_html=True)
        programs = get_programs(user["id"])[:6]
        if programs:
            for p in programs:
                st.markdown(f"""
                <div style='padding:0.6rem 0.8rem; background:#f8fafc; border-radius:8px;
                            margin-bottom:6px; border-left:3px solid #10b981;'>
                    <b>{p['name']}</b>
                    <span style='color:#64748b; font-size:0.8rem; margin-left:8px;'>{p['weeks']} weeks · {p['goal']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No programs yet. Build one in the Programs tab.")


# ── Athletes ───────────────────────────────────────────────────────────────────
def show_athletes(user):
    st.markdown("## 🏃 Athletes")
    tab_roster, tab_add, tab_assign, tab_logs = st.tabs(["Roster", "Add Athlete", "Assign Program", "View Logs"])

    with tab_roster:
        athletes = get_athletes(user["id"])
        if not athletes:
            st.info("No athletes yet.")
        else:
            st.markdown(f"**{len(athletes)} athletes**")
            for a in athletes:
                with st.expander(f"**{a['name']}** — {a.get('sport','')} {a.get('position','')} ({a.get('year','')})"):
                    c1, c2 = st.columns(2)
                    c1.write(f"📧 {a['email']}")
                    c2.write(f"🏅 {a.get('sport','')} · {a.get('position','')}")
                    if a.get("notes"):
                        st.write(f"📝 {a['notes']}")

    with tab_add:
        st.markdown("### Add New Athlete")
        with st.form("add_athlete_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            pw = st.text_input("Temporary Password", type="password", value="athlete123")
            c1, c2, c3 = st.columns(3)
            sport = c1.text_input("Sport")
            position = c2.text_input("Position")
            year = c3.selectbox("Year", ["Freshman","Sophomore","Junior","Senior","Grad"])
            notes = st.text_area("Notes (optional)", height=80)
            submitted = st.form_submit_button("Add Athlete", type="primary")
            if submitted:
                if not name or not email:
                    st.error("Name and email required.")
                else:
                    ok, msg = create_user(name, email, pw, "athlete",
                                          coach_id=user["id"], sport=sport,
                                          position=position, year=year)
                    if ok:
                        st.success(f"✅ {name} added! They can log in with {email} / {pw}")
                    else:
                        st.error(msg)

    with tab_assign:
        st.markdown("### Assign Program to Athlete")
        athletes = get_athletes(user["id"])
        programs = get_programs(user["id"])
        if not athletes:
            st.info("Add athletes first.")
        elif not programs:
            st.info("Build a program first.")
        else:
            athlete_map = {a["name"]: a["id"] for a in athletes}
            program_map = {p["name"]: p["id"] for p in programs}
            sel_athlete = st.selectbox("Select Athlete", list(athlete_map.keys()))
            sel_program = st.selectbox("Select Program", list(program_map.keys()))
            if st.button("Assign Program", type="primary"):
                assign_program(athlete_map[sel_athlete], program_map[sel_program])
                st.success(f"✅ {sel_program} assigned to {sel_athlete}!")

    with tab_logs:
        st.markdown("### Athlete Workout Logs")
        athletes = get_athletes(user["id"])
        if not athletes:
            st.info("No athletes yet.")
        else:
            athlete_map = {a["name"]: a["id"] for a in athletes}
            sel = st.selectbox("Select Athlete", list(athlete_map.keys()), key="log_athlete")
            logs = get_athlete_logs(athlete_map[sel])
            if not logs:
                st.info("No logs yet for this athlete.")
            else:
                import pandas as pd
                df = pd.DataFrame(logs)[["logged_at","exercise_name","sets_done","reps_done","weight","rpe_actual","notes"]]
                df.columns = ["Date","Exercise","Sets","Reps","Weight","RPE","Notes"]
                st.dataframe(df, use_container_width=True)


# ── Programs ───────────────────────────────────────────────────────────────────
def show_programs(user):
    st.markdown("## 📋 Programs")
    tab_list, tab_new = st.tabs(["My Programs", "Create New Program"])

    with tab_new:
        st.markdown("### New Program")
        with st.form("new_program_form"):
            name = st.text_input("Program Name", placeholder="e.g. Summer Lifting Plan 2025")
            description = st.text_area("Description", height=80)
            c1, c2 = st.columns(2)
            goal = c1.selectbox("Primary Goal", ["Strength & Injury Prevention", "Velocity Development",
                                                  "Hypertrophy", "Power", "Conditioning", "Balanced"])
            weeks = c2.number_input("Total Weeks", min_value=1, max_value=52, value=12)
            submitted = st.form_submit_button("Create Program", type="primary")
            if submitted:
                if not name:
                    st.error("Program name required.")
                else:
                    pid = create_program(user["id"], name, description, goal, weeks)
                    st.success(f"✅ Program created!")
                    st.session_state["open_program"] = pid
                    st.rerun()

    with tab_list:
        programs = get_programs(user["id"])
        if not programs:
            st.info("No programs yet. Create one above.")
            return

        for prog in programs:
            with st.expander(f"**{prog['name']}** — {prog['weeks']} weeks · {prog['goal']}"):
                st.markdown(f"*{prog.get('description','') or 'No description'}*")
                if st.button(f"🗑 Delete Program", key=f"del_prog_{prog['id']}", type="secondary"):
                    delete_program(prog["id"])
                    st.success("Program deleted.")
                    st.rerun()
                st.markdown("---")
                show_program_builder(prog)


def show_program_builder(prog):
    pid = prog["id"]
    st.markdown("### Phases")

    phases = get_phases(pid)
    for phase in phases:
        ph_col = "#1B4F72"
        st.markdown(f"""
        <div style='background:{ph_col}; color:white; padding:0.5rem 1rem;
                    border-radius:8px 8px 0 0; font-weight:700; margin-top:1rem;'>
            {phase['name']}  &nbsp;·&nbsp; Weeks {phase['week_start']}–{phase['week_end']}
            &nbsp;·&nbsp; {phase['sets']} sets · {phase['reps']} reps · RPE {phase['rpe']}
        </div>
        """, unsafe_allow_html=True)

        days = get_days(phase["id"])
        for day in days:
            focus_color = FOCUS_COLORS.get(day["focus"], "#2874A6")
            st.markdown(f"""
            <div style='background:#1e293b; color:white; padding:0.4rem 1rem;
                        font-weight:600; font-size:0.9rem;'>
                Day {day['day_number']} — {day['title']}
                <span style='background:{focus_color}; color:white; font-size:0.75rem;
                             padding:2px 8px; border-radius:10px; margin-left:8px;'>{day['focus']}</span>
            </div>
            """, unsafe_allow_html=True)

            exercises = get_exercises_for_day(day["id"])
            if exercises:
                import pandas as pd
                df = pd.DataFrame(exercises)[["name","sets","reps","notes"]]
                df.columns = ["Exercise","Sets","Reps","Notes"]
                st.dataframe(df, use_container_width=True, hide_index=True)

            with st.form(f"add_ex_{day['id']}"):
                c1,c2,c3,c4 = st.columns([3,1,1,2])
                ex_name = c1.text_input("Exercise", key=f"exn_{day['id']}", placeholder="Exercise name")
                ex_sets = c2.text_input("Sets", key=f"exs_{day['id']}", placeholder="4")
                ex_reps = c3.text_input("Reps", key=f"exr_{day['id']}", placeholder="6–8")
                ex_notes = c4.text_input("Notes", key=f"exno_{day['id']}", placeholder="Optional")
                if st.form_submit_button("➕ Add Exercise"):
                    if ex_name:
                        add_exercise(day["id"], ex_name, ex_sets, ex_reps, ex_notes)
                        st.rerun()

            if st.button(f"🗑 Delete Day {day['day_number']}", key=f"del_day_{day['id']}"):
                delete_day(day["id"])
                st.rerun()

        # Add day form
        with st.form(f"add_day_{phase['id']}"):
            st.markdown("**Add Day**")
            c1,c2,c3 = st.columns(3)
            day_num = c1.number_input("Day #", min_value=1, max_value=7, value=len(days)+1, key=f"dnum_{phase['id']}")
            day_title = c2.text_input("Title", key=f"dtitle_{phase['id']}", placeholder="Lower Body — Posterior Chain")
            day_focus = c3.selectbox("Focus", FOCUS_OPTIONS, key=f"dfocus_{phase['id']}")
            if st.form_submit_button("Add Day"):
                if day_title:
                    add_day(phase["id"], day_num, day_title, day_focus)
                    st.rerun()

        if st.button(f"🗑 Delete Phase: {phase['name']}", key=f"del_phase_{phase['id']}"):
            delete_phase(phase["id"])
            st.rerun()

    # Add phase form
    st.markdown("---")
    st.markdown("#### ➕ Add Phase")
    with st.form(f"add_phase_{pid}"):
        ph_name = st.text_input("Phase Name", placeholder="Phase 1 — Accumulation")
        c1,c2,c3,c4,c5 = st.columns(5)
        ws = c1.number_input("Week Start", min_value=1, value=1, key=f"ws_{pid}")
        we = c2.number_input("Week End", min_value=1, value=4, key=f"we_{pid}")
        sets = c3.text_input("Sets", value="3–4", key=f"sets_{pid}")
        reps = c4.text_input("Reps", value="8–12", key=f"reps_{pid}")
        rpe  = c5.text_input("RPE", value="6–7", key=f"rpe_{pid}")
        ph_notes = st.text_area("Phase Notes", height=60, key=f"pnotes_{pid}")
        if st.form_submit_button("Add Phase", type="primary"):
            if ph_name:
                add_phase(pid, ph_name, ws, we, sets, reps, rpe, ph_notes)
                st.rerun()


# ── Exercise Library ───────────────────────────────────────────────────────────
def show_library():
    st.markdown("## 📚 Exercise Library")
    library = get_exercise_library()
    if not library:
        st.info("Library is empty.")
        return

    search = st.text_input("🔍 Search exercises", placeholder="e.g. deadlift, rotational, core...")
    categories = sorted(set(e["category"] for e in library))
    cat_filter = st.multiselect("Filter by category", categories, default=categories)

    filtered = [e for e in library
                if e["category"] in cat_filter
                and (not search or search.lower() in e["name"].lower()
                     or search.lower() in (e.get("muscle_group","") or "").lower())]

    st.markdown(f"**{len(filtered)} exercises**")
    for ex in filtered:
        with st.expander(f"**{ex['name']}** — {ex['category']} · {ex['muscle_group']}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {ex.get('description','')}")
            c2.markdown(f"**Coaching Cues:** {ex.get('coaching_cues','')}")
