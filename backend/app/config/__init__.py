"""
Configuration module for SpecSharp
All configuration data separated from business logic
"""

from .regional_multipliers import get_regional_multiplier, REGIONAL_MULTIPLIERS

__all__ = [
    'get_regional_multiplier',
    'REGIONAL_MULTIPLIERS',
]
