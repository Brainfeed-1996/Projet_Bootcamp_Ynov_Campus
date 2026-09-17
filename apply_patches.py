#!/usr/bin/env python3
"""Apply app.py changes in logical chunks for multiple commits."""
import subprocess
import sys

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {cmd}")
        print(result.stderr)
        return False
    return True

def read_file(path, encoding='utf-8'):
    with open(path, 'r', encoding=encoding) as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Read both versions
original = read_file('app.py.orig', encoding='utf-16-le')
new = read_file('app.py.new', encoding='utf-8')

print(f"Original: {len(original)} chars, New: {len(new)} chars")

# Define patches as (description, search_pattern, replacement)
# We'll apply them sequentially to the original file

patches = []

# Patch 1: Add new imports and oauth2_scheme
old_imports = """import atexit
import csv
import json
import logging
import os
import re
import smtplib
import time
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from functools import lru_cache
from io import StringIO

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, EmailStr, Field, field_validator"""

new_imports = """import atexit
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
from pydantic import BaseModel, EmailStr, Field, field_validator"""

patches.append(("feat: add auth imports and OAuth2 scheme", old_imports, new_imports))

# Patch 2: Add oauth2_scheme after ACCESS_TOKEN_EXPIRE_MINUTES
old_config = """SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MAX_REQUEST_SIZE = 10 * 1024 * 1024"""

new_config = """SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

MAX_REQUEST_SIZE = 10 * 1024 * 1024"""

patches.append(("feat: add OAuth2 password bearer scheme", old_config, new_config))

# Patch 3: Add RateLimitMiddleware after APIKeyMiddleware
old_middleware_end = """class APIKeyMiddleware(BaseHTTPMiddleware):
    \"\"\"Authentifie les appels service-\u00e0-service via une API key dans l'ent\u00eate X-API-Key.

    Les routes sous le pr\u00e9fixe `/admin` et `/webhooks` n\u00e9cessitent une cl\u00e9 valide.
    \"\"\"

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


SENSITIVE_PATTERNS = ["""

new_middleware_end = """class APIKeyMiddleware(BaseHTTPMiddleware):
    \"\"\"Authentifie les appels service-\u00e0-service via une API key dans l'ent\u00eate X-API-Key.

    Les routes sous le pr\u00e9fixe `/admin` et `/webhooks` n\u00e9cessitent une cl\u00e9 valide.
    \"\"\"

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


class RateLimitMiddleware(BaseHTTPMiddleware):
    _instances: list["RateLimitMiddleware"] = []

    def __init__(
        self,
        app,
        default_limit: str = RATE_LIMIT_DEFAULT,
        auth_limit: str = RATE_LIMIT_AUTH,
        logs_write_limit: str = RATE_LIMIT_LOGS_WRITE,
        analyze_limit: str = RATE_LIMIT_ANALYZE,
    ):
        super().__init__(app)
        self.default_limit = self._parse_limit(default_limit)
        self.auth_limit = self._parse_limit(auth_limit)
        self.logs_write_limit = self._parse_limit(logs_write_limit)
        self.analyze_limit = self._parse_limit(analyze_limit)
        self.requests: dict[str, list[float]] = defaultdict(list)
        RateLimitMiddleware._instances.append(self)

    @classmethod
    def reset_all(cls):
        for instance in cls._instances:
            instance.requests.clear()

    def _parse_limit(self, limit_str: str) -> tuple[int, int]:
        if "/" not in limit_str:
            return int(limit_str), 60
        count_str, period = limit_str.split("/")
        count = int(count_str)
        if period == "minute":
            window = 60
        elif period == "hour":
            window = 3600
        elif period == "day":
            window = 86400
        elif period == "second":
            window = 1
        else:
            window = 60
        return count, window

    def _get_client_ip(self, request: StarletteRequest) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_limit(self, path: str, method: str) -> tuple[int, int]:
        if path.startswith("/logs/") and path.endswith("/analyze") and method == "POST":
            return self.analyze_limit
        if path == "/auth/login" and method == "POST":
            return self.auth_limit
        if path.startswith("/logs") and method in ("POST", "PUT", "PATCH", "DELETE"):
            return self.logs_write_limit
        return self.default_limit

    async def dispatch(self, request: StarletteRequest, call_next):
        path = request.url.path
        method = request.method
        client_ip = self._get_client_ip(request)
        key = f"{client_ip}:{path}:{method}"
        limit, window = self._get_limit(path, method)
        now = current_time()
        self.requests[key] = [ts for ts in self.requests[key] if now - ts < window]
        remaining = max(0, limit - len(self.requests[key]) - 1)
        if len(self.requests[key]) >= limit:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(int(now + window))
            return response
        self.requests[key].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + window))
        return response


SENSITIVE_PATTERNS = ["""

patches.append(("feat: add rate limiting middleware", old_middleware_end, new_middleware_end))

# Patch 4: Update production engine with pool_use_lifo and pool_reset_on_return
old_prod_engine = """def _create_production_engine():
    return create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
    )"""

new_prod_engine = """def _create_production_engine():
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
    )"""

patches.append(("perf: add pool_use_lifo and pool_reset_on_return to production engine", old_prod_engine, new_prod_engine))

