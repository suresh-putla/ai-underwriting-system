import sqlite3
import hashlib
import os
from pathlib import Path

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_dir = Path(__file__).parent
            db_path = db_dir / "lous.db"

        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints (SQLite default is OFF)
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'loan_officer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Create loan documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS LOAN_DOCS (
                DOC_TYPE TEXT PRIMARY KEY,
                REQUIRED_FLAG INTEGER NOT NULL DEFAULT 1
            )
        ''')

        # Create submitted loan documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SUBMITTED_LOAN_DOCS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID TEXT NOT NULL REFERENCES users(username),
                DOC_TYPE TEXT NOT NULL REFERENCES LOAN_DOCS(DOC_TYPE),
                STATUS TEXT NOT NULL DEFAULT 'Evaluating'
                       CHECK (STATUS IN ('Evaluating','Under Review','Valid','Not Valid'))
            )
        ''')

        # Create default admin user if not exists
        self._create_default_users(cursor)

        # Seed default loan document types
        self._seed_loan_docs(cursor)

        conn.commit()
        conn.close()

    def _create_default_users(self, cursor):
        """Create default users for testing"""
        default_users = [
            ('admin', 'admin123', 'admin@lous.com', 'System Administrator', 'admin'),
            ('loan_officer', 'officer123', 'officer@lous.com', 'Loan Officer', 'loan_officer'),
            ('underwriter', 'under123', 'underwriter@lous.com', 'Underwriter', 'underwriter'),
            ('borrower', 'borrower123', 'borrower@lous.com', 'Borrower User', 'borrower'),
        ]

        for username, password, email, full_name, role in default_users:
            try:
                password_hash = self._hash_password(password)
                cursor.execute(
                    'INSERT INTO users (username, password_hash, email, full_name, role) VALUES (?, ?, ?, ?, ?)',
                    (username, password_hash, email, full_name, role)
                )
            except sqlite3.IntegrityError:
                # User already exists
                pass

    def _seed_loan_docs(self, cursor):
        """Seed default loan document types"""
        default_docs = [
            ('W2', 1),
            ('Pay stub', 1),
            ('Bank Statement', 1),
        ]

        for doc_type, required_flag in default_docs:
            try:
                cursor.execute(
                    'INSERT INTO LOAN_DOCS (DOC_TYPE, REQUIRED_FLAG) VALUES (?, ?)',
                    (doc_type, required_flag)
                )
            except sqlite3.IntegrityError:
                # Document type already exists
                pass

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user credentials"""
        conn = self.get_connection()
        cursor = conn.cursor()

        password_hash = self._hash_password(password)

        cursor.execute(
            'SELECT id, username, email, full_name, role FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )

        user = cursor.fetchone()

        if user:
            # Update last login
            cursor.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'],)
            )
            conn.commit()

            # Convert to dict
            user_dict = dict(user)
            conn.close()
            return user_dict

        conn.close()
        return None

    def get_user_by_username(self, username: str) -> dict:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, username, email, full_name, role, created_at, last_login FROM users WHERE username = ?',
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        return dict(user) if user else None

    def get_submitted_docs_by_user(self, user_id: str) -> list[dict]:
        """Get all submitted loan documents for a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT DOC_TYPE, STATUS FROM SUBMITTED_LOAN_DOCS WHERE USER_ID = ?',
            (user_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
