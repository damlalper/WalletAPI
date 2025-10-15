import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ExpenseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    category: str = Field(..., min_length=1, max_length=50)
    note: str | None = None
    spent_at: datetime.datetime

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=120)
    amount: Decimal | None = Field(None, gt=0)
    currency: str | None = Field(None, min_length=3, max_length=3)
    category: str | None = Field(None, min_length=1, max_length=50)
    note: str | None = None
    spent_at: datetime.datetime | None = None

class Expense(ExpenseBase):
    id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
