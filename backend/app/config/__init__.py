"""
Configuration module for SpecSharp
All configuration data separated from business logic
"""

from .regional_multipliers import get_regional_multiplier, REGIONAL_MULTIPLIERS
from .feature_costs import get_feature_cost, get_all_features_for_type, FEATURE_COSTS
from .trade_percentages import (
    get_trade_percentages, 
    validate_trade_percentages,
    get_adjusted_percentages,
    TRADE_PERCENTAGES
)
from .finish_levels import (
    get_finish_multiplier,
    get_classification_multiplier,
    get_finish_level_description,
    get_classification_description,
    detect_classification_from_text,
    FINISH_LEVELS,
    PROJECT_CLASSIFICATIONS,
    HEALTHCARE_CLASSIFICATION_MULTIPLIERS
)

__all__ = [
    # Functions
    'get_regional_multiplier',
    'get_feature_cost',
    'get_all_features_for_type',
    'get_trade_percentages',
    'validate_trade_percentages',
    'get_adjusted_percentages',
    'get_finish_multiplier',
    'get_classification_multiplier',
    'get_finish_level_description',
    'get_classification_description',
    'detect_classification_from_text',
    
    # Constants
    'REGIONAL_MULTIPLIERS',
    'FEATURE_COSTS',
    'TRADE_PERCENTAGES',
    'FINISH_LEVELS',
    'PROJECT_CLASSIFICATIONS',
    'HEALTHCARE_CLASSIFICATION_MULTIPLIERS'
]