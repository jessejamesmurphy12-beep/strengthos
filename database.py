import os
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:$Whatthefuckelseineed@db.eokkeqgkcqmzfmpgcmmt.supabase.co:5432/postgres")

def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('coach','athlete')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS athletes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        coach_id INTEGER REFERENCES users(id),
        sport TEXT,
        position TEXT,
        year TEXT,
        notes TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        id SERIAL PRIMARY KEY,
        coach_id INTEGER REFERENCES users(id),
        name TEXT NOT NULL,
        description TEXT,
        goal TEXT,
        weeks INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS phases (
        id SERIAL PRIMARY KEY,
        program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        week_start INTEGER,
        week_end INTEGER,
        sets TEXT,
        reps TEXT,
        rpe TEXT,
        notes TEXT,
        sort_order INTEGER DEFAULT 0
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS workout_days (
        id SERIAL PRIMARY KEY,
        phase_id INTEGER REFERENCES phases(id) ON DELETE CASCADE,
        day_number INTEGER,
        title TEXT,
        focus TEXT,
        sort_order INTEGER DEFAULT 0
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id SERIAL PRIMARY KEY,
        day_id INTEGER REFERENCES workout_days(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        sets TEXT,
        reps TEXT,
        notes TEXT,
        sort_order INTEGER DEFAULT 0
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS exercise_library (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        muscle_group TEXT,
        description TEXT,
        coaching_cues TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS athlete_programs (
        id SERIAL PRIMARY KEY,
        athlete_id INTEGER REFERENCES users(id),
        program_id INTEGER REFERENCES programs(id),
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS workout_logs (
        id SERIAL PRIMARY KEY,
        athlete_id INTEGER REFERENCES users(id),
        exercise_id INTEGER REFERENCES exercises(id),
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sets_done INTEGER,
        reps_done TEXT,
        weight TEXT,
        rpe_actual TEXT,
        notes TEXT
    )""")

    # Seed default coach if none exists
    c.execute("SELECT id FROM users WHERE role='coach' LIMIT 1")
    existing = c.fetchone()
    if not existing:
        pw = bcrypt.hashpw(b"coach123", bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s,%s,%s,%s)",
                  ("Coach Demo", "coach@demo.com", pw, "coach"))

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
        c.executemany("""INSERT INTO exercise_library (name, category, muscle_group, description, coaching_cues)
                         VALUES (%s,%s,%s,%s,%s)""", exercises)

    conn.commit()
    conn.close()

# ── User helpers ───────────────────────────────────────────────────────────────
def get_user_by_email(email):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=%s", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(name, email, password, role, coach_id=None, sport="", position="", year=""):
    conn = get_conn()
    c = conn.cursor()
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        c.execute("INSERT INTO users (name,email,password_hash,role) VALUES (%s,%s,%s,%s)",
                  (name, email, pw_hash, role))
        c.execute("SELECT id FROM users WHERE email=%s", (email,))
        uid = c.fetchone()["id"]
        if role == "athlete":
            c.execute("INSERT INTO athletes (user_id,coach_id,sport,position,year) VALUES (%s,%s,%s,%s,%s)",
                      (uid, coach_id, sport, position, year))
        conn.commit()
        conn.close()
        return True, "Account created."
    except Exception as e:
        conn.close()
        return False, "Email already exists."

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ── Coach helpers ──────────────────────────────────────────────────────────────
def get_athletes(coach_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT u.id, u.name, u.email, a.sport, a.position, a.year, a.notes
                 FROM users u JOIN athletes a ON u.id=a.user_id
                 WHERE a.coach_id=%s ORDER BY u.name""", (coach_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_programs(coach_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM programs WHERE coach_id=%s ORDER BY created_at DESC", (coach_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_program(coach_id, name, description, goal, weeks):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO programs (coach_id,name,description,goal,weeks) VALUES (%s,%s,%s,%s,%s) RETURNING id",
              (coach_id, name, description, goal, weeks))
    pid = c.fetchone()["id"]
    conn.commit()
    conn.close()
    return pid

def get_program(program_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM programs WHERE id=%s", (program_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_phases(program_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM phases WHERE program_id=%s ORDER BY sort_order, week_start", (program_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_phase(program_id, name, week_start, week_end, sets, reps, rpe, notes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO phases (program_id,name,week_start,week_end,sets,reps,rpe,notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
              (program_id, name, week_start, week_end, sets, reps, rpe, notes))
    conn.commit()
    conn.close()

def get_days(phase_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM workout_days WHERE phase_id=%s ORDER BY day_number", (phase_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_day(phase_id, day_number, title, focus):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO workout_days (phase_id,day_number,title,focus) VALUES (%s,%s,%s,%s)",
              (phase_id, day_number, title, focus))
    conn.commit()
    conn.close()

def get_exercises_for_day(day_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM exercises WHERE day_id=%s ORDER BY sort_order, id", (day_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_exercise(day_id, name, sets, reps, notes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO exercises (day_id,name,sets,reps,notes) VALUES (%s,%s,%s,%s,%s)",
              (day_id, name, sets, reps, notes))
    conn.commit()
    conn.close()

def delete_exercise(exercise_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM exercises WHERE id=%s", (exercise_id,))
    conn.commit()
    conn.close()

def delete_day(day_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM exercises WHERE day_id=%s", (day_id,))
    c.execute("DELETE FROM workout_days WHERE id=%s", (day_id,))
    conn.commit()
    conn.close()

def delete_phase(phase_id):
    conn = get_conn()
    c = conn.cursor()
    days = get_days(phase_id)
    for d in days:
        delete_day(d["id"])
    c.execute("DELETE FROM phases WHERE id=%s", (phase_id,))
    conn.commit()
    conn.close()

def delete_program(program_id):
    phases = get_phases(program_id)
    for p in phases:
        delete_phase(p["id"])
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM athlete_programs WHERE program_id=%s", (program_id,))
    c.execute("DELETE FROM programs WHERE id=%s", (program_id,))
    conn.commit()
    conn.close()

def assign_program(athlete_id, program_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE athlete_programs SET status='inactive' WHERE athlete_id=%s", (athlete_id,))
    c.execute("INSERT INTO athlete_programs (athlete_id,program_id,status) VALUES (%s,%s,'active')",
              (athlete_id, program_id))
    conn.commit()
    conn.close()

def get_assigned_program(athlete_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT p.*, ap.assigned_at FROM programs p
                 JOIN athlete_programs ap ON p.id=ap.program_id
                 WHERE ap.athlete_id=%s AND ap.status='active'
                 ORDER BY ap.assigned_at DESC LIMIT 1""", (athlete_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_exercise_library():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM exercise_library ORDER BY category, name")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_workout(athlete_id, exercise_id, sets_done, reps_done, weight, rpe_actual, notes):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO workout_logs (athlete_id,exercise_id,sets_done,reps_done,weight,rpe_actual,notes)
                 VALUES (%s,%s,%s,%s,%s,%s,%s)""",
              (athlete_id, exercise_id, sets_done, reps_done, weight, rpe_actual, notes))
    conn.commit()
    conn.close()

def get_athlete_logs(athlete_id, limit=200):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT wl.*, e.name as exercise_name, wd.title as day_title
                 FROM workout_logs wl
                 LEFT JOIN exercises e ON wl.exercise_id=e.id
                 LEFT JOIN workout_days wd ON e.day_id=wd.id
                 WHERE wl.athlete_id=%s
                 ORDER BY wl.logged_at DESC LIMIT %s""", (athlete_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_coach_stats(coach_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as n FROM athletes WHERE coach_id=%s", (coach_id,))
    athletes = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) as n FROM programs WHERE coach_id=%s", (coach_id,))
    programs = c.fetchone()["n"]
    c.execute("""SELECT COUNT(*) as n FROM athlete_programs ap
                 JOIN programs p ON ap.program_id=p.id
                 WHERE p.coach_id=%s AND ap.status='active'""", (coach_id,))
    assigned = c.fetchone()["n"]
    conn.close()
    return {"athletes": athletes, "programs": programs, "assigned": assigned}
