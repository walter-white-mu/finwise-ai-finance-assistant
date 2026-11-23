from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.budget import CategoryBudget
from app.schemas.insights import (
    Anomaly, BudgetCreate, BudgetProgress, BudgetResponse, BudgetUpdate,
    MonthlySummary, RecommendationsResponse, SpendingAnalysis,
)
from app.services import insights_service

router = APIRouter(tags=["Financial Insights"])


@router.get("/api/insights/summary", response_model=MonthlySummary)
def summary(month: date | None = None, db: Session = Depends(get_db)):
    return insights_service.get_summary(db, month)


@router.get("/api/insights/spending", response_model=SpendingAnalysis)
def spending(month: date | None = None, db: Session = Depends(get_db)):
    return insights_service.get_spending(db, month)


@router.get("/api/insights/recommendations", response_model=RecommendationsResponse)
def recommendations(month: date | None = None, db: Session = Depends(get_db)):
    return insights_service.get_recommendations(db, month)


@router.get("/api/insights/anomalies", response_model=list[Anomaly])
def anomalies(month: date | None = None, db: Session = Depends(get_db)):
    return insights_service.get_anomalies(db, month)


@router.get("/api/budgets", response_model=list[BudgetResponse])
def budgets(db: Session = Depends(get_db)):
    return insights_service.list_budgets(db)


@router.get("/api/budgets/progress", response_model=list[BudgetProgress])
def budget_progress(month: date | None = None, db: Session = Depends(get_db)):
    return insights_service.get_budget_progress(db, month)


@router.post("/api/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(data: BudgetCreate, db: Session = Depends(get_db)):
    try:
        return insights_service.create_budget(db, data.category, data.amount)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/api/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, data: BudgetUpdate, db: Session = Depends(get_db)):
    budget = db.get(CategoryBudget, budget_id)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    changes = data.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=400, detail="Provide non-null budget fields to update")
    try:
        return insights_service.update_budget(db, budget, changes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/api/budgets/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.get(CategoryBudget, budget_id)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    insights_service.delete_budget(db, budget)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
