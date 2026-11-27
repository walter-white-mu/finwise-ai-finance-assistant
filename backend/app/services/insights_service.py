from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.budget import CategoryBudget
from app.db.models.transaction import Transaction

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _shift_month(value: date, offset: int) -> date:
    index = value.year * 12 + value.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


def _month_transactions(db: Session, month: date) -> list[Transaction]:
    start = _month_start(month)
    end = _shift_month(start, 1)
    return list(db.scalars(select(Transaction).where(
        Transaction.transaction_date >= start,
        Transaction.transaction_date < end,
    )).all())


def _totals(rows: list[Transaction], month: date) -> dict:
    income = sum((row.amount for row in rows if row.type == "INCOME"), ZERO)
    expenses = sum((row.amount for row in rows if row.type == "EXPENSE"), ZERO)
    savings = income - expenses
    rate = (savings / income * 100).quantize(CENT, rounding=ROUND_HALF_UP) if income else ZERO
    return {"month": _month_start(month).strftime("%Y-%m"), "total_income": _money(income),
            "total_expenses": _money(expenses), "net_savings": _money(savings), "savings_rate": rate}


def get_summary(db: Session, month: date | None = None) -> dict:
    current_month = _month_start(month or date.today())
    previous_month = _shift_month(current_month, -1)
    current = _totals(_month_transactions(db, current_month), current_month)
    previous = _totals(_month_transactions(db, previous_month), previous_month)
    return {"current": current, "previous": previous,
            "income_change": _money(current["total_income"] - previous["total_income"]),
            "expense_change": _money(current["total_expenses"] - previous["total_expenses"]),
            "savings_change": _money(current["net_savings"] - previous["net_savings"])}


def get_spending(db: Session, month: date | None = None) -> dict:
    current_month = _month_start(month or date.today())
    previous_month = _shift_month(current_month, -1)
    current_rows = [r for r in _month_transactions(db, current_month) if r.type == "EXPENSE"]
    previous_rows = [r for r in _month_transactions(db, previous_month) if r.type == "EXPENSE"]
    current: dict[str, Decimal] = {}
    previous: dict[str, Decimal] = {}
    for row in current_rows:
        current[row.category] = current.get(row.category, ZERO) + row.amount
    for row in previous_rows:
        previous[row.category] = previous.get(row.category, ZERO) + row.amount
    total = sum(current.values(), ZERO)
    categories = []
    for category in sorted(current.keys() | previous.keys(), key=lambda name: current.get(name, ZERO), reverse=True):
        amount, before = current.get(category, ZERO), previous.get(category, ZERO)
        categories.append({"category": category, "amount": _money(amount),
            "percentage": (amount / total * 100).quantize(CENT, rounding=ROUND_HALF_UP) if total else ZERO,
            "previous_amount": _money(before), "change": _money(amount - before),
            "change_percentage": ((amount - before) / before * 100).quantize(CENT, rounding=ROUND_HALF_UP) if before else None})
    return {"month": current_month.strftime("%Y-%m"), "total_expenses": _money(total), "categories": categories}


def get_budget_progress(db: Session, month: date | None = None) -> list[dict]:
    spent: dict[str, Decimal] = {}
    for row in _month_transactions(db, month or date.today()):
        if row.type == "EXPENSE":
            spent[row.category] = spent.get(row.category, ZERO) + row.amount
    result = []
    for budget in db.scalars(select(CategoryBudget).order_by(CategoryBudget.category)).all():
        actual = _money(spent.get(budget.category, ZERO))
        result.append({"category": budget.category, "budget": budget.amount, "spent": actual,
            "remaining": _money(budget.amount - actual),
            "percentage_used": (actual / budget.amount * 100).quantize(CENT, rounding=ROUND_HALF_UP),
            "exceeded": actual > budget.amount})
    return result


def get_anomalies(db: Session, month: date | None = None) -> list[dict]:
    target = _month_start(month or date.today())
    rows = list(db.scalars(select(Transaction).where(
        Transaction.type == "EXPENSE", Transaction.transaction_date < _shift_month(target, 1),
    ).order_by(Transaction.transaction_date)).all())
    history: dict[str, list[Decimal]] = {}
    flagged = []
    for row in rows:
        baseline = sorted(history.get(row.category, []))
        if target <= row.transaction_date < _shift_month(target, 1) and len(baseline) >= 3:
            middle = len(baseline) // 2
            median = baseline[middle] if len(baseline) % 2 else (baseline[middle - 1] + baseline[middle]) / 2
            threshold = median * 3
            if median > 0 and row.amount >= threshold:
                flagged.append({"transaction_id": row.id, "description": row.description,
                    "category": row.category, "amount": row.amount, "transaction_date": row.transaction_date,
                    "baseline_median": _money(median),
                    "reason": f"This is at least 3× the prior {len(baseline)} {row.category} transactions' median ({_money(median)})."})
        history.setdefault(row.category, []).append(row.amount)
    return flagged


def get_recommendations(db: Session, month: date | None = None) -> dict:
    target = _month_start(month or date.today())
    months = [_shift_month(target, -i) for i in (2, 1, 0)]
    data = {m: _month_transactions(db, m) for m in months}
    history_count = sum(bool(data[m]) for m in months)
    if history_count < 3:
        return {"available": False, "months_of_history": history_count, "recommendations": [],
                "message": "Recommendations need transactions in three consecutive months."}
    category_totals: dict[date, dict[str, Decimal]] = {}
    for m, rows in data.items():
        category_totals[m] = {}
        for row in rows:
            if row.type == "EXPENSE":
                category_totals[m][row.category] = category_totals[m].get(row.category, ZERO) + row.amount
    results = []
    for category in set().union(*(set(v) for v in category_totals.values())):
        earlier = (category_totals[months[0]].get(category, ZERO) + category_totals[months[1]].get(category, ZERO)) / 2
        recent = category_totals[months[2]].get(category, ZERO)
        if recent > earlier:
            savings = min((recent - earlier) * Decimal("0.10"), recent).quantize(CENT, rounding=ROUND_HALF_UP)
            if savings > 0:
                results.append({"category": category, "recent_month_spending": _money(recent),
                    "comparison_monthly_average": _money(earlier), "estimated_monthly_savings": savings,
                    "reason": f"Spending is above the average of the prior two months; reducing it by 10% of that increase could save this amount."})
    results.sort(key=lambda item: item["estimated_monthly_savings"], reverse=True)
    return {"available": True, "months_of_history": 3, "recommendations": results, "message": None}


def list_budgets(db: Session) -> list[CategoryBudget]:
    return list(db.scalars(select(CategoryBudget).order_by(CategoryBudget.category)).all())


def create_budget(db: Session, category: str, amount: Decimal) -> CategoryBudget:
    budget = CategoryBudget(category=category.strip(), amount=amount)
    db.add(budget)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("A budget already exists for this category") from exc
    db.refresh(budget)
    return budget


def update_budget(db: Session, budget: CategoryBudget, changes: dict) -> CategoryBudget:
    for key, value in changes.items():
        setattr(budget, key, value.strip() if key == "category" else value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("A budget already exists for this category") from exc
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget: CategoryBudget) -> None:
    db.delete(budget)
    db.commit()
