
import asyncio
from typing import Any, Dict

from app.clients.abuseipdb_client import fetch_abuseipdb_data
from app.clients.ipqualityscore_client import fetch_ipqs_data
from app.clients.ipapi_client import fetch_ipapi_data

from app.utils.normalizer import normalize_all_sources
from app.ai.llm_risk_analyzer import generate_risk_assessment
from app.cache.redis_cache import cache_get, cache_set, redis_cache, make_cache_key
from app.utils.error_handlers import ensure_minimal_response



# Cache Validation — Prevent Serving Old/Invalid Gemini Outputs

def is_cached_entry_valid(entry: dict) -> bool:
    """
    Validate cached LLM results.
    """

    if not isinstance(entry, dict):
        return False

    required = ["risk_level", "risk_analysis", "recommendations", "model_used", "confidence"]
    for key in required:
        if key not in entry:
            return False

    if entry["risk_level"] not in ("Low", "Medium", "High"):
        return False

    # If model_used contains Gemini, reject it.
    model = str(entry["model_used"]).lower()
    if "gemini" in model or model == "none" or model == "null":
        return False

    # Remove old Gemini error text
    if "gemini" in entry["risk_analysis"].lower():
        return False

    conf = entry.get("confidence")
    if not isinstance(conf, (int, float)):
        return False
    if not (0 <= conf <= 1):
        return False

    if not isinstance(entry["recommendations"], list):
        return False

    return True



# MAIN PIPELINE


async def analyze_ip(ip: str) -> Dict[str, Any]:


    # 1. VERSIONED CACHE CHECK

    cached = cache_get(ip, model="openai")

    if cached is not None:
        print(f"[CACHE] Found cached entry for {ip}")

        if is_cached_entry_valid(cached):
            print(f"[CACHE] VALID cache → Using cached result for {ip}")
            return cached

        print(f"[CACHE] INVALID cache for {ip} → deleting")
        redis_cache.delete(make_cache_key(ip, "openai"))


    # 2. EXTERNAL API LOOKUP

    try:
        abuse_data, ipqs_data, geo_data = await asyncio.gather(
            fetch_abuseipdb_data(ip),
            fetch_ipqs_data(ip),
            fetch_ipapi_data(ip),
        )
    except Exception as e:
        print("[ERROR] External API Failure:", e)

        minimal = ensure_minimal_response(ip, {}, {}, {})
        minimal["warning"] = f"External API failure: {e}"

        return {
            **minimal,
            "risk_level": "unknown",
            "risk_analysis": "External APIs failed — no threat Intel.",
            "recommendations": [],
            "confidence": 0.0,
            "model_used": None,
        }


    # 3. ALL EXTERNAL APIs FAILED?

    all_failed = (
        isinstance(abuse_data, dict) and "error" in abuse_data and
        isinstance(ipqs_data, dict) and "error" in ipqs_data and
        isinstance(geo_data, dict) and "error" in geo_data
    )

    if all_failed:
        print("[WARN] ALL external threat feeds failed.")

        minimal = ensure_minimal_response(ip, abuse_data, ipqs_data, geo_data)

        try:
            ai_result = await generate_risk_assessment(minimal)
        except Exception as e:
            print("[LLM ERROR]", e)
            ai_result = {
                "risk_level": "unknown",
                "risk_analysis": "AI model could not generate assessment.",
                "recommendations": [],
                "confidence": 0.0,
                "model_used": None,
            }

        return {**minimal, **ai_result}


    # 4. NORMALIZE

    normalized = normalize_all_sources(ip, abuse_data, ipqs_data, geo_data)


    # 5. BUILD DATASET FOR LLM

    full_dataset = {
        "normalized": normalized,
        "raw_sources": {
            "abuseipdb": abuse_data,
            "ipqualityscore": ipqs_data,
            "ipapi": geo_data
        }
    }


    # 6. RUN OPENAI LLM

    try:
        print("[LLM] Running OpenAI risk assessment…")
        ai_result = await generate_risk_assessment(full_dataset)
    except Exception as e:
        print("[LLM ERROR] OpenAI exception:", e)
        ai_result = {
            "risk_level": "unknown",
            "risk_analysis": "AI model failed.",
            "recommendations": [],
            "confidence": 0.0,
            "model_used": None,
        }


    # 7. MERGE FINAL RESULT

    final_result: Dict[str, Any] = {
        **normalized,
        **ai_result,
        "full_input_to_llm": full_dataset,
    }


    # 8. STORE TO VERSIONED CACHE IF VALID

    model_name = final_result.get("model_used", "openai")

    if final_result["risk_level"] != "unknown":
        cache_set(ip, final_result, model=model_name)
        print(f"[CACHE] Stored valid result for {ip}")
    else:
        print(f"[CACHE] Not storing fallback result for {ip}")

    return final_result
