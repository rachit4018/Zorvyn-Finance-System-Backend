from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.schemas.summary import FinancialSummary, CategoryBreakdown, MonthlyTotal


def _scoped_query(db: Session, user: User):
    q = db.query(Transaction)
    if user.role == UserRole.viewer:
        q = q.filter(Transaction.user_id == user.id)
    return q


def get_summary(db: Session, current_user: User) -> FinancialSummary:
    transactions = _scoped_query(db, current_user).all()

    total_income = 0.0
    total_expenses = 0.0
    income_cats: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
    expense_cats: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "count": 0})
    monthly: dict[tuple, dict] = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})

    for tx in transactions:
        year_month = (tx.date.year, tx.date.month)
        if tx.type == TransactionType.income:
            total_income += tx.amount
            income_cats[tx.category]["total"] += tx.amount
            income_cats[tx.category]["count"] += 1
            monthly[year_month]["income"] += tx.amount
        else:
            total_expenses += tx.amount
            expense_cats[tx.category]["total"] += tx.amount
            expense_cats[tx.category]["count"] += 1
            monthly[year_month]["expenses"] += tx.amount

    income_breakdown = [
        CategoryBreakdown(category=cat, total=round(vals["total"], 2), count=vals["count"])
        for cat, vals in sorted(income_cats.items(), key=lambda x: -x[1]["total"])
    ]
    expense_breakdown = [
        CategoryBreakdown(category=cat, total=round(vals["total"], 2), count=vals["count"])
        for cat, vals in sorted(expense_cats.items(), key=lambda x: -x[1]["total"])
    ]
    monthly_totals = [
        MonthlyTotal(
            year=ym[0],
            month=ym[1],
            income=round(v["income"], 2),
            expenses=round(v["expenses"], 2),
            net=round(v["income"] - v["expenses"], 2),
        )
        for ym, v in sorted(monthly.items())
    ]

    recent = sorted(transactions, key=lambda t: t.date, reverse=True)[:5]

    return FinancialSummary(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        balance=round(total_income - total_expenses, 2),
        transaction_count=len(transactions),
        income_by_category=income_breakdown,
        expense_by_category=expense_breakdown,
        monthly_totals=monthly_totals,
        recent_transactions=recent,
    )
