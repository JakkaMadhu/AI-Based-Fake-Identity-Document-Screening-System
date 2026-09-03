from fastapi import APIRouter, Query
from typing import Optional
from ...models.schemas import PaginatedHistoryResponse, DashboardStatsResponse
from ...storage.sqlite_store import sqlite_store as store

router = APIRouter(prefix="/api/documents", tags=["history"])

@router.get("/history", response_model=PaginatedHistoryResponse)
async def get_screening_history(
    search: Optional[str] = Query(None, description="Search term for filename or ID"),
    status: Optional[str] = Query(None, description="Filter by status ('Likely Genuine', 'Suspicious', 'Requires Manual Review')"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level ('Low Risk', 'Medium Risk', 'High Risk')"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Returns paginated list of past screened documents with search and filtering.
    """
    history_data = store.list_history(
        search=search,
        status=status,
        risk_level=risk_level,
        page=page,
        page_size=page_size
    )
    return PaginatedHistoryResponse(**history_data)

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_statistics():
    """
    Returns aggregate statistics and top recent activity for the dashboard.
    """
    stats_data = store.get_dashboard_stats()
    return DashboardStatsResponse(**stats_data)
