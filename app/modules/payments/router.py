import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.platform.database import get_db
from app.modules.payments.models import (
    EscrowTransaction,
    TransactionStatus,
    TransactionType,
)
from app.modules.payments.schemas import EscrowHoldCreate, EscrowResponse

router = APIRouter(prefix="", tags=["Payments & Escrow"])


@router.post("/", response_model=EscrowResponse, status_code=status.HTTP_201_CREATED)
async def create_escrow_hold(
    payload: EscrowHoldCreate, db: AsyncSession = Depends(get_db)
):
    transaction = EscrowTransaction(
        order_id=payload.order_id,
        payer_workspace_id=payload.payer_workspace_id,
        payee_workspace_id=payload.payee_workspace_id,
        amount_minor=payload.amount_minor,
        currency=payload.currency,
        transaction_type=TransactionType.ESCROW_HOLD,
        status=TransactionStatus.COMPLETED,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.get("/", response_model=List[EscrowResponse])
async def list_transactions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EscrowTransaction))
    transactions = result.scalars().all()
    return transactions


@router.post("/{transaction_id}/release", response_model=EscrowResponse)
async def release_escrow(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EscrowTransaction).where(EscrowTransaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.transaction_type != TransactionType.ESCROW_HOLD:
        raise HTTPException(
            status_code=400, detail="Only escrow hold transactions can be released"
        )

    release_tx = EscrowTransaction(
        order_id=transaction.order_id,
        payer_workspace_id=transaction.payer_workspace_id,
        payee_workspace_id=transaction.payee_workspace_id,
        amount_minor=transaction.amount_minor,
        currency=transaction.currency,
        transaction_type=TransactionType.ESCROW_RELEASE,
        status=TransactionStatus.COMPLETED,
    )
    db.add(release_tx)
    await db.commit()
    await db.refresh(release_tx)
    return release_tx
