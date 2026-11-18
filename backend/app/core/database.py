"""
PDF NEXUS - Database Engine
High-performance SQLite engine with WAL mode, foreign key support, and migration readiness for PostgreSQL.
"""

import sqlite3
import contextlib
from typing import Generator
from app.core.config import settings

def init_db():
    """Initializes tables and indexes for PDF NEXUS."""
    conn = get_db_connection()
    try:
        with conn:
            conn.executescript("""
            PRAGMA journal_mode = WAL;
            PRAGMA foreign_keys = ON;

            -- Users
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Documents
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                page_count INTEGER DEFAULT 1,
                thumbnail_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            -- Document Versions
            CREATE TABLE IF NOT EXISTS document_versions (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                version_num INTEGER NOT NULL,
                stored_filename TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            -- Editing Sessions
            CREATE TABLE IF NOT EXISTS editing_sessions (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                user_id TEXT,
                active_page INTEGER DEFAULT 1,
                zoom_level REAL DEFAULT 1.0,
                edit_mode TEXT DEFAULT 'direct', -- 'direct' or 'overlay'
                last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            -- Document Operations (for undo/redo tracking & version history)
            CREATE TABLE IF NOT EXISTS document_operations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                operation_type TEXT NOT NULL, -- 'text_edit', 'redact', 'add_text', 'image_edit', 'page_op'
                page_number INTEGER NOT NULL,
                data_json TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES editing_sessions(id) ON DELETE CASCADE
            );

            -- User Signatures
            CREATE TABLE IF NOT EXISTS signatures (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                signature_data_url TEXT NOT NULL,
                is_cryptographic INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            -- Export History
            CREATE TABLE IF NOT EXISTS export_history (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                export_type TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Indexes for fast querying
            CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);
            CREATE INDEX IF NOT EXISTS idx_doc_versions ON document_versions(document_id);
            CREATE INDEX IF NOT EXISTS idx_doc_ops ON document_operations(session_id);
            """)
    finally:
        conn.close()

def get_db_connection() -> sqlite3.Connection:
    """Returns a new SQLite connection with row_factory as Row."""
    conn = sqlite3.connect(str(settings.DATABASE_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextlib.contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for DB transactions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
