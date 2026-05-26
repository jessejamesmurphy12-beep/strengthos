import streamlit as st
import pandas as pd
from database import (get_athletes, get_programs, create_program, delete_athlete, update_athlete,
                      get_phases, add_phase, get_days, add_day,
                      get_exercises_for_day, add_exercise, delete_exercise,
                      delete_day, delete_phase, delete_program, assign_program,
                      get_exercise_library, get_coach_stats, create_user,
                      get_athlete_logs, get_conn)

FOCUS_OPTIONS = ["Strength", "Power", "Stability", "Recovery", "Conditioning",
                 "Upper Body", "Lower Body", "Full Body"]
FOCUS_COLORS  = {
    "Strength":"#1B4F72","Power":"#6E2F0A","Stability":"#1D6A39",
    "Recovery":"#555555","Conditioning":"#7D3C0A","Upper Body":"#2874A6",
    "Lower Body":"#1A5276","Full Body":"#4A235A"
}

# ── helpers ────────────────────────────────────────────────────────────────────
def add_exercise_with_superset(day_id, name, sets, reps, notes, superset_group=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO exercises (day_id,name,sets,reps,notes,sort_order) VALUES (%s,%s,%s,%s,%s,%s)",
        (day_id, name, sets, reps,
         f"[Superset {superset_group}] {notes}".strip() if superset_group else notes,
         0)
    )
    conn.commit()
    conn.close()

