import httpx
from app.config.settings import settings

BASE_URL = "https://ipapi.co"

async def fetch_ipapi_data(ip: str):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{BASE_URL}/{ip}/json/")
            resp.raise_for_status()
            data = resp.json()
            return {
                "hostname": data.get("hostname"),
                "country": data.get("country_name"),
                "isp": data.get("org")
            }
    except Exception as e:
        return {"error": str(e)}
