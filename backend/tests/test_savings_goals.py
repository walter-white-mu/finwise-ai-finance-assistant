from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.savings_goals import router
from app.db.database import Base, get_db
from app.db import models  # noqa: F401 - register all mapped models on Base


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(router)

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_goal(client: TestClient):
    response = client.post("/api/savings-goals", json={
        "name": "Emergency fund",
        "description": "Six months of expenses",
        "target_amount": "1000.00",
        "target_date": "2027-12-31",
    })
    assert response.status_code == 201
    return response.json()


def test_goal_crud_and_decimal_progress(client: TestClient):
    goal = create_goal(client)
    goal_id = goal["id"]
    assert Decimal(str(goal["remaining_amount"])) == Decimal("1000.00")
    assert Decimal(str(goal["progress_percent"])) == Decimal("0.00")

    detail = client.get(f"/api/savings-goals/{goal_id}")
    assert detail.status_code == 200

    updated = client.patch(f"/api/savings-goals/{goal_id}", json={"name": "New emergency fund"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "New emergency fund"

    assert client.get("/api/savings-goals").json()[0]["id"] == goal_id
    assert client.delete(f"/api/savings-goals/{goal_id}").status_code == 204
    assert client.get(f"/api/savings-goals/{goal_id}").status_code == 404


def test_contributions_update_saved_status_and_history_atomically(client: TestClient):
    goal_id = create_goal(client)["id"]
    first = client.post(f"/api/savings-goals/{goal_id}/contributions", json={
        "amount": "250.25", "contribution_date": "2026-11-19", "note": "Monthly saving"
    })
    assert first.status_code == 201

    goal = client.get(f"/api/savings-goals/{goal_id}").json()
    assert Decimal(str(goal["current_saved_amount"])) == Decimal("250.25")
    assert Decimal(str(goal["remaining_amount"])) == Decimal("749.75")
    assert Decimal(str(goal["progress_percent"])) == Decimal("25.03")

    complete = client.post(f"/api/savings-goals/{goal_id}/contributions", json={
        "amount": "749.75", "contribution_date": "2026-11-19"
    })
    assert complete.status_code == 201
    assert client.get(f"/api/savings-goals/{goal_id}").json()["status"] == "COMPLETED"

    too_much = client.post(f"/api/savings-goals/{goal_id}/contributions", json={
        "amount": "0.01", "contribution_date": "2026-11-19"
    })
    assert too_much.status_code == 409

    history = client.get(f"/api/savings-goals/{goal_id}/contributions")
    assert history.status_code == 200
    assert len(history.json()) == 2

    removed = client.delete(f"/api/savings-goals/{goal_id}/contributions/{complete.json()['id']}")
    assert removed.status_code == 204
    goal = client.get(f"/api/savings-goals/{goal_id}").json()
    assert Decimal(str(goal["current_saved_amount"])) == Decimal("250.25")
    assert goal["status"] == "ACTIVE"


@pytest.mark.parametrize("amount", ["0", "-0.01"])
def test_nonpositive_contributions_are_rejected(client: TestClient, amount: str):
    goal_id = create_goal(client)["id"]
    response = client.post(f"/api/savings-goals/{goal_id}/contributions", json={
        "amount": amount, "contribution_date": "2026-11-19"
    })
    assert response.status_code == 422
    goal = client.get(f"/api/savings-goals/{goal_id}").json()
    assert Decimal(str(goal["current_saved_amount"])) == Decimal("0.00")


def test_goal_target_cannot_be_reduced_below_saved_amount(client: TestClient):
    goal_id = create_goal(client)["id"]
    client.post(f"/api/savings-goals/{goal_id}/contributions", json={
        "amount": "100.00", "contribution_date": "2026-11-19"
    })
    response = client.patch(f"/api/savings-goals/{goal_id}", json={"target_amount": "99.99"})
    assert response.status_code == 422
