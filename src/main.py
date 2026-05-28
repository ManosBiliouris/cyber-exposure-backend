from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.routers import scans, assets, vulnerability
from src.database import init_db, get_db, AssetDB
from src.services.credential_manager import credential_manager
from src.services.proxy_manager import proxy_manager
from src.services.ml_predictor import ml_predictor
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/credentials/stats")
def credential_stats():
    return credential_manager.get_stats()

@app.get("/proxy/stats")
def proxy_stats():
    return proxy_manager.get_stats()

@app.get("/ml/predict")
def ml_predict_all(db: Session = Depends(get_db)):
    assets_list = db.query(AssetDB).all()
    asset_dicts = [
        {
            "id": a.id,
            "ip": a.ip,
            "port": a.port,
            "service": a.service,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
        }
        for a in assets_list
    ]
    predictions = ml_predictor.predict_batch(asset_dicts)
    return {"total": len(predictions), "predictions": predictions}

@app.get("/ml/predict/{asset_id}")
def ml_predict_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    if not asset:
        return {"error": "Asset not found"}
    asset_dict = {
        "id": asset.id,
        "ip": asset.ip,
        "port": asset.port,
        "service": asset.service,
        "risk_score": asset.risk_score,
        "risk_level": asset.risk_level,
    }
    prediction = ml_predictor.predict(asset_dict)
    return {**asset_dict, "ml_prediction": prediction}


class TestKeyRequest(BaseModel):
    key: str
    email: str | None = None

@app.post("/credentials/test/{service}")
def test_credential_with_key(service: str, req: TestKeyRequest):
    try:
        if service == "shodan":
            import requests as req_lib
            response = req_lib.get(
                "https://api.shodan.io/shodan/host/search",
                params={"key": req.key, "query": "apache country:GR"}
            )
            return {"valid": response.status_code == 200}

        elif service == "groq":
            from groq import Groq
            client = Groq(api_key=req.key)
            client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            return {"valid": True}

        elif service == "zoomeye":
            import requests as req_lib
            response = req_lib.get(
                "https://api.zoomeye.org/host/search",
                headers={"API-KEY": req.key},
                params={"query": "apache", "page": 1}
            )
            return {"valid": response.status_code == 200}

        elif service == "fofa_key":
            import requests as req_lib
            import base64
            query_b64 = base64.b64encode(b"apache").decode()
            response = req_lib.get(
                "https://fofa.info/api/v1/search/all",
                params={"email": req.email, "key": req.key, "qbase64": query_b64, "size": 1}
            )
            data = response.json()
            return {"valid": not data.get("error", False)}

        else:
            return {"valid": False}

    except Exception as e:
        return {"valid": False, "error": str(e)}
    
    
app.include_router(scans.router, prefix="/scan")
app.include_router(assets.router, prefix="/assets")
app.include_router(vulnerability.router, prefix="/vulnerabilities")