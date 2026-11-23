from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.db.models import CategoryBudget, Transaction
from app.main import app
from app.services import insights_service


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def add(db, kind, amount, category, day):
    row = Transaction(type=kind, amount=Decimal(amount), category=category, description=category,
                      transaction_date=date.fromisoformat(day))
    db.add(row)
    db.commit()
    return row


def test_summary_compares_months_and_handles_decimal_rate(db):
    add(db, "INCOME", "5000.00", "Salary", "2026-10-03")
    add(db, "EXPENSE", "2000.00", "Rent", "2026-10-04")
    add(db, "INCOME", "6000.00", "Salary", "2026-11-03")
    add(db, "EXPENSE", "2400.00", "Rent", "2026-11-04")

    result = insights_service.get_summary(db, date(2026, 11, 1))

    assert result["current"]["net_savings"] == Decimal("3600.00")
    assert result["current"]["savings_rate"] == Decimal("60.00")
    assert result["expense_change"] == Decimal("400.00")


def test_spending_share_and_budget_progress(db):
    add(db, "EXPENSE", "75.00", "Food", "2026-11-03")
    add(db, "EXPENSE", "25.00", "Travel", "2026-11-04")
    budget = CategoryBudget(category="Food", amount=Decimal("60.00"))
    db.add(budget)
    db.commit()

    spending = insights_service.get_spending(db, date(2026, 11, 1))
    progress = insights_service.get_budget_progress(db, date(2026, 11, 1))[0]

    assert spending["categories"][0]["percentage"] == Decimal("75.00")
    assert progress["remaining"] == Decimal("-15.00")
    assert progress["exceeded"] is True


def test_anomaly_uses_category_median_and_explains_flag(db):
    for day in ("2026-10-01", "2026-10-05", "2026-10-10"):
        add(db, "EXPENSE", "20.00", "Dining", day)
    add(db, "EXPENSE", "100.00", "Dining", "2026-11-02")

    anomaly = insights_service.get_anomalies(db, date(2026, 11, 1))[0]

    assert anomaly["baseline_median"] == Decimal("20.00")
    assert "3×" in anomaly["reason"]


def test_recommendations_require_three_months_and_are_deterministic(db):
    unavailable = insights_service.get_recommendations(db, date(2026, 11, 1))
    for month, amount in (("2026-09-05", "100.00"), ("2026-10-05", "100.00"), ("2026-11-05", "200.00")):
        add(db, "EXPENSE", amount, "Shopping", month)

    result = insights_service.get_recommendations(db, date(2026, 11, 1))

    assert unavailable["available"] is False
    assert result["recommendations"][0]["estimated_monthly_savings"] == Decimal("10.00")


def test_insight_and_budget_api_endpoints(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app)
        summary_response = client.get("/api/insights/summary?month=2026-11-01")
        created = client.post("/api/budgets", json={"category": "Food", "amount": "300.00"})
        progress = client.get("/api/budgets/progress?month=2026-11-01")
        changed = client.patch(f"/api/budgets/{created.json()['id']}", json={"amount": "350.00"})
        deleted = client.delete(f"/api/budgets/{created.json()['id']}")

        assert summary_response.status_code == 200
        assert summary_response.json()["current"]["total_income"] == "0.00"
        assert created.status_code == 201
        assert progress.json()[0]["category"] == "Food"
        assert changed.json()["amount"] == "350.00"
        assert deleted.status_code == 204
    finally:
        app.dependency_overrides.pop(get_db, None)
