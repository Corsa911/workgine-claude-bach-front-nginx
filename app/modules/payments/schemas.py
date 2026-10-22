import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.modules.payments.models import TransactionType, TransactionStatus


class EscrowHoldCreate(BaseModel):
    order_id: uuid.UUID
    payer_workspace_id: uuid.UUID
    payee_workspace_id: uuid.UUID
    amount_minor: int
    currency: str = "USD"


class EscrowResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    payer_workspace_id: uuid.UUID
    payee_workspace_id: uuid.UUID
    amount_minor: int
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
