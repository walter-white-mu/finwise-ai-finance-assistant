from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db.models.savings_goal import SavingsGoal
from app.services import dashboard_service, insights_service


class ToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MonthArguments(ToolArguments):
    month: date | None = None


def _goals(db: Session) -> list[dict[str, Any]]:
    goals = db.query(SavingsGoal).order_by(SavingsGoal.target_date).all()
    return [{
        "name": goal.name,
        "target_amount": goal.target_amount,
        "current_saved_amount": goal.current_saved_amount,
        "progress_percentage": round(float(goal.current_saved_amount / goal.target_amount * 100), 2),
        "remaining_amount": goal.target_amount - goal.current_saved_amount,
        "target_date": goal.target_date,
        "status": goal.status,
    } for goal in goals]


TOOL_DEFINITIONS = [
    {"type": "function", "function": {"name": "get_financial_summary", "description": "Get this month's and previous month's income, expenses, net savings, savings rate, and changes.", "parameters": {"type": "object", "properties": {"month": {"type": "string", "description": "Optional month date YYYY-MM-DD; defaults to current month."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_spending_by_category", "description": "Get this month's spending totals and changes for each expense category.", "parameters": {"type": "object", "properties": {"month": {"type": "string", "description": "Optional month date YYYY-MM-DD; defaults to current month."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_monthly_trends", "description": "Get monthly income, expenses and balance trends across recorded transactions.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_savings_goals", "description": "List savings goals with calculated progress and remaining amounts.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_budget_status", "description": "Get budget usage and remaining amount for the selected month.", "parameters": {"type": "object", "properties": {"month": {"type": "string", "description": "Optional month date YYYY-MM-DD; defaults to current month."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "get_financial_recommendations", "description": "Get Python-generated spending recommendations and unusual transaction flags for the selected month.", "parameters": {"type": "object", "properties": {"month": {"type": "string", "description": "Optional month date YYYY-MM-DD; defaults to current month."}}, "additionalProperties": False}}},
]


def run_tool(name: str, arguments: dict[str, Any], db: Session) -> dict | list:
    registry = {
        "get_financial_summary": (MonthArguments, lambda a: insights_service.get_summary(db, a.month)),
        "get_spending_by_category": (MonthArguments, lambda a: insights_service.get_spending(db, a.month)),
        "get_monthly_trends": (ToolArguments, lambda _: dashboard_service.get_monthly_trends(db)),
        "get_savings_goals": (ToolArguments, lambda _: _goals(db)),
        "get_budget_status": (MonthArguments, lambda a: insights_service.get_budget_progress(db, a.month)),
        "get_financial_recommendations": (MonthArguments, lambda a: {
            "recommendations": insights_service.get_recommendations(db, a.month),
            "unusual_transactions": insights_service.get_anomalies(db, a.month),
        }),
    }
    if name not in registry:
        raise ValueError("Unsupported financial tool")
    schema, handler = registry[name]
    parsed = schema.model_validate(arguments)
    return handler(parsed)
