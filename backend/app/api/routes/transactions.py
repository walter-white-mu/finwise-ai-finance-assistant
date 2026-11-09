from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionType
)
from app.services import transaction_service


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"]
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    return transaction_service.create_transaction(
        db,
        transaction_data
    )


@router.get(
    "",
    response_model=list[TransactionResponse]
)
def get_transactions(
    transaction_type: TransactionType | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    return transaction_service.get_transactions(
        db,
        transaction_type.value if transaction_type else None,
        category
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = transaction_service.get_transaction_by_id(
        db,
        transaction_id
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return transaction


@router.patch(
    "/{transaction_id}",
    response_model=TransactionResponse
)
def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db)
):
    transaction = transaction_service.get_transaction_by_id(
        db,
        transaction_id
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    changes = update_data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided"
        )

    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Transaction fields cannot be null"
        )

    return transaction_service.update_transaction(
        db,
        transaction,
        changes
    )


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = transaction_service.get_transaction_by_id(
        db,
        transaction_id
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    transaction_service.delete_transaction(
        db,
        transaction
    )

    return None