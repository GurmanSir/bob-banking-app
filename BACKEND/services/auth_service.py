"""
Authentication service.

Handles credential verification and password hashing.
No Flask or HTTP knowledge — pure Python logic.
"""

from werkzeug.security import check_password_hash, generate_password_hash
from models.db import get_connection


def verify_credentials(username: str, password: str):
    """
    Look up *username* in the customers table and verify *password*
    against the stored hash.

    Returns the customer row (sqlite3.Row) on success, or None on failure.
    Never reveals which of username / password was wrong.
    """
    conn = get_connection()
    try:
        customer = conn.execute(
            "SELECT * FROM customers WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()

    if customer is None:
        return None

    if not check_password_hash(customer["password"], password):
        return None

    return customer


def hash_password(plain_text: str) -> str:
    """
    Return a Werkzeug-hashed version of *plain_text*.
    Used by db.py seeding — not called at request time.
    """
    return generate_password_hash(plain_text)
