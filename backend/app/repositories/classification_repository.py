"""EcoSort AI - Classification Repository (Stage 5).

Data access layer for classification audit records and anonymous history.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.models import ClassificationRecord


class ClassificationRepository:
    """Encapsulates all database operations for ClassificationRecord."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, record: ClassificationRecord) -> ClassificationRecord:
        """Persists a new classification audit record with transaction safety."""
        try:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record
        except Exception:
            self.db.rollback()
            raise

    def get_by_request_id(self, request_id: str) -> Optional[ClassificationRecord]:
        """Finds a record by its unique correlation request ID."""
        stmt = select(ClassificationRecord).where(ClassificationRecord.request_id == request_id)
        return self.db.scalars(stmt).first()

    def get_by_session_id(
        self, session_id: str, limit: int = 20, offset: int = 0
    ) -> List[ClassificationRecord]:
        """Returns ordered classification records for an anonymous session."""
        stmt = (
            select(ClassificationRecord)
            .where(ClassificationRecord.session_id == session_id)
            .order_by(ClassificationRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def count_by_session_id(self, session_id: str) -> int:
        """Returns total records for a given anonymous session."""
        stmt = (
            select(func.count(ClassificationRecord.id))
            .where(ClassificationRecord.session_id == session_id)
        )
        return self.db.scalar(stmt) or 0

    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Calculates aggregate classification statistics.
        
        Zero data fabrication: returns clean zero/empty values if no data exists.
        """
        total = self.db.scalar(select(func.count(ClassificationRecord.id))) or 0
        if total == 0:
            return {
                "total_classifications": 0,
                "successful_classifications": 0,
                "failed_classifications": 0,
                "average_processing_time_ms": 0.0,
                "low_confidence_percentage": 0.0,
                "categories": [],
            }

        successful = self.db.scalar(
            select(func.count(ClassificationRecord.id)).where(
                ClassificationRecord.status == "SUCCESS"
            )
        ) or 0

        failed = total - successful

        avg_time = self.db.scalar(
            select(func.avg(ClassificationRecord.processing_time_ms))
        ) or 0.0

        low_conf_count = self.db.scalar(
            select(func.count(ClassificationRecord.id)).where(
                ClassificationRecord.ai_confidence == "LOW"
            )
        ) or 0
        low_conf_pct = round((low_conf_count / total) * 100.0, 1)

        # Category distribution
        cat_stmt = (
            select(
                ClassificationRecord.category,
                func.count(ClassificationRecord.id).label("count"),
            )
            .group_by(ClassificationRecord.category)
            .order_by(func.count(ClassificationRecord.id).desc())
        )
        cat_rows = self.db.execute(cat_stmt).all()
        categories = [
            {
                "category": row[0],
                "count": row[1],
                "percentage": round((row[1] / total) * 100.0, 1),
            }
            for row in cat_rows
        ]

        return {
            "total_classifications": total,
            "successful_classifications": successful,
            "failed_classifications": failed,
            "average_processing_time_ms": round(float(avg_time), 1),
            "low_confidence_percentage": low_conf_pct,
            "categories": categories,
        }

    def delete_older_than(self, days: int) -> int:
        """Enforces privacy retention by deleting records older than N days."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        records_to_delete = (
            select(ClassificationRecord)
            .where(ClassificationRecord.created_at < cutoff_date)
        )
        results = self.db.scalars(records_to_delete).all()
        count = len(results)
        for record in results:
            self.db.delete(record)
        self.db.commit()
        return count
