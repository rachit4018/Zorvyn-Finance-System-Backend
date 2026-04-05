from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionFilter


def _base_query(db: Session, current_user: User):
    """Admins and analysts see all transactions; viewers see only their own."""
    q = db.query(Transaction)
    if current_user.role == UserRole.viewer:
        q = q.filter(Transaction.user_id == current_user.id)
    return q


def get_transactions(
    db: Session,
    current_user: User,
    filters: TransactionFilter,
    page: int = 1,
    page_size: int = 20,
):
    q = _base_query(db, current_user)

    if filters.type:
        q = q.filter(Transaction.type == filters.type)
    if filters.category:
        q = q.filter(Transaction.category.ilike(f"%{filters.category}%"))
    if filters.date_from:
        q = q.filter(Transaction.date >= filters.date_from)
    if filters.date_to:
        q = q.filter(Transaction.date <= filters.date_to)

    total = q.count()
    items = q.order_by(Transaction.date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def get_transaction_by_id(db: Session, transaction_id: int, current_user: User) -> Transaction | None:
    q = _base_query(db, current_user)
    return q.filter(Transaction.id == transaction_id).first()


def create_transaction(db: Session, data: TransactionCreate, current_user: User) -> Transaction:
    tx = Transaction(
        amount=data.amount,
        type=data.type,
        category=data.category,
        date=data.date or date.today(),
        notes=data.notes,
        user_id=current_user.id,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def update_transaction(
    db: Session,
    transaction: Transaction,
    data: TransactionUpdate,
) -> Transaction:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()
