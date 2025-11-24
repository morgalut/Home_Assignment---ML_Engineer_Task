from app.utils.normalizer import normalize_all_sources

def test_normalizer_minimal():
    abuse = {"abuseConfidenceScore": 10, "totalReports": 5}
    ipqs = {"fraud_score": 40, "proxy": False}
    geo = {"hostname": "host", "country": "US", "isp": "ISP"}

    result = normalize_all_sources("8.8.8.8", abuse, ipqs, geo)

    assert result["ip"] == "8.8.8.8"
    assert result["abuse_score"] == 10
    assert result["recent_reports"] == 5
    assert result["vpn_proxy"] is False
    assert result["fraud_score"] == 40
    assert result["hostname"] == "host"
    assert "raw_sources" in result
