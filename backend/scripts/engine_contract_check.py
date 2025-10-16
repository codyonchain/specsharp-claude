#!/usr/bin/env python3
"""Compute a stable checksum for UnifiedEngine public surface and trace steps."""
import hashlib
import inspect
import os
import re
import sys
from pathlib import Path

# Ensure backend package importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config import master_config


def collect_public_api() -> str:
    signatures = []
    for name, member in inspect.getmembers(UnifiedEngine, predicate=inspect.isfunction):
        if name.startswith('_'):
            continue
        sig = inspect.signature(member)
        signatures.append(f"{name}{sig}")
    signatures.sort()
    return '\n'.join(signatures)


def collect_trace_steps() -> str:
    steps = set()
    engine_source = inspect.getsource(UnifiedEngine)
    for match in re.finditer(r"_log_trace\(\s*['\"]([^'\"]+)['\"]", engine_source):
        steps.add(match.group(1))

    for name, obj in inspect.getmembers(master_config):
        if inspect.isfunction(obj):
            source = inspect.getsource(obj)
            for match in re.finditer(r"_log_trace\(\s*['\"]([^'\"]+)['\"]", source):
                steps.add(match.group(1))
    return '\n'.join(sorted(steps))


def compute_hash() -> str:
    payload = collect_public_api() + '\n' + collect_trace_steps()
    return hashlib.md5(payload.encode('utf-8')).hexdigest()


def main() -> None:
    checksum = compute_hash()
    print(f"ENGINE_CONTRACT_HASH={checksum}")

    docs_path = ROOT / "docs" / "ENGINE_CONTRACT.md"
    if docs_path.exists():
        content = docs_path.read_text(encoding="utf-8")
        match = re.search(r"ENGINE_CONTRACT_HASH=([a-f0-9]{32})", content)
        if match and match.group(1) != checksum:
            print(
                "WARNING: Engine contract hash changed (previous vs current).",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
