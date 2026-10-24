"""
Database connection, transaction management, and schema migrations using SQLite.
Guarantees ACID transactions, foreign key enforcement, and dictionary-like row access.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, Any, List, Tuple


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    national_id TEXT UNIQUE NOT NULL,
    birth_date TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    blood_type TEXT,
    allergies TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS doctors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    license_number TEXT UNIQUE NOT NULL,
    specialty TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    start_time TEXT NOT NULL DEFAULT '08:00',
    end_time TEXT NOT NULL DEFAULT '18:00',
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS appointments (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED')),
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_appointments_doctor_slot 
ON appointments(doctor_id, appointment_date, time_slot) 
WHERE status != 'CANCELLED';

CREATE TABLE IF NOT EXISTS medicines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    active_ingredient TEXT,
    dosage TEXT NOT NULL,
    form TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0),
    min_threshold INTEGER NOT NULL DEFAULT 10,
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    expiration_date TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    appointment_id TEXT,
    notes TEXT DEFAULT '',
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'DISPENSED', 'CANCELLED')),
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id TEXT NOT NULL,
    medicine_id TEXT NOT NULL,
    dosage_instructions TEXT NOT NULL,
    quantity_prescribed INTEGER NOT NULL CHECK(quantity_prescribed > 0),
    quantity_dispensed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS dispense_records (
    id TEXT PRIMARY KEY,
    prescription_id TEXT,
    patient_id TEXT NOT NULL,
    medicine_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL,
    total_cost REAL NOT NULL,
    pharmacist_notes TEXT DEFAULT '',
    dispensed_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE SET NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines(name);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
"""


class DatabaseManager:
    """Manages SQLite connections, schema initialization, and transactional queries."""

    def __init__(self, db_path: str = "data/hospital.db"):
        self.db_path = db_path
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._shared_memory_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            # Keep a persistent connection for in-memory databases during tests
            self._shared_memory_conn = sqlite3.connect(":memory:")
            self._shared_memory_conn.row_factory = sqlite3.Row
            self._shared_memory_conn.execute("PRAGMA foreign_keys = ON;")
        self.initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection."""
        if self.db_path == ":memory:" and self._shared_memory_conn:
            return self._shared_memory_conn

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_schema(self) -> None:
        """Runs the schema DDL to create tables and indexes."""
        conn = self.get_connection()
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()

    @contextmanager
    def transaction(self):
        """Context manager providing an atomic transaction block."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> int:
        """Executes an INSERT, UPDATE, or DELETE query and returns rows affected."""
        with self.transaction() as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount

    def fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        """Fetches a single row for a SELECT query."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            return cursor.fetchone()
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Fetches all rows for a SELECT query."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def get_next_id(self, table: str, prefix: str, conn: Optional[sqlite3.Connection] = None) -> str:
        """Generates the next sequential ID (e.g. PAT-0001, DSP-0042) safely."""
        target_conn = conn or self.get_connection()
        try:
            cursor = target_conn.execute(
                f"SELECT id FROM {table} WHERE id LIKE ? ORDER BY id DESC LIMIT 1",
                (f"{prefix}-%",),
            )
            row = cursor.fetchone()
            if row and row[0]:
                try:
                    num = int(row[0].split("-")[1])
                except (IndexError, ValueError):
                    num = 0
            else:
                num = 0
            return f"{prefix}-{num + 1:04d}"
        finally:
            if not conn and self.db_path != ":memory:":
                target_conn.close()

    def close(self) -> None:
        """Closes any persistent connections (like in-memory)."""
        if self._shared_memory_conn:
            self._shared_memory_conn.close()
            self._shared_memory_conn = None