# Patch 5: Simplify test engine (remove pool settings)
old_test_engine = """    if os.environ.get("TESTING") == "1":
        _engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_size=DB_POOL_SIZE,
            max_overflow=DB_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_timeout=DB_POOL_TIMEOUT,
            pool_recycle=DB_POOL_RECYCLE,
        )
        logger.info("Using in-memory SQLite for testing.")"""

new_test_engine = """    if os.environ.get("TESTING") == "1":
        _engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_pre_ping=True,
        )
        logger.info("Using in-memory SQLite for testing.")"""

patches.append(("refactor: simplify test engine configuration", old_test_engine, new_test_engine))

# Patch 6: Add auth functions (create_access_token, verify_token, get_current_user) after get_db
old_get_db = """def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache(maxsize=USER_CACHE_SIZE)
def get_user_by_username(username: str) -> tuple[int, str, str, bool] | None:
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if user is None:
            return None
        return user.id, user.username, user.email, bool(user.is_active)"""

new_get_db = """def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    \"\"\"Create a JWT access token.\"\"\"
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    \"\"\"Verify a JWT token and return the username if valid.\"\"\"
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    \"\"\"Dependency to get the current authenticated user.\"\"\"
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
        return user.id, user.username, user.email, bool(user.is_active)"""

patches.append(("feat: add JWT token creation, verification, and user dependency", old_get_db, new_get_db))

# Patch 7: Add Token model and login endpoint after delete_user
old_delete_user = """@app.delete("/users/{user_id}", tags=["Users"])
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


# --- Routes logs ---"""

new_delete_user = """@app.delete("/users/{user_id}", tags=["Users"])
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
    \"\"\"Authenticate user and return JWT access token.\"\"\"
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


# --- Routes logs ---"""

patches.append(("feat: add Token model and /auth/login endpoint", old_delete_user, new_delete_user))

# Patch 8: Add AnalysisCreate model after BulkResult
old_bulkresult = """class BulkResult(BaseModel):
    ingested: int = Field(..., description="Nombre de logs accept\u00e9s")
    rejected: int = Field(..., description="Nombre de lignes rejet\u00e9es")
    errors: list[str] = Field(default_factory=list, description="Erreurs explicites par ligne")


# --- Fournisseur LLM (rempla\u00e7able, hors ligne possible) ---"""

new_bulkresult = """class BulkResult(BaseModel):
    ingested: int = Field(..., description="Nombre de logs accept\u00e9s")
    rejected: int = Field(..., description="Nombre de lignes rejet\u00e9es")
    errors: list[str] = Field(default_factory=list, description="Erreurs explicites par ligne")


class AnalysisCreate(BaseModel):
    log_id: int = Field(..., description="ID du log analys\u00e9")
    severity: str = Field(..., description="Niveau de s\u00e9v\u00e9rit\u00e9 (LOW, MEDIUM, HIGH, CRITICAL)")
    category: str = Field(..., description="Cat\u00e9gorie du log (ex: AUTH, NETWORK, SYSTEM)")
    summary: str = Field(..., description="R\u00e9sum\u00e9 de l'analyse")
    recommendations: list[str] = Field(..., description="Liste des recommandations")
    provider: str = Field(..., description="Fournisseur IA utilis\u00e9 (openai, ollama, fake)")


# --- Fournisseur LLM (rempla\u00e7able, hors ligne possible) ---"""

patches.append(("feat: add AnalysisCreate model for structured analysis output", old_bulkresult, new_bulkresult))

# Patch 9: Add serialize_log and stream_logs_as_json after bulk_insert_logs
old_bulk_insert = """def bulk_insert_logs(db: Session, logs: list[dict], batch_size: int = 1000):
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")
    inserted = 0
    for batch in process_batch(logs, batch_size):
        db.execute(insert(Log), batch)
        db.commit()
        inserted += len(batch)
    return inserted


def stream_logs_as_csv(db: Session, chunk_size: int = 100):"""

new_bulk_insert = """def bulk_insert_logs(db: Session, logs: list[dict], batch_size: int = 1000):
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


def stream_logs_as_csv(db: Session, chunk_size: int = 100):"""

patches.append(("feat: add log serialization and JSON streaming export", old_bulk_insert, new_bulk_insert))

# Patch 10: Add RateLimitMiddleware to app middleware stack
old_middleware_stack = """app.add_middleware(RequestIDMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=MAX_REQUEST_SIZE)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)


MAX_LIMIT = 1000"""

new_middleware_stack = """app.add_middleware(RequestIDMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size=MAX_REQUEST_SIZE)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(RateLimitMiddleware)


MAX_LIMIT = 1000"""

patches.append(("feat: register rate limiting middleware", old_middleware_stack, new_middleware_stack))

# Apply patches sequentially
current = original
for i, (msg, old, new) in enumerate(patches):
    if old not in current:
        print(f"Patch {i+1} NOT FOUND: {msg}")
        # Try to find similar
        print(f"  Looking for: {old[:100]}...")
        continue
    current = current.replace(old, new)
    write_file('app.py', current)
    run('git add app.py')
    run(f'git commit -m "{msg}"')
    print(f"Applied patch {i+1}: {msg}")

print("All patches applied!")