from fastapi import APIRouter
from pydantic import BaseModel
from src.services.shodan_client import ShodanClient

router = APIRouter()
shodan = ShodanClient()

LAST_SCAN_RESULT = None  # store results until new scan

class ScanRequest(BaseModel):
    target: str

@router.post("/run")
def run_scan(req: ScanRequest):
    global LAST_SCAN_RESULT

    # Build query based on target type
    query = req.target.strip()

    # 1 CREDIT QUERY
    scan_data = shodan.run_single_query(query)

    LAST_SCAN_RESULT = scan_data
    return scan_data


@router.get("/last")
def get_last_scan():
    return LAST_SCAN_RESULT or {"message": "No scan executed yet"}
