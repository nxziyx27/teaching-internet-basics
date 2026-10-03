import sqlite3
from datetime import datetime


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_NAME = "internet_basics.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database():
    return sqlite3.connect(DATABASE_NAME)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_tables():

    connection = connect_database()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # LEARNERS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course_started TEXT,
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # QUIZ ATTEMPTS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            score INTEGER,
            total_questions INTEGER,
            percentage REAL,
            result TEXT,
            attempt_date TEXT,
            FOREIGN KEY (learner_id)
                REFERENCES learners(id)
        )
    """)

    # --------------------------------------------------------
    # LESSON PROGRESS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER NOT NULL,
            lesson_number INTEGER NOT NULL,
            completed_at TEXT,
            UNIQUE(learner_id, lesson_number),
            FOREIGN KEY (learner_id)
                REFERENCES learners(id)
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# ADD LEARNER
# ============================================================

def add_learner(name, email):

    connection = connect_database()
    cursor = connection.cursor()

    current_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    try:

        cursor.execute("""
            INSERT INTO learners
            (
                name,
                email,
                course_started,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            current_time,
            current_time
        ))

        connection.commit()

    except sqlite3.IntegrityError:

        pass

    connection.close()


# ============================================================
# REGISTER LEARNER
# ============================================================

def register_learner(name, email):
    """
    Create a learner account.

    Returns:
        (True, success message)
        OR
        (False, error message)
    """

    connection = connect_database()
    cursor = connection.cursor()

    current_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    try:

        cursor.execute("""
            INSERT INTO learners
            (
                name,
                email,
                course_started,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            current_time,
            current_time
        ))

        connection.commit()

        return (
            True,
            "Registration successful! "
            "You can now start learning."
        )

    except sqlite3.IntegrityError:

        return (
            False,
            "An account with this email already exists. "
            "Please use the login form."
        )

    finally:

        connection.close()


# ============================================================
# GET LEARNER
# ============================================================

def get_learner(name, email):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email
        FROM learners
        WHERE name = ?
        AND email = ?
    """, (
        name,
        email
    ))

    learner = cursor.fetchone()

    connection.close()

    return learner


# ============================================================
# ADD QUIZ ATTEMPT
# ============================================================

def add_quiz_attempt(
    learner_id,
    score,
    total_questions,
    percentage,
    result
):

    connection = connect_database()
    cursor = connection.cursor()

    attempt_date = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO quiz_attempts
        (
            learner_id,
            score,
            total_questions,
            percentage,
            result,
            attempt_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        learner_id,
        score,
        total_questions,
        percentage,
        result,
        attempt_date
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET ALL LEARNERS
# ============================================================

def get_all_learners():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            course_started,
            created_at
        FROM learners
        ORDER BY id DESC
    """)

    learners = cursor.fetchall()

    connection.close()

    return learners


# ============================================================
# QUIZ STATISTICS — INDIVIDUAL LEARNER
# ============================================================

def get_quiz_statistics(learner_id):
    """
    Get quiz statistics for one learner.

    Returns:
        attempts
        best_percentage
        latest_percentage
        passed
    """

    if learner_id is None:

        return {
            "attempts": 0,
            "best_percentage": 0,
            "latest_percentage": 0,
            "passed": False
        }

    connection = connect_database()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # NUMBER OF ATTEMPTS + BEST SCORE
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            COUNT(*),
            MAX(percentage)
        FROM quiz_attempts
        WHERE learner_id = ?
    """, (
        learner_id,
    ))

    result = cursor.fetchone()

    attempts = result[0] or 0
    best_percentage = result[1] or 0

    # --------------------------------------------------------
    # LATEST SCORE
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            percentage
        FROM quiz_attempts
        WHERE learner_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        learner_id,
    ))

    latest = cursor.fetchone()

    if latest:
        latest_percentage = latest[0] or 0
    else:
        latest_percentage = 0

    connection.close()

    # --------------------------------------------------------
    # PASS STATUS
    # --------------------------------------------------------

    passed = (
        float(best_percentage) >= 70
    )

    return {
        "attempts": attempts,
        "best_percentage": best_percentage,
        "latest_percentage": latest_percentage,
        "passed": passed
    }


