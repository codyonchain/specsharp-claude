"""
Clean number formatting utilities for professional presentation
"""
from typing import Union, Optional


def format_currency(amount: Union[float, int], decimals: Optional[int] = None) -> str:
    """
    Format currency for professional display
    - Large amounts: $1,234,567 (no cents)
    - Small amounts: $123.45 (with cents)
    - Negative amounts: ($1,234)
    """
    if amount is None:
        return "$0"
    
    # Handle negative numbers with parentheses
    if amount < 0:
        return f"({format_currency(abs(amount), decimals)})"
    
    # Auto-determine decimal places if not specified
    if decimals is None:
        if amount >= 1000:
            decimals = 0  # No cents for large amounts
        else:
            decimals = 2  # Show cents for small amounts
    
    # Format based on decimal specification
    if decimals == 0:
        return f"${amount:,.0f}"
    else:
        return f"${amount:,.{decimals}f}"


def format_currency_compact(amount: Union[float, int]) -> str:
    """
    Format large amounts in compact form
    Examples: $1.2M, $850K, $1.5B
    """
    if amount is None:
        return "$0"
    
    abs_amount = abs(amount)
    
    if abs_amount >= 1_000_000_000:  # Billions
        formatted = f"${abs_amount / 1_000_000_000:.1f}B"
    elif abs_amount >= 1_000_000:  # Millions
        formatted = f"${abs_amount / 1_000_000:.1f}M"
    elif abs_amount >= 100_000:  # Hundreds of thousands
        formatted = f"${abs_amount / 1_000:.0f}K"
    elif abs_amount >= 10_000:  # Tens of thousands
        formatted = f"${abs_amount / 1_000:.1f}K"
    else:
        formatted = format_currency(abs_amount)
    
    return f"({formatted})" if amount < 0 else formatted


def format_percentage(value: Union[float, int], decimals: int = 1) -> str:
    """
    Format percentage with consistent decimal places
    """
    if value is None:
        return "0%"
    
    if decimals == 0:
        return f"{value:.0f}%"
    else:
        return f"{value:.{decimals}f}%"


def format_number(value: Union[float, int], decimals: int = 0) -> str:
    """
    Format general numbers with thousands separators
    """
    if value is None:
        return "0"
    
    if decimals == 0:
        return f"{value:,.0f}"
    else:
        return f"{value:,.{decimals}f}"


def format_square_feet(value: Union[float, int]) -> str:
    """
    Format square footage consistently
    """
    if value is None:
        return "0 SF"
    
    return f"{value:,.0f} SF"


def format_unit_cost(cost: float, unit: str = "") -> str:
    """
    Format unit costs with appropriate precision
    Examples: $1,234/SF, $45.50/HR, $2,500 EA
    """
    if cost is None:
        cost = 0
    
    # Different precision for different magnitudes
    if cost >= 1000:
        formatted = f"${cost:,.0f}"
    elif cost >= 100:
        formatted = f"${cost:,.1f}"
    else:
        formatted = f"${cost:,.2f}"
    
    if unit:
        # Clean up unit formatting
        unit = unit.upper()
        if unit not in ["EA", "LS", "HR"]:
            formatted += f"/{unit}"
        else:
            formatted += f" {unit}"
    
    return formatted


def format_quantity(value: float, unit: str) -> str:
    """
    Format quantities with appropriate precision based on unit
    """
    if value is None:
        value = 0
    
    unit_upper = unit.upper() if unit else ""
    
    # Whole numbers for counts
    if unit_upper in ["EA", "UNITS", "ROOMS", "SPACES", "FLOORS"]:
        return f"{value:,.0f} {unit}"
    
    # One decimal for most measurements
    elif unit_upper in ["SF", "LF", "SY", "CY", "TONS"]:
        if value >= 1000:
            return f"{value:,.0f} {unit}"
        else:
            return f"{value:,.1f} {unit}"
    
    # Two decimals for precise measurements
    elif unit_upper in ["HR", "HOURS", "DAYS"]:
        return f"{value:,.2f} {unit}"
    
    # Default
    else:
        return f"{value:,.1f} {unit}"


def format_cost_range(low: float, high: float) -> str:
    """
    Format a cost range for estimates
    Example: $1.2M - $1.5M
    """
    if low is None:
        low = 0
    if high is None:
        high = 0
    
    # Use compact format for large ranges
    if low >= 100_000 or high >= 100_000:
        return f"{format_currency_compact(low)} - {format_currency_compact(high)}"
    else:
        return f"{format_currency(low)} - {format_currency(high)}"


def format_cost_per_sf(total_cost: float, square_feet: float) -> str:
    """
    Format cost per square foot
    """
    if not square_feet or square_feet == 0:
        return "$0/SF"
    
    cost_per_sf = total_cost / square_feet
    
    if cost_per_sf >= 100:
        return f"${cost_per_sf:,.0f}/SF"
    else:
        return f"${cost_per_sf:,.2f}/SF"


# Utility function for consistent formatting in reports
def format_line_item(description: str, quantity: float, unit: str, 
                    unit_cost: float, total_cost: float) -> dict:
    """
    Format a complete line item for reports
    """
    return {
        "description": description,
        "quantity": format_quantity(quantity, unit),
        "unit_cost": format_unit_cost(unit_cost, unit),
        "total_cost": format_currency(total_cost),
        "raw_values": {
            "quantity": quantity,
            "unit": unit,
            "unit_cost": unit_cost,
            "total_cost": total_cost
        }
    }