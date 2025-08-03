from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Report
from app.schemas.report import ReportInSchema, ReportUpdateSchema
from app.enums import ReportStatusTypes


async def create_report(
    db: AsyncSession, from_user_id: UUID, report_data: ReportInSchema
) -> Report:
    """Creates a new report."""
    try:
        report = Report(
            from_user_id=from_user_id,
            to_user_id=report_data.to_user_id,
            reason=report_data.reason,
            status=ReportStatusTypes.pending
        )
        db.add(report)
        await db.commit()
        return report
    except Exception as e:
        await db.rollback()
        raise e


async def get_reports(
    db: AsyncSession, 
    from_user_id: Optional[UUID] = None,
    to_user_id: Optional[UUID] = None,
    status: Optional[ReportStatusTypes] = None,
    limit: int = 100,
    offset: int = 0
) -> list[Report]:
    """Fetches reports with optional filters."""
    query = select(Report)
    
    if from_user_id:
        query = query.where(Report.from_user_id == from_user_id)
    if to_user_id:
        query = query.where(Report.to_user_id == to_user_id)
    if status:
        query = query.where(Report.status == status)
    
    query = query.order_by(Report.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.scalars(query)
    return list(result.all())


async def get_report_by_id(db: AsyncSession, report_id: int) -> Report | None:
    """Fetches a report by ID."""
    return await db.scalar(select(Report).where(Report.id == report_id))


async def update_report_status(
    db: AsyncSession, report_id: int, update_data: ReportUpdateSchema
) -> Report:
    """Updates a report's status."""
    try:
        report = await db.scalar(select(Report).where(Report.id == report_id))
        if not report:
            raise ValueError("Report not found")
        
        report.status = update_data.status
        await db.commit()
        await db.refresh(report)
        return report
    except Exception as e:
        await db.rollback()
        raise e


async def delete_report(db: AsyncSession, report_id: int) -> None:
    """Deletes a report."""
    try:
        report = await db.scalar(select(Report).where(Report.id == report_id))
        if not report:
            raise ValueError("Report not found")
        
        await db.delete(report)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e
