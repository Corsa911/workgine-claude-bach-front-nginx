import uuid
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid as UUID

from app.platform.database import Base


class ExecutorProfile(Base):
    __tablename__ = "executor_profiles"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    hourly_rate_minor: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    publication_status: Mapped[str] = mapped_column(
        String(50), default="draft", nullable=False
    )
