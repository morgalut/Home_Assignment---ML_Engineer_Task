import httpx
from app.config.settings import settings

BASE_URL = "https://ipqualityscore.com/api/json/ip"

async def fetch_ipqs_data(ip: str):
    url = f"{BASE_URL}/{settings.IPQS_KEY}/{ip}"

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": str(e)}
