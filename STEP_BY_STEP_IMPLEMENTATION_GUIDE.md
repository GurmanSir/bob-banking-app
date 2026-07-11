# STEP-BY-STEP IMPLEMENTATION GUIDE — Banking Web Application

> **Reference:** [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md)
> **Document Type:** Plain-English Implementation Instructions
> **No code is included — this guide describes logic and steps only.**

---

## 1. Environment Setup

### 1.1 Prerequisites

Before starting, confirm the following tools are available on your machine:

- **Python 3.9 or higher** — the runtime for the Flask backend.
- **pip** — Python's package installer, bundled with Python.
- A terminal (PowerShell, bash, or similar).
- A code editor (VS Code recommended).

Verify by running `python --version` and `pip --version` in your terminal. Both should return version numbers without errors.

---

### 1.2 Create the Project Folder Structure

Manually create the top-level directory layout described in the plan before writing any code:

```
Banking-Application/
├── FRONTEND/
│   ├── templates/
│   └── static/
└── BACKEND/
    ├── routes/
    ├── controllers/
    ├── services/
    └── models/
```

Every folder can start empty. The goal of this step is simply to establish the physical separation between frontend and backend before any files are added.

---

### 1.3 Create and Activate a Virtual Environment

Navigate into the `BACKEND/` folder in your terminal and create a Python virtual environment there. A virtual environment isolates the project's dependencies from the rest of your system — any packages installed inside it do not affect other projects.

- On Windows, activate the environment using the activation script inside the `Scripts/` folder.
- On macOS/Linux, activate it using the `bin/activate` script.

Once activated, your terminal prompt will show the environment name, confirming that subsequent `pip` commands will install into the project — not globally.

---

### 1.4 Install Dependencies

With the virtual environment active, install the following packages using `pip`:

| Package | Purpose |
|---|---|
| `flask` | Core web framework — routing, templating, sessions |
| `werkzeug` | Bundled with Flask; provides password hashing utilities |

After installation, create a `requirements.txt` file inside `BACKEND/` by running `pip freeze > requirements.txt`. This file records every installed package and its version so the environment can be reproduced exactly on any other machine.

---

### 1.5 Verify Flask is Working

Create a minimal `app.py` inside `BACKEND/` that:

1. Imports Flask and creates an application instance.
2. Defines a single test route that returns a plain "Hello, Banking App" message.
3. Starts the development server when the file is run directly.

Run the file and open `http://127.0.0.1:5000` in a browser. If you see the message, the environment is confirmed working. Delete or comment out the test route before proceeding.

---

## 2. Backend Implementation

### 2.1 Configure the Flask Application (`app.py`)

The `app.py` file is the single entry point that ties the whole backend together. Its responsibilities are:

- Create the Flask app instance and set a `SECRET_KEY` (a random string used to sign session cookies — keep this value out of version control in a real project).
- Tell Flask where to find templates and static files. Since the templates live in `FRONTEND/templates/` rather than the default location, the template folder path must be set explicitly when creating the app instance.
- Import and register all route blueprints (auth and account) so Flask knows about them.
- When run directly, start the development server with debug mode enabled for helpful error pages.

---

### 2.2 Database Initialisation (`models/db.py`)

Before any feature is built, the database layer must be in place because every other layer depends on it.

The `db.py` file should provide two things:

1. **A connection helper** — a function that opens a connection to `bank.db` (located inside `BACKEND/`), configures it to return rows as dictionary-like objects (so columns can be accessed by name rather than by index), and returns the connection to the caller. Every function that needs the database calls this helper.

2. **An initialisation function** — a function that creates all required tables if they do not already exist, then seeds one demo customer and account record. This function is called once when `app.py` starts up. If the database file already exists with the tables populated, the function does nothing (use `CREATE TABLE IF NOT EXISTS` logic).

The three tables to create are: `customers` (identity + credentials), `accounts` (balance linked to a customer), and `transactions` (a log of every deposit and withdrawal).

---

### 2.3 Routes (`routes/`)

Routes are the URL definitions — they map an HTTP method + path combination to a controller function. Keep routes thin: they should contain no logic beyond calling the appropriate controller.

**`auth_routes.py`** registers a Flask Blueprint named `auth` and defines:

| Method | Path | Action |
|---|---|---|
| GET | `/` or `/login` | Display the login page |
| POST | `/login` | Submit login credentials |
| GET | `/logout` | End the session and redirect to login |

**`account_routes.py`** registers a Flask Blueprint named `account` and defines:

| Method | Path | Action |
|---|---|---|
| GET | `/dashboard` | Display the dashboard |
| GET | `/deposit` | Display the deposit form |
| POST | `/deposit` | Submit the deposit amount |
| GET | `/withdraw` | Display the withdraw form |
| POST | `/withdraw` | Submit the withdrawal amount |

