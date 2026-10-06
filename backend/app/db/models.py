"""EcoSort AI - SQLAlchemy ORM Models (Stage 5).

Models for structured classification audit logs and anonymous user feedback.
STRICT PRIVACY POLICY: Raw image binaries and image URLs are never stored.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ClassificationRecord(Base):
    """Stores structured metadata for each completed waste classification event.
    
    Serves auditing, analytical metrics, and anonymous session history without
    compromising privacy or persisting binary image contents.
    """

    __tablename__ = "classification_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    input_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "IMAGE" | "TEXT"
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    material: Mapped[str] = mapped_column(String(100), nullable=False)
    condition: Mapped[str] = mapped_column(String(100), nullable=False)
    contamination: Mapped[str] = mapped_column(String(20), nullable=False)  # "NONE" | "LOW" | "MEDIUM" | "HIGH" | "UNKNOWN"
    ai_confidence: Mapped[str] = mapped_column(String(10), nullable=False)  # "HIGH" | "MEDIUM" | "LOW"
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    recommendation_confidence: Mapped[str] = mapped_column(String(10), nullable=False)
    warning_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="SUCCESS", index=True, nullable=False)  # "SUCCESS" | "FAILED"
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    feedbacks: Mapped[List["Feedback"]] = relationship(
        "Feedback",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ClassificationRecord(request_id={self.request_id}, item={self.item_name}, category={self.category})>"


class Feedback(Base):
    """Stores user ratings and helpfulness reviews linked to a classification request."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("classification_records.request_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Controlled 1 to 5
    feedback_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # HELPFUL | NOT_HELPFUL | INCORRECT_CATEGORY | INCORRECT_IDENTIFICATION | UNCLEAR_GUIDANCE | OTHER
    comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )

    # Relationship back to ClassificationRecord
    classification: Mapped["ClassificationRecord"] = relationship(
        "ClassificationRecord",
        back_populates="feedbacks",
    )

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, request_id={self.request_id}, type={self.feedback_type}, rating={self.rating})>"
