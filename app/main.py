from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .deps import get_db



app = FastAPI(
    title="Wallet API",
    description="A minimal but production-minded Wallet (expense tracker) REST service.",
    version="0.1.0",
)


@app.post("/expenses", response_model=schemas.Expense, status_code=201)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db=db, expense=expense)


@app.get("/expenses", response_model=List[schemas.Expense])
def read_expenses(
    skip: int = 0,
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    expenses = crud.get_expenses(db, skip=skip, limit=limit, category=category, from_date=from_date, to_date=to_date)
    return expenses


@app.get("/expenses/{expense_id}", response_model=schemas.Expense)
def read_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = crud.get_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense


@app.patch("/expenses/{expense_id}", response_model=schemas.Expense)
def update_expense(
    expense_id: int, expense: schemas.ExpenseUpdate, db: Session = Depends(get_db)
):
    db_expense = crud.update_expense(db, expense_id=expense_id, expense=expense)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = crud.delete_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return Response(status_code=204)


@app.get("/reports/summary")
def get_summary_report(
    from_date: datetime,
    to_date: datetime,
    group_by: str = Query(..., enum=["day", "month", "category"]),
    db: Session = Depends(get_db),
):
    return crud.get_summary_report(db, from_date=from_date, to_date=to_date, group_by=group_by)


@app.get("/charts/expenses")
def get_chart_data(
    from_date: datetime,
    to_date: datetime,
    group_by: str = Query(..., enum=["day", "month", "category"]),
    db: Session = Depends(get_db),
):
    return crud.get_chart_data(db, from_date=from_date, to_date=to_date, group_by=group_by)


@app.get("/export")
def export_expenses(
    from_date: datetime,
    to_date: datetime,
    format: str = Query(..., enum=["csv", "json"]),
    db: Session = Depends(get_db),
):
    if format == "csv":
        csv_data = crud.export_expenses(db, from_date=from_date, to_date=to_date, format="csv")
        return Response(content=csv_data, media_type="text/csv")
    else:
        json_data = crud.export_expenses(db, from_date=from_date, to_date=to_date, format="json")
        return json_data


@app.get("/about")
def about():
    return {
        "name": "Wallet",
        "version": "0.1.0",
        "description": "A minimal but production-minded Wallet (expense tracker) REST service.",
    }
