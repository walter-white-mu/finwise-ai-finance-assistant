from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionCreate(BaseModel):

    type: TransactionType

    description: str = Field(
        min_length=2,
        max_length=255
    )

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )

    category: str = Field(
        min_length=2,
        max_length=100
    )

    transaction_date: date


class TransactionUpdate(BaseModel):

    type: TransactionType | None = None

    description: str | None = Field(
        default=None,
        min_length=2,
        max_length=255
    )

    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2
    )

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    transaction_date: date | None = None


class TransactionResponse(BaseModel):

    id: int
    type: TransactionType
    description: str
    amount: Decimal
    category: str
    transaction_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)