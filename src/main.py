from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.routers import scans, assets, vulnerability
from src.database import init_db, get_db, AssetDB
from src.services.credential_manager import credential_manager
from src.services.proxy_manager import proxy_manager
from src.services.ml_predictor import ml_predictor

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

app.include_router(scans.router, prefix="/scan")
app.include_router(assets.router, prefix="/assets")
app.include_router(vulnerability.router, prefix="/vulnerabilities")