from decimal import Decimal
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    savings_rate: float


class CategorySpending(BaseModel):
    category: str
    total: Decimal

class MonthlyTrend(BaseModel):
    month: str
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal