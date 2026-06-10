import base64
import math

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select

from app.db.database import AsyncSessionLocal
from app.models.skin import SkinAnalysis
from app.schemas.common import PaginatedResponse


class AnalysisRepository:
    @staticmethod
    async def save(device_id: str, report: dict, image_data: bytes) -> SkinAnalysis:
        thumbnail_b64 = base64.b64encode(image_data).decode()
        record = SkinAnalysis(
            device_id=device_id,
            overall_score=report["overall_score"],
            skin_type=report["skin_type"],
            conditions=report["conditions"],
            recommendations=report["recommendations"],
            image_blob=thumbnail_b64,
        )
        async with AsyncSessionLocal() as session:
            session.add(record)
            await session.commit()
            await session.refresh(record)
        return record

    @staticmethod
    async def get_by_device(
        device_id: str, page: int, page_size: int
    ) -> PaginatedResponse:
        offset = (page - 1) * page_size
        async with AsyncSessionLocal() as session:
            total = await session.scalar(
                select(func.count()).where(SkinAnalysis.device_id == device_id)
            )
            result = await session.execute(
                select(SkinAnalysis)
                .where(SkinAnalysis.device_id == device_id)
                .order_by(SkinAnalysis.created_at.desc())
                .offset(offset)
                .limit(page_size)
            )
            items = result.scalars().all()
        return PaginatedResponse(
            items=list(items),
            total=total,
            page=page,
            page_size=page_size,
            has_next=page < math.ceil(total / page_size),
        )

    @staticmethod
    async def get_one(device_id: str, report_id: str) -> SkinAnalysis:
        async with AsyncSessionLocal() as session:
            record = await session.scalar(
                select(SkinAnalysis).where(
                    SkinAnalysis.id == report_id,
                    SkinAnalysis.device_id == device_id,
                )
            )
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        return record

    @staticmethod
    async def delete(device_id: str, report_id: str) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(SkinAnalysis).where(
                    SkinAnalysis.id == report_id,
                    SkinAnalysis.device_id == device_id,
                )
            )
            await session.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
