import enum
from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(SAEnum(TransactionType), nullable=False)
    category = Column(String(100), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", backref="transactions")
