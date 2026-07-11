"""
conftest.py — shared pytest fixtures for unit and integration tests.

All tests use an isolated in-memory SQLite database so they are
fast, independent, and leave no side effects on bank.db.
"""

import os
import sys
import sqlite3
import pytest

# Ensure BACKEND/ is on sys.path so all package imports resolve
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


# ---------------------------------------------------------------------------
# In-memory database helpers
# ---------------------------------------------------------------------------

def _create_in_memory_db():
    """
    Create and return a fresh in-memory SQLite connection with the full
    schema and one seeded customer (demo / password123, balance £1000).
    """
    from werkzeug.security import generate_password_hash

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE customers (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            name     TEXT    NOT NULL
        );
        CREATE TABLE accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL UNIQUE,
            balance     REAL    NOT NULL DEFAULT 0.0,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
        CREATE TABLE transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            type        TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );
    """)

    hashed = generate_password_hash("password123")
    conn.execute(
        "INSERT INTO customers (username, password, name) VALUES (?,?,?)",
        ("demo", hashed, "Alex Johnson"),
    )
    conn.execute(
        "INSERT INTO accounts (customer_id, balance) VALUES (?,?)", (1, 1000.00)
    )
    conn.commit()
    return conn


class _NonClosingConnection:
    """
    Wraps a real sqlite3.Connection but makes close() a no-op.

    Services call conn.close() after each operation. In tests we share
    one in-memory connection for the entire test, so we must prevent
    the service from closing it between calls.
    """

    def __init__(self, conn):
        self._conn = conn

    # Proxy all attribute access to the real connection
    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        # Intentional no-op: the fixture owns the connection lifetime
        pass

    def cursor(self):
        return self._conn.cursor()

    def execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    def executescript(self, *args, **kwargs):
        return self._conn.executescript(*args, **kwargs)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def real_close(self):
        """Actually close the underlying connection (called by the fixture)."""
        self._conn.close()


# ---------------------------------------------------------------------------
# Patch get_connection() to return the in-memory DB for every test
# ---------------------------------------------------------------------------

@pytest.fixture()
def patch_db(monkeypatch):
    """
    Replace get_connection everywhere it is used so every test operates on
    a fresh, isolated in-memory SQLite database.

    Uses _NonClosingConnection so that service calls to conn.close()
    are no-ops — the fixture owns the connection lifetime and closes
    it during teardown.

    Patches both the canonical models.db module AND the local names
    already imported by each service module (from models.db import
    get_connection binds the name locally, so patching the module
    attribute alone is not enough).
    """
    import models.db as db_module
    import services.auth_service as auth_svc
    import services.account_service as acct_svc

    real_conn = _create_in_memory_db()
    wrapped = _NonClosingConnection(real_conn)

    def fake_get_connection():
        return wrapped

    monkeypatch.setattr(db_module, "get_connection", fake_get_connection)
    monkeypatch.setattr(auth_svc, "get_connection", fake_get_connection)
    monkeypatch.setattr(acct_svc, "get_connection", fake_get_connection)

    yield wrapped          # tests that need direct DB access can use this
    wrapped.real_close()   # actually close after the test is done


# ---------------------------------------------------------------------------
# Flask test client fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_client(patch_db):
    """Return a Flask test client backed by the in-memory database."""
    import app as app_module

    app_module.app.config["TESTING"] = True
    app_module.app.config["SECRET_KEY"] = "test-secret"

    with app_module.app.test_client() as client:
        yield client
