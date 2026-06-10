import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SkinAnalysis(Base):
    __tablename__ = "skin_analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    skin_type: Mapped[str] = mapped_column(String(32), nullable=False)
    conditions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    image_blob: Mapped[bytes] = mapped_column(Text, nullable=True)  # base64 thumbnail
    user_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
