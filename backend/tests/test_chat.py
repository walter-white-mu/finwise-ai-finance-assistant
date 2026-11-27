from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.ai import service as ai_service
from app.ai.tools import run_tool
from app.db.database import Base, get_db
from app.db.models import Transaction
from app.main import app


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_tools_reject_unknown_names_and_extra_arguments(db):
    with pytest.raises(ValueError, match="Unsupported"):
        run_tool("execute_sql", {}, db)
    with pytest.raises(ValueError):
        run_tool("get_financial_summary", {"sql": "select *"}, db)


def test_chat_endpoint_uses_read_only_tool_and_returns_grounded_result(db, monkeypatch):
    db.add(Transaction(type="EXPENSE", description="Groceries", amount=Decimal("125.00"), category="Food", transaction_date=date(2026, 11, 4)))
    db.commit()
    calls = 0

    async def fake_ollama(messages):
        nonlocal calls
        calls += 1
        if calls == 1:
            return {"message": {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": "get_spending_by_category", "arguments": {"month": "2026-11-01"}}}]}}
        assert '"amount": "125.00"' in messages[-1]["content"]
        return {"message": {"role": "assistant", "content": "You spent ₹125.00 on Food this month."}}

    monkeypatch.setattr(ai_service, "_ollama_chat", fake_ollama)

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        response = TestClient(app).post("/api/chat", json={"message": "How much did I spend?"})
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"]
    assert body["assistant_message"] == "You spent ₹125.00 on Food this month."
    assert body["tool_results"][0]["name"] == "get_spending_by_category"
    assert calls == 2
    cleared = TestClient(app).delete(f"/api/chat/{body['conversation_id']}")
    assert cleared.status_code == 204
