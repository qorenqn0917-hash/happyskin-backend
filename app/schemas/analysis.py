from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ConditionType(str, Enum):
    ACNE = "acne"
    REDNESS = "redness"
    DRYNESS = "dryness"
    OILINESS = "oiliness"
    DARK_CIRCLES = "dark_circles"
    HYPERPIGMENTATION = "hyperpigmentation"
    WRINKLES = "wrinkles"
    ENLARGED_PORES = "enlarged_pores"


class SkinCondition(BaseModel):
    type: ConditionType
    severity: Severity
    affected_area: str
    description: str


class SkinReportResponse(BaseModel):
    id: str
    device_id: str
    created_at: datetime
    overall_score: int = Field(..., ge=0, le=100)
    skin_type: str
    conditions: list[SkinCondition]
    recommendations: list[str]
    disclaimer: str = "이 분석 결과는 참고용이며 의학적 진단을 대체하지 않습니다. 피부 질환이 의심될 경우 전문의와 상담하세요."

    model_config = {"from_attributes": True}
