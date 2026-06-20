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

        # Create default admin user if not exists
        self._create_default_users(cursor)

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
