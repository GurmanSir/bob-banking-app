# SecureBank — Banking Web Application

A full-stack banking demo built with **Python Flask**, **Bootstrap 5**, and **SQLite**.

---

## Features

| Feature | Description |
|---|---|
| Customer Login | Secure login with hashed password verification |
| Dashboard | Displays current account balance |
| Deposit Funds | Add a positive amount to your balance |
| Withdraw Funds | Deduct an amount (up to available balance) |
| Logout | Terminates the session |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML + Bootstrap 5 (CDN) + Jinja2 templates |
| Backend | Python 3.9+ / Flask 3.x |
| Database | SQLite (file-based, no server required) |

---

## Project Structure

```
Banking-Application/
├── FRONTEND/
│   ├── templates/          # Jinja2 HTML templates (base, login, dashboard, deposit, withdraw)
│   └── static/             # Custom CSS overrides
├── BACKEND/
│   ├── app.py              # Flask entry point
│   ├── routes/             # URL blueprints
│   ├── controllers/        # Request handling + input validation
│   ├── services/           # Business logic (auth, account, transactions)
│   ├── models/             # SQLite connection + schema initialisation
│   ├── tests/              # Unit and integration tests
│   ├── bank.db             # Auto-created on first run (excluded from VCS)
│   └── requirements.txt    # Python dependencies
├── IMPLEMENTATION_PLAN.md
└── STEP_BY_STEP_IMPLEMENTATION_GUIDE.md
```

---

## Quick Start

### 1. Clone / open the project

```bash
cd Banking-Application
```

### 2. Create and activate the virtual environment

```bash
# From the BACKEND/ directory
cd BACKEND
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Flask will print the local address:

```
 * Running on http://127.0.0.1:5000
```

Open that URL in your browser.

### 5. Login with the demo account

| Field | Value |
|---|---|
| Username | `demo` |
| Password | `password123` |

> The demo account is seeded automatically with a starting balance of **£1,000.00**.

### 6. Stop the server

Press `Ctrl + C` in the terminal.

---

## Running Tests

From the `BACKEND/` directory (with the virtual environment active):

```bash
pytest
```

This runs all unit and integration tests using an in-memory SQLite database.
No files are created or modified during testing.

---

## Demo Credentials

| Username | Password | Starting Balance |
|---|---|---|
| demo | password123 | £1,000.00 |

---

## Notes

- `bank.db` is created automatically on first run — do not commit it to version control.
- The `SECRET_KEY` in `app.py` is for local development only. Set it via an environment variable in any shared or production environment.
- Debug mode is enabled for local development. Set `debug=False` for any production deployment.
