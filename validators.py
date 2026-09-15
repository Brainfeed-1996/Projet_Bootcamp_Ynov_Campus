VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def validate_log_level(level: str) -> bool:
    return level.upper() in VALID_LEVELS


def check_level(level: str) -> str:
    level = level.upper()
    if level not in VALID_LEVELS:
        raise ValueError(f"level invalide : {level}. Valeurs acceptées : {sorted(VALID_LEVELS)}")
    return level


def check_source(source: str) -> str:
    source = source.strip()
    if not source:
        raise ValueError("source ne peut pas être vide")
    return source