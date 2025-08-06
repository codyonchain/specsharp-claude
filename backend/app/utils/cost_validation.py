"""
Cost validation utilities to ensure data consistency across the application.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CostValidationError(Exception):
    """Raised when cost validation fails"""
    pass


def validate_cost_consistency(
    subtotal: float,
    contingency_percentage: float,
    contingency_amount: float,
    total_cost: float,
    tolerance: float = 0.01
) -> bool:
    """
    Validate that cost components are mathematically consistent.
    
    Args:
        subtotal: Base construction cost
        contingency_percentage: Contingency percentage (e.g., 10.0 for 10%)
        contingency_amount: Calculated contingency amount
        total_cost: Final total cost
        tolerance: Acceptable difference due to rounding (default $0.01)
    
    Returns:
        True if costs are consistent, False otherwise
        
    Raises:
        CostValidationError: If validation fails with details
    """
    # Calculate expected values
    expected_contingency = subtotal * (contingency_percentage / 100)
    expected_total = subtotal + contingency_amount
    
    # Check contingency calculation
    contingency_diff = abs(expected_contingency - contingency_amount)
    if contingency_diff > tolerance:
        error_msg = (
            f"Contingency mismatch: Expected ${expected_contingency:.2f} "
            f"but got ${contingency_amount:.2f} (diff: ${contingency_diff:.2f})"
        )
        logger.error(error_msg)
        raise CostValidationError(error_msg)
    
    # Check total calculation
    total_diff = abs(expected_total - total_cost)
    if total_diff > tolerance:
        error_msg = (
            f"Total cost mismatch: Expected ${expected_total:.2f} "
            f"but got ${total_cost:.2f} (diff: ${total_diff:.2f})"
        )
        logger.error(error_msg)
        raise CostValidationError(error_msg)
    
    return True


def validate_project_costs(project) -> bool:
    """
    Validate cost consistency for a project object.
    
    Args:
        project: Project model instance with cost fields
        
    Returns:
        True if validation passes
        
    Raises:
        CostValidationError: If validation fails
    """
    # Skip validation if costs haven't been set yet
    if not project.subtotal or not project.total_cost:
        return True
    
    try:
        return validate_cost_consistency(
            subtotal=project.subtotal,
            contingency_percentage=project.contingency_percentage or 10.0,
            contingency_amount=project.contingency_amount or 0,
            total_cost=project.total_cost
        )
    except CostValidationError as e:
        # Add project context to error
        error_msg = f"Project '{project.name}' (ID: {project.id}): {str(e)}"
        logger.error(error_msg)
        raise CostValidationError(error_msg)


def detect_cost_discrepancy(
    stored_total: float,
    calculated_total: float,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    threshold: float = 1.0
) -> Optional[float]:
    """
    Detect and log cost discrepancies between stored and calculated values.
    
    Args:
        stored_total: Total cost stored in database
        calculated_total: Total cost calculated from components
        project_id: Optional project ID for logging
        project_name: Optional project name for logging
        threshold: Threshold for warning (default $1.00)
        
    Returns:
        Difference amount if discrepancy exists, None otherwise
    """
    difference = abs(stored_total - calculated_total)
    
    if difference > threshold:
        project_info = ""
        if project_name:
            project_info = f" for project '{project_name}'"
        elif project_id:
            project_info = f" for project ID {project_id}"
            
        logger.warning(
            f"Cost inconsistency detected{project_info}: "
            f"Stored=${stored_total:.2f}, Calculated=${calculated_total:.2f}, "
            f"Difference=${difference:.2f}"
        )
        
        # Log additional context for debugging
        logger.debug(
            f"Cost breakdown{project_info}: "
            f"stored_total={stored_total}, calculated_total={calculated_total}, "
            f"difference={difference}, threshold={threshold}"
        )
        
        return difference
    
    return None


def log_cost_calculation(
    project_id: str,
    project_name: str,
    subtotal: float,
    contingency_percentage: float,
    contingency_amount: float,
    total_cost: float,
    cost_per_sqft: float,
    square_footage: float
):
    """
    Log cost calculation details for audit trail.
    
    This helps with debugging and provides transparency for cost calculations.
    """
    logger.info(
        f"Cost calculation for '{project_name}' (ID: {project_id}):\n"
        f"  Square Footage: {square_footage:,.0f} SF\n"
        f"  Subtotal: ${subtotal:,.2f}\n"
        f"  Contingency ({contingency_percentage}%): ${contingency_amount:,.2f}\n"
        f"  Total Cost: ${total_cost:,.2f}\n"
        f"  Cost per SF: ${cost_per_sqft:.2f}"
    )