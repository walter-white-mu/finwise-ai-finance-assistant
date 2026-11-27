from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MonthTotals(BaseModel):
    month: str
    total_income: Decimal
    total_expenses: Decimal
    net_savings: Decimal
    savings_rate: Decimal


class MonthlySummary(BaseModel):
    current: MonthTotals
    previous: MonthTotals
    income_change: Decimal
    expense_change: Decimal
    savings_change: Decimal


class CategorySpending(BaseModel):
    category: str
    amount: Decimal
    percentage: Decimal
    previous_amount: Decimal
    change: Decimal
    change_percentage: Decimal | None


class SpendingAnalysis(BaseModel):
    month: str
    total_expenses: Decimal
    categories: list[CategorySpending]


class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class BudgetUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)


class BudgetResponse(BaseModel):
    id: int
    category: str
    amount: Decimal
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BudgetProgress(BaseModel):
    category: str
    budget: Decimal
    spent: Decimal
    remaining: Decimal
    percentage_used: Decimal
    exceeded: bool


class Anomaly(BaseModel):
    transaction_id: int
    description: str
    category: str
    amount: Decimal
    transaction_date: date
    baseline_median: Decimal
    reason: str


class Recommendation(BaseModel):
    category: str
    recent_month_spending: Decimal
    comparison_monthly_average: Decimal
    estimated_monthly_savings: Decimal
    reason: str


class RecommendationsResponse(BaseModel):
    available: bool
    months_of_history: int
    recommendations: list[Recommendation]
    message: str | None = None
