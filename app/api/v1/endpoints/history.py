from fastapi import APIRouter, Depends, Query

from app.dependencies import verify_api_key
from app.schemas.analysis import SkinReportResponse
from app.schemas.common import PaginatedResponse
from app.db.repositories.analysis_repo import AnalysisRepository

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/{device_id}", response_model=PaginatedResponse[SkinReportResponse])
async def get_history(
    device_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    return await AnalysisRepository.get_by_device(
        device_id=device_id, page=page, page_size=page_size
    )


@router.get("/{device_id}/{report_id}", response_model=SkinReportResponse)
async def get_report(device_id: str, report_id: str):
    return await AnalysisRepository.get_one(device_id=device_id, report_id=report_id)


@router.delete("/{device_id}/{report_id}", status_code=204)
async def delete_report(device_id: str, report_id: str):
    await AnalysisRepository.delete(device_id=device_id, report_id=report_id)
