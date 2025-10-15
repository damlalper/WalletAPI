import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from .database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    category = Column(String(50), nullable=False)
    note = Column(String, nullable=True)
    spent_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
