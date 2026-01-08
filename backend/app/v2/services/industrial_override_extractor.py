import re
from typing import Any, Dict, List, Optional, Pattern


class OverrideRule:
    def __init__(self, key: str, pattern: Pattern[str], clamp: Optional[tuple[int, int]] = None):
        self.key = key
        self.pattern = pattern
        self.clamp = clamp

    def extract(self, text: str) -> Optional[Any]:
        match = self.pattern.search(text)
        if not match:
            return None
        value = match.group(1)
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None

        if self.clamp:
            low, high = self.clamp
            number = max(low, min(high, number))
        return number


_DOCK_DOOR_RULES: List[OverrideRule] = [
    OverrideRule(
        key="dock_doors",
        pattern=re.compile(r'\b(\d{1,3})\s*(?:dock\s+doors?|docks?)\b', re.IGNORECASE),
        clamp=(0, 300),
    ),
    OverrideRule(
        key="dock_doors",
        pattern=re.compile(r'\bdock\s+doors?\s*[:=]?\s*(\d{1,3})\b', re.IGNORECASE),
        clamp=(0, 300),
    ),
]


def extract_industrial_overrides(text: Optional[str]) -> Dict[str, Any]:
    """
    Deterministically extract structured overrides for industrial prompts.
    Currently supports dock door counts and is designed for future rules.
    """
    if not text or not text.strip():
        return {}

    overrides: Dict[str, Any] = {}
    for rule in _DOCK_DOOR_RULES:
        value = rule.extract(text)
        if value is not None:
            overrides[rule.key] = value
            break

    return overrides
