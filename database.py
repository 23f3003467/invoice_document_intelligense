"""
Step 5: Storage.
Plain SQLite — zero setup, good enough to prove the pipeline works.
Swap for Postgres later if you want this to feel more "production".
"""

import sqlite3
import json
from models import ProcessedDocument

DB_PATH = "documents.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            doc_type TEXT,
            confidence REAL,
            fields_json TEXT,
            flagged INTEGER,
            flag_reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_document(doc: ProcessedDocument) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        """
        INSERT INTO documents (filename, doc_type, confidence, fields_json, flagged, flag_reason)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            doc.filename,
            doc.classification.doc_type,
            doc.classification.confidence,
            json.dumps(doc.fields),
            int(doc.flagged),
            doc.flag_reason,
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def list_documents() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]