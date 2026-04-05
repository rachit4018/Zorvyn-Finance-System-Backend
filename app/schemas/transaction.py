from datetime import date as Date
from pydantic import BaseModel, field_validator
from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: Date = None
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category cannot be empty")
        return v

    def model_post_init(self, __context):
        if self.date is None:
            object.__setattr__(self, "date", date.today())


class TransactionUpdate(BaseModel):
    amount: float | None = None
    type: TransactionType | None = None
    category: str | None = None
    date: Date | None = None
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2) if v is not None else v


class TransactionOut(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: Date
    notes: str | None
    user_id: int

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
    type: TransactionType | None = None
    category: str | None = None
    date_from: Date | None = None
    date_to: Date | None = None


class PaginatedTransactions(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TransactionOut]
