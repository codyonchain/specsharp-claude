"""
Utility modules for SpecSharp
"""
from .formatting import (
    format_currency,
    format_currency_compact,
    format_percentage,
    format_number,
    format_square_feet,
    format_unit_cost,
    format_quantity,
    format_cost_range,
    format_cost_per_sf,
    format_line_item
)

from .grouping import (
    group_similar_items,
    format_grouped_export,
    group_scope_items,
    ItemGrouper
)

__all__ = [
    # Formatting utilities
    'format_currency',
    'format_currency_compact',
    'format_percentage',
    'format_number',
    'format_square_feet',
    'format_unit_cost',
    'format_quantity',
    'format_cost_range',
    'format_cost_per_sf',
    'format_line_item',
    # Grouping utilities
    'group_similar_items',
    'format_grouped_export',
    'group_scope_items',
    'ItemGrouper'
]