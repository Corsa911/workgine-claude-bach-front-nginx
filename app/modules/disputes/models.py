import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy import Uuid as UUID

from app.platform.database import Base


class DisputeStatus(str, enum.Enum):
    OPENED = "opened"
    IN_PROGRESS = "in_progress"
    RESOLVED_REFUND = "resolved_refund"  # Деньги возвращены клиенту
    RESOLVED_PAYOUT = "resolved_payout"  # Деньги выплачены фрилансеру


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    initiator_workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    reason = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        SQLEnum(DisputeStatus), default=DisputeStatus.OPENED, nullable=False
    )
    resolution_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
