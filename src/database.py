from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./cyberexposure.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AssetDB(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    ip = Column(String)
    port = Column(Integer)
    org = Column(String, nullable=True)
    service = Column(String, nullable=True)
    source = Column(String)
    risk_score = Column(Integer)
    risk_level = Column(String)
    status = Column(String, default="online")
    vulnerability_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class VulnerabilityDB(Base):
    __tablename__ = "vulnerabilities"

    id = Column(String, primary_key=True)
    asset_id = Column(String)
    ip = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    service = Column(String, nullable=True)
    severity = Column(String)
    title = Column(String)
    description = Column(String)
    source = Column(String)
    status = Column(String, default="open")
    cve_id = Column(String, nullable=True)
    cvss_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScanDB(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True)
    original_query = Column(String)
    shodan_query = Column(String, nullable=True)
    zoomeye_query = Column(String, nullable=True)
    fofa_query = Column(String, nullable=True)
    shodan_total = Column(Integer, default=0)
    zoomeye_total = Column(Integer, default=0)
    fofa_total = Column(Integer, default=0)
    assets_found = Column(Integer, default=0)
    errors = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()