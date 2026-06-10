import base64
import json
import logging

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.analysis import ConditionType, Severity, SkinCondition, SkinReportResponse

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)

_SYSTEM_PROMPT = """당신은 전문 피부 분석 AI 어시스턴트입니다.
제공된 얼굴 이미지를 분석하고 구조화된 JSON 응답을 반환하세요.
모든 피부 톤에 대해 객관적으로 분석하고, 의학적 우려가 있을 경우 반드시 피부과 전문의 상담을 권장하세요.

절대 규칙: description, affected_area, recommendations 필드는 반드시 한국어로만 작성하세요.
아래 열거형 값(enum)만 영어로 유지하세요: skin_type, conditions[].type, conditions[].severity

Return ONLY valid JSON matching this schema:
{
  "overall_score": <int 0-100, 높을수록 건강한 피부>,
  "skin_type": <반드시 다음 중 하나만: "oily"|"dry"|"combination"|"normal"|"sensitive">,
  "conditions": [
    {
      "type": <반드시 다음 중 하나만: acne|redness|dryness|oiliness|dark_circles|hyperpigmentation|wrinkles|enlarged_pores>,
      "severity": <반드시 다음 중 하나만: "none"|"mild"|"moderate"|"severe">,
      "affected_area": <한국어로 피부 부위, 예: "이마", "볼", "코", "턱", "T존", "눈 아래">,
      "description": <한국어로 1-2문장 관찰 내용. 영어 사용 금지.>
    }
  ],
  "recommendations": [<한국어로 3-5개의 스킨케어 조언. 영어 사용 금지.>]
}"""


class AIService:
    @staticmethod
    async def analyze(image_data: bytes, skin_type: str, concerns: str) -> dict:
        b64 = base64.standard_b64encode(image_data).decode()
        context = f"사용자 피부 타입: {skin_type}. 주요 피부 고민: {concerns or '없음'}. 모든 텍스트 응답은 한국어로 작성하세요."
        response = await _client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=1024,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                        {"type": "text", "text": context},
                    ],
                },
            ],
        )
        raw = response.choices[0].message.content
        logger.warning("=== GPT 원본 응답 ===\n%s", raw)
        result = json.loads(raw)
        logger.warning("=== 파싱된 점수: %s, 피부타입: %s ===", result.get("overall_score"), result.get("skin_type"))
        valid_types = {"acne", "redness", "dryness", "oiliness", "dark_circles", "hyperpigmentation", "wrinkles", "enlarged_pores"}
        result["conditions"] = [c for c in result.get("conditions") or [] if c.get("type") in valid_types]
        return result
