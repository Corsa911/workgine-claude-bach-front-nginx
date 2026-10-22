import enum
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID

from app.platform.database import Base


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    ESCROW_HOLD = "escrow_hold"
    ESCROW_RELEASE = "escrow_release"
    REFUND = "refund"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    payer_workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    payee_workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), default=TransactionType.ESCROW_HOLD, nullable=False
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
