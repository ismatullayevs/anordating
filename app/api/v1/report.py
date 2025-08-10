from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.api.dependencies import CurrentUserDep, DbDep
from app.enums import ReportStatusTypes
from app.schemas.report import ReportInSchema, ReportOutSchema, ReportUpdateSchema
from app.services.report import (
    create_report,
    delete_report,
    get_report_by_id,
    get_reports,
    update_report_status,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportOutSchema)
async def create_user_report(
    db: DbDep,
    current_user: CurrentUserDep,
    report_data: ReportInSchema,
):
    """Creates a new report."""
    if current_user.id == report_data.to_user_id:
        raise HTTPException(status_code=400, detail="Cannot report yourself")

    try:
        report = await create_report(db, current_user.id, report_data)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[ReportOutSchema])
async def get_user_reports(
    db: DbDep,
    current_user: CurrentUserDep,
    from_user_id: UUID | None,
    to_user_id: UUID | None,
    status: ReportStatusTypes | None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Fetches reports. Regular users can only see their own reports, superusers can see all."""
    if not current_user.is_superuser:
        if from_user_id is not None and from_user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own reports",
            )
        from_user_id = current_user.id
        to_user_id = None

    reports = await get_reports(
        db,
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return reports


@router.get("/{report_id}", response_model=ReportOutSchema)
async def get_report(db: DbDep, current_user: CurrentUserDep, report_id: int):
    """Fetches a specific report by ID."""
    report = await get_report_by_id(db, report_id)
    if not current_user.is_superuser and (
        not report or report.from_user_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.patch("/{report_id}", response_model=ReportOutSchema)
async def update_report(
    db: DbDep,
    current_user: CurrentUserDep,
    report_id: int,
    update_data: ReportUpdateSchema,
):
    """Updates a report's status. Only superusers can update reports."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can update reports",
        )

    try:
        report = await update_report_status(db, report_id, update_data)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{report_id}")
async def delete_user_report(db: DbDep, current_user: CurrentUserDep, report_id: int):
    """Deletes a report. Only superusers can delete reports."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can delete reports",
        )

    try:
        await delete_report(db, report_id)
        return {"detail": "Report deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
