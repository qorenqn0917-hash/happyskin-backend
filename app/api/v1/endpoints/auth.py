from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repositories.user_repo import UserRepository
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest):
    """회원가입 — 이메일 중복 체크 후 사용자 생성 및 토큰 발급"""
    existing = await UserRepository.get_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다",
        )

    password_hash = AuthService.hash_password(body.password)
    user = await UserRepository.create(
        name=body.name,
        email=body.email,
        password_hash=password_hash,
    )

    token = AuthService.create_access_token(user_id=user.id, email=user.email)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """로그인 — 이메일/비밀번호 검증 후 토큰 발급"""
    user = await UserRepository.get_by_email(body.email)
    if not user or not AuthService.verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
        )

    token = AuthService.create_access_token(user_id=user.id, email=user.email)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회 (Authorization: Bearer <token> 필요)"""
    return UserResponse(
        user_id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
    )
