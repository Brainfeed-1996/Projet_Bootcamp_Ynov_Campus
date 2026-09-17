import atexit
import csv
import json
import logging
import os
import re
import smtplib
import time
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from collections import defaultdict
from functools import lru_cache
from io import StringIO
from time import time as current_time
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    insert,
    select,
    text,
)
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from middleware import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    CSRFMiddleware,
    RequestIDMiddleware,
)

from providers.base import ProviderConfigurationError, ProviderError
from providers.fake_provider import FakeLLMProvider
from providers.ollama_provider import OllamaLLMProvider
from providers.openai_provider import OpenAILLMProvider
from schemas.analysis import AnalysisResult
from validators import VALID_LEVELS, check_level, check_source

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

MAX_REQUEST_SIZE = 10 * 1024 * 1024
MAX_BULK_ITEMS = 10000
DEFAULT_REPORT_PAGE_SIZE = 1000
MAX_REPORT_PAGE_SIZE = 5000
USER_CACHE_SIZE = int(os.getenv("USER_CACHE_SIZE", "256"))
CONFIG_CACHE_SIZE = int(os.getenv("CONFIG_CACHE_SIZE", "64"))

RATE_LIMIT_DEFAULT = "100/minute"
RATE_LIMIT_AUTH = "10/minute"
RATE_LIMIT_LOGS_WRITE = "50/minute"
RATE_LIMIT_ANALYZE = "30/minute"

# --- Authentification API key (service-à-service) ---
def _load_api_keys() -> dict[str, str]:
    raw = os.environ.get("API_KEYS", "")
    keys: dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if ":" not in entry:
            continue
        service, key = entry.split(":", 1)
        keys[service.strip()] = key.strip()
    if not keys:
        keys = {
            "service_a": "key123",
            "service_b": "key456",
        }
    return keys


API_KEYS = _load_api_keys()
API_KEY_HEADER = "X-API-Key"


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Authentifie les appels service-à-service via une API key dans l'entête X-API-Key.

    Les routes sous le préfixe `/admin` et `/webhooks` nécessitent une clé valide.
    """

    PROTECTED_PREFIXES = ("/admin", "/webhooks")

    async def dispatch(self, request: StarletteRequest, call_next):
        path = request.url.path
        if not any(path.startswith(prefix) for prefix in self.PROTECTED_PREFIXES):
            return await call_next(request)
        api_key = request.headers.get(API_KEY_HEADER)
        if not api_key or api_key not in API_KEYS.values():
            return JSONResponse(
                status_code=401,
                content={"detail": "API key manquante ou invalide."},
            )
        request.state.service_name = next(
            (name for name, key in API_KEYS.items() if key == api_key), None
        )
        return await call_next(request)

SENSITIVE_PATTERNS = [
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), '[IP_REDACTED]'),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL_REDACTED]'),
    (re.compile(r'\b(?:password|passwd|pwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*\S+', re.IGNORECASE), '[CREDENTIAL_REDACTED]'),
    (re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'), '[CARD_REDACTED]'),
    (re.compile(r'\b[A-Za-z0-9+/=]{40,}\b'), '[TOKEN_REDACTED]'),
]


def sanitize_log_message(message: str) -> str:
    sanitized = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


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
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))


def _create_production_engine():
    return create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
        pool_use_lifo=True,
        pool_reset_on_return="rollback",
    )


def wait_for_db(max_retries=30, delay=2):
    engine = _create_production_engine()
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established.")
            return engine
        except (OperationalError, SQLAlchemyError):
            logger.warning("DB not ready (attempt %s/%s)", attempt, max_retries)
            time.sleep(delay)
    engine.dispose()
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
            pool_pre_ping=True,
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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the username if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency to get the current authenticated user."""
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@lru_cache(maxsize=USER_CACHE_SIZE)
def get_user_by_username(username: str) -> tuple[int, str, str, bool] | None:
    with SessionLocal() as db:
        user = db.execute(
            select(User.id, User.username, User.email, User.is_active)
            .where(User.username == username)
        ).first()
        if user is None:
            return None
        return user.id, user.username, user.email, bool(user.is_active)


def clear_user_cache():
    get_user_by_username.cache_clear()


@lru_cache(maxsize=CONFIG_CACHE_SIZE)
def get_configuration(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def clear_configuration_cache():
    get_configuration.cache_clear()


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

app.add_middleware(RequestIDMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=MAX_REQUEST_SIZE)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)


MAX_LIMIT = 1000
MIN_LIMIT = 1


# --- Helpers ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


