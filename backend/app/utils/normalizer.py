from app.utils.error_handlers import safe_extract


def normalize_all_sources(ip, abuse_data, ipqs_data, geo_data):
    """
    Normalize responses from:
    - AbuseIPDB
    - IPQualityScore
    - IPAPI

    Ensures consistent structured output even when some APIs fail.
    """

    # Extracted fields (safe extraction prevents crashes)
    hostname = safe_extract(geo_data, "hostname")
    isp = safe_extract(geo_data, "isp")
    country = safe_extract(geo_data, "country")

    abuse_score = safe_extract(abuse_data, "abuseConfidenceScore")
    recent_reports = safe_extract(abuse_data, "totalReports")

    vpn_proxy = safe_extract(ipqs_data, "proxy")
    fraud_score = safe_extract(ipqs_data, "fraud_score") or safe_extract(ipqs_data, "fraud_score", default=None)

    # Build unified normalized structure
    normalized = {
        "ip": ip,
        "hostname": hostname,
        "isp": isp,
        "country": country,

        "abuse_score": abuse_score,
        "recent_reports": recent_reports,

        "vpn_proxy": vpn_proxy,
        "fraud_score": fraud_score,

        "raw_sources": {
            "abuseipdb": abuse_data,
            "ipqualityscore": ipqs_data,
            "ipapi": geo_data
        }
    }

    return normalized
