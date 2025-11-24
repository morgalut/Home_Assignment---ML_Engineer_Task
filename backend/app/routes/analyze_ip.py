
from fastapi import APIRouter, HTTPException, Query
from app.utils.ip_validator import validate_ip
from app.services.ip_analyzer_service import analyze_ip

router = APIRouter(prefix="/api")

@router.get("/analyze-ip")
async def analyze_ip_route(ip: str = Query(...)):
    if not validate_ip(ip):
        raise HTTPException(status_code=400, detail="Invalid IP address")

    result = await analyze_ip(ip)
    return result
