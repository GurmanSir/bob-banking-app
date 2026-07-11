# IMPLEMENTATION PLAN — Banking Web Application

> **Document Type:** High-Level Planning Document
> **Technology Stack:** HTML + Bootstrap · Python Flask · SQLite
> **Status:** Planning

---

## 1. Solution Overview

### Objective

Build a simple, functional banking web application that allows customers to log in, view their account balance, and perform basic financial transactions (deposit and withdrawal) through a clean browser-based interface.

### Scope

| In Scope | Out of Scope |
|---|---|
| Customer login and session management | Multi-user roles (admin, teller) |
| Balance enquiry | Inter-account transfers |
| Deposit funds | Scheduled / recurring payments |
| Withdraw funds | External payment gateway integration |
| Logout | Email / SMS notifications |
| Lightweight SQLite persistence | Production-grade database (PostgreSQL, MySQL) |

### Users

- **Customer** — a single authenticated user role. Customers log in with credentials, manage their own account, and log out when done.

### Functional Requirements

1. A customer can log in using a username and password.
2. On successful login the customer is taken to a personal dashboard.
3. The dashboard displays the current account balance.
4. A customer can deposit a positive monetary amount; the balance updates immediately.
5. A customer can withdraw a monetary amount up to the available balance; the balance updates immediately.
6. A customer can log out, which terminates their session.
7. Unauthenticated requests to protected pages redirect to the login page.

### Non-Functional Requirements

| Concern | Expectation |
|---|---|
| Security | Passwords stored hashed; sessions expire on logout |
| Usability | Responsive Bootstrap UI that works on desktop and mobile |
| Reliability | All transactions reflected immediately; no silent failures |
| Maintainability | Clear separation of frontend, backend and database layers |
| Performance | Sub-second response for all operations on a local SQLite store |

### Assumptions

- A single customer account is pre-seeded in the database for demo purposes.
- The application runs locally; no public hosting or TLS configuration is required.
- SQLite is sufficient for the data volume and concurrency of this application.
- Bootstrap is loaded via CDN — no separate build step for CSS/JS.
- Session management is handled entirely server-side by Flask.

---

## 2. High-Level Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        BROWSER                          │
│                                                         │
│   ┌──────────┐  ┌───────────┐  ┌──────────────────┐   │
│   │  login   │  │ dashboard │  │ deposit/withdraw │   │
│   │  .html   │  │  .html    │  │     .html        │   │
│   └────┬─────┘  └─────┬─────┘  └────────┬─────────┘   │
│        │ Bootstrap + HTML forms          │              │
└────────┼────────────────────────────────┼──────────────┘
         │  HTTP POST / GET (form submit)  │
         ▼                                ▼
