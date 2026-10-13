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