# ── main router ────────────────────────────────────────────────────────────────
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

        page = st.radio("Navigation",
                        ["Dashboard", "Athletes", "Programs", "Build Workout", "Exercise Library"],
                        label_visibility="collapsed")
        st.markdown("<br>" * 6, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if page == "Dashboard":         show_coach_home(user)
    elif page == "Athletes":        show_athletes(user)
    elif page == "Programs":        show_programs(user)
    elif page == "Build Workout":   show_workout_builder(user)
    elif page == "Exercise Library":show_library()


# ── Dashboard ──────────────────────────────────────────────────────────────────
def show_coach_home(user):
    st.markdown(f"## 👋 Welcome back, {user['name'].split()[0]}")
    stats = get_coach_stats(user["id"])

    c1, c2, c3 = st.columns(3)
    for col, label, val, icon in [
        (c1, "Total Athletes",      stats["athletes"], "🏃"),
        (c2, "Programs Built",      stats["programs"], "📋"),
        (c3, "Active Assignments",  stats["assigned"], "✅"),
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
        st.markdown("<div class='section-header'>Athletes</div>", unsafe_allow_html=True)
        for a in get_athletes(user["id"])[:8]:
            st.markdown(f"""
            <div style='padding:0.5rem 0.8rem; background:#f8fafc; border-radius:8px;
                        margin-bottom:5px; border-left:3px solid #3b82f6;'>
                <b>{a['name']}</b>
                <span style='color:#64748b; font-size:0.8rem; margin-left:8px;'>
                    {a.get('sport','')} · {a.get('position','')} · {a.get('year','')}
                </span>
            </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("<div class='section-header'>Programs</div>", unsafe_allow_html=True)
        for p in get_programs(user["id"])[:6]:
            st.markdown(f"""
            <div style='padding:0.5rem 0.8rem; background:#f8fafc; border-radius:8px;
                        margin-bottom:5px; border-left:3px solid #10b981;'>
                <b>{p['name']}</b>
                <span style='color:#64748b; font-size:0.8rem; margin-left:8px;'>
                    {p['weeks']} wks · {p['goal']}
                </span>
            </div>""", unsafe_allow_html=True)


# ── Athletes ───────────────────────────────────────────────────────────────────
def show_athletes(user):
    st.markdown("## 🏃 Athletes")
    tab_roster, tab_add, tab_assign, tab_logs = st.tabs(
        ["Roster", "Add Athlete", "Assign Program", "View Logs"])

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

                    # Edit form
                    with st.form(key=f"edit_{a['id']}"):
                        st.markdown("**Edit Athlete**")
                        new_name = st.text_input("Name", value=a["name"], key=f"en_{a['id']}")
                        ec1, ec2, ec3 = st.columns(3)
                        new_sport    = ec1.text_input("Sport",    value=a.get("sport",""),    key=f"es_{a['id']}")
                        new_position = ec2.text_input("Position", value=a.get("position",""), key=f"ep_{a['id']}")
                        new_year     = ec3.selectbox("Year",
                                            ["Freshman","Sophomore","Junior","Senior","Grad"],
                                            index=["Freshman","Sophomore","Junior","Senior","Grad"].index(a.get("year","Freshman")) if a.get("year") in ["Freshman","Sophomore","Junior","Senior","Grad"] else 0,
                                            key=f"ey_{a['id']}")
                        new_notes = st.text_area("Notes", value=a.get("notes","") or "", height=60, key=f"eno_{a['id']}")
                        ec1b, ec2b = st.columns(2)
                        if ec1b.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                            update_athlete(a["id"], new_name, new_sport, new_position, new_year, new_notes)
                            st.success("✅ Updated!")
                            st.rerun()
                        if ec2b.form_submit_button("🗑 Remove Athlete", use_container_width=True):
                            delete_athlete(a["id"])
                            st.success(f"{a['name']} removed.")
                            st.rerun()

    with tab_add:
        st.markdown("### Add New Athlete")
        with st.form("add_athlete_form"):
            name  = st.text_input("Full Name")
            email = st.text_input("Email")
            pw    = st.text_input("Temporary Password", type="password", value="athlete123")
            c1, c2, c3 = st.columns(3)
            sport    = c1.text_input("Sport")
            position = c2.text_input("Position")
            year     = c3.selectbox("Year", ["Freshman","Sophomore","Junior","Senior","Grad"])
            if st.form_submit_button("Add Athlete", type="primary"):
                if not name or not email:
                    st.error("Name and email required.")
                else:
                    ok, msg = create_user(name, email, pw, "athlete",
                                          coach_id=user["id"], sport=sport,
                                          position=position, year=year)
                    st.success(f"✅ {name} added! Login: {email} / {pw}") if ok else st.error(msg)

    with tab_assign:
        st.markdown("### Assign Program to Athlete")
        athletes = get_athletes(user["id"])
        programs = get_programs(user["id"])
        if not athletes: st.info("Add athletes first.")
        elif not programs: st.info("Build a program first.")
        else:
            athlete_map = {a["name"]: a["id"] for a in athletes}
            program_map = {p["name"]: p["id"] for p in programs}
            sel_a = st.selectbox("Athlete", list(athlete_map.keys()))
            sel_p = st.selectbox("Program", list(program_map.keys()))
            if st.button("Assign Program", type="primary"):
                assign_program(athlete_map[sel_a], program_map[sel_p])
                st.success(f"✅ {sel_p} assigned to {sel_a}!")

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
                st.info("No logs yet.")
            else:
                df = pd.DataFrame(logs)[["logged_at","exercise_name","sets_done","reps_done","weight","notes"]]
                df.columns = ["Date","Exercise","Sets","Reps","Weight","Notes"]
                st.dataframe(df, use_container_width=True)


# ── Programs (create / manage structure) ──────────────────────────────────────
def show_programs(user):
    st.markdown("## 📋 Programs")
    tab_list, tab_new = st.tabs(["My Programs", "Create New"])

    with tab_new:
        with st.form("new_prog"):
            name  = st.text_input("Program Name", placeholder="Summer Lifting Plan 2025")
            desc  = st.text_area("Description", height=70)
            c1,c2 = st.columns(2)
            goal  = c1.selectbox("Goal", ["Strength & Injury Prevention","Velocity Development",
                                           "Hypertrophy","Power","Conditioning","Balanced"])
            weeks = c2.number_input("Total Weeks", 1, 52, 12)
            if st.form_submit_button("Create Program", type="primary"):
                if not name: st.error("Name required.")
                else:
                    create_program(user["id"], name, desc, goal, weeks)
                    st.success("✅ Program created! Now go to Build Workout to add days.")
                    st.rerun()

    with tab_list:
        programs = get_programs(user["id"])
        if not programs:
            st.info("No programs yet.")
            return
        for prog in programs:
            with st.expander(f"**{prog['name']}** — {prog['weeks']} wks · {prog['goal']}"):
                st.markdown(f"*{prog.get('description','') or 'No description'}*")

                # Phase management inside expander
                phases = get_phases(prog["id"])
                if phases:
                    st.markdown("**Phases:**")
                    for ph in phases:
                        days = get_days(ph["id"])
                        st.markdown(f"• **{ph['name']}** (Wks {ph['week_start']}–{ph['week_end']}) — {len(days)} days")
                        if st.button(f"🗑 Delete Phase: {ph['name']}", key=f"dph_{ph['id']}"):
                            delete_phase(ph["id"]); st.rerun()

                st.markdown("---")
                # Add phase inline
                with st.form(f"ph_{prog['id']}"):
                    st.markdown("**Add Phase**")
                    ph_name = st.text_input("Phase Name", placeholder="Phase 1 — Accumulation", key=f"phn_{prog['id']}")
                    c1,c2,c3,c4,c5 = st.columns(5)
                    ws   = c1.number_input("Wk Start", 1, 52, 1,  key=f"ws_{prog['id']}")
                    we   = c2.number_input("Wk End",   1, 52, 4,  key=f"we_{prog['id']}")
                    sets = c3.text_input("Sets", "3–4",            key=f"st_{prog['id']}")
                    reps = c4.text_input("Reps", "8–12",           key=f"rp_{prog['id']}")
                    rpe  = c5.text_input("RPE",  "6–7",            key=f"rpe_{prog['id']}")
                    if st.form_submit_button("Add Phase"):
                        if ph_name:
                            add_phase(prog["id"], ph_name, ws, we, sets, reps, rpe, "")
                            st.rerun()

                st.markdown("---")
                if st.button("🗑 Delete Entire Program", key=f"dp_{prog['id']}"):
                    delete_program(prog["id"]); st.success("Deleted."); st.rerun()


# ── BUILD WORKOUT (the fast day builder) ──────────────────────────────────────
def show_workout_builder(user):
    st.markdown("## 🏗️ Build Workout")

    programs = get_programs(user["id"])
    if not programs:
        st.info("Create a program first in the Programs tab.")
        return

    # Step 1 — pick program
    prog_map = {p["name"]: p for p in programs}
    sel_prog = st.selectbox("Program", list(prog_map.keys()))
    prog = prog_map[sel_prog]

    phases = get_phases(prog["id"])
    if not phases:
        st.warning("This program has no phases yet. Add phases in the Programs tab.")
        return

    # Step 2 — pick or create a day
    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### Select Existing Day")
        all_days = []
        for ph in phases:
            for d in get_days(ph["id"]):
                all_days.append({"label": f"[{ph['name']}] Day {d['day_number']} — {d['title']}", "day": d, "phase": ph})

        if all_days:
            day_labels = [x["label"] for x in all_days]
            sel_label  = st.selectbox("Choose a day to edit", day_labels, key="sel_day_edit")
            chosen     = next(x for x in all_days if x["label"] == sel_label)
            active_day = chosen["day"]
            active_phase = chosen["phase"]
        else:
            st.info("No days yet — create one →")
            active_day = None
            active_phase = None

    with col_right:
        st.markdown("#### Create New Day")
        with st.form("new_day_form"):
            phase_map = {ph["name"]: ph for ph in phases}
            sel_phase_name = st.selectbox("Phase", list(phase_map.keys()))
            day_title  = st.text_input("Day Title", placeholder="Lower Body — Posterior Chain")
            c1, c2    = st.columns(2)
            day_number = c1.number_input("Day #", 1, 7, 1)
            day_focus  = c2.selectbox("Focus", FOCUS_OPTIONS)
            if st.form_submit_button("➕ Create Day", type="primary"):
                if day_title:
                    ph = phase_map[sel_phase_name]
                    add_day(ph["id"], day_number, day_title, day_focus)
                    st.success(f"✅ Day created!")
                    st.rerun()

    if not active_day:
        return

    # Step 3 — show current exercises + add form
    st.markdown("---")
    fc = FOCUS_COLORS.get(active_day["focus"], "#2874A6")
    st.markdown(f"""
    <div style='background:{fc}; color:white; padding:0.6rem 1.2rem;
                border-radius:8px; font-weight:700; font-size:1rem; margin-bottom:1rem;'>
        {active_phase['name']}  ·  Day {active_day['day_number']} — {active_day['title']}
        &nbsp; <span style='font-weight:400; font-size:0.85rem;'>
        {active_phase['sets']} sets · {active_phase['reps']} reps · RPE {active_phase['rpe']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    exercises = get_exercises_for_day(active_day["id"])

    if exercises:
        st.markdown("**Current Exercises:**")
        for i, ex in enumerate(exercises):
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 2, 1])
            c1.markdown(f"**{ex['name']}**")
            c2.markdown(ex.get("sets",""))
            c3.markdown(ex.get("reps",""))
            c4.markdown(f"*{ex.get('notes','') or ''}*")
            if c5.button("🗑", key=f"delex_{ex['id']}"):
                delete_exercise(ex["id"])
                st.rerun()
        st.markdown("---")
    else:
        st.info("No exercises yet. Add them below.")

    # Add exercises — tabs for single vs superset
    tab_single, tab_superset = st.tabs(["➕ Add Exercise", "🔗 Add Superset"])

    with tab_single:
        with st.form("add_single"):
            # Search library or type custom
            library = get_exercise_library()
            lib_names = ["— type custom name below —"] + [e["name"] for e in library]
            picked = st.selectbox("Pick from library (optional)", lib_names, key="lib_pick")
            custom_name = st.text_input("Exercise Name", value="" if picked.startswith("—") else picked,
                                         placeholder="e.g. Trap Bar Deadlift")
            c1, c2, c3 = st.columns(3)
            sets  = c1.text_input("Sets",  placeholder="4")
            reps  = c2.text_input("Reps",  placeholder="6–8")
            notes = c3.text_input("Notes", placeholder="Optional cue")
            if st.form_submit_button("Add Exercise", type="primary"):
                name = custom_name if custom_name else picked
                if name and not name.startswith("—"):
                    add_exercise(active_day["id"], name, sets, reps, notes)
                    st.success(f"✅ {name} added!")
                    st.rerun()
                else:
                    st.error("Enter or pick an exercise name.")

    with tab_superset:
        st.markdown("Add 2–3 exercises as a superset. They'll be grouped together for the athlete.")
        with st.form("add_superset"):
            ss_label = st.text_input("Superset Label", value="A", placeholder="A, B, C...")
            st.markdown("**Exercise 1**")
            c1,c2,c3 = st.columns(3)
            n1 = c1.text_input("Name",  key="ss_n1", placeholder="Exercise 1")
            s1 = c2.text_input("Sets",  key="ss_s1", placeholder="3")
            r1 = c3.text_input("Reps",  key="ss_r1", placeholder="10")
            st.markdown("**Exercise 2**")
            c1,c2,c3 = st.columns(3)
            n2 = c1.text_input("Name",  key="ss_n2", placeholder="Exercise 2")
            s2 = c2.text_input("Sets",  key="ss_s2", placeholder="3")
            r2 = c3.text_input("Reps",  key="ss_r2", placeholder="10")
            st.markdown("**Exercise 3 (optional)**")
            c1,c2,c3 = st.columns(3)
            n3 = c1.text_input("Name",  key="ss_n3", placeholder="Leave blank if not needed")
            s3 = c2.text_input("Sets",  key="ss_s3", placeholder="3")
            r3 = c3.text_input("Reps",  key="ss_r3", placeholder="10")

            if st.form_submit_button("Add Superset", type="primary"):
                added = 0
                for name, sets, reps in [(n1,s1,r1),(n2,s2,r2),(n3,s3,r3)]:
                    if name.strip():
                        add_exercise_with_superset(active_day["id"], name, sets, reps, "", ss_label)
                        added += 1
                if added >= 2:
                    st.success(f"✅ Superset {ss_label} added ({added} exercises)!")
                    st.rerun()
                else:
                    st.error("Enter at least 2 exercises for a superset.")

    st.markdown("---")
    if st.button(f"🗑 Delete This Day", key=f"del_active_day"):
        delete_day(active_day["id"])
        st.success("Day deleted.")
        st.rerun()


# ── Exercise Library ───────────────────────────────────────────────────────────
def show_library():
    st.markdown("## 📚 Exercise Library")
    library = get_exercise_library()
    if not library:
        st.info("Library is empty.")
        return
    search     = st.text_input("🔍 Search", placeholder="e.g. deadlift, core, rotational...")
    categories = sorted(set(e["category"] for e in library))
    cat_filter = st.multiselect("Category", categories, default=categories)
    filtered   = [e for e in library
                  if e["category"] in cat_filter
                  and (not search or search.lower() in e["name"].lower()
                       or search.lower() in (e.get("muscle_group","") or "").lower())]
    st.markdown(f"**{len(filtered)} exercises**")
    for ex in filtered:
        with st.expander(f"**{ex['name']}** — {ex['category']} · {ex['muscle_group']}"):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Description:** {ex.get('description','')}")
            c2.markdown(f"**Coaching Cues:** {ex.get('coaching_cues','')}")
