import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ExternalAPIError(Exception):
    """
    Custom exception for external API failures.
    Helps distinguish API-related issues from internal errors.
    """
    def __init__(self, message: str, service: str, details: Optional[dict] = None):
        super().__init__(message)
        self.service = service
        self.details = details or {}


def handle_external_api_error(service: str, error: Exception) -> Dict[str, Any]:
    """
    Converts exceptions from external APIs into a normalized error structure.
    This avoids breaking the entire pipeline when one source fails.
    """
    logger.error(f"[{service}] API error: {error}")

    return {
        "error": True,
        "service": service,
        "message": str(error),
        "fallback_used": True
    }


def safe_extract(data: dict, key: str, default=None):
    """
    Safely extracts a field from an external API response, logging if missing.
    """
    try:
        return data.get(key, default)
    except Exception as e:
        logger.warning(f"Key extraction failed: {key} — {e}")
        return default


def ensure_minimal_response(
    ip: str,
    abuse_data: dict,
    ipqs_data: dict,
    geo_data: dict
) -> Dict[str, Any]:
    """
    Ensures that even if multiple APIs fail, the pipeline returns a usable response.
    Required by assignment to handle partial failures gracefully.
    """
    return {
        "ip": ip,
        "raw_sources": {
            "abuseipdb": abuse_data,
            "ipqualityscore": ipqs_data,
            "ipapi": geo_data
        },
        "warning": "Partial threat intelligence data due to external API errors."
    }
