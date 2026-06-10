import json
from unittest.mock import AsyncMock, patch

import pytest


MOCK_AI_RESPONSE = {
    "overall_score": 72,
    "skin_type": "combination",
    "conditions": [
        {
            "type": "acne",
            "severity": "mild",
            "affected_area": "forehead",
            "description": "A few small comedones visible on the forehead.",
        }
    ],
    "recommendations": [
        "Use a gentle foaming cleanser twice daily.",
        "Apply a non-comedogenic moisturiser.",
        "Consult a dermatologist if breakouts persist.",
    ],
}


@pytest.mark.anyio
async def test_analyze_returns_report(client, sample_image_bytes):
    with patch(
        "app.services.ai_service.AIService.analyze",
        new=AsyncMock(return_value=MOCK_AI_RESPONSE),
    ):
        response = await client.post(
            "/api/v1/analysis/",
            data={"device_id": "device-123", "skin_type": "combination"},
            files={"image": ("face.jpg", sample_image_bytes, "image/jpeg")},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["overall_score"] == 72
    assert body["skin_type"] == "combination"
    assert len(body["conditions"]) == 1
    assert "disclaimer" in body


@pytest.mark.anyio
async def test_analyze_rejects_missing_api_key(sample_image_bytes):
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/analysis/",
            data={"device_id": "device-123"},
            files={"image": ("face.jpg", sample_image_bytes, "image/jpeg")},
        )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_history_empty_for_new_device(client):
    response = await client.get("/api/v1/history/unknown-device-xyz")
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0
