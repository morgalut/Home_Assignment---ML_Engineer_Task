import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_analyze_ip_success():

    # Mock LLM result
    llm_output = {
        "risk_level": "Low",
        "risk_analysis": "Clean",
        "recommendations": ["None"],
        "confidence": 0.8,
        "model_used": "gpt-4.1-mini"
    }

    async def mock_llm(*args, **kwargs):
        return llm_output

    with patch("app.services.ip_analyzer_service.generate_risk_assessment", new=mock_llm):
        resp = client.get("/api/analyze-ip?ip=8.8.8.8")
        data = resp.json()

    assert resp.status_code == 200
    assert data["risk_level"] == "Low"
    assert "raw_sources" in data
