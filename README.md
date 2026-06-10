# HappySkin Skin Analysis API

FastAPI 기반 피부 분석 백엔드 서버입니다. GPT-4o Vision으로 피부를 분석하고, 사용자 인증(JWT)을 제공합니다.

## 시작하기

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

`.env.example`을 복사해 `.env`로 이름을 바꾸고 값을 채워주세요.

---

## 인증 API (`/api/v1/auth`)

### POST /api/v1/auth/signup — 회원가입

**Request**
```json
{
  "name": "홍길동",
  "email": "user@example.com",
  "password": "mypassword123",
  "password_confirm": "mypassword123"
}
```

**Response 201**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "a1b2c3d4-...",
  "name": "홍길동",
  "email": "user@example.com"
}
```

**오류**
| 코드 | 원인 |
|------|------|
| 409  | 이미 사용 중인 이메일 |
| 422  | 비밀번호 8자 미만 / 비밀번호 불일치 / 이메일 형식 오류 |

---

### POST /api/v1/auth/login — 로그인

**Request**
```json
{
  "email": "user@example.com",
  "password": "mypassword123"
}
```

**Response 200**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "a1b2c3d4-...",
  "name": "홍길동",
  "email": "user@example.com"
}
```

**오류**
| 코드 | 원인 |
|------|------|
| 401  | 이메일 또는 비밀번호 불일치 |

---

### GET /api/v1/auth/me — 내 정보 조회

**Headers**
```
Authorization: Bearer <access_token>
```

**Response 200**
```json
{
  "user_id": "a1b2c3d4-...",
  "name": "홍길동",
  "email": "user@example.com",
  "created_at": "2026-06-07T12:00:00Z"
}
```

**오류**
| 코드 | 원인 |
|------|------|
| 401  | 토큰 없음 / 만료 / 유효하지 않음 |

---

## 분석 API (`/api/v1/analysis`)

> `X-API-Key` 헤더에 `API_SECRET_KEY` 값을 담아 전송해야 합니다.

### POST /api/v1/analysis/ — 피부 분석

**Headers**
```
X-API-Key: <api_secret_key>
Content-Type: multipart/form-data
```

**Form Data**
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `image` | file | ✅ | JPEG/PNG (최대 5 MB) |
| `device_id` | string | ✅ | 기기 고유 ID |
| `skin_type` | string | | dry / oily / combination / normal |

**Response 201**
```json
{
  "report_id": "b2c3d4e5-...",
  "device_id": "device-abc",
  "overall_score": 72,
  "skin_type": "combination",
  "conditions": [
    {
      "type": "acne",
      "severity": "mild",
      "affected_area": "forehead",
      "description": "이마에 작은 면포가 일부 관찰됩니다."
    }
  ],
  "recommendations": [
    "하루 2회 부드러운 폼 클렌저 사용을 권장합니다.",
    "논코메도제닉 보습제를 바르세요."
  ],
  "disclaimer": "본 결과는 AI 참고 정보이며 의학적 진단을 대체하지 않습니다.",
  "analyzed_at": "2026-06-07T12:00:00Z"
}
```

---

## 기록 API (`/api/v1/history`)

### GET /api/v1/history/{device_id}

분석 기록 목록 (최신순).

**Response 200**
```json
{
  "items": [ { "report_id": "...", "overall_score": 72, "analyzed_at": "..." } ],
  "total": 1
}
```

### GET /api/v1/history/{device_id}/{report_id}

단일 기록 상세 조회. (분석 응답과 동일한 형태)

### DELETE /api/v1/history/{device_id}/{report_id}

기록 삭제. **Response 204 No Content**

---

## 테스트 실행

```bash
pytest tests/ -v
```

---

## 환경 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | `sk-proj-...` |
| `API_SECRET_KEY` | 모바일 클라이언트 인증 키 | `test3260` |
| `DATABASE_URL` | SQLite 경로 | `sqlite+aiosqlite:///./skin_analysis.db` |
| `JWT_SECRET_KEY` | JWT 서명 비밀키 (변경 필수) | `change-me-...` |
| `JWT_ALGORITHM` | JWT 알고리즘 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간 (분) | `10080` (7일) |
