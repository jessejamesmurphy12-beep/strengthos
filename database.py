import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "strengthos.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('coach','athlete')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS athletes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        coach_id INTEGER REFERENCES users(id),
        sport TEXT,
        position TEXT,
        year TEXT,
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coach_id INTEGER REFERENCES users(id),
        name TEXT NOT NULL,
        description TEXT,
        goal TEXT,
        weeks INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS phases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        week_start INTEGER,
        week_end INTEGER,
        sets TEXT,
        reps TEXT,
        rpe TEXT,
        notes TEXT,
        sort_order INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS workout_days (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phase_id INTEGER REFERENCES phases(id) ON DELETE CASCADE,
        day_number INTEGER,
        title TEXT,
        focus TEXT,
        sort_order INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_id INTEGER REFERENCES workout_days(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        sets TEXT,
        reps TEXT,
        notes TEXT,
        sort_order INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS exercise_library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        muscle_group TEXT,
        description TEXT,
        coaching_cues TEXT
    );

    CREATE TABLE IF NOT EXISTS athlete_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER REFERENCES users(id),
        program_id INTEGER REFERENCES programs(id),
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS workout_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER REFERENCES users(id),
        exercise_id INTEGER REFERENCES exercises(id),
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sets_done INTEGER,
        reps_done TEXT,
        weight TEXT,
        rpe_actual TEXT,
        notes TEXT
    );
    """)

    # Seed a default coach if none exist
    existing = c.execute("SELECT id FROM users WHERE role='coach'").fetchone()
    if not existing:
        pw = bcrypt.hashpw(b"coach123", bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
                  ("Coach Demo", "coach@demo.com", pw, "coach"))

        # Seed exercise library
        exercises = [
            ("Trap Bar Deadlift", "Lower Body", "Hamstrings / Glutes", "Hip hinge with trap bar", "Neutral spine, drive through floor"),
            ("Romanian Deadlift", "Lower Body", "Hamstrings", "Hinge-dominant RDL", "Soft knee, push hips back"),
            ("Bulgarian Split Squat", "Lower Body", "Quads / Glutes", "Rear-foot elevated squat", "Front shin vertical, chest up"),
            ("Nordic Hamstring Curl", "Lower Body", "Hamstrings", "Eccentric hamstring exercise", "Control the descent"),
            ("Hip Thrust", "Lower Body", "Glutes", "Barbell or bodyweight glute bridge", "Full hip extension at top"),
            ("Pallof Press", "Core", "Anti-rotation", "Anti-rotation cable press", "No rotation at hips"),
            ("Landmine Press", "Upper Body", "Shoulders / Chest", "Single arm landmine", "Lat tight, press at angle"),
            ("Seated Cable Row", "Upper Body", "Back", "Horizontal pull", "Retract scapula at end"),
            ("Face Pulls", "Upper Body", "Rear Delt / Rotator Cuff", "Cable face pull", "External rotate at end"),
            ("Goblet Squat", "Lower Body", "Quads", "Front-loaded squat", "Elbows inside knees"),
            ("Cable Woodchop", "Core", "Obliques", "Rotational cable movement", "Generate from hips"),
            ("Copenhagen Plank", "Core", "Adductors", "Side plank hip adduction", "Straight body line"),
            ("Lateral Bound to Stick", "Power", "Glutes / Quads", "Lateral plyometric", "Stick the landing, absorb"),
            ("Med Ball Rotational Throw", "Power", "Full body", "Rotational wall throw", "Hip lead the rotation"),
            ("Hex Bar Jump", "Power", "Full body", "Loaded jump with trap bar", "Full extension at top"),
            ("Band Pull Apart", "Upper Body", "Rear Delt / Rotator Cuff", "Band shoulder health", "Straight arms, squeeze at end"),
            ("Single Leg RDL", "Lower Body", "Hamstrings / Glutes", "Unilateral hip hinge", "Hips square, controlled"),
            ("Farmers Carry", "Accessory", "Full body", "Loaded carry for grip and core", "Tall posture, small steps"),
            ("Sled Push", "Conditioning", "Full body", "Prowler / sled push", "Low hips, drive through legs"),
            ("Serratus Wall Slide", "Upper Body", "Serratus Anterior", "Scapular upward rotation drill", "Push into wall at top"),
        ]
        c.executemany("INSERT INTO exercise_library (name, category, muscle_group, description, coaching_cues) VALUES (?,?,?,?,?)", exercises)

    conn.commit()
    conn.close()

# ── User helpers ───────────────────────────────────────────────────────────────
def get_user_by_email(email):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(name, email, password, role, coach_id=None, sport="", position="", year=""):
    conn = get_conn()
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        conn.execute("INSERT INTO users (name,email,password_hash,role) VALUES (?,?,?,?)",
                     (name, email, pw_hash, role))
        conn.commit()
        uid = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]
        if role == "athlete":
            conn.execute("INSERT INTO athletes (user_id,coach_id,sport,position,year) VALUES (?,?,?,?,?)",
                         (uid, coach_id, sport, position, year))
            conn.commit()
        conn.close()
        return True, "Account created."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Email already exists."

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ── Coach helpers ──────────────────────────────────────────────────────────────
def get_athletes(coach_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT u.id, u.name, u.email, a.sport, a.position, a.year, a.notes
        FROM users u JOIN athletes a ON u.id=a.user_id
        WHERE a.coach_id=? ORDER BY u.name
    """, (coach_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_programs(coach_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM programs WHERE coach_id=? ORDER BY created_at DESC", (coach_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_program(coach_id, name, description, goal, weeks):
    conn = get_conn()
    conn.execute("INSERT INTO programs (coach_id,name,description,goal,weeks) VALUES (?,?,?,?,?)",
                 (coach_id, name, description, goal, weeks))
    conn.commit()
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return pid

def get_program(program_id):
    conn = get_conn()
    p = conn.execute("SELECT * FROM programs WHERE id=?", (program_id,)).fetchone()
    conn.close()
    return dict(p) if p else None

def get_phases(program_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM phases WHERE program_id=? ORDER BY sort_order,week_start", (program_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_phase(program_id, name, week_start, week_end, sets, reps, rpe, notes):
    conn = get_conn()
    conn.execute("INSERT INTO phases (program_id,name,week_start,week_end,sets,reps,rpe,notes) VALUES (?,?,?,?,?,?,?,?)",
                 (program_id, name, week_start, week_end, sets, reps, rpe, notes))
    conn.commit()
    conn.close()

def get_days(phase_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM workout_days WHERE phase_id=? ORDER BY day_number", (phase_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_day(phase_id, day_number, title, focus):
    conn = get_conn()
    conn.execute("INSERT INTO workout_days (phase_id,day_number,title,focus) VALUES (?,?,?,?)",
                 (phase_id, day_number, title, focus))
    conn.commit()
    conn.close()

def get_exercises_for_day(day_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM exercises WHERE day_id=? ORDER BY sort_order", (day_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_exercise(day_id, name, sets, reps, notes):
    conn = get_conn()
    conn.execute("INSERT INTO exercises (day_id,name,sets,reps,notes) VALUES (?,?,?,?,?)",
                 (day_id, name, sets, reps, notes))
    conn.commit()
    conn.close()

def delete_exercise(exercise_id):
    conn = get_conn()
    conn.execute("DELETE FROM exercises WHERE id=?", (exercise_id,))
    conn.commit()
    conn.close()

def delete_day(day_id):
    conn = get_conn()
    conn.execute("DELETE FROM exercises WHERE day_id=?", (day_id,))
    conn.execute("DELETE FROM workout_days WHERE id=?", (day_id,))
    conn.commit()
    conn.close()

def delete_phase(phase_id):
    conn = get_conn()
    days = get_days(phase_id)
    for d in days:
        delete_day(d["id"])
    conn.execute("DELETE FROM phases WHERE id=?", (phase_id,))
    conn.commit()
    conn.close()

def assign_program(athlete_id, program_id):
    conn = get_conn()
    conn.execute("UPDATE athlete_programs SET status='inactive' WHERE athlete_id=?", (athlete_id,))
    conn.execute("INSERT INTO athlete_programs (athlete_id,program_id,status) VALUES (?,?,'active')",
                 (athlete_id, program_id))
    conn.commit()
    conn.close()

def get_assigned_program(athlete_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT p.*, ap.assigned_at FROM programs p
        JOIN athlete_programs ap ON p.id=ap.program_id
        WHERE ap.athlete_id=? AND ap.status='active'
        ORDER BY ap.assigned_at DESC LIMIT 1
    """, (athlete_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_exercise_library():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM exercise_library ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_workout(athlete_id, exercise_id, sets_done, reps_done, weight, rpe_actual, notes):
    conn = get_conn()
    conn.execute("""INSERT INTO workout_logs (athlete_id,exercise_id,sets_done,reps_done,weight,rpe_actual,notes)
                    VALUES (?,?,?,?,?,?,?)""",
                 (athlete_id, exercise_id, sets_done, reps_done, weight, rpe_actual, notes))
    conn.commit()
    conn.close()

def get_athlete_logs(athlete_id, limit=50):
    conn = get_conn()
    rows = conn.execute("""
        SELECT wl.*, e.name as exercise_name, wd.title as day_title
        FROM workout_logs wl
        LEFT JOIN exercises e ON wl.exercise_id=e.id
        LEFT JOIN workout_days wd ON e.day_id=wd.id
        WHERE wl.athlete_id=?
        ORDER BY wl.logged_at DESC LIMIT ?
    """, (athlete_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_coach_stats(coach_id):
    conn = get_conn()
    athletes = conn.execute("SELECT COUNT(*) as n FROM athletes WHERE coach_id=?", (coach_id,)).fetchone()["n"]
    programs = conn.execute("SELECT COUNT(*) as n FROM programs WHERE coach_id=?", (coach_id,)).fetchone()["n"]
    assigned = conn.execute("""
        SELECT COUNT(*) as n FROM athlete_programs ap
        JOIN programs p ON ap.program_id=p.id
        WHERE p.coach_id=? AND ap.status='active'
    """, (coach_id,)).fetchone()["n"]
    conn.close()
    return {"athletes": athletes, "programs": programs, "assigned": assigned}
