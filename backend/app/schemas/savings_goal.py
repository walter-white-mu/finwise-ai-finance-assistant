from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class SavingsGoalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    target_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    target_date: date

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Goal name must contain at least 2 non-space characters")
        return value


class SavingsGoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    target_amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    target_date: date | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Goal name must contain at least 2 non-space characters")
        return value


class SavingsGoalResponse(BaseModel):
    id: int
    name: str
    description: str | None
    target_amount: Decimal
    current_saved_amount: Decimal
    target_date: date
    created_at: datetime
    status: SavingsGoalStatus

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def remaining_amount(self) -> Decimal:
        return self.target_amount - self.current_saved_amount

    @computed_field
    @property
    def progress_percent(self) -> Decimal:
        return (self.current_saved_amount / self.target_amount * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )


class ContributionCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    contribution_date: date
    note: str | None = Field(default=None, max_length=255)


class ContributionResponse(BaseModel):
    id: int
    goal_id: int
    amount: Decimal
    contribution_date: date
    note: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
