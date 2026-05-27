from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import scans, assets, vulnerability
from src.database import init_db

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

app.include_router(scans.router, prefix="/scan")
app.include_router(assets.router, prefix="/assets")
app.include_router(vulnerability.router, prefix="/vulnerabilities")