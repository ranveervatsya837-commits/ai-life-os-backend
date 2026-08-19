
import sqlite3

def get_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection

# =====================================================
# DATABASE CONFIG
# =====================================================

DATABASE_NAME = "database.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():
    """
    Create SQLite database connection.
    """

    connection = sqlite3.connect(DATABASE_NAME)

    print("DATABASE:", DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    return connection

# =====================================================
# CREATE TABLES
# =====================================================

def create_tables():
    """
    Create all required project tables.
    """

    with closing(get_connection()) as connection:

        cursor = connection.cursor()

        # =================================================
        # USERS TABLE
        # =================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
            """
        )

        # =================================================
        # DOCTORS TABLE
        # =================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                experience INTEGER NOT NULL,
                consultation_fee INTEGER NOT NULL,
                available INTEGER DEFAULT 1
            )
            """
        )

        # =================================================
        # APPOINTMENTS TABLE
        # =================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                patient TEXT NOT NULL,
                doctor TEXT NOT NULL,
                hospital TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                fee INTEGER NOT NULL
            )
            """
        )

        # =================================================
        # AUTH USERS TABLE
        # =================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
            """
        )        # =================================================
        # AI CONVERSATIONS TABLE
        # =================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    create_tables()

    print("Database initialized successfully.")
