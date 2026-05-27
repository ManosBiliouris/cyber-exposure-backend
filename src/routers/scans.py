from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.services.llm_agent import LLMAgent
from src.routers.assets import ingest_assets
from src.routers.vulnerability import ingest_vulnerabilities
from src.database import get_db, ScanDB
import uuid
import json

router = APIRouter()
agent = LLMAgent()

class ScanRequest(BaseModel):
    target: str

@router.post("/run")
def run_scan(req: ScanRequest, db: Session = Depends(get_db)):
    scan_data = agent.run_parallel(req.target)

    assets_response = ingest_assets(scan_data, db)
    ingest_vulnerabilities({"assets": assets_response["assets"]}, db)

    scan = ScanDB(
        id=str(uuid.uuid4()),
        original_query=req.target,
        shodan_query=scan_data.get("translated_queries", {}).get("shodan"),
        zoomeye_query=scan_data.get("translated_queries", {}).get("zoomeye"),
        fofa_query=scan_data.get("translated_queries", {}).get("fofa"),
        shodan_total=scan_data.get("shodan", {}).get("total", 0) if scan_data.get("shodan") else 0,
        zoomeye_total=scan_data.get("zoomeye", {}).get("total", 0) if scan_data.get("zoomeye") else 0,
        fofa_total=scan_data.get("fofa", {}).get("total", 0) if scan_data.get("fofa") else 0,
        assets_found=assets_response["ingested"],
        errors=json.dumps(scan_data.get("errors", {})),
    )
    db.add(scan)
    db.commit()

    return {
        "scan": scan_data,
        "assets_found": assets_response["ingested"],
        "total_assets": assets_response["total"],
    }

@router.get("/last")
def get_last_scan(db: Session = Depends(get_db)):
    scan = db.query(ScanDB).order_by(ScanDB.created_at.desc()).first()
    if not scan:
        return {"message": "No scan executed yet"}
    return {
        "original_query": scan.original_query,
        "translated_queries": {
            "shodan": scan.shodan_query,
            "zoomeye": scan.zoomeye_query,
            "fofa": scan.fofa_query,
        },
        "shodan": {"total": scan.shodan_total},
        "zoomeye": {"total": scan.zoomeye_total},
        "fofa": {"total": scan.fofa_total},
        "assets_found": scan.assets_found,
        "startedAt": scan.created_at.isoformat(),
    }

@router.get("/history")
def get_scan_history(db: Session = Depends(get_db)):
    scans = db.query(ScanDB).order_by(ScanDB.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "original_query": s.original_query,
            "assets_found": s.assets_found,
            "shodan_total": s.shodan_total,
            "startedAt": s.created_at.isoformat(),
        }
        for s in scans
    ]