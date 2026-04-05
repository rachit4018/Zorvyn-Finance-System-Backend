from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.dependencies import get_current_user, require_viewer, require_analyst, require_admin
from app.models.user import User
from app.models.transaction import TransactionType
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionOut,
    TransactionFilter,
    PaginatedTransactions,
)
from app.services import transactions as tx_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=PaginatedTransactions)
def list_transactions(
    type: TransactionType | None = Query(None),
    category: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    filters = TransactionFilter(type=type, category=category, date_from=date_from, date_to=date_to)
    total, items = tx_service.get_transactions(db, current_user, filters, page, page_size)
    return PaginatedTransactions(total=total, page=page, page_size=page_size, items=items)


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    tx = tx_service.get_transaction_by_id(db, transaction_id, current_user)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return tx_service.create_transaction(db, data, current_user)


@router.patch("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    tx = tx_service.get_transaction_by_id(db, transaction_id, current_user)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx_service.update_transaction(db, tx, data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    tx = tx_service.get_transaction_by_id(db, transaction_id, current_user)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    tx_service.delete_transaction(db, tx)
