# Finance Tracking System

A clean, role-based finance tracking backend built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

---

## Features

- JWT authentication (register, login, token-based access)
- Role-based access control: `viewer`, `analyst`, `admin`
- Full CRUD on financial transactions (income & expenses)
- Filtering by type, category, and date range
- Pagination on transaction listings
- Financial summaries: total income/expenses, balance, category breakdowns, monthly totals
- Admin user management
- Input validation with Pydantic v2
- Auto-generated interactive API docs at `/docs`

---

## Project Structure

```
finance_system/
├── app/
│   ├── config.py           # App settings (loaded from .env)
│   ├── database.py         # SQLAlchemy engine, session, Base
│   ├── dependencies.py     # JWT decoding + RBAC dependency guards
│   ├── main.py             # FastAPI app entry point
│   ├── models/
│   │   ├── user.py         # User model + UserRole enum
│   │   └── transaction.py  # Transaction model + TransactionType enum
│   ├── schemas/
│   │   ├── user.py         # Request/response schemas for users
│   │   ├── transaction.py  # Request/response schemas for transactions
│   │   └── summary.py      # Financial summary response schemas
│   ├── routers/
│   │   ├── auth.py         # POST /auth/register, POST /auth/login
│   │   ├── transactions.py # GET/POST/PATCH/DELETE /transactions
│   │   ├── summary.py      # GET /summary
│   │   └── users.py        # Admin-only user management
│   └── services/
│       ├── auth.py         # Password hashing, JWT creation, authentication
│       ├── transactions.py # CRUD logic with role-scoped queries
│       └── summary.py      # Financial aggregation logic
├── seed.py                 # Populates DB with demo users and transactions
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd finance_system
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env to set a strong SECRET_KEY before deploying
```

### 3. Seed the database

```bash
python seed.py
```

This creates:

| Username | Password     | Role     |
|----------|--------------|----------|
| admin    | Admin1234    | admin    |
| analyst  | Analyst1234  | analyst  |
| viewer   | Viewer1234   | viewer   |

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

## API Reference

### Auth

| Method | Endpoint         | Description              | Auth Required |
|--------|------------------|--------------------------|---------------|
| POST   | /auth/register   | Register a new user      | No            |
| POST   | /auth/login      | Login and receive a JWT  | No            |

**Login example:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=admin&password=Admin1234" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

Returns:
```json
{ "access_token": "<token>", "token_type": "bearer" }
```

Use the token as a `Bearer` header on all subsequent requests:
```
Authorization: Bearer <token>
```

---

### Transactions

| Method | Endpoint                  | Description                    | Minimum Role |
|--------|---------------------------|--------------------------------|--------------|
| GET    | /transactions             | List transactions (paginated)  | viewer       |
| GET    | /transactions/{id}        | Get a single transaction       | viewer       |
| POST   | /transactions             | Create a transaction           | admin        |
| PATCH  | /transactions/{id}        | Update a transaction           | admin        |
| DELETE | /transactions/{id}        | Delete a transaction           | admin        |

**Filtering (query params):**
- `type` — `income` or `expense`
- `category` — partial match, case-insensitive
- `date_from` / `date_to` — `YYYY-MM-DD`
- `page` / `page_size` — default `1` / `20`, max page_size `100`

**Create transaction body:**
```json
{
  "amount": 1500.00,
  "type": "income",
  "category": "Freelance",
  "date": "2024-03-15",
  "notes": "Website project"
}
```

---

### Summary

| Method | Endpoint  | Description                  | Minimum Role |
|--------|-----------|------------------------------|--------------|
| GET    | /summary  | Full financial summary        | viewer       |

**Response includes:**
- `total_income`, `total_expenses`, `balance`
- `income_by_category` and `expense_by_category` (sorted by total)
- `monthly_totals` (net per month)
- `recent_transactions` (last 5)

> Viewers see only their own data. Analysts and Admins see aggregated data across all users.

---

### Users (Admin only)

| Method | Endpoint        | Description            | Minimum Role |
|--------|-----------------|------------------------|--------------|
| GET    | /users/me       | Current user profile   | any          |
| GET    | /users          | List all users         | admin        |
| GET    | /users/{id}     | Get a user by ID       | admin        |
| PATCH  | /users/{id}     | Update role/status     | admin        |
| DELETE | /users/{id}     | Delete a user          | admin        |

---

## Role-Based Access Control

| Capability                        | Viewer | Analyst | Admin |
|-----------------------------------|--------|---------|-------|
| View own transactions             | ✅     | ✅      | ✅    |
| View all transactions             | ❌     | ✅      | ✅    |
| Filter & detailed analytics       | ❌     | ✅      | ✅    |
| Create / update / delete records  | ❌     | ❌      | ✅    |
| Manage users                      | ❌     | ❌      | ✅    |

Roles are enforced at the **service layer** — not just the route level — so scoped queries prevent data leakage regardless of how a route is called.

---

## Validation & Error Handling

- `amount` must be a positive number; stored rounded to 2 decimal places
- `category` cannot be blank
- `password` must be at least 8 characters
- `username` must be 3+ chars, alphanumeric (hyphens and underscores allowed)
- Duplicate usernames and emails return `400 Bad Request`
- Missing or expired JWT returns `401 Unauthorized`
- Insufficient role returns `403 Forbidden`
- Non-existent resources return `404 Not Found`
- Unexpected server errors return a safe `500` without leaking internals

---

## Assumptions

- SQLite is used as the default database for portability. To switch to PostgreSQL, update `DATABASE_URL` in `.env` and remove the `check_same_thread` argument in `database.py`.
- Admins can only create transactions on behalf of themselves (their own `user_id` is used). A more advanced system could allow admins to assign transactions to any user.
- The `/summary` endpoint computes aggregates in Python. For very large datasets, this would be moved to SQL-level `GROUP BY` queries.
- Token expiry is 24 hours by default. This can be changed via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`.

---

## Tech Stack

| Layer        | Technology                    |
|--------------|-------------------------------|
| Framework    | FastAPI 0.115                 |
| ORM          | SQLAlchemy 2.0                |
| Database     | SQLite (default)              |
| Validation   | Pydantic v2                   |
| Auth         | JWT via python-jose + bcrypt  |
| Server       | Uvicorn                       |
