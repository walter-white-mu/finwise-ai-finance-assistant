from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.transaction import Transaction
from sqlalchemy import case
from app.schemas.dashboard import MonthlyTrend


def get_dashboard_summary(db: Session):
    # Calculate total income
    income_query = select(
        func.sum(Transaction.amount)
    ).where(Transaction.type == "INCOME")

    total_income = db.scalar(income_query) or Decimal("0.00")

    # Calculate total expenses
    expense_query = select(
        func.sum(Transaction.amount)
    ).where(Transaction.type == "EXPENSE")

    total_expenses = db.scalar(expense_query) or Decimal("0.00")

    # Calculate balance
    balance = total_income - total_expenses

    # Calculate savings rate
    if total_income > 0:
        savings_rate = float(
            (balance / total_income) * 100
        )
    else:
        savings_rate = 0.0

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "savings_rate": round(savings_rate, 2)
    }


def get_category_spending(db: Session):
    query = (
        select(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        )
        .where(Transaction.type == "EXPENSE")
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    )

    results = db.execute(query).all()

    return [
        {
            "category": row.category,
            "total": row.total
        }
        for row in results
    ]


def get_monthly_trends(db: Session):
    month_column = func.strftime(
        "%Y-%m",
        Transaction.transaction_date
    )

    query = (
        select(
            month_column.label("month"),

            func.sum(
                case(
                    (Transaction.type == "INCOME", Transaction.amount),
                    else_=0
                )
            ).label("total_income"),

            func.sum(
                case(
                    (Transaction.type == "EXPENSE", Transaction.amount),
                    else_=0
                )
            ).label("total_expenses")
        )
        .group_by(month_column)
        .order_by(month_column)
    )

    results = db.execute(query).all()

    trends = []

    for row in results:
        income = row.total_income or Decimal("0.00")
        expenses = row.total_expenses or Decimal("0.00")

        trends.append(
            {
                "month": row.month,
                "total_income": income,
                "total_expenses": expenses,
                "balance": income - expenses
            }
        )

    return trends