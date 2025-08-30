import pytest
from httpx import AsyncClient

from app.enums import ReportStatusTypes


@pytest.mark.asyncio
async def test_create_report_success(authenticated_client: AsyncClient, test_user_2):
    """Test successful report creation."""
    report_data = {
        "to_user_id": str(test_user_2.id),
        "reason": "Inappropriate behavior",
    }

    response = await authenticated_client.post("/v1/reports", json=report_data)

    assert response.status_code == 200
    data = response.json()
    assert data["to_user_id"] == report_data["to_user_id"]
    assert data["reason"] == report_data["reason"]
    assert data["status"] == ReportStatusTypes.pending.value
    assert "id" in data
    assert "from_user_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_report_self_report(authenticated_client: AsyncClient, test_user):
    """Test reporting yourself (should fail)."""
    report_data = {
        "to_user_id": str(test_user.id),
        "reason": "Self report attempt",
    }

    response = await authenticated_client.post("/v1/reports", json=report_data)

    assert response.status_code == 400
    assert "Cannot report yourself" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_duplicate_report(authenticated_client: AsyncClient, test_report):
    """Test creating duplicate report (should fail)."""
    report_data = {
        "to_user_id": str(test_report.to_user_id),
        "reason": "Duplicate report attempt",
    }

    response = await authenticated_client.post("/v1/reports", json=report_data)

    assert response.status_code == 400
    assert "Report already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_report_invalid_user_id(authenticated_client: AsyncClient):
    """Test creating report with invalid user ID."""
    report_data = {
        "to_user_id": "invalid-uuid",
        "reason": "Test reason",
    }

    response = await authenticated_client.post("/v1/reports", json=report_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_reports_user(authenticated_client: AsyncClient, test_report):
    """Test getting reports as regular user (only own reports)."""
    response = await authenticated_client.get("/v1/reports")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should only see own reports
    assert all(report["from_user_id"] == str(test_report.from_user_id) for report in data)


@pytest.mark.asyncio
async def test_get_reports_superuser(superuser_client: AsyncClient, test_report):
    """Test getting reports as superuser (can see all reports)."""
    response = await superuser_client.get("/v1/reports")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check if test_report is in the response
    report_ids = [report["id"] for report in data]
    assert test_report.id in report_ids


@pytest.mark.asyncio
async def test_get_reports_with_filters_superuser(superuser_client: AsyncClient, test_report):
    """Test getting reports with filters as superuser."""
    # Test filtering by status
    response = await superuser_client.get(f"/v1/reports?status={ReportStatusTypes.pending.value}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(report["status"] == ReportStatusTypes.pending.value for report in data)

    # Test filtering by to_user_id
    response = await superuser_client.get(f"/v1/reports?to_user_id={test_report.to_user_id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(report["to_user_id"] == str(test_report.to_user_id) for report in data)


@pytest.mark.asyncio
async def test_get_reports_pagination(authenticated_client: AsyncClient):
    """Test reports pagination."""
    response = await authenticated_client.get("/v1/reports?limit=1&offset=0")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1


@pytest.mark.asyncio
async def test_get_report_by_id_owner(authenticated_client: AsyncClient, test_report):
    """Test getting specific report by ID as owner."""
    response = await authenticated_client.get(f"/v1/reports/{test_report.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_report.id
    assert data["reason"] == test_report.reason
    assert data["status"] == test_report.status.value


@pytest.mark.asyncio
async def test_get_report_by_id_superuser(superuser_client: AsyncClient, test_report):
    """Test getting specific report by ID as superuser."""
    response = await superuser_client.get(f"/v1/reports/{test_report.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_report.id
    assert data["reason"] == test_report.reason


@pytest.mark.asyncio
async def test_get_report_by_id_not_owner(authenticated_client: AsyncClient, session, test_user_2):
    """Test getting report by ID as non-owner (should fail)."""
    # Create a report from test_user_2 to someone else
    from uuid import uuid4

    from app.models.user import Report

    other_report = Report(
        from_user_id=test_user_2.id,
        to_user_id=uuid4(),
        reason="Other user's report",
        status=ReportStatusTypes.pending,
    )
    session.add(other_report)
    await session.commit()
    await session.refresh(other_report)

    response = await authenticated_client.get(f"/v1/reports/{other_report.id}")

    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_report_by_id_not_found(authenticated_client: AsyncClient):
    """Test getting non-existent report."""
    response = await authenticated_client.get("/v1/reports/99999")

    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_report_status_superuser(superuser_client: AsyncClient, test_report):
    """Test updating report status as superuser."""
    update_data = {
        "status": ReportStatusTypes.reviewing.value,
    }

    response = await superuser_client.patch(f"/v1/reports/{test_report.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == update_data["status"]
    assert data["id"] == test_report.id


@pytest.mark.asyncio
async def test_update_report_status_user(authenticated_client: AsyncClient, test_report):
    """Test updating report status as regular user (should fail)."""
    update_data = {
        "status": ReportStatusTypes.reviewing.value,
    }

    response = await authenticated_client.patch(f"/v1/reports/{test_report.id}", json=update_data)

    assert response.status_code == 403
    assert "Only superusers can update reports" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_report_status_not_found(superuser_client: AsyncClient):
    """Test updating non-existent report."""
    update_data = {
        "status": ReportStatusTypes.reviewing.value,
    }

    response = await superuser_client.patch("/v1/reports/99999", json=update_data)

    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_report_status_invalid_status(superuser_client: AsyncClient, test_report):
    """Test updating report with invalid status."""
    update_data = {
        "status": "invalid_status",
    }

    response = await superuser_client.patch(f"/v1/reports/{test_report.id}", json=update_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_delete_report_superuser(superuser_client: AsyncClient, test_report):
    """Test deleting report as superuser."""
    response = await superuser_client.delete(f"/v1/reports/{test_report.id}")

    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["detail"]

    # Verify report is deleted
    get_response = await superuser_client.get(f"/v1/reports/{test_report.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_report_user(authenticated_client: AsyncClient, test_report):
    """Test deleting report as regular user (should fail)."""
    response = await authenticated_client.delete(f"/v1/reports/{test_report.id}")

    assert response.status_code == 403
    assert "Only superusers can delete reports" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_report_not_found(superuser_client: AsyncClient):
    """Test deleting non-existent report."""
    response = await superuser_client.delete("/v1/reports/99999")

    assert response.status_code == 404
    assert "Report not found" in response.json()["detail"]