# --- Modèles SQLAlchemy ---
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_username", "username", unique=True),
        Index("ix_users_email", "email", unique=True),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(120), nullable=False)
    password_hash = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"
    __table_args__ = (
        Index("ix_logs_level", "level"),
        Index("ix_logs_source", "source"),
        Index("ix_logs_created_at", "created_at"),
        Index("ix_logs_level_created_at", "level", "created_at"),
        Index("ix_logs_source_created_at", "source", "created_at"),
        Index("ix_logs_level_source_created_at", "level", "source", "created_at"),
    )
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
        return check_level(v)

    @field_validator("source")
    @classmethod
    def check_source(cls, v: str) -> str:
        return check_source(v)


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


class AnalysisCreate(BaseModel):
    log_id: int = Field(..., description="ID du log analysé")
    severity: str = Field(..., description="Niveau de sévérité (LOW, MEDIUM, HIGH, CRITICAL)")
    category: str = Field(..., description="Catégorie du log (ex: AUTH, NETWORK, SYSTEM)")
    summary: str = Field(..., description="Résumé de l'analyse")
    recommendations: list[str] = Field(..., description="Liste des recommandations")
    provider: str = Field(..., description="Fournisseur IA utilisé (openai, ollama, fake)")


# --- Fournisseur LLM (remplaçable, hors ligne possible) ---
_provider = None

_PROVIDER_FALLBACK = [
    ("openai", OpenAILLMProvider),
    ("ollama", OllamaLLMProvider),
    ("fake", FakeLLMProvider),
]


def _get_ordered_providers(requested: str):
    if requested in ("openai", "ollama", "fake"):
        return [
            (name, cls) for name, cls in _PROVIDER_FALLBACK if name == requested
        ] + [
            (name, cls) for name, cls in _PROVIDER_FALLBACK if name != requested
        ]
    return _PROVIDER_FALLBACK


def get_llm_provider():
    """Get LLM provider with fallback chain: OpenAI -> Ollama -> Fake."""
    global _provider
    if _provider is not None:
        return _provider

    requested = get_configuration("LLM_PROVIDER", "").lower()
    ordered = _get_ordered_providers(requested)

    last_error = None
    for name, provider_class in ordered:
        try:
            _provider = provider_class()
            logger.info("LLM provider initialized: %s", name)
            return _provider
        except (ProviderError, ProviderConfigurationError, RuntimeError, ValueError, OSError) as e:
            logger.warning("Failed to initialize %s provider: %s", name, e)
            last_error = e

    logger.error("All LLM providers failed to initialize")
    raise last_error or RuntimeError("No LLM provider available")


def process_batch(items: list, batch_size: int = 1000):
    for offset in range(0, len(items), batch_size):
        yield items[offset:offset + batch_size]


def bulk_insert_logs(db: Session, logs: list[dict], batch_size: int = 1000):
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")
    inserted = 0
    for batch in process_batch(logs, batch_size):
        db.execute(insert(Log), batch)
        db.commit()
        inserted += len(batch)
    return inserted


def serialize_log(log: Log) -> dict:
    return {
        "id": log.id,
        "level": log.level,
        "message": log.message,
        "source": log.source,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def stream_logs_as_json(db: Session, chunk_size: int = 100):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    stmt = (
        select(Log)
        .order_by(Log.created_at, Log.id)
        .execution_options(stream_results=True)
    )
    yield "["
    first_chunk = True
    records = []
    for log in db.execute(stmt).scalars():
        records.append(json.dumps(serialize_log(log), ensure_ascii=False))
        if len(records) >= chunk_size:
            if not first_chunk:
                yield ","
            yield ",".join(records)
            records = []
            first_chunk = False
    if records:
        if not first_chunk:
            yield ","
        yield ",".join(records)
    yield "]"


def stream_logs_as_csv(db: Session, chunk_size: int = 100):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "level", "message", "source", "created_at"])
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)
    stmt = (
        select(Log)
        .order_by(Log.created_at, Log.id)
        .execution_options(stream_results=True)
    )
    count = 0
    for log in db.execute(stmt).scalars():
        writer.writerow(
            [
                log.id,
                log.level,
                log.message,
                log.source or "",
                log.created_at.isoformat() if log.created_at else "",
            ]
        )
        count += 1
        if count >= chunk_size:
            output.seek(0)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            count = 0
    if count > 0:
        output.seek(0)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


