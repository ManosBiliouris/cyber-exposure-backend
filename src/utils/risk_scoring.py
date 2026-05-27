from typing import List, Dict

PORT_RISK = {
    21: 70,   # FTP
    22: 40,   # SSH
    23: 95,   # Telnet
    25: 40,   # SMTP
    80: 20,   # HTTP
    443: 10,  # HTTPS
    445: 85,  # SMB
    1433: 80, # MSSQL
    1521: 80, # Oracle DB
    3306: 80, # MySQL
    3389: 90, # RDP
    5432: 80, # PostgreSQL
    5900: 85, # VNC
    6379: 95, # Redis
    8080: 30, # HTTP Alt
    8443: 15, # HTTPS Alt
    9200: 95, # Elasticsearch
    27017: 95,# MongoDB
}

SERVICE_RISK = {
    "telnet": 95,
    "ftp": 70,
    "rdp": 90,
    "remote desktop protocol": 90,
    "vnc": 85,
    "redis": 95,
    "mongodb": 90,
    "elasticsearch": 90,
    "mysql": 75,
    "postgresql": 75,
    "mssql": 80,
    "smb": 85,
    "http": 20,
    "https": 10,
    "ssh": 35,
    "smtp": 35,
    "apache httpd": 20,
    "apache tomcat": 35,
    "nginx": 20,
}

SEVERITY_WEIGHTS = {
    "critical": 40,
    "high": 25,
    "medium": 15,
    "low": 5,
    "info": 1,
}

def calculate_port_risk(port: int) -> int:
    return PORT_RISK.get(port, 15)

def calculate_service_risk(service: str) -> int:
    if not service:
        return 15
    service_lower = service.lower()
    # Check exact match first
    if service_lower in SERVICE_RISK:
        return SERVICE_RISK[service_lower]
    # Check partial match
    for key, value in SERVICE_RISK.items():
        if key in service_lower:
            return value
    return 15

def calculate_vulnerability_risk(findings: Dict[str, int]) -> int:
    score = 0
    for severity, count in findings.items():
        weight = SEVERITY_WEIGHTS.get(severity, 0)
        score += weight * count
    return min(score, 100)

def calculate_asset_risk(
    port: int,
    service: str,
    findings: Dict[str, int] = None
) -> int:
    if findings is None:
        findings = {}

    port_score = calculate_port_risk(port)
    service_score = calculate_service_risk(service)
    vuln_score = calculate_vulnerability_risk(findings)

    # Take the MAX of port and service risk, then blend with vuln score
    base_risk = max(port_score, service_score)
    total = (base_risk * 0.7) + (vuln_score * 0.3)

    return round(min(total, 100))

def score_scan_results(results: List[Dict]) -> List[Dict]:
    scored = []
    for item in results:
        port = item.get("port") or 0
        service = item.get("service") or ""

        risk = calculate_asset_risk(port=port, service=service)

        scored.append({
            **item,
            "risk_score": risk,
            "risk_level": get_risk_level(risk)
        })

    return scored

def get_risk_level(score: int) -> str:
    if score >= 75:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 25:
        return "medium"
    else:
        return "low"