from fastapi import HTTPException, Request, status

from app.services.cache import check_rate_limit


async def rate_limit_dependency(request: Request) -> None:
    client_key = request.client.host if request.client else "unknown"
    allowed, remaining = await check_rate_limit(client_key)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before submitting more requests.",
        )
