from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate
)


def create_transaction(
    db: Session,
    transaction_data: TransactionCreate
):
    transaction = Transaction(
        type=transaction_data.type.value,
        description=transaction_data.description,
        amount=transaction_data.amount,
        category=transaction_data.category,
        transaction_date=transaction_data.transaction_date
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def get_transactions(
    db: Session,
    transaction_type: str | None = None,
    category: str | None = None
):
    query = select(Transaction)

    if transaction_type:
        query = query.where(Transaction.type == transaction_type)

    if category:
        query = query.where(Transaction.category == category)

    query = query.order_by(
        Transaction.transaction_date.desc(),
        Transaction.id.desc()
    )

    return db.scalars(query).all()


def get_transaction_by_id(
    db: Session,
    transaction_id: int
):
    return db.get(Transaction, transaction_id)


def update_transaction(
    db: Session,
    transaction: Transaction,
    update_data: dict
):
    for field, value in update_data.items():
        if field == "type":
            value = value.value

        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)

    return transaction


def delete_transaction(
    db: Session,
    transaction: Transaction
):
    db.delete(transaction)
    db.commit()