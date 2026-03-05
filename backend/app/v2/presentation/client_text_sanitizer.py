from __future__ import annotations

import re
from typing import Any, Dict

_TILE_PATTERN = re.compile(r"\s*\(tile:\s*[^)]*\)", re.IGNORECASE)
_BANNED_LINE_PATTERNS = [
    re.compile(r"policy\s+source\s*:", re.IGNORECASE),
    re.compile(r"dealshield_policy_v1", re.IGNORECASE),
    re.compile(r"dealshield_canonical_policy_v1", re.IGNORECASE),
    re.compile(r"metric_refs_used", re.IGNORECASE),
]
_BANNED_KEY_PATTERN = re.compile(r"metric_refs_used", re.IGNORECASE)
_EXTRA_SPACE_PATTERN = re.compile(r"\s{2,}")


def _sanitize_string(value: str) -> str:
    cleaned = _TILE_PATTERN.sub("", value)

    lines = []
    for raw_line in cleaned.splitlines():
        if any(pattern.search(raw_line) for pattern in _BANNED_LINE_PATTERNS):
            continue
        line = raw_line.replace("\t", " ").strip()
        if not line:
            continue
        line = re.sub(r"\bMarginal\b", "Thin Cushion", line, flags=re.IGNORECASE)
        line = re.sub(r"\bNot\s+Feasible\b", "Target Yield: Not Met", line, flags=re.IGNORECASE)
        line = _EXTRA_SPACE_PATTERN.sub(" ", line)
        lines.append(line)

    return "\n".join(lines).strip()


def sanitize_client_text(value: Any) -> Any:
    """Recursively sanitize client-facing strings and drop known debug-only keys."""

    if isinstance(value, str):
        return _sanitize_string(value)

    if isinstance(value, list):
        output = []
        for item in value:
            sanitized = sanitize_client_text(item)
            if sanitized in (None, "", [], {}):
                continue
            output.append(sanitized)
        return output

    if isinstance(value, tuple):
        return tuple(sanitize_client_text(item) for item in value)

    if isinstance(value, dict):
        output: Dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(key, str) and _BANNED_KEY_PATTERN.search(key):
                continue
            sanitized = sanitize_client_text(item)
            if sanitized in (None, "", [], {}):
                continue
            output[key] = sanitized
        return output

    return value
