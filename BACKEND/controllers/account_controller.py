"""
Account controller.

Handles: dashboard, deposit form, process deposit,
         withdraw form, process withdrawal.
"""

from functools import wraps

from flask import redirect, render_template, request, session, url_for
from services.account_service import deposit, get_balance, withdraw


# ---------------------------------------------------------------------------
# Session guard
# ---------------------------------------------------------------------------

def login_required(f):
    """Decorator — redirects to login if no active session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "customer_id" not in session:
            return redirect(url_for("auth.login_get"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def show_dashboard():
    """GET /dashboard — display balance and navigation."""
    customer_id = session["customer_id"]
    balance = get_balance(customer_id)
    message = session.pop("flash_message", None)
    return render_template(
        "dashboard.html",
        name=session.get("customer_name", "Customer"),
        balance=balance,
        message=message,
    )


# ---------------------------------------------------------------------------
# Deposit
# ---------------------------------------------------------------------------

@login_required
def show_deposit():
    """GET /deposit — render the deposit form."""
    return render_template("deposit.html")


@login_required
def process_deposit():
    """POST /deposit — validate amount and call deposit service."""
    raw_amount = request.form.get("amount", "").strip()

    # Validation
    if not raw_amount:
        return render_template("deposit.html", error="Please enter an amount.")
    try:
        amount = float(raw_amount)
    except ValueError:
        return render_template("deposit.html", error="Amount must be a number.")
    if amount <= 0:
        return render_template(
            "deposit.html", error="Amount must be greater than zero."
        )

    customer_id = session["customer_id"]
    new_balance = deposit(customer_id, amount)
    session["flash_message"] = (
        f"Deposit of £{amount:,.2f} successful. New balance: £{new_balance:,.2f}."
    )
    return redirect(url_for("account.dashboard"))


# ---------------------------------------------------------------------------
# Withdraw
# ---------------------------------------------------------------------------

@login_required
def show_withdraw():
    """GET /withdraw — render the withdraw form with current balance."""
    customer_id = session["customer_id"]
    balance = get_balance(customer_id)
    return render_template("withdraw.html", balance=balance)


@login_required
def process_withdraw():
    """POST /withdraw — validate amount and call withdraw service."""
    raw_amount = request.form.get("amount", "").strip()
    customer_id = session["customer_id"]

    # Validation
    if not raw_amount:
        balance = get_balance(customer_id)
        return render_template(
            "withdraw.html", balance=balance, error="Please enter an amount."
        )
    try:
        amount = float(raw_amount)
    except ValueError:
        balance = get_balance(customer_id)
        return render_template(
            "withdraw.html", balance=balance, error="Amount must be a number."
        )
    if amount <= 0:
        balance = get_balance(customer_id)
        return render_template(
            "withdraw.html",
            balance=balance,
            error="Amount must be greater than zero.",
        )

    try:
        new_balance = withdraw(customer_id, amount)
    except ValueError as exc:
        balance = get_balance(customer_id)
        return render_template("withdraw.html", balance=balance, error=str(exc))

    session["flash_message"] = (
        f"Withdrawal of £{amount:,.2f} successful. New balance: £{new_balance:,.2f}."
    )
    return redirect(url_for("account.dashboard"))
