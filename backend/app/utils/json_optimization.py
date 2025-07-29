"""
JSON optimization utilities for handling large scope_details data
"""
import json
from typing import Dict, Any, Optional

def create_scope_summary(scope_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a lightweight summary of scope data for listing views.
    This avoids loading full scope_details JSON into memory for list operations.
    """
    summary = {
        "project_id": scope_data.get("project_id"),
        "project_name": scope_data.get("project_name"),
        "total_cost": scope_data.get("total_cost"),
        "cost_per_sqft": scope_data.get("cost_per_sqft"),
        "building_type": scope_data.get("building_type"),
        "square_footage": scope_data.get("square_footage"),
        "location": scope_data.get("location"),
        # Include high-level cost breakdown without detailed items
        "cost_summary": {
            trade: details.get("total", 0)
            for trade, details in scope_data.get("cost_breakdown", {}).items()
            if isinstance(details, dict)
        }
    }
    return summary

def extract_trade_data(scope_data: Dict[str, Any], trade: str) -> Optional[Dict[str, Any]]:
    """
    Extract specific trade data from scope without loading entire JSON.
    """
    cost_breakdown = scope_data.get("cost_breakdown", {})
    trade_details = scope_data.get("trade_details", {})
    
    return {
        "cost": cost_breakdown.get(trade, {}),
        "details": trade_details.get(trade, {}),
        "items": scope_data.get(f"{trade}_items", [])
    }

def optimize_scope_for_storage(scope_data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Split scope data into main data and detailed data for optimized storage.
    Returns (main_data, detail_data) tuple.
    """
    # Fields to keep in main data
    main_fields = [
        "project_id", "project_name", "total_cost", "cost_per_sqft",
        "building_type", "square_footage", "location", "climate_zone",
        "num_floors", "ceiling_height", "request_data"
    ]
    
    main_data = {k: v for k, v in scope_data.items() if k in main_fields}
    
    # Add cost summary to main data
    main_data["cost_summary"] = {
        trade: details.get("total", 0)
        for trade, details in scope_data.get("cost_breakdown", {}).items()
        if isinstance(details, dict)
    }
    
    # Everything else goes to detail data
    detail_data = {k: v for k, v in scope_data.items() if k not in main_fields}
    
    return main_data, detail_data