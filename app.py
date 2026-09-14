import atexit
import csv
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, Form, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, Response
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    select,
    text,
)
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from providers.base import ProviderConfigurationError, ProviderError
from providers.fake_provider import FakeLLMProvider
from providers.ollama_provider import OllamaLLMProvider
from providers.openai_provider import OpenAILLMProvider
from schemas.analysis import AnalysisResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MAX_REQUEST_SIZE = 10 * 1024 * 1024
MAX_BULK_ITEMS = 10000

RATE_LIMIT_DEFAULT = "100/minute"
RATE_LIMIT_AUTH = "10/minute"
RATE_LIMIT_LOGS_WRITE = "50/minute"
RATE_LIMIT_ANALYZE = "30/minute"

SENSITIVE_PATTERNS = [
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), '[IP_REDACTED]'),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL_REDACTED]'),
    (re.compile(r'\b(?:password|passwd|pwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*\S+', re.IGNORECASE), '[CREDENTIAL_REDACTED]'),
    (re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'), '[CARD_REDACTED]'),
    (re.compile(r'\b[A-Za-z0-9+/=]{40,}\b'), '[TOKEN_REDACTED]'),
]


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": f"Request body too large. Maximum size is {MAX_REQUEST_SIZE} bytes."},
                    )
            except ValueError:
                pass
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'"
        return response


def _read_secret_from_file(env_var: str, file_env_var: str, default: str = "") -> str:
    file_path = os.environ.get(file_env_var)
    if file_path and os.path.isfile(file_path):
        try:
            with open(file_path, "r") as f:
                return f.read().strip()
        except OSError:
            pass
    return os.environ.get(env_var, default)


def _build_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url

    user = _read_secret_from_file("DB_USER", "DB_USER_FILE", "")
    password = _read_secret_from_file("DB_PASSWORD", "DB_PASSWORD_FILE", "")
    if user and password:
        host = os.environ.get("DB_HOST", "db")
        port = os.environ.get("DB_PORT", "5432")
        name = os.environ.get("DB_NAME", "music_hall")
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

    if os.environ.get("TESTING") == "1":
        return "sqlite:///:memory:"

    raise RuntimeError("DATABASE_URL or DB_USER/DB_PASSWORD must be configured")


DATABASE_URL = _build_database_url()


def wait_for_db(max_retries=30, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established.")
            return engine
        except (OperationalError, SQLAlchemyError):
            logger.warning("DB not ready (attempt %s/%s)", attempt, max_retries)
            time.sleep(delay)
    raise RuntimeError("Database unavailable after max retries.")


_engine = None


def _create_engine():
    global _engine
    if _engine is not None:
        return _engine
    if os.environ.get("TESTING") == "1":
        _engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        logger.info("Using in-memory SQLite for testing.")
    else:
        _engine = wait_for_db()
    return _engine


def get_engine():
    return _create_engine()


def _dispose_engine():
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Database engine disposed.")


atexit.register(_dispose_engine)


SessionLocal = sessionmaker(bind=_create_engine())
Base = declarative_base()

engine = get_engine()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="Log Sentinel API",
    description=(
        "API d'ingestion et d'analyse de logs sécurisée (DevSecOps). "
        "Ingère des logs JSON ou CSV, les valide, puis les analyse via "
        "un fournisseur LLM (OpenAI / Ollama) ou un fournisseur factice hors ligne."
    ),
    version="1.0.0",
    contact={"name": "Music Hall - DevSecOps"},
)

# Add request size limit middleware
app.add_middleware(RequestSizeLimitMiddleware)


VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
MAX_LIMIT = 1000
MIN_LIMIT = 1


# --- Helpers ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# --- Modèles SQLAlchemy ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class Analyse(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    input_data = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=_create_engine())


# --- Schémas Pydantic (documentent l'API dans Swagger) ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur unique")
    email: EmailStr = Field(..., max_length=120, description="Email unique")
    password: str = Field(..., min_length=8, description="Mot de passe (haché en base)")


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}


class LogCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096, description="Corps du message de log")
    level: str = Field("INFO", description="Niveau de sévérité")
    source: str = Field("unknown", min_length=1, max_length=100, description="Source du log")

    @field_validator("level")
    @classmethod
    def check_level(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_LEVELS:
            raise ValueError(f"level invalide : {v}. Valeurs acceptées : {sorted(VALID_LEVELS)}")
        return v

    @field_validator("source")
    @classmethod
    def check_source(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("source ne peut pas être vide")
        return v


class LogRead(BaseModel):
    id: int
    level: str
    message: str
    source: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class AnalyseRead(BaseModel):
    id: int
    type: str
    input_data: str | None
    result: str | None
    created_at: datetime | None

    model_config = {"from_attributes": True}


class BulkResult(BaseModel):
    ingested: int = Field(..., description="Nombre de logs acceptés")
    rejected: int = Field(..., description="Nombre de lignes rejetées")
    errors: list[str] = Field(default_factory=list, description="Erreurs explicites par ligne")


# --- Fournisseur LLM (remplaçable, hors ligne possible) ---
_provider = None


def get_llm_provider():
    """Get LLM provider with fallback chain: OpenAI -> Ollama -> Fake."""
    global _provider
    if _provider is not None:
        return _provider

    # Try providers in order of preference
    providers_to_try = [
        ("openai", OpenAILLMProvider),
        ("ollama", OllamaLLMProvider),
        ("fake", FakeLLMProvider),
    ]

    # Check if a specific provider is requested
    requested = os.environ.get("LLM_PROVIDER", "").lower()
    if requested in ("openai", "ollama", "fake"):
        # Move requested provider to front of list
        providers_to_try = [
            (name, cls) for name, cls in providers_to_try if name == requested
        ] + [(name, cls) for name, cls in providers_to_try if name != requested]

    last_error = None
    for name, provider_class in providers_to_try:
        try:
            _provider = provider_class()
            logger.info("LLM provider initialized: %s", name)
            return _provider
        except (ProviderError, ProviderConfigurationError, RuntimeError, ValueError, OSError) as e:
            logger.warning("Failed to initialize %s provider: %s", name, e)
            last_error = e
            continue

    # If all providers fail, raise the last error
    logger.error("All LLM providers failed to initialize")
    raise last_error or RuntimeError("No LLM provider available")


# --- Routes utilisateurs ---
@app.get("/users/{user_id}", response_model=UserRead, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    if user_id <= 0:
        raise HTTPException(400, "ID utilisateur invalide (doit être > 0).")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(404, "Utilisateur introuvable.")
    return user


@app.post("/users", response_model=UserRead, status_code=201, tags=["Users"])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT id FROM users WHERE username = :u OR email = :e"),
        {"u": payload.username, "e": payload.email},
    ).fetchone()
    if existing:
        raise HTTPException(409, "Utilisateur ou email déjà existant.")
    user = User(username=payload.username, email=payload.email)
    user.password_hash = hash_password(payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if user_id <= 0:
        raise HTTPException(400, "ID utilisateur invalide.")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable.")
    user.is_active = False
    db.commit()
    return {"id": user_id, "status": "deleted"}


# --- Routes logs ---
@app.get("/logs", response_model=list[LogRead], tags=["Logs"])
def get_logs(
    level: str | None = None,
    source: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        raise HTTPException(400, f"limit doit être entre {MIN_LIMIT} et {MAX_LIMIT}")
    if level:
        level = level.upper()
        if level not in VALID_LEVELS:
            raise HTTPException(400, f"level invalide : {level}. Valeurs : {sorted(VALID_LEVELS)}")
    stmt = select(Log)
    if level:
        stmt = stmt.where(Log.level == level)
    if source:
        stmt = stmt.where(Log.source == source)
    stmt = stmt.order_by(Log.created_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return [
        {
            "id": r.id,
            "level": r.level,
            "message": r.message,
            "source": r.source,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@app.post("/logs", response_model=LogRead, status_code=201, tags=["Logs"])
def create_log(payload: LogCreate, db: Session = Depends(get_db)):
    log = Log(level=payload.level, message=payload.message, source=payload.source)
    db.add(log)
    db.commit()
    db.refresh(log)
    return {
        "id": log.id,
        "level": log.level,
        "message": log.message,
        "source": log.source,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


@app.get("/logs/{log_id}", response_model=LogRead, tags=["Logs"])
def get_log(log_id: int, db: Session = Depends(get_db)):
    if log_id <= 0:
        raise HTTPException(400, "ID de log invalide.")
    log = db.get(Log, log_id)
    if not log:
        raise HTTPException(404, "Log introuvable.")
    return {
        "id": log.id,
        "level": log.level,
        "message": log.message,
        "source": log.source,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


@app.post("/logs/bulk", response_model=BulkResult, tags=["Logs"])
async def ingest_logs(request: Request, db: Session = Depends(get_db)):
    """Ingère une liste de logs au format JSON.

    Corps attendu :
    [{"message": "...", "level": "ERROR", "source": "api"}, ...]
    """
    try:
        payload = await request.json()
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(400, "Corps JSON invalide.")
    if not isinstance(payload, list):
        raise HTTPException(400, "Le corps doit être un tableau JSON de logs.")
    if len(payload) > MAX_BULK_ITEMS:
        raise HTTPException(400, f"Trop d'éléments (max {MAX_BULK_ITEMS}).")
    errors: list[str] = []
    ingested = 0
    for i, rec in enumerate(payload, start=1):
        if not isinstance(rec, dict):
            errors.append(f"Ligne {i} : entrée non-objet.")
            continue
        message = (rec.get("message") or "").strip()
        level = (rec.get("level") or "INFO").upper()
        source = (rec.get("source") or "unknown").strip()
        if not message:
            errors.append(f"Ligne {i} : le champ 'message' est vide.")
            continue
        if level not in VALID_LEVELS:
            errors.append(
                f"Ligne {i} : level '{level}' invalide. Valeurs : {sorted(VALID_LEVELS)}"
            )
            continue
        if len(message) > 4096:
            errors.append(f"Ligne {i} : 'message' dépasse 4096 caractères.")
            continue
        db.add(Log(level=level, message=message, source=source))
        ingested += 1
    db.commit()
    return BulkResult(ingested=ingested, rejected=len(errors), errors=errors)


@app.post("/logs/ingest-csv", response_model=BulkResult, tags=["Logs"])
async def ingest_csv(file: UploadFile, db: Session = Depends(get_db)):
    """Ingère des logs au format CSV.

    Colonnes attendues : level,message,source
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Seul le format CSV (.csv) est accepté.")
    content = await file.read()
    if len(content) > MAX_REQUEST_SIZE:
        raise HTTPException(413, f"Fichier trop volumineux (max {MAX_REQUEST_SIZE} bytes).")

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(400, "Encodage invalide : le CSV doit être en UTF-8.")

    reader = csv.DictReader(text_content.splitlines())
    required = {"message"}
    if reader.fieldnames is None or not required.issubset({(f or "").strip() for f in reader.fieldnames}):
        raise HTTPException(
            422,
            "En-tête CSV invalide : la colonne 'message' est requise. "
            "Colonnes optionnelles : level, source.",
        )
    errors: list[str] = []
    records = []
    for i, row in enumerate(reader, start=2):
        if len(records) >= MAX_BULK_ITEMS:
            errors.append(f"Ligne {i} : limite de {MAX_BULK_ITEMS} enregistrements atteinte.")
            break
        message = (row.get("message") or "").strip()
        level = (row.get("level") or "INFO").upper()
        source = (row.get("source") or "unknown").strip()
        if not message:
            errors.append(f"Ligne {i} : le champ 'message' est vide.")
            continue
        if level not in VALID_LEVELS:
            errors.append(f"Ligne {i} : level '{level}' invalide. Valeurs : {sorted(VALID_LEVELS)}")
            continue
        records.append({"message": message, "level": level, "source": source})
    ingested = 0
    for rec in records:
        db.add(Log(**rec))
        ingested += 1
    db.commit()
    return BulkResult(ingested=ingested, rejected=len(errors), errors=errors)


@app.post("/logs/{log_id}/analyze", response_model=dict, status_code=201, tags=["Analyses"])
def analyze_log(log_id: int, db: Session = Depends(get_db)):
    if log_id <= 0:
        raise HTTPException(400, "ID de log invalide.")
    log = db.get(Log, log_id)
    if not log:
        raise HTTPException(404, "Log introuvable.")
    provider = get_llm_provider()
    try:
        result: AnalysisResult = provider.analyze(log.message)
    except (ProviderError, RuntimeError, ValueError, TimeoutError):
        logger.error("LLM analysis failed")
        raise HTTPException(502, "Analyse IA indisponible.")
    analyse = Analyse(
        type="log_analysis",
        input_data=log.message,
        result=result.model_dump_json(),
    )
    db.add(analyse)
    db.commit()
    db.refresh(analyse)
    return {
        "id": analyse.id,
        "log_id": log.id,
        "result": result.model_dump(),
    }


# --- Routes analyses ---
@app.get("/analyses", response_model=list[AnalyseRead], tags=["Analyses"])
def get_analyses(limit: int = 50, db: Session = Depends(get_db)):
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        raise HTTPException(400, f"limit doit être entre {MIN_LIMIT} et {MAX_LIMIT}")
    stmt = select(Analyse).order_by(Analyse.created_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return [
        {
            "id": r.id,
            "type": r.type,
            "input_data": r.input_data,
            "result": r.result,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@app.post("/analyses", response_model=AnalyseRead, status_code=201, tags=["Analyses"])
def create_analyse(payload: dict, db: Session = Depends(get_db)):
    if "type" not in payload:
        raise HTTPException(400, "Champ 'type' requis.")
    analyse_type = payload["type"]
    input_data = payload.get("input_data", "")
    result = payload.get("result", "")
    a = Analyse(type=analyse_type, input_data=input_data, result=result)
    db.add(a)
    db.commit()
    db.refresh(a)
    return {
        "id": a.id,
        "type": a.type,
        "input_data": a.input_data,
        "result": a.result,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


# --- Santé ---
@app.get("/health", tags=["Monitoring"])
def health():
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "up"}
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503, content={"status": "error", "database": "down"}
        )


# --- Gestionnaires d'erreurs explicites ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "")
        details.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation échouée.", "errors": details},
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions (500 errors)."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

# Validation helper functions
def validate_log_level(level: str) -> bool:
    return level.upper() in VALID_LEVELS

def validate_severity(severity: str) -> bool:
    return severity.upper() in VALID_SEVERITIES

# Enhanced error handling for bulk operations
def handle_bulk_error(error: Exception, line_number: int) -> str:
    return f'Line {line_number}: {str(error)}'
