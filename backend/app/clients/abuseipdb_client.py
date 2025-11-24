import httpx
from app.config.settings import settings

BASE_URL = "https://api.abuseipdb.com/api/v2/check"

async def fetch_abuseipdb_data(ip: str):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                BASE_URL,
                params={"ipAddress": ip, "maxAgeInDays": 90},
                headers={
                    "Accept": "application/json",
                    "Key": settings.ABUSEIPDB_KEY
                }
            )
            resp.raise_for_status()
            return resp.json().get("data", {})
    except Exception as e:
        return {"error": str(e)}
