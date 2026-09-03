from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AnalysisRequest
from app.db.session import get_db
from app.schemas.verification import HistoryItemOut

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=list[HistoryItemOut])
async def list_history(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnalysisRequest).order_by(AnalysisRequest.created_at.desc()).limit(limit)
    )
    requests = result.scalars().all()
    return [
        HistoryItemOut(
            request_id=r.id,
            content_type=r.content_type.value,
            status=r.status.value,
            input_summary=r.input_summary,
            verdict=r.verdict.value if r.verdict else None,
            confidence=r.confidence,
            created_at=r.created_at,
        )
        for r in requests
    ]