def iter_log_report_rows(
    db: Session,
    page: int,
    page_size: int,
    level: str | None = None,
    source: str | None = None,
):
    stmt = select(Log)
    if level:
        stmt = stmt.where(Log.level == level)
    if source:
        stmt = stmt.where(Log.source == source)
    stmt = (
        stmt.order_by(Log.created_at, Log.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .execution_options(stream_results=True)
    )
    result = db.execute(stmt)
    try:
        yield from result.scalars()
    finally:
        result.close()


def stream_log_report_as_csv(
    db: Session,
    page: int = 1,
    page_size: int = DEFAULT_REPORT_PAGE_SIZE,
    level: str | None = None,
    source: str | None = None,
):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "level", "message", "source", "created_at"])
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)
    for log in iter_log_report_rows(db, page, page_size, level, source):
        writer.writerow(
            [
                log.id,
                log.level,
                log.message,
                log.source or "",
                log.created_at.isoformat() if log.created_at else "",
            ]
        )
        output.seek(0)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


# --- Routes utilisateurs ---
@app.get("/users/{user_id}", response_model=UserRead, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    if user_id <= 0:
        return create_error_response(400, "ID utilisateur invalide (doit être > 0).")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        return create_error_response(404, "Utilisateur introuvable.")
    return user


@app.post("/users", response_model=UserRead, status_code=201, tags=["Users"])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(payload.username):
        return create_error_response(409, "Utilisateur ou email déjà existant.")
    existing_email = db.execute(
        select(User.id).where(User.email == payload.email)
    ).first()
    if existing_email:
        return create_error_response(409, "Utilisateur ou email déjà existant.")
    user = User(username=payload.username, email=payload.email)
    user.password_hash = hash_password(payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    clear_user_cache()
    return user


@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if user_id <= 0:
        return create_error_response(400, "ID utilisateur invalide.")
    user = db.get(User, user_id)
    if not user:
        return create_error_response(404, "Utilisateur introuvable.")
    user.is_active = False
    db.commit()
    clear_user_cache()
    return {"id": user_id, "status": "deleted"}


class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/auth/login", response_model=Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return JWT access token."""
    user = db.execute(select(User).where(User.username == form_data.username)).scalar_one_or_none()
    if not user or not bcrypt.checkpw(form_data.password.encode(), user.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Routes logs ---
@app.get("/logs", response_model=list[LogRead], tags=["Logs"])
def get_logs(
    level: str | None = None,
    source: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        return create_error_response(400, f"limit doit être entre {MIN_LIMIT} et {MAX_LIMIT}")
    if level:
        level = level.upper()
        if level not in VALID_LEVELS:
            return create_error_response(400, f"level invalide : {level}. Valeurs : {sorted(VALID_LEVELS)}")
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


@app.get("/logs/export", tags=["Logs"])
def export_logs(
    chunk_size: int = 100,
    db: Session = Depends(get_db),
):
    return StreamingResponse(
        stream_logs_as_csv(db, chunk_size=chunk_size),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs.csv"},
    )


@app.get("/logs/report", tags=["Logs"])
def export_log_report(
    page: int = 1,
    page_size: int = DEFAULT_REPORT_PAGE_SIZE,
    level: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
):
    if page < 1:
        return create_error_response(400, "page doit être supérieur ou égal à 1.")
    if page_size < 1 or page_size > MAX_REPORT_PAGE_SIZE:
        return create_error_response(
            400,
            f"page_size doit être entre 1 et {MAX_REPORT_PAGE_SIZE}.",
        )
    try:
        if level:
            level = check_level(level)
        if source:
            source = check_source(source)
    except ValueError as exc:
        return create_error_response(400, str(exc))
    return StreamingResponse(
        stream_log_report_as_csv(db, page, page_size, level, source),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="logs-report-page-{page}.csv"',
            "X-Page": str(page),
            "X-Page-Size": str(page_size),
        },
    )


@app.get("/logs/{log_id}", response_model=LogRead, tags=["Logs"])
def get_log(log_id: int, db: Session = Depends(get_db)):
    if log_id <= 0:
        return create_error_response(400, "ID de log invalide.")
    log = db.get(Log, log_id)
    if not log:
        return create_error_response(404, "Log introuvable.")
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
        return create_error_response(400, "Corps JSON invalide.")
    if not isinstance(payload, list):
        return create_error_response(400, "Le corps doit être un tableau JSON de logs.")
    if len(payload) > MAX_BULK_ITEMS:
        return create_error_response(400, f"Trop d'éléments (max {MAX_BULK_ITEMS}).")
    errors: list[str] = []
    records: list[dict] = []
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
        records.append({"message": message, "level": level, "source": source})
    ingested = bulk_insert_logs(db, records) if records else 0
    return BulkResult(ingested=ingested, rejected=len(errors), errors=errors)


@app.post("/logs/ingest-csv", response_model=BulkResult, tags=["Logs"])
async def ingest_csv(file: UploadFile, db: Session = Depends(get_db)):
    """Ingère des logs au format CSV.

    Colonnes attendues : level,message,source
    """
    if not file.filename.lower().endswith(".csv"):
        return create_error_response(400, "Seul le format CSV (.csv) est accepté.")
    content = await file.read()
    if len(content) > MAX_REQUEST_SIZE:
        return create_error_response(413, f"Fichier trop volumineux (max {MAX_REQUEST_SIZE} bytes).")

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        return create_error_response(400, "Encodage invalide : le CSV doit être en UTF-8.")

    reader = csv.DictReader(text_content.splitlines())
    required = {"message"}
    if reader.fieldnames is None or not required.issubset({(f or "").strip() for f in reader.fieldnames}):
        return create_error_response(
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
    ingested = bulk_insert_logs(db, records)
    return BulkResult(ingested=ingested, rejected=len(errors), errors=errors)


@app.post("/logs/{log_id}/analyze", response_model=dict, status_code=201, tags=["Analyses"])
def analyze_log(log_id: int, db: Session = Depends(get_db)):
    if log_id <= 0:
        return create_error_response(400, "ID de log invalide.")
    log = db.get(Log, log_id)
    if not log:
        return create_error_response(404, "Log introuvable.")
    provider = get_llm_provider()
    try:
        result: AnalysisResult = provider.analyze(log.message)
    except (ProviderError, RuntimeError, ValueError, TimeoutError):
        logger.error("LLM analysis failed")
        return create_error_response(502, "Analyse IA indisponible.")
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
        return create_error_response(400, f"limit doit être entre {MIN_LIMIT} et {MAX_LIMIT}")
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
        return create_error_response(400, "Champ 'type' requis.")
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


def create_error_response(status_code: int, message: str, context: dict = None) -> JSONResponse:
    content = {"detail": message}
    if context:
        content["context"] = context
    return JSONResponse(status_code=status_code, content=content)


# --- Service de nettoyage ---
class CleanupService:
    """Supprime les logs et analyses plus anciens qu'un seuil (jours)."""

    def __init__(self, db: Session):
        self.db = db

    def cleanup_old_logs(self, days: int = 90) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = self.db.execute(
            Log.__table__.delete().where(Log.created_at < cutoff)
        )
        self.db.commit()
        return result.rowcount or 0

    def cleanup_old_analyses(self, days: int = 90) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = self.db.execute(
            Analyse.__table__.delete().where(Analyse.created_at < cutoff)
        )
        self.db.commit()
        return result.rowcount or 0


@app.post("/admin/cleanup", tags=["Admin"])
def cleanup_old_data(
    days: int = 90,
    db: Session = Depends(get_db),
):
    """Nettoie les logs et analyses plus anciens que `days` jours (défaut: 90)."""
    service = CleanupService(db)
    logs_deleted = service.cleanup_old_logs(days)
    analyses_deleted = service.cleanup_old_analyses(days)
    return {
        "logs_deleted": logs_deleted,
        "analyses_deleted": analyses_deleted,
        "cutoff_days": days,
    }


# --- Service d'alerte email ---
class EmailService:
    """Envoi d'emails via SMTP pour les alertes critiques."""

    def __init__(self, smtp_server: str | None = None, port: int = 587):
        self.smtp_server = smtp_server or os.environ.get("SMTP_SERVER", "localhost")
        self.port = port
        self.sender = os.environ.get("ALERT_EMAIL_FROM", "log-sentinel@example.com")

    def send(self, to: str, subject: str, body: str) -> None:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["To"] = to
        msg["From"] = self.sender
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.send_message(msg)


class AlertPayload(BaseModel):
    to_email: str = Field(..., description="Destinataire de l'alerte")
    subject: str = Field(..., min_length=1, max_length=200, description="Objet de l'alerte")
    body: str = Field(..., min_length=1, max_length=4096, description="Corps de l'alerte")
    level: str = Field("CRITICAL", description="Niveau de sévérité de l'alerte")


@app.post("/admin/alerts", tags=["Admin"])
def send_alert_email(payload: AlertPayload):
    """Envoie une alerte email pour un événement critique."""
    service = EmailService()
    try:
        service.send(payload.to_email, payload.subject, payload.body)
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Email alert failed: %s", exc)
        return create_error_response(502, "Envoi d'email échoué.")
    return {"status": "sent", "to": payload.to_email, "level": payload.level}

