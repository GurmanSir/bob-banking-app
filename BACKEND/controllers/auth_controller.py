"""
Authentication controller.

Handles: show login page, process login form, logout.
"""

from flask import redirect, render_template, request, session, url_for
from services.auth_service import verify_credentials


def show_login():
    """GET /login — render the login form."""
    # Already logged in? Send straight to dashboard.
    if "customer_id" in session:
        return redirect(url_for("account.dashboard"))
    return render_template("login.html")


def process_login():
    """POST /login — validate credentials and create session."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    # Field-presence validation
    if not username or not password:
        return render_template(
            "login.html", error="Please enter your username and password."
        )

    customer = verify_credentials(username, password)

    if customer is None:
        return render_template(
            "login.html", error="Invalid username or password."
        )

    # Credentials valid — create session
    session["customer_id"] = customer["id"]
    session["customer_name"] = customer["name"]
    return redirect(url_for("account.dashboard"))


def logout():
    """GET /logout — clear session and redirect to login."""
    session.clear()
    return redirect(url_for("auth.login_get"))
