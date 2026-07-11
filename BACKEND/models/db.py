"""
Database layer — SQLite connection helper and schema initialisation.

All direct SQLite interaction is isolated here.
Every service imports get_connection() from this module.
"""

import os
import sqlite3

# bank.db lives alongside this file (inside BACKEND/)
_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "bank.db")


def get_connection():
    """
    Open and return a SQLite connection configured to return
    rows as dict-like sqlite3.Row objects.
    Callers are responsible for closing the connection.
    """
    conn = sqlite3.connect(os.path.abspath(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create tables (if they do not already exist) and seed one
    demo customer + account.  Safe to call on every startup.
    """
    from werkzeug.security import generate_password_hash

    conn = get_connection()
    cur = conn.cursor()

    # --- Schema ---
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            name     TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL UNIQUE,
            balance     REAL    NOT NULL DEFAULT 0.0,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            type        TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
    """)

    # --- Seed demo customer (skip if already present) ---
    existing = cur.execute(
        "SELECT id FROM customers WHERE username = ?", ("demo",)
    ).fetchone()

    if not existing:
        hashed = generate_password_hash("password123")
        cur.execute(
            "INSERT INTO customers (username, password, name) VALUES (?, ?, ?)",
            ("demo", hashed, "Alex Johnson"),
        )
        customer_id = cur.lastrowid
        cur.execute(
            "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
            (customer_id, 1000.00),
        )

    conn.commit()
    conn.close()
