"""
Account service.

Handles balance queries, deposits, and withdrawals.
Raises ValueError for business-rule violations so the
controller can catch them and pass messages to the template.
"""

from datetime import datetime, timezone
from models.db import get_connection


def get_balance(customer_id: int) -> float:
    """Return the current balance for *customer_id*."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT balance FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise RuntimeError(f"No account found for customer_id={customer_id}")

    return float(row["balance"])


def deposit(customer_id: int, amount: float) -> float:
    """
    Add *amount* to the account balance.
    Records the transaction and returns the new balance.
    Raises ValueError if *amount* is not positive.
    """
    if amount <= 0:
        raise ValueError("Deposit amount must be greater than zero.")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Read current balance
        row = cur.execute(
            "SELECT balance FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"No account found for customer_id={customer_id}")

        new_balance = float(row["balance"]) + amount

        # Update balance
        cur.execute(
            "UPDATE accounts SET balance = ? WHERE customer_id = ?",
            (new_balance, customer_id),
        )

        # Record transaction
        cur.execute(
            "INSERT INTO transactions (customer_id, type, amount, created_at) "
            "VALUES (?, ?, ?, ?)",
            (customer_id, "deposit", amount, datetime.now(timezone.utc).isoformat()),
        )

        conn.commit()
    finally:
        conn.close()

    return new_balance


def withdraw(customer_id: int, amount: float) -> float:
    """
    Deduct *amount* from the account balance.
    Records the transaction and returns the new balance.
    Raises ValueError if *amount* is not positive or exceeds the balance.
    """
    if amount <= 0:
        raise ValueError("Withdrawal amount must be greater than zero.")

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Read current balance — always fresh from DB
        row = cur.execute(
            "SELECT balance FROM accounts WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"No account found for customer_id={customer_id}")

        current_balance = float(row["balance"])

        if amount > current_balance:
            raise ValueError(
                f"Insufficient funds. Your current balance is £{current_balance:,.2f}."
            )

        new_balance = current_balance - amount

        # Update balance
        cur.execute(
            "UPDATE accounts SET balance = ? WHERE customer_id = ?",
            (new_balance, customer_id),
        )

        # Record transaction
        cur.execute(
            "INSERT INTO transactions (customer_id, type, amount, created_at) "
            "VALUES (?, ?, ?, ?)",
            (customer_id, "withdrawal", amount, datetime.now(timezone.utc).isoformat()),
        )

        conn.commit()
    finally:
        conn.close()

    return new_balance