Register both blueprints in `app.py` using `app.register_blueprint(...)`.

---

### 2.4 Controllers (`controllers/`)

Controllers sit between routes and services. Each controller function:

1. Reads data from the incoming HTTP request (form fields, session values).
2. Performs basic input validation (is the field present? is the value the right type?).
3. Calls the appropriate service function with the validated data.
4. Decides what response to return — either render a template or issue a redirect.

**`auth_controller.py`** handles two actions:

- **Show login page** — simply render `login.html`.
- **Process login** — read the username and password from the form, call the auth service to verify them, store the customer's ID in the Flask session on success, redirect to the dashboard; re-render the login page with an error message on failure.
- **Logout** — clear the session and redirect to the login page.

**`account_controller.py`** handles four actions:

- **Show dashboard** — check the session, fetch the balance from the account service, render `dashboard.html` passing the balance value.
- **Show deposit form** — check the session, render `deposit.html`.
- **Process deposit** — read the amount from the form, call the transaction service, redirect back to the dashboard with a success message.
- **Show withdraw form** and **Process withdrawal** — same pattern as deposit.

---

### 2.5 Services (`services/`)

Services contain the business logic. They have no knowledge of HTTP — they receive plain Python values and return plain Python values.

**`auth_service.py`** provides:

- **`verify_credentials(username, password)`** — query the `customers` table for the given username, then use Werkzeug's `check_password_hash` function to compare the submitted password against the stored hash. Return the customer record if the check passes, or `None` if it fails. Never compare passwords as plain text.

- **`hash_password(plain_text)`** — used during database seeding to store the demo password as a hash. Call Werkzeug's `generate_password_hash` function.

**`account_service.py`** provides:

- **`get_balance(customer_id)`** — query the `accounts` table and return the current balance for the given customer.
- **`deposit(customer_id, amount)`** — add the given amount to the current balance. Write the updated balance back to the `accounts` table. Insert a row into the `transactions` table recording the type as "deposit", the amount, and the current timestamp.
- **`withdraw(customer_id, amount)`** — first read the current balance. If the amount is greater than the balance, raise an error (or return a failure indicator — do not silently ignore it). Otherwise, subtract the amount from the balance, update the `accounts` table, and insert a "withdrawal" transaction record.

---

### 2.6 Session Management

Flask sessions work as signed cookies stored on the client. The session behaves like a Python dictionary.

- **On login success:** store the customer's database ID in the session (`session['customer_id'] = ...`).
- **On logout:** call `session.clear()` to remove all session data.
- **On every protected route:** check that `'customer_id'` exists in the session at the start of the controller function. If it does not, redirect immediately to the login page. This check should be centralised — write a single helper function or decorator (e.g. `login_required`) and apply it to every protected controller, rather than repeating the check in each one.

---

### 2.7 Error Handling

Handle the two most common error scenarios gracefully:

- **Invalid login** — do not expose whether the username or the password was wrong (this would help an attacker enumerate valid usernames). Instead, show a single generic message such as "Invalid username or password."
- **Insufficient funds** — if a withdrawal is attempted for more than the available balance, return the withdraw form again with a clear error message telling the customer the maximum they can withdraw. Never process the transaction partially.

For unexpected errors (database errors, unhandled exceptions), Flask's default error pages are sufficient for a local development application.

---

## 3. Frontend Implementation

All HTML templates live in `FRONTEND/templates/`. Flask must be told to look there. All pages share a common visual structure — consider using a Jinja2 base template that the other pages extend, to avoid repeating the Bootstrap `<head>` and navigation HTML on every page.

### 3.1 Bootstrap Layout Strategy

Load Bootstrap from its CDN link inside the `<head>` of your base template. This avoids any npm/build-tool setup. Every page then inherits:

- A responsive grid system for centred card layouts.
- Pre-styled buttons, form inputs, and alert boxes.
- A consistent font and colour scheme.

Use Bootstrap's `container`, `row`, `col`, and `card` classes to centre content on the page. Use `alert alert-success` and `alert alert-danger` classes to render feedback messages passed from the Flask controller.

---

### 3.2 Login Page (`login.html`)

**Purpose:** Collect the customer's credentials and submit them to the backend.

The page should contain:

- A centred card with the application name as a heading.
- A form with two fields: **Username** (text input) and **Password** (password input).
- A submit button labelled "Login."
- A conditional error message area that only renders when the controller passes an error string to the template.

The form's `action` attribute should point to the `/login` POST route. No JavaScript is needed.

---

### 3.3 Dashboard Page (`dashboard.html`)

**Purpose:** Show the customer's account summary and navigation options after a successful login.

