import csv
import io
from typing import List
from . import models

def export_expenses_to_csv(expenses: List[models.Expense]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "amount", "currency", "category", "note", "spent_at", "created_at"])
    for expense in expenses:
        writer.writerow([
            expense.id,
            expense.title,
            expense.amount,
            expense.currency,
            expense.category,
            expense.note,
            expense.spent_at.isoformat(),
            expense.created_at.isoformat(),
        ])
    return output.getvalue()
