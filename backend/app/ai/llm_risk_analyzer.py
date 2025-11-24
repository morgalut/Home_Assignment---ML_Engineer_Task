
import json
import re
import asyncio
from typing import List, Optional

from pydantic import BaseModel, ValidationError
from openai import AsyncOpenAI
from app.config.settings import settings


# OpenAI Client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Output Schema
class LLMResponse(BaseModel):
    risk_level: str
    risk_analysis: str
    recommendations: List[str]
    confidence: float
    model_used: Optional[str] = None


# JSON Extraction
def extract_json(text: str):
    if not text:
        return None

    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            return None
    return None


# Normalize risk level
def normalize_risk(parsed: dict):
    rl = parsed.get("risk_level", "").lower()

    if rl.startswith("low"):
        parsed["risk_level"] = "Low"
    elif rl.startswith("med"):
        parsed["risk_level"] = "Medium"
    elif rl.startswith("high"):
        parsed["risk_level"] = "High"
    else:
        parsed["risk_level"] = "Medium"

    return parsed


# Chunk Text
def chunk_text(text: str, size=2000):
    return [text[i:i + size] for i in range(0, len(text), size)]


# Semantic Compression
async def compress_chunk(model: str, text_chunk: str):
    prompt = f"""
Extract cyber-security relevant indicators from this text.

RULES:
- Always return valid JSON
- Never return empty output
- If text is poorly formatted, extract what is possible

CHUNK:
{text_chunk}

Return ONLY JSON:
{{
  "signals": ["list important indicators"],
  "summary": "short compressed analysis"
}}
"""

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw = response.choices[0].message.content
        return extract_json(raw)

    except Exception as e:
        print("[ERROR] Chunk compression failed:", e)
        return None


# JSON Repair
async def attempt_json_fix(model: str, broken_text: str):
    prompt = f"""
Repair the following into valid JSON ONLY.

TEXT:
{broken_text}

Return ONLY valid JSON:
"""

    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return extract_json(resp.choices[0].message.content)
    except:
        return None


# OpenAI model order (fast → accurate)
OPENAI_MODEL_ORDER = [
    "gpt-4.1-mini",
    "gpt-4.1"
]


# FINAL RISK ASSESSMENT PIPELINE
async def generate_risk_assessment(full_dataset: dict):

    data_json = json.dumps(full_dataset)
    chunks = chunk_text(data_json, size=2000)

    print(f"[LLM] Generated {len(chunks)} chunks")

    for model_name in OPENAI_MODEL_ORDER:

        print(f"[LLM] Using model: {model_name}")

        # --------------------------------------------------------
        # 1. Compress all chunks in parallel
        # --------------------------------------------------------
        tasks = [compress_chunk(model_name, ch) for ch in chunks]
        compressed = await asyncio.gather(*tasks)

        compressed = [c for c in compressed if c]

        # Fallback if compression fails
        if not compressed:
            print("[LLM WARNING] No compressed chunks produced. Using raw truncated dataset.")
            compressed = [{
                "signals": [],
                "summary": data_json[:4000]
            }]

        compressed_json = json.dumps(compressed)

        # --------------------------------------------------------
        # 2. Final risk analysis prompt
        # --------------------------------------------------------
        final_prompt = f"""
You are a senior cybersecurity threat intelligence analyst.

Below are all compressed indicators from multiple threat intelligence sources:

{compressed_json}

Using ALL indicators, produce STRICT JSON ONLY:

{{
  "risk_level": "Low" | "Medium" | "High",
  "risk_analysis": "text",
  "recommendations": ["list actions"],
  "confidence": number_between_0_and_1
}}
"""

        # --------------------------------------------------------
        # 3. Try generating risk assessment (3 attempts)
        # --------------------------------------------------------
        for attempt in range(3):
            print(f"[LLM] Final attempt {attempt+1} on model {model_name}")

            try:
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": final_prompt}],
                    temperature=0.1
                )

                raw = response.choices[0].message.content
                parsed = extract_json(raw)

                # Try repair if invalid JSON
                if not parsed:
                    parsed = await attempt_json_fix(model_name, raw)

                if not parsed:
                    print("[LLM] JSON extraction FAILED")
                    continue

                parsed = normalize_risk(parsed)
                parsed["model_used"] = model_name

                validated = LLMResponse(**parsed)
                return validated.model_dump()

            except Exception as e:
                print("[LLM ERROR]", e)
                continue

    # --------------------------------------------------------
    # If everything fails
    # --------------------------------------------------------
    return {
        "risk_level": "unknown",
        "risk_analysis": "AI model could not generate a valid assessment.",
        "recommendations": [],
        "confidence": 0.0,
        "model_used": None
    }
