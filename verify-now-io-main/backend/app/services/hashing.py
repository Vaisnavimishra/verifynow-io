import hashlib


def normalize_and_hash(content_type: str, value: str) -> str:
    normalized = f"{content_type}:{value.strip().lower()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
