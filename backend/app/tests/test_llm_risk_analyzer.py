import pytest
from unittest.mock import patch

from app.ai.llm_risk_analyzer import generate_risk_assessment


@pytest.mark.asyncio
async def test_llm_valid_json():
    # Valid JSON output the pipeline expects
    final_json = {
        "risk_level": "Low",
        "risk_analysis": "Good",
        "recommendations": ["Monitor"],
        "confidence": 0.9,
        "model_used": "gpt-4.1-mini"
    }

    # This is what the compression step should return
    compressed_json = {
        "signals": ["normal"],
        "summary": "clean"
    }

    async def mock_create(*args, **kwargs):
        class FakeChoice:
            message = type("obj", (object,), {"content": '{"risk_level":"Low","risk_analysis":"Good","recommendations":["Monitor"],"confidence":0.9}'})
        return type("obj", (object,), {"choices": [FakeChoice()]})

    async def mock_compress_chunk(*args, **kwargs):
        return compressed_json

    with patch("app.ai.llm_risk_analyzer.compress_chunk", new=mock_compress_chunk):
        with patch("app.ai.llm_risk_analyzer.client.chat.completions.create", new=mock_create):
            result = await generate_risk_assessment({"a": 1})

            assert result["risk_level"] == "Low"
            assert result["confidence"] == 0.9
            assert result["recommendations"] == ["Monitor"]
