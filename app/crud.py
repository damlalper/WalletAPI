from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas, utils

def create_expense(db: Session, expense: schemas.ExpenseCreate) -> models.Expense:
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expense(db: Session, expense_id: int) -> Optional[models.Expense]:
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def get_expenses(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[models.Expense]:
    query = db.query(models.Expense)
    if category:
        query = query.filter(models.Expense.category == category)
    if from_date:
        query = query.filter(models.Expense.spent_at >= from_date)
    if to_date:
        query = query.filter(models.Expense.spent_at <= to_date)
    return query.offset(skip).limit(limit).all()

def update_expense(
    db: Session, expense_id: int, expense: schemas.ExpenseUpdate
) -> Optional[models.Expense]:
    db_expense = get_expense(db, expense_id)
    if db_expense:
        update_data = expense.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_expense, key, value)
        db.commit()
        db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int) -> Optional[models.Expense]:
    db_expense = get_expense(db, expense_id)
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense

def get_summary_report(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    group_by: str,
) -> dict:
    query = (
        db.query(
            func.sum(models.Expense.amount).label("total"),
        )
        .filter(models.Expense.spent_at >= from_date)
        .filter(models.Expense.spent_at <= to_date)
    )

    if group_by in ["day", "month", "category"]:
        if group_by == "day":
            group_by_field = func.date(models.Expense.spent_at)
        elif group_by == "month":
            group_by_field = func.strftime("%Y-%m", models.Expense.spent_at)
        else: # category
            group_by_field = models.Expense.category

        query = query.add_columns(group_by_field.label("label")).group_by("label")

    results = query.all()

    grand_total = sum(r.total for r in results)
    buckets = [{"label": r.label, "total": str(r.total)} for r in results]

    return {
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "group_by": group_by,
        "buckets": buckets,
        "grand_total": str(grand_total),
    }

def get_chart_data(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    group_by: str,
) -> List[dict]:
    if group_by == "day":
        group_by_field = func.date(models.Expense.spent_at)
    elif group_by == "month":
        group_by_field = func.strftime("%Y-%m", models.Expense.spent_at)
    else: # category
        group_by_field = models.Expense.category

    results = (
        db.query(
            group_by_field.label("timestamp"),
            func.sum(models.Expense.amount).label("value"),
        )
        .filter(models.Expense.spent_at >= from_date)
        .filter(models.Expense.spent_at <= to_date)
        .group_by("timestamp")
        .order_by("timestamp")
        .all()
    )

    return [
        {"timestamp": r.timestamp, "value": str(r.value)} for r in results
    ]

def export_expenses(
    db: Session,
    from_date: datetime,
    to_date: datetime,
    format: str,
) -> str:
    expenses = get_expenses(db, from_date=from_date, to_date=to_date, limit=200) # Use a reasonable limit for export

    if format == "json":
        return [schemas.Expense.from_orm(e).model_dump() for e in expenses]

    return utils.export_expenses_to_csv(expenses)