# ============================================================
# QUIZ STATISTICS — ALL LEARNERS / ADMIN
# ============================================================

def get_overall_quiz_statistics():
    """
    Get overall quiz statistics for the Admin Dashboard.

    Returns:
        attempts
        passed
        average_percentage
    """

    connection = connect_database()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # TOTAL ATTEMPTS + AVERAGE SCORE
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            COUNT(*),
            AVG(percentage)
        FROM quiz_attempts
    """)

    result = cursor.fetchone()

    attempts = result[0] or 0
    average_percentage = result[1] or 0

    # --------------------------------------------------------
    # TOTAL PASSED ATTEMPTS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM quiz_attempts
        WHERE percentage >= 70
    """)

    passed_result = cursor.fetchone()

    passed = passed_result[0] or 0

    connection.close()

    return {
        "attempts": attempts,
        "passed": passed,
        "average_percentage": average_percentage
    }


# ============================================================
# CREATE LESSON PROGRESS TABLE
# ============================================================

def create_lesson_progress_table():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER NOT NULL,
            lesson_number INTEGER NOT NULL,
            completed_at TEXT,
            UNIQUE(learner_id, lesson_number),
            FOREIGN KEY (learner_id)
                REFERENCES learners(id)
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# MARK LESSON AS COMPLETED
# ============================================================

def mark_lesson_completed(
    learner_id,
    lesson_number
):
    """
    Mark one of the five lessons as completed.

    lesson_number must be between 1 and 5.
    """

    if learner_id is None:
        return False

    if lesson_number < 1 or lesson_number > 5:
        return False

    create_lesson_progress_table()

    connection = connect_database()
    cursor = connection.cursor()

    completed_at = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    try:

        cursor.execute("""
            INSERT OR IGNORE INTO lesson_progress
            (
                learner_id,
                lesson_number,
                completed_at
            )
            VALUES (?, ?, ?)
        """, (
            learner_id,
            lesson_number,
            completed_at
        ))

        connection.commit()

        inserted = (
            cursor.rowcount > 0
        )

        return inserted

    except sqlite3.Error as error:

        print(
            "Lesson progress error:",
            error
        )

        return False

    finally:

        connection.close()


# ============================================================
# GET COMPLETED LESSONS
# ============================================================

def get_completed_lessons(learner_id):
    """
    Return a list containing completed lesson numbers.
    """

    if learner_id is None:
        return []

    create_lesson_progress_table()

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            lesson_number
        FROM lesson_progress
        WHERE learner_id = ?
        ORDER BY lesson_number ASC
    """, (
        learner_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    return [
        row[0]
        for row in rows
    ]


# ============================================================
# GET COURSE PROGRESS
# ============================================================

def get_course_progress(learner_id):
    """
    Get complete five-day course progress.
    """

    completed_lessons = (
        get_completed_lessons(
            learner_id
        )
    )

    total_lessons = 5

    completed_count = len(
        completed_lessons
    )

    percentage = (
        completed_count
        / total_lessons
    ) * 100

    course_completed = (
        completed_count == total_lessons
    )

    return {
        "completed_lessons": completed_lessons,
        "completed_count": completed_count,
        "total_lessons": total_lessons,
        "percentage": percentage,
        "course_completed": course_completed
    }


# ============================================================
# GET LEARNER PROGRESS SUMMARY
# ============================================================

def get_learner_progress(learner_id):
    """
    Get both course and quiz progress.
    """

    quiz = get_quiz_statistics(
        learner_id
    )

    course = get_course_progress(
        learner_id
    )

    return {
        "quiz": quiz,
        "course": course
    }


# ============================================================
# INITIALIZE DATABASE
# ============================================================

create_tables()