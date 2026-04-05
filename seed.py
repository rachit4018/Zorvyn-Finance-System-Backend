"""
Seed script — populates the database with 3 demo users and sample transactions.

Users created:
  admin    / Admin1234    (role: admin)
  analyst  / Analyst1234  (role: analyst)
  viewer   / Viewer1234   (role: viewer)

Run:
    python seed.py
"""

from datetime import date
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionType
from app.services.auth import hash_password

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Skip seed if data already exists
    if db.query(User).count() > 0:
        print("Database already seeded. Skipping.")
        raise SystemExit(0)

    # --- Users ---
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("Admin1234"),
        role=UserRole.admin,
    )
    analyst = User(
        username="analyst",
        email="analyst@example.com",
        hashed_password=hash_password("Analyst1234"),
        role=UserRole.analyst,
    )
    viewer = User(
        username="viewer",
        email="viewer@example.com",
        hashed_password=hash_password("Viewer1234"),
        role=UserRole.viewer,
    )
    db.add_all([admin, analyst, viewer])
    db.commit()
    db.refresh(admin)
    db.refresh(viewer)

    # --- Transactions (assigned to admin) ---
    transactions = [
        # January
        Transaction(amount=6500.00, type=TransactionType.income,  category="Salary",      date=date(2024, 1, 1),  notes="Monthly salary",          user_id=admin.id),
        Transaction(amount=1200.00, type=TransactionType.expense, category="Rent",         date=date(2024, 1, 3),  notes="Apartment rent",          user_id=admin.id),
        Transaction(amount=320.50,  type=TransactionType.expense, category="Groceries",    date=date(2024, 1, 10), notes="Weekly grocery run",       user_id=admin.id),
        Transaction(amount=85.00,   type=TransactionType.expense, category="Transport",    date=date(2024, 1, 15), notes="Monthly transit pass",     user_id=admin.id),
        Transaction(amount=200.00,  type=TransactionType.income,  category="Freelance",    date=date(2024, 1, 20), notes="Logo design project",      user_id=admin.id),
        Transaction(amount=59.99,   type=TransactionType.expense, category="Subscriptions",date=date(2024, 1, 22), notes="Streaming + cloud storage",user_id=admin.id),
        # February
        Transaction(amount=6500.00, type=TransactionType.income,  category="Salary",      date=date(2024, 2, 1),  notes="Monthly salary",           user_id=admin.id),
        Transaction(amount=1200.00, type=TransactionType.expense, category="Rent",         date=date(2024, 2, 3),  notes="Apartment rent",           user_id=admin.id),
        Transaction(amount=290.00,  type=TransactionType.expense, category="Groceries",    date=date(2024, 2, 9),  notes="Grocery run",              user_id=admin.id),
        Transaction(amount=450.00,  type=TransactionType.expense, category="Healthcare",   date=date(2024, 2, 14), notes="Dental checkup",           user_id=admin.id),
        Transaction(amount=750.00,  type=TransactionType.income,  category="Freelance",    date=date(2024, 2, 18), notes="Website redesign",         user_id=admin.id),
        # March
        Transaction(amount=6500.00, type=TransactionType.income,  category="Salary",      date=date(2024, 3, 1),  notes="Monthly salary",           user_id=admin.id),
        Transaction(amount=1200.00, type=TransactionType.expense, category="Rent",         date=date(2024, 3, 3),  notes="Apartment rent",           user_id=admin.id),
        Transaction(amount=310.75,  type=TransactionType.expense, category="Groceries",    date=date(2024, 3, 8),  notes="Grocery run",              user_id=admin.id),
        Transaction(amount=120.00,  type=TransactionType.expense, category="Entertainment",date=date(2024, 3, 16), notes="Concert tickets",          user_id=admin.id),
        Transaction(amount=85.00,   type=TransactionType.expense, category="Transport",    date=date(2024, 3, 20), notes="Monthly transit pass",     user_id=admin.id),
        Transaction(amount=500.00,  type=TransactionType.income,  category="Bonus",        date=date(2024, 3, 28), notes="Q1 performance bonus",     user_id=admin.id),
    ]

    # A couple of transactions for the viewer account
    viewer_transactions = [
        Transaction(amount=3200.00, type=TransactionType.income,  category="Salary",   date=date(2024, 3, 1),  notes="Monthly salary", user_id=viewer.id),
        Transaction(amount=900.00,  type=TransactionType.expense, category="Rent",      date=date(2024, 3, 3),  notes="Room rent",      user_id=viewer.id),
        Transaction(amount=150.00,  type=TransactionType.expense, category="Groceries", date=date(2024, 3, 12), notes="Groceries",      user_id=viewer.id),
    ]

    db.add_all(transactions + viewer_transactions)
    db.commit()

    print("✅ Seed complete.")
    print("   admin    / Admin1234    (admin)")
    print("   analyst  / Analyst1234  (analyst)")
    print("   viewer   / Viewer1234   (viewer)")

finally:
    db.close()
