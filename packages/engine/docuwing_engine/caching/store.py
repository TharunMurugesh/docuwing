from __future__ import annotations

import hashlib
from typing import Any


def cache_key(content: str | bytes, *, schema_version: int | str, prompt_version: str, model_identifier: str) -> str:
    raw = content if isinstance(content, bytes) else content.encode()
    return hashlib.sha256(b"\0".join((raw, str(schema_version).encode(), prompt_version.encode(), model_identifier.encode()))).hexdigest()


class VersionedCache:
    def __init__(self) -> None: self._values: dict[str, Any] = {}
    def get(self, key: str) -> Any | None: return self._values.get(key)
    def set(self, key: str, value: Any) -> None: self._values[key] = value
