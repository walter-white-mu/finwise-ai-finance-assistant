from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.savings_goal import (
    ContributionCreate, ContributionResponse, SavingsGoalCreate,
    SavingsGoalResponse, SavingsGoalUpdate,
)
from app.services import savings_goal_service as service

router = APIRouter(prefix="/api/savings-goals", tags=["Savings Goals"])


@router.post("", response_model=SavingsGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(data: SavingsGoalCreate, db: Session = Depends(get_db)):
    return service.create_goal(db, data)


@router.get("", response_model=list[SavingsGoalResponse])
def list_goals(db: Session = Depends(get_db)):
    return service.list_goals(db)


@router.get("/{goal_id}", response_model=SavingsGoalResponse)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = service.get_goal(db, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    return goal


@router.patch("/{goal_id}", response_model=SavingsGoalResponse)
def update_goal(goal_id: int, data: SavingsGoalUpdate, db: Session = Depends(get_db)):
    goal = service.get_goal(db, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No update fields provided")
    if any(value is None for field, value in changes.items() if field != "description"):
        raise HTTPException(status_code=422, detail="Only description may be cleared")
    try:
        return service.update_goal(db, goal, changes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = service.get_goal(db, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    service.delete_goal(db, goal)


@router.post("/{goal_id}/contributions", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
def create_contribution(goal_id: int, data: ContributionCreate, db: Session = Depends(get_db)):
    goal = service.get_goal(db, goal_id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    contribution = service.add_contribution(db, goal_id, data)
    if contribution is None:
        raise HTTPException(status_code=409, detail="Contribution exceeds the remaining target amount")
    return contribution


@router.get("/{goal_id}/contributions", response_model=list[ContributionResponse])
def list_contributions(goal_id: int, db: Session = Depends(get_db)):
    if service.get_goal(db, goal_id) is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    return service.list_contributions(db, goal_id)


@router.delete("/{goal_id}/contributions/{contribution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contribution(goal_id: int, contribution_id: int, db: Session = Depends(get_db)):
    if service.get_goal(db, goal_id) is None:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    if not service.delete_contribution(db, goal_id, contribution_id):
        raise HTTPException(status_code=404, detail="Contribution not found")
