# BillNest

**BillNest** is a full‑stack web application for tracking, splitting, and understanding shared *and* personal recurring expenses. It is designed for small groups (housemates, couples, travel groups) as well as individuals who want better visibility into where their money is going.

This project is intentionally built as a **realistic software engineering system**, focusing on clean architecture, clear domain modelling, and non‑trivial business logic rather than flashy UI or over‑engineered features.

---

## 🚀 What Problem Does BillNest Solve?

Managing shared expenses is often messy:

* One person pays upfront for everything
* Only some people are involved in certain costs
* Splits are uneven
* Subscriptions renew quietly and go unnoticed

BillNest solves this by answering three simple but powerful questions:

1. **Who paid for what?**
2. **Who owes whom, and how much?**
3. **Which recurring costs are quietly draining money over time?**

The system acts as a **tracking and accountability tool**, not a bank. No payments are processed — BillNest simply records obligations and confirmations between users.

---

## 🧠 Key Design Principles

* **Backend‑first design** – the backend is the source of truth
* **Derived balances** – no stored totals that can become inconsistent
* **Explicit domain modelling** – expenses, splits, subscriptions, settlements
* **Tight scope** – finishable, maintainable, and realistic
* **Industry‑standard tooling** – Flask, SQLAlchemy, Alembic, React

---

## 🧱 High‑Level Architecture

```
React Frontend (SPA)
        ↓ REST (JSON)
Flask API (JWT Auth)
        ↓ ORM
SQLite Database (Relational Model)
```

### Frontend

* React (Vite)
* Single Page Application
* Communicates exclusively via REST APIs
* No direct database access

### Backend

* Flask REST API
* Stateless architecture
* JWT‑based authentication
* Business logic separated from HTTP routes

### Database

* SQLite (development)
* Relational schema
* Versioned using migrations (Alembic)
* Designed to be PostgreSQL‑ready

---

## 🧩 Core Domain Model

BillNest is built around a clear financial domain model:

* **User** – an individual account
* **Group** – a shared expense context (e.g. *Malta Trip*)
* **Membership** – links users to groups with roles
* **Expense** – a single purchase paid by one user
* **ExpenseSplit** – defines who owes what for an expense
* **Subscription** – a recurring cost (personal or shared)
* **GeneratedExpense** – an expense created automatically from a subscription
* **Settlement** – a trust‑based confirmation that money was paid outside the app

Balances are **never stored**. They are always derived from expenses and splits.

---

## 🔐 Authentication & Security

* JWT‑based authentication
* Passwords are **hashed**, never stored in plain text
* Protected routes require valid tokens
* Role‑based access control inside groups (admin vs member)

---

## 📡 REST API Overview

The API follows REST principles:

* Resource‑based URLs
* JSON request/response
* Stateless requests

### Core Capabilities

* User registration and login
* Group creation and membership management
* Expense creation with **custom uneven splits**
* Derived group balances
* Subscription tracking and automatic expense generation
* Settlement confirmations (no money handling)

Example (create expense):

```json
{
  "description": "Groceries",
  "total_amount": 50,
  "splits": [
    { "user_id": 1, "amount_owed": 25 },
    { "user_id": 2, "amount_owed": 10 },
    { "user_id": 3, "amount_owed": 15 }
  ]
}
```

Invariant enforced by backend:

```
SUM(amount_owed) == total_amount
```

---

## 🗄️ Database & Migrations

The database schema is implemented using **SQLAlchemy** and versioned using **Flask‑Migrate / Alembic**.

* Each table is defined as a Python model
* Schema changes are tracked via migrations
* Databases can be rebuilt or upgraded safely

This allows the system to evolve without breaking existing data — a critical real‑world requirement.

---

## 🛠️ Project Structure

```
backend/
  app/
    models/        # SQLAlchemy models (schema)
    routes/        # HTTP endpoints
    services/      # Business logic
    schemas/       # Request/response validation
    utils/         # Helpers
  migrations/      # Alembic migration history
  run.py           # App entry point

frontend/
  src/             # React application
```

This separation mirrors production Flask applications and keeps concerns isolated.

---

## 🧪 Why This Project Matters (CV Context)

This project demonstrates:

* Full‑stack system design
* Relational data modelling
* REST API design
* Authentication and security
* Non‑trivial business logic
* Schema migrations and versioning
* Realistic scoping and architectural decisions

It is intentionally built to be **understandable, defensible, and extensible** — not just a demo app.

---

## 📈 Current Status

* Backend architecture established
* Database schema implemented
* Migrations working
* Models loading correctly

Next steps:

* Add SQLAlchemy relationships
* Implement core service logic
* Build frontend views mapped to API

---

## 📌 Notes

BillNest does **not**:

* Process payments
* Integrate with banks
* Attempt to be a financial authority

It is a transparency and accountability tool — by design.

---

## 👤 Author

**Joseph Trent**
Computer Science Student
Full‑stack software engineering project
