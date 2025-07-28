"""
Confidence Calculator for Scope Items

Calculates confidence scores based on various factors:
- Building type complexity
- Quantity reasonableness
- Regional market volatility
- System complexity
- Data source reliability
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass


# Typical quantity ranges for validation
TYPICAL_RANGES = {
    "structural": {
        "steel_frame_lbs": {"low": 5, "typical": 10, "high": 20},  # lbs/SF
        "concrete_cy": {"low": 0.01, "typical": 0.025, "high": 0.05},  # CY/SF
    },
    "mechanical": {
        "hvac_tons": {"low": 200, "typical": 400, "high": 600},  # SF/ton
        "ductwork_lbs": {"low": 1.5, "typical": 2.5, "high": 4.0},  # lbs/SF
        "exhaust_fans": {"low": 2000, "typical": 5000, "high": 10000},  # SF/fan
    },
    "electrical": {
        "watts_per_sf": {"low": 2, "typical": 6, "high": 15},
        "outlets": {"low": 50, "typical": 100, "high": 200},  # SF/outlet
        "panel_amps": {"low": 200, "typical": 600, "high": 2000},
    },
    "plumbing": {
        "fixture_units": {"low": 0.05, "typical": 0.1, "high": 0.2},  # FU/occupant
        "pipe_lf": {"low": 0.3, "typical": 0.5, "high": 0.8},  # LF/SF
    }
}

# Volatile market regions
VOLATILE_REGIONS = {
    "CA": ["San Francisco", "Los Angeles", "San Diego"],
    "NY": ["New York", "NYC", "Manhattan", "Brooklyn"],
    "WA": ["Seattle"],
    "MA": ["Boston"],
    "DC": ["Washington"],
}

# Building type complexity scores
BUILDING_COMPLEXITY = {
    "office": 1.0,
    "retail": 1.0,
    "warehouse": 0.8,
    "educational": 1.2,
    "healthcare": 1.5,
    "restaurant": 1.3,
    "industrial": 1.4,
    "multi_family_residential": 1.1,
}


class ConfidenceCalculator:
    """Calculate confidence scores for scope items"""
    
    @staticmethod
    def calculate_item_confidence(
        item_name: str,
        quantity: float,
        unit: str,
        category: str,
        building_type: str,
        square_footage: float,
        region: str = "",
        location: str = ""
    ) -> Tuple[int, str, Dict[str, Any]]:
        """
        Calculate confidence score for a single scope item
        
        Returns:
            Tuple of (score, label, factors_dict)
        """
        base_score = 95
        factors = {
            "base_score": base_score,
            "adjustments": []
        }
        
        # 1. Building type complexity adjustment
        complexity = BUILDING_COMPLEXITY.get(building_type, 1.0)
        if complexity > 1.3:
            adjustment = -5
            base_score += adjustment
            factors["adjustments"].append({
                "factor": "building_complexity",
                "adjustment": adjustment,
                "reason": f"Complex {building_type} building"
            })
        elif complexity < 0.9:
            adjustment = 3
            base_score += adjustment
            factors["adjustments"].append({
                "factor": "building_complexity",
                "adjustment": adjustment,
                "reason": f"Simple {building_type} building"
            })
        
        # 2. Quantity reasonableness check
        quantity_factor = ConfidenceCalculator._check_quantity_reasonableness(
            item_name, quantity, unit, category, square_footage
        )
        if quantity_factor != 0:
            base_score += quantity_factor
            factors["adjustments"].append({
                "factor": "quantity_check",
                "adjustment": quantity_factor,
                "reason": "Quantity outside typical range" if quantity_factor < 0 else "Quantity within typical range"
            })
        
        # 3. Regional volatility
        if ConfidenceCalculator._is_volatile_region(region, location):
            adjustment = -5
            base_score += adjustment
            factors["adjustments"].append({
                "factor": "regional_volatility",
                "adjustment": adjustment,
                "reason": f"Volatile market in {location or region}"
            })
        
        # 4. Special system complexity
        if any(term in item_name.lower() for term in [
            "clean room", "medical gas", "ups", "crac", "crane", "hepa"
        ]):
            adjustment = -3
            base_score += adjustment
            factors["adjustments"].append({
                "factor": "special_system",
                "adjustment": adjustment,
                "reason": "Specialized system with variable pricing"
            })
        
        # 5. Material volatility
        if any(term in item_name.lower() for term in ["steel", "copper", "lumber"]):
            adjustment = -2
            base_score += adjustment
            factors["adjustments"].append({
                "factor": "material_volatility",
                "adjustment": adjustment,
                "reason": "Commodity price volatility"
            })
        
        # Ensure score stays within bounds
        base_score = max(50, min(100, base_score))
        
        # Determine label
        if base_score >= 90:
            label = "High"
        elif base_score >= 75:
            label = "Medium"
        else:
            label = "Low"
        
        factors["final_score"] = base_score
        factors["label"] = label
        
        return base_score, label, factors
    
    @staticmethod
    def _check_quantity_reasonableness(
        item_name: str,
        quantity: float,
        unit: str,
        category: str,
        square_footage: float
    ) -> int:
        """Check if quantity is within reasonable range"""
        
        # Normalize quantity to per SF for comparison
        normalized_quantity = 0
        
        if "steel frame" in item_name.lower() and unit.lower() in ["lbs", "lb"]:
            normalized_quantity = quantity / square_footage
            ranges = TYPICAL_RANGES.get("structural", {}).get("steel_frame_lbs", {})
            
        elif "hvac" in item_name.lower() and unit.lower() in ["tons", "ton"]:
            normalized_quantity = square_footage / quantity if quantity > 0 else 0
            ranges = TYPICAL_RANGES.get("mechanical", {}).get("hvac_tons", {})
            
        elif "ductwork" in item_name.lower() and unit.lower() in ["lbs", "lb"]:
            normalized_quantity = quantity / square_footage
            ranges = TYPICAL_RANGES.get("mechanical", {}).get("ductwork_lbs", {})
            
        elif "outlet" in item_name.lower():
            normalized_quantity = square_footage / quantity if quantity > 0 else 0
            ranges = TYPICAL_RANGES.get("electrical", {}).get("outlets", {})
            
        else:
            # No specific range check
            return 0
        
        # Check against ranges
        if ranges:
            if normalized_quantity < ranges.get("low", 0):
                return -10  # Very unusual
            elif normalized_quantity > ranges.get("high", float('inf')):
                return -10  # Very unusual
            elif ranges.get("low", 0) <= normalized_quantity <= ranges.get("high", float('inf')):
                return 2  # Within expected range
        
        return 0
    
    @staticmethod
    def _is_volatile_region(region: str, location: str) -> bool:
        """Check if location is in a volatile market"""
        location_lower = location.lower()
        
        for state, cities in VOLATILE_REGIONS.items():
            if region == state:
                for city in cities:
                    if city.lower() in location_lower:
                        return True
        
        # Also check for direct mentions
        volatile_keywords = ["san francisco", "new york", "nyc", "manhattan", "seattle", "boston"]
        return any(keyword in location_lower for keyword in volatile_keywords)
    
    @staticmethod
    def apply_confidence_to_items(
        scope_items: list,
        building_type: str,
        square_footage: float,
        region: str = "",
        location: str = ""
    ) -> list:
        """Apply confidence scores to a list of scope items"""
        
        for item in scope_items:
            score, label, factors = ConfidenceCalculator.calculate_item_confidence(
                item_name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                category=item.category,
                building_type=building_type,
                square_footage=square_footage,
                region=region,
                location=location
            )
            
            item.confidence_score = score
            item.confidence_label = label
            item.confidence_factors = factors
        
        return scope_items