┌─────────────────────────────────────────────────────────┐
│                   PYTHON FLASK (BACKEND)                 │
│                                                         │
│   ┌────────────┐  ┌────────────┐  ┌─────────────────┐  │
│   │   Auth     │  │  Account   │  │   Transaction   │  │
│   │  Module    │  │  Module    │  │    Module       │  │
│   └────────────┘  └────────────┘  └─────────────────┘  │
│                                                         │
│   Session Management · Input Validation · Routing       │
└──────────────────────────┬──────────────────────────────┘
                           │ SQL queries via Python
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   SQLITE DATABASE                        │
│              (bank.db — inside BACKEND/)                 │
│                                                         │
│   customers table · accounts table · transactions table  │
└─────────────────────────────────────────────────────────┘
```

### Frontend → Backend → Database Interaction

| Layer | Technology | Role |
|---|---|---|
| Frontend | HTML + Bootstrap | Renders pages, captures user input, submits forms |
| Backend | Python Flask | Processes requests, enforces business logic, manages sessions |
| Database | SQLite | Persists customer credentials, balances, and transactions |

### Request Lifecycle

1. **Browser** sends an HTTP request (form POST or page GET) to Flask.
2. **Flask router** matches the URL to the appropriate route handler.
3. **Route handler** validates the session; redirects to login if unauthenticated.
4. **Business logic** validates input, applies the operation (e.g. deposit), and updates the database.
5. **Flask** renders the appropriate HTML template with updated data and returns it to the browser.
6. **Browser** displays the updated page to the customer.

---

## 3. Component Design

### Frontend Responsibilities

- Provide HTML pages for: Login, Dashboard, Deposit, Withdraw.
- Use Bootstrap for a responsive, consistent visual layout.
- Submit user input to the backend via standard HTML form POST.
- Display server-rendered data (balance, success/error messages) returned by Flask templates (Jinja2).
- No client-side state management or JavaScript frameworks required.

### Backend Responsibilities

- Define and expose URL routes mapped to application features.
- Authenticate customers and create/destroy Flask sessions.
- Validate all incoming form data (field presence, data types, business rules).
- Execute account operations (balance read, deposit, withdraw) through a service layer.
- Return rendered HTML templates or redirect responses to the browser.
- Guard all protected routes so unauthenticated access is rejected.

### Database Responsibilities

- Persist customer login credentials (hashed passwords).
- Store current account balance per customer.
- Record a log of all transactions (type, amount, timestamp) for auditability.
- Provide the backend with a simple file-based store requiring no separate server process.

---

## 4. Folder Structure

```
Banking-Application/
│
├── FRONTEND/                     # All browser-facing assets
│   ├── templates/                # Jinja2 HTML templates served by Flask
│   │   ├── login.html            # Login page
│   │   ├── dashboard.html        # Account overview / balance page
│   │   ├── deposit.html          # Deposit funds form
│   │   └── withdraw.html         # Withdraw funds form
│   └── static/                   # Static files (CSS overrides, images)
│       └── style.css             # Optional custom styles
│
├── BACKEND/                      # All server-side application code
│   ├── app.py                    # Flask application entry point
│   ├── routes/                   # URL route definitions
│   │   ├── auth_routes.py        # Login / logout routes
│   │   └── account_routes.py     # Dashboard, deposit, withdraw routes
│   ├── controllers/              # Request handling & input validation
│   │   ├── auth_controller.py
│   │   └── account_controller.py
│   ├── services/                 # Business logic layer
│   │   ├── auth_service.py       # Credential verification, session handling
│   │   └── account_service.py    # Balance reads, deposit/withdraw logic
│   ├── models/                   # Database access layer
│   │   └── db.py                 # SQLite connection and query helpers
│   ├── bank.db                   # SQLite database file (auto-created on first run)
│   └── requirements.txt          # Python dependencies
│
├── IMPLEMENTATION_PLAN.md        # This document
└── README.md                     # Project overview and run instructions
```

### Folder Responsibility Summary

| Folder / File | Responsibility |
|---|---|
| `FRONTEND/templates/` | HTML views rendered and returned by Flask |
| `FRONTEND/static/` | CSS and static assets referenced by templates |
| `BACKEND/app.py` | Creates and configures the Flask application instance |
| `BACKEND/routes/` | Maps HTTP paths to controller functions |
| `BACKEND/controllers/` | Parses requests, validates input, calls services |
| `BACKEND/services/` | Encapsulates business logic independent of HTTP |
| `BACKEND/models/` | All direct database interaction isolated here |
| `BACKEND/bank.db` | SQLite data file — excluded from version control |

---

## 5. Module Breakdown

### Authentication Module

**Purpose:** Control access to the application.

| Concern | Description |
|---|---|
| Login | Accept username + password, verify against stored hash, create session |
| Session guard | Decorator / helper applied to all protected routes |
| Logout | Clear session data and redirect to login page |
| Password handling | Passwords hashed at rest; plain-text never stored |

### Dashboard Module

**Purpose:** Present the customer's current account state after login.

| Concern | Description |
|---|---|
| Balance display | Retrieve and render current balance for the logged-in customer |
| Navigation | Provide links to Deposit, Withdraw, and Logout actions |
| Session context | Identify the customer from the active session |

### Account Management Module

**Purpose:** Maintain accurate account data.

| Concern | Description |
|---|---|
| Balance read | Query the current balance for a given customer account |
| Balance write | Update balance following a successful deposit or withdrawal |
| Account lookup | Map a logged-in session to the correct account record |

### Transactions Module

**Purpose:** Process and record monetary operations.

| Concern | Description |
|---|---|
| Deposit | Validate a positive amount; add to balance; record transaction |
| Withdrawal | Validate amount is positive and ≤ current balance; deduct; record |
| Transaction log | Persist type, amount, and timestamp for every completed operation |
| Validation rules | Reject zero/negative amounts; reject withdrawals exceeding balance |

---

## 6. Implementation Roadmap

### Development Phases

#### Phase 1 — Project Setup & Foundation
> Establish the skeleton before writing any feature code.

- Initialise folder structure (`FRONTEND/`, `BACKEND/`)
- Create Python virtual environment and install Flask
- Create `app.py` with a basic Flask instance
- Set up the SQLite database connection helper in `models/db.py`
- Seed the database with one test customer and account record
- Verify the app starts and serves a placeholder page

**Dependencies:** None — this is the starting point.

---

#### Phase 2 — Authentication
> Gate access to the application.

- Implement login route, controller, and service
- Render `login.html` with Bootstrap form
- Validate credentials against the database
- Create and destroy Flask sessions
- Implement the session guard for protected routes
- Implement logout route

**Dependencies:** Phase 1 complete.

---

#### Phase 3 — Dashboard & Balance Display
> Deliver the first post-login experience.

- Implement dashboard route and controller
- Retrieve current balance from the account service
- Render `dashboard.html` with balance and navigation links
- Apply the session guard

**Dependencies:** Phase 2 complete.

---

#### Phase 4 — Deposit & Withdrawal Transactions
> Enable the core financial operations.

- Implement deposit route, controller, and service method
- Implement withdraw route, controller, and service method
- Render `deposit.html` and `withdraw.html` with Bootstrap forms
- Apply input validation (amount > 0; withdrawal ≤ balance)
- Update balance and record each transaction in the database
- Show success and error feedback messages in the UI

**Dependencies:** Phase 3 complete.

---

#### Phase 5 — Integration & Polish
> Connect all layers and prepare for demo.

- End-to-end walkthrough of all user flows
- Ensure all redirects, session expirations, and error paths behave correctly
- Apply consistent Bootstrap styling across all pages
- Write `README.md` with setup and run instructions

**Dependencies:** Phases 1–4 complete.

---

### Estimated Effort

| Phase | Effort |
|---|---|
| Phase 1 — Setup & Foundation | Small |
| Phase 2 — Authentication | Small–Medium |
| Phase 3 — Dashboard & Balance | Small |
| Phase 4 — Deposit & Withdrawal | Medium |
| Phase 5 — Integration & Polish | Small |

### Key Dependencies

```
Phase 1
   └── Phase 2 (Auth)
          └── Phase 3 (Dashboard)
                 └── Phase 4 (Transactions)
                        └── Phase 5 (Integration)
```

Each phase must be completed and verified before the next begins. The database layer (Phase 1) underpins every subsequent phase and must be stable before any feature work starts.

---

*End of Implementation Plan*