The page should contain:

- A welcome heading that includes the customer's name (passed from the controller via the template context).
- A prominent display of the current account balance, formatted as a currency value.
- Two buttons linking to the Deposit and Withdraw pages.
- A Logout link.
- A conditional success message area (used to confirm a completed deposit or withdrawal when redirecting back from those pages).

---

### 3.4 Deposit Form (`deposit.html`)

**Purpose:** Let the customer enter an amount to add to their balance.

The page should contain:

- A heading such as "Deposit Funds."
- A form with a single numeric input for the amount.
- A submit button labelled "Deposit."
- A "Back to Dashboard" link.
- A conditional error message area for validation failures (e.g. amount was zero or negative).

The form's `action` attribute should point to the `/deposit` POST route.

---

### 3.5 Withdraw Form (`withdraw.html`)

**Purpose:** Let the customer enter an amount to deduct from their balance.

The structure is identical to the deposit form, with the following differences:

- Heading reads "Withdraw Funds."
- The submit button is labelled "Withdraw."
- The error message should include the case where the withdrawal amount exceeds the available balance.
- Optionally, display the current balance on this page so the customer knows their limit before submitting.

---

### 3.6 Passing Data from Flask to Templates

Flask uses Jinja2 templating. When a controller calls `render_template('dashboard.html', balance=1200.00, name='Alice')`, the template can access those values as `{{ balance }}` and `{{ name }}`. Use this mechanism to:

- Pass the balance from the account service to the dashboard and withdraw templates.
- Pass error/success messages from controllers to all form templates.
- Pass the customer's name to the dashboard greeting.

Conditionally show message blocks using `{% if message %}...{% endif %}` so the block is absent when there is nothing to show.

---

## 4. Integration Steps

### 4.1 Tell Flask Where the Templates and Static Files Live

By default Flask looks for templates in a `templates/` folder next to `app.py`. Because the templates are in `FRONTEND/templates/`, pass the correct path as the `template_folder` argument when constructing the Flask app instance. Similarly, pass the `static_folder` argument pointing to `FRONTEND/static/`. Do this once in `app.py` — all `render_template` calls will then resolve correctly.

---

### 4.2 Connect Flask to SQLite

The `db.py` connection helper is the only place in the codebase that opens a database connection. Services import and call this helper when they need to run a query. The flow is:

1. Service calls `get_connection()` from `db.py`.
2. `get_connection()` uses Python's built-in `sqlite3` module to open `bank.db`.
3. The connection is used to run a query and fetch results.
4. The connection is closed after each operation.

Do not share a single long-lived connection across requests — open, use, and close within each function call to keep things simple and avoid locking issues with SQLite.

---

### 4.3 Wire Routes to Controllers to Services

The chain for every request looks like this:

```
Browser form submit
  → Flask route (Blueprint)
      → Controller function
          → Service function
              → db.py query
                  → SQLite
```

Verify this chain works for each feature by testing it end-to-end in the browser before moving on to the next feature.

---

### 4.4 Register Blueprints and Initialise the Database on Startup

In `app.py`, after creating the Flask instance:

1. Import both Blueprints and call `app.register_blueprint(auth_bp)` and `app.register_blueprint(account_bp)`.
2. Import the `init_db()` function from `db.py` and call it once. Use Flask's `with app.app_context():` block to ensure the database context is available during initialisation.

This ensures the database tables exist and the demo data is seeded every time the app starts, without failing if the data is already there.

---

## 5. Validation Rules

### 5.1 Login Validation

Apply these checks when processing a login POST request, in the controller:

| Check | What to do if it fails |
|---|---|
| Username field is not empty | Re-render login form with a generic error |
| Password field is not empty | Re-render login form with a generic error |
| Username exists in the database | Re-render login form with "Invalid username or password" |
| Password hash matches the stored hash | Re-render login form with "Invalid username or password" |

Always use the same generic error message regardless of which check failed. This prevents username enumeration.

---

### 5.2 Balance Validation

Apply these checks in `account_service.py` before any balance-modifying operation:

| Check | What to do if it fails |
|---|---|
| Account exists for the customer | Raise an exception — this should never happen in a seeded app |
| Balance is a valid numeric value | Treat as a data integrity error |

The balance is always read fresh from the database before a transaction — never rely on a cached or session-stored balance value.

---

### 5.3 Deposit Checks

Apply these checks in the deposit controller before calling the service:

| Check | What to do if it fails |
|---|---|
| Amount field is not empty | Re-render deposit form with "Please enter an amount" |
| Amount is a valid number | Re-render deposit form with "Amount must be a number" |
| Amount is greater than zero | Re-render deposit form with "Amount must be greater than zero" |

If all checks pass, call the deposit service. On success, redirect to the dashboard with a success message.

