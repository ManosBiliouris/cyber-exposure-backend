from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db, AssetDB
from src.utils.risk_scoring import score_scan_results, get_risk_level
import uuid

router = APIRouter()

@router.get("/")
def get_assets(db: Session = Depends(get_db)):
    assets = db.query(AssetDB).all()
    return [
        {
            "id": a.id,
            "ip": a.ip,
            "port": a.port,
            "org": a.org,
            "service": a.service,
            "source": a.source,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
            "status": a.status,
            "vulnerabilityCount": a.vulnerability_count,
        }
        for a in assets
    ]

@router.get("/{asset_id}")
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    if not asset:
        return {"error": "Asset not found"}
    return {
        "id": asset.id,
        "ip": asset.ip,
        "port": asset.port,
        "org": asset.org,
        "service": asset.service,
        "source": asset.source,
        "risk_score": asset.risk_score,
        "risk_level": asset.risk_level,
        "status": asset.status,
        "vulnerabilityCount": asset.vulnerability_count,
    }

@router.post("/ingest")
def ingest_assets(scan_results: dict, db: Session = Depends(get_db)):
    all_results = []
    for source in ["shodan", "zoomeye", "fofa"]:
        source_data = scan_results.get(source) or {}
        for item in source_data.get("results", []):
            all_results.append({**item, "source": source})

    # Deduplicate by ip+port
    seen = set()
    unique = []
    for item in all_results:
        key = f"{item.get('ip')}:{item.get('port')}"
        if key not in seen:
            seen.add(key)
            unique.append(item)

    scored = score_scan_results(unique)
    new_count = 0

    for item in scored:
        existing = db.query(AssetDB).filter(
            AssetDB.ip == item.get("ip"),
            AssetDB.port == item.get("port")
        ).first()

        if not existing:
            asset = AssetDB(
                id=f"ast-{uuid.uuid4().hex[:8]}",
                ip=item.get("ip"),
                port=item.get("port"),
                org=item.get("org"),
                service=item.get("service"),
                source=item.get("source"),
                risk_score=item.get("risk_score"),
                risk_level=item.get("risk_level"),
                status="online",
                vulnerability_count=0,
            )
            db.add(asset)
            new_count += 1

    db.commit()

    total = db.query(AssetDB).count()
    assets = db.query(AssetDB).all()

    return {
        "ingested": new_count,
        "total": total,
        "assets": [
            {
                "id": a.id,
                "ip": a.ip,
                "port": a.port,
                "org": a.org,
                "service": a.service,
                "source": a.source,
                "risk_score": a.risk_score,
                "risk_level": a.risk_level,
                "status": a.status,
                "vulnerabilityCount": a.vulnerability_count,
            }
            for a in assets
        ]
    }