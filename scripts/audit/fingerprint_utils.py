import sys
from typing import Iterable, List, Tuple

from taxonomy_utils import ensure_backend_on_path


def load_master_config():
    ensure_backend_on_path()
    from app.v2.config import master_config as mc
    return mc


def type_key(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def sorted_type_keys(values: Iterable) -> List[str]:
    return sorted(type_key(v) for v in values)


def sample_keys(keys: Iterable[str], count: int = 3) -> Tuple[List[str], List[str]]:
    items = sorted(keys)
    if not items:
        return ([], [])
    first = items[:count]
    last = items[-count:] if len(items) > count else items
    return (first, last)


def format_sample(keys: Iterable[str], count: int = 3) -> str:
    first, last = sample_keys(keys, count=count)
    return f"first={first} last={last}"
