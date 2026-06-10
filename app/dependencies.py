from typing import Optional

from fastapi import Header, HTTPException, status

from app.config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    """모바일 클라이언트용 API 키 인증 (기존 분석 엔드포인트 보호)"""
    if x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


async def get_current_user(authorization: Optional[str] = Header(default=None)):
    """JWT Bearer 토큰으로 현재 사용자 조회"""
    # 순환 import 방지를 위해 함수 내부에서 import
    from app.db.repositories.user_repo import UserRepository
    from app.services.auth_service import AuthService

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[len("Bearer "):]
    payload = AuthService.decode_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다")

    user = await UserRepository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다")

    return user