---

### 5.4 Withdrawal Checks

Apply these checks in the withdraw controller — the first three are identical to deposit, with one additional rule:

| Check | What to do if it fails |
|---|---|
| Amount field is not empty | Re-render withdraw form with "Please enter an amount" |
| Amount is a valid number | Re-render withdraw form with "Amount must be a number" |
| Amount is greater than zero | Re-render withdraw form with "Amount must be greater than zero" |
| Amount does not exceed current balance | Re-render withdraw form with "Insufficient funds. Your balance is £X." |

Read the current balance from the database before applying the final check — use the service's `get_balance` function for this.

---

## 6. Testing

### 6.1 Unit Tests

Unit tests verify individual service functions in isolation, without a running Flask server or a real database. Use Python's built-in `unittest` module or `pytest`.

**What to unit-test:**

| Function | Test cases |
|---|---|
| `verify_credentials` | Valid credentials return a customer record; wrong password returns None; unknown username returns None |
| `deposit` | Balance increases by the deposited amount; a transaction record is created |
| `withdraw` | Balance decreases correctly; a transaction record is created; withdrawing more than the balance is rejected |
| `get_balance` | Returns the correct numeric balance for a known account |

For unit tests, use an in-memory SQLite database (`:memory:`) rather than the real `bank.db` file, so tests are fast, isolated, and leave no side effects.

---

### 6.2 Integration Tests

Integration tests verify that routes, controllers, services, and the database work together correctly. Use Flask's built-in test client (`app.test_client()`).

**What to integration-test:**

| Scenario | Expected result |
|---|---|
| GET `/login` | Returns 200 and the login page HTML |
| POST `/login` with valid credentials | Redirects to `/dashboard` |
| POST `/login` with wrong password | Returns 200 with the error message on the login page |
| GET `/dashboard` without a session | Redirects to `/login` |
| GET `/dashboard` with a valid session | Returns 200 and shows the balance |
| POST `/deposit` with a valid amount | Redirects to dashboard; balance is higher |
| POST `/deposit` with amount = 0 | Returns the deposit form with a validation error |
| POST `/withdraw` with amount > balance | Returns the withdraw form with "Insufficient funds" |
| GET `/logout` | Clears the session and redirects to login |

---

### 6.3 Manual Testing Checklist

Walk through the application in a real browser after all automated tests pass:

- [ ] Navigate to the root URL — login page is displayed.
- [ ] Submit the login form with an empty username — error message appears.
- [ ] Submit the login form with wrong credentials — generic error appears.
- [ ] Submit the login form with correct credentials — dashboard is shown with the correct balance.
- [ ] Click Deposit — deposit form is shown.
- [ ] Submit a deposit of £500 — redirected to dashboard; balance has increased by £500.
- [ ] Submit a deposit of £0 — error message shown, balance unchanged.
- [ ] Submit a deposit of a non-numeric value — error message shown.
- [ ] Click Withdraw — withdraw form is shown with current balance.
- [ ] Submit a withdrawal for more than the available balance — error message shown.
- [ ] Submit a valid withdrawal — redirected to dashboard; balance has decreased correctly.
- [ ] Click Logout — session cleared, login page shown.
- [ ] Attempt to navigate to `/dashboard` directly after logout — redirected to login.

---

## 7. Deployment

### 7.1 Run Locally

To start the application on your local machine:

1. Open a terminal and navigate to the `BACKEND/` folder.
2. Activate the virtual environment.
3. Run `python app.py`.
4. Flask will print the local URL — typically `http://127.0.0.1:5000`.
5. Open that URL in a browser.

The database file (`bank.db`) is created automatically on first run if it does not exist. The demo customer credentials are seeded at the same time.

To stop the server, press `Ctrl + C` in the terminal.

---

### 7.2 Production Considerations

The Flask development server (`app.run()`) is not suitable for production. For a real deployment, consider the following:

| Concern | Recommendation |
|---|---|
| WSGI server | Replace the dev server with Gunicorn (Linux/macOS) or Waitress (Windows) |
| Secret key | Read `SECRET_KEY` from an environment variable — never hard-code it |
| Database | Migrate from SQLite to PostgreSQL or MySQL for multi-user or high-volume use |
| HTTPS | Place the application behind a reverse proxy (nginx, Caddy) that handles TLS |
| Debug mode | Set `debug=False` in production — debug mode exposes an interactive console |
| Password policy | Enforce minimum password length and complexity at registration time |
| Session timeout | Configure Flask sessions to expire after a period of inactivity |

For this lab, none of the production considerations need to be implemented — they are noted here as a reference for anyone extending the application beyond the demo environment.

---

*End of Step-by-Step Implementation Guide*
