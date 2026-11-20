from decimal import Decimal

from sqlalchemy import case, delete, select, update
from sqlalchemy.orm import Session

from app.db.models.savings_goal import GoalContribution, SavingsGoal
from app.schemas.savings_goal import ContributionCreate, SavingsGoalCreate


def list_goals(db: Session) -> list[SavingsGoal]:
    return list(db.scalars(select(SavingsGoal).order_by(SavingsGoal.created_at.desc(), SavingsGoal.id.desc())).all())


def get_goal(db: Session, goal_id: int) -> SavingsGoal | None:
    return db.get(SavingsGoal, goal_id)


def create_goal(db: Session, data: SavingsGoalCreate) -> SavingsGoal:
    goal = SavingsGoal(**data.model_dump(), current_saved_amount=Decimal("0.00"), status="ACTIVE")
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def update_goal(db: Session, goal: SavingsGoal, changes: dict) -> SavingsGoal:
    target = changes.get("target_amount", goal.target_amount)
    if target < goal.current_saved_amount:
        raise ValueError("Target amount cannot be less than the amount already saved")
    for field, value in changes.items():
        setattr(goal, field, value)
    goal.status = "COMPLETED" if goal.current_saved_amount == goal.target_amount else "ACTIVE"
    db.commit()
    db.refresh(goal)
    return goal


def delete_goal(db: Session, goal: SavingsGoal) -> None:
    db.delete(goal)
    db.commit()


def list_contributions(db: Session, goal_id: int) -> list[GoalContribution]:
    return list(db.scalars(
        select(GoalContribution)
        .where(GoalContribution.goal_id == goal_id)
        .order_by(GoalContribution.contribution_date.desc(), GoalContribution.id.desc())
    ).all())


def add_contribution(db: Session, goal_id: int, data: ContributionCreate) -> GoalContribution | None:
    """Atomically increment the goal within target and insert the matching history row."""
    amount = data.amount
    new_total = SavingsGoal.current_saved_amount + amount
    result = db.execute(
        update(SavingsGoal)
        .where(
            SavingsGoal.id == goal_id,
            new_total <= SavingsGoal.target_amount,
        )
        .values(
            current_saved_amount=new_total,
            status=case((new_total >= SavingsGoal.target_amount, "COMPLETED"), else_="ACTIVE"),
        )
    )
    if result.rowcount != 1:
        db.rollback()
        return None

    contribution = GoalContribution(goal_id=goal_id, **data.model_dump())
    try:
        db.add(contribution)
        db.commit()
        db.refresh(contribution)
        return contribution
    except Exception:
        db.rollback()
        raise


def delete_contribution(db: Session, goal_id: int, contribution_id: int) -> bool:
    contribution = db.scalar(select(GoalContribution).where(
        GoalContribution.id == contribution_id,
        GoalContribution.goal_id == goal_id,
    ))
    if contribution is None:
        return False

    try:
        result = db.execute(delete(GoalContribution).where(
            GoalContribution.id == contribution_id,
            GoalContribution.goal_id == goal_id,
        ))
        if result.rowcount != 1:
            db.rollback()
            return False
        amount = contribution.amount
        new_total = SavingsGoal.current_saved_amount - amount
        db.execute(
            update(SavingsGoal)
            .where(SavingsGoal.id == goal_id)
            .values(
                current_saved_amount=new_total,
                status=case((new_total >= SavingsGoal.target_amount, "COMPLETED"), else_="ACTIVE"),
            )
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
