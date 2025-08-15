"""
Clean Scope Calculation Engine V2
Pure logic, no hardcoded values - reads everything from configs
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import uuid
import logging
from datetime import datetime

# Import ALL configs
from app.services.building_types_config import BUILDING_TYPES_CONFIG
from app.config.regional_multipliers import get_regional_multiplier
from app.config.feature_costs import get_feature_cost
from app.config.trade_percentages import get_trade_percentages
from app.config.finish_levels import (
    get_finish_multiplier, 
    get_classification_multiplier,
    detect_classification_from_text
)

logger = logging.getLogger(__name__)

@dataclass
class CalculationRequest:
    """Clean request structure"""
    building_type: str
    building_subtype: str
    square_footage: float
    location: str
    features: List[str] = None
    num_floors: int = 1
    finish_level: str = 'standard'
    project_classification: str = 'ground_up'
    project_description: str = None
    project_name: str = None

class CleanEngineV2:
    """
    Pure calculation engine - no hardcoded values.
    All data comes from config files.
    """
    
    def calculate(self, request: CalculationRequest) -> Dict:
        """
        Main calculation method - simple, transparent, testable
        """
        
        logger.info(f"Starting calculation for {request.building_type}/{request.building_subtype}")
        logger.info(f"[CLEAN ENGINE V2] Input features: {request.features}")
        
        # Auto-detect classification if not provided but description exists
        if request.project_classification == 'ground_up' and request.project_description:
            detected = detect_classification_from_text(request.project_description)
            if detected != 'ground_up':
                logger.info(f"Auto-detected project classification: {detected}")
                request.project_classification = detected
        
        # Step 1: Get base costs from config
        base_cost = self._get_base_cost(request.building_type, request.building_subtype)
        equipment_cost = self._get_equipment_cost(request.building_type, request.building_subtype)
        
        logger.info(f"[CLEAN ENGINE V2] Base costs: ${base_cost}/SF base, ${equipment_cost}/SF equipment")
        
        # Step 2: Calculate feature costs
        feature_cost, feature_details = self._calculate_feature_costs(
            request.building_type, 
            request.features or []
        )
        
        # Step 3: Sum raw construction cost
        raw_construction = base_cost + equipment_cost + feature_cost
        
        logger.info(f"[CLEAN ENGINE V2] Feature cost: ${feature_cost}/SF for features: {request.features}")
        logger.info(f"[CLEAN ENGINE V2] Raw construction: ${raw_construction}/SF (${base_cost} + ${equipment_cost} + ${feature_cost})")
        
        # Step 4: Get all multipliers
        regional_mult = get_regional_multiplier(request.location)
        finish_mult = get_finish_multiplier(request.finish_level)
        classification_mult = get_classification_multiplier(
            request.project_classification,
            request.building_type,
            request.building_subtype
        )
        
        # Step 5: Apply multipliers
        total_multiplier = regional_mult * finish_mult * classification_mult
        adjusted_cost_per_sf = raw_construction * total_multiplier
        
        logger.info(f"Multipliers: regional={regional_mult:.2f}, finish={finish_mult:.2f}, "
                   f"classification={classification_mult:.2f}, total={total_multiplier:.3f}")
        logger.info(f"Adjusted cost: ${adjusted_cost_per_sf:.2f}/SF")
        
        # Debug output for middle school calculations
        if request.building_type == "education" and request.building_subtype == "middle_school":
            print(f"DEBUG: Middle School Calculation")
            print(f"  Base: ${base_cost}")
            print(f"  Equipment: ${equipment_cost}")
            print(f"  Features: ${feature_cost}")
            print(f"  Raw total: ${base_cost + equipment_cost + feature_cost}")
            print(f"  Regional mult: {regional_mult}")
            print(f"  Finish mult: {finish_mult}")
            print(f"  Classification mult: {classification_mult}")
            print(f"  Final: ${adjusted_cost_per_sf}")
        
        # Step 6: Calculate totals - PURE CONSTRUCTION COST ONLY
        construction_subtotal = adjusted_cost_per_sf * request.square_footage  # Pure construction
        
        print(f"DEBUG CLEAN ENGINE:")
        print(f"  Construction: ${adjusted_cost_per_sf}/SF × {request.square_footage} SF = ${construction_subtotal:,.0f}")
        
        # Remove contingency - show pure construction cost only
        subtotal = adjusted_cost_per_sf * request.square_footage
        total_cost = subtotal  # No contingency added
        
        print(f"  Subtotal passed to categories: ${subtotal:,.0f}")
        print(f"  Total cost: ${total_cost:,.0f}")
        
        # Step 7: Generate trade breakdown
        categories = self._generate_categories(
            subtotal,
            request.building_type,
            request.building_subtype,
            request.square_footage,
            request.num_floors
        )
        
        # Step 8: Build response with all required fields
        # Generate project name if not provided
        if request.project_name:
            project_name = request.project_name
        else:
            # Auto-generate a descriptive project name
            subtype_display = request.building_subtype.replace('_', ' ').title()
            project_name = f"{int(request.square_footage):,} SF {subtype_display} - {request.location}"
        
        print(f"🚨 CLEAN ENGINE FINAL: Setting cost_per_sqft to ${adjusted_cost_per_sf}/SF")
        
        return {
            'project_id': str(uuid.uuid4())[:8],
            'project_name': project_name,
            'created_at': datetime.utcnow().isoformat(),
            'building_type': request.building_type,
            'building_subtype': request.building_subtype,
            'square_footage': request.square_footage,
            'location': request.location,
            'num_floors': request.num_floors,
            'finish_level': request.finish_level,
            'project_classification': request.project_classification,
            'features': request.features or [],
            'cost_per_sqft': round(adjusted_cost_per_sf, 2),
            'subtotal': round(subtotal, 2),
            'total_cost': round(total_cost, 2),
            'categories': categories,
            'request_data': {
                'building_type': request.building_type,
                'building_subtype': request.building_subtype,
                'square_footage': request.square_footage,
                'location': request.location,
                'num_floors': request.num_floors,
                'finish_level': request.finish_level,
                'project_classification': request.project_classification,
                'features': request.features or [],
                'project_description': request.project_description,
                'project_name': request.project_name
            },
            'calculation_breakdown': {
                'base_cost': base_cost,
                'equipment_cost': equipment_cost,
                'feature_cost': feature_cost,
                'feature_details': feature_details,
                'raw_construction': raw_construction,
                'multipliers': {
                    'regional': regional_mult,
                    'finish_level': finish_mult,
                    'classification': classification_mult,
                    'total': round(total_multiplier, 3)
                },
                'formula': (
                    f"(${base_cost} base + ${equipment_cost} equip + "
                    f"${feature_cost} features) × {total_multiplier:.3f} = "
                    f"${adjusted_cost_per_sf:.2f}/SF"
                )
            }
        }
    
    def _get_base_cost(self, building_type: str, subtype: str) -> float:
        """Get base cost from building config"""
        try:
            return BUILDING_TYPES_CONFIG[building_type]['subtypes'][subtype]['base_cost']
        except KeyError:
            logger.warning(f"No base cost for {building_type}/{subtype}, using default")
            # Try to find a reasonable default
            if building_type in BUILDING_TYPES_CONFIG:
                # Use first subtype as default
                first_subtype = list(BUILDING_TYPES_CONFIG[building_type]['subtypes'].keys())[0]
                return BUILDING_TYPES_CONFIG[building_type]['subtypes'][first_subtype]['base_cost']
            return 200  # Safe default
    
    def _get_equipment_cost(self, building_type: str, subtype: str) -> float:
        """Get equipment cost from building config"""
        try:
            return BUILDING_TYPES_CONFIG[building_type]['subtypes'][subtype]['equipment_cost']
        except KeyError:
            return 0
    
    def _calculate_feature_costs(self, building_type: str, features: List[str]) -> Tuple[float, List[Dict]]:
        """Calculate total cost of all features and return details"""
        if not features:
            return 0, []
        
        total = 0
        details = []
        for feature in features:
            cost = get_feature_cost(building_type, feature)
            if cost > 0:
                total += cost
                details.append({
                    'feature': feature,
                    'cost_per_sf': cost
                })
                logger.info(f"  Feature '{feature}': +${cost}/SF")
        
        return total, details
    
    def _generate_categories(self, subtotal: float, building_type: str, 
                            building_subtype: str, square_footage: float, 
                            num_floors: int) -> List[Dict]:
        """Generate trade breakdown categories"""
        
        percentages = get_trade_percentages(building_type, building_subtype)
        categories = []
        
        # Generate each trade category
        for trade in ['structural', 'mechanical', 'electrical', 'plumbing', 'finishes']:
            percentage = percentages.get(trade, 15)
            amount = subtotal * (percentage / 100)
            
            categories.append({
                'name': trade.capitalize(),
                'amount': round(amount, 2),
                'percentage': percentage,
                'systems': self._generate_systems(
                    trade, amount, square_footage, num_floors, building_type, building_subtype
                )
            })
        
        # General Conditions removed - showing pure construction costs only
        
        return categories
    
    def _generate_systems(self, trade: str, amount: float, 
                          sqft: float, floors: int, building_type: str,
                          building_subtype: str) -> List[Dict]:
        """Generate detailed systems for each trade"""
        
        if trade == 'structural':
            foundation_sf = sqft / floors
            return [
                {
                    'name': 'Foundation & Footings',
                    'quantity': round(foundation_sf, 0),
                    'unit': 'SF',
                    'unit_cost': round(amount * 0.30 / foundation_sf, 2),
                    'total_cost': round(amount * 0.30, 2)
                },
                {
                    'name': 'Structural Frame',
                    'quantity': round(sqft, 0),
                    'unit': 'SF',
                    'unit_cost': round(amount * 0.45 / sqft, 2),
                    'total_cost': round(amount * 0.45, 2)
                },
                {
                    'name': 'Roof Structure',
                    'quantity': round(foundation_sf, 0),
                    'unit': 'SF',
                    'unit_cost': round(amount * 0.25 / foundation_sf, 2),
                    'total_cost': round(amount * 0.25, 2)
                }
            ]
        
        elif trade == 'mechanical':
            # Customize by building type
            if building_type == 'education':
                tons = sqft / 500  # Schools need more ventilation
                return [
                    {
                        'name': 'HVAC Units & Equipment',
                        'quantity': round(tons, 1),
                        'unit': 'tons',
                        'unit_cost': round(amount * 0.60 / tons, 2),
                        'total_cost': round(amount * 0.60, 2)
                    },
                    {
                        'name': 'Ventilation & Ductwork',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.40 / sqft, 2),
                        'total_cost': round(amount * 0.40, 2)
                    }
                ]
            elif building_type == 'healthcare':
                tons = sqft / 300  # Healthcare needs more capacity
                return [
                    {
                        'name': 'Medical Grade HVAC',
                        'quantity': round(tons, 1),
                        'unit': 'tons',
                        'unit_cost': round(amount * 0.50 / tons, 2),
                        'total_cost': round(amount * 0.50, 2)
                    },
                    {
                        'name': 'Medical Gas Systems',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.25 / sqft, 2),
                        'total_cost': round(amount * 0.25, 2)
                    },
                    {
                        'name': 'Specialized Ventilation',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.25 / sqft, 2),
                        'total_cost': round(amount * 0.25, 2)
                    }
                ]
            elif building_type == 'restaurant':
                tons = sqft / 350
                return [
                    {
                        'name': 'Kitchen Ventilation & Hoods',
                        'quantity': round(sqft * 0.3, 0),  # Kitchen area
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.40 / (sqft * 0.3), 2),
                        'total_cost': round(amount * 0.40, 2)
                    },
                    {
                        'name': 'Dining HVAC',
                        'quantity': round(tons, 1),
                        'unit': 'tons',
                        'unit_cost': round(amount * 0.60 / tons, 2),
                        'total_cost': round(amount * 0.60, 2)
                    }
                ]
            else:
                # Generic mechanical
                tons = sqft / 400
                return [
                    {
                        'name': 'HVAC Equipment',
                        'quantity': round(tons, 1),
                        'unit': 'tons',
                        'unit_cost': round(amount * 0.60 / tons, 2),
                        'total_cost': round(amount * 0.60, 2)
                    },
                    {
                        'name': 'Distribution & Controls',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.40 / sqft, 2),
                        'total_cost': round(amount * 0.40, 2)
                    }
                ]
        
        elif trade == 'electrical':
            if building_type == 'healthcare':
                return [
                    {
                        'name': 'Emergency Power Systems',
                        'quantity': round(sqft / 100, 0),
                        'unit': 'KVA',
                        'unit_cost': round(amount * 0.30 / (sqft / 100), 2),
                        'total_cost': round(amount * 0.30, 2)
                    },
                    {
                        'name': 'Medical Equipment Power',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.40 / sqft, 2),
                        'total_cost': round(amount * 0.40, 2)
                    },
                    {
                        'name': 'Lighting & General Power',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.30 / sqft, 2),
                        'total_cost': round(amount * 0.30, 2)
                    }
                ]
            else:
                return [
                    {
                        'name': 'Power Distribution',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.50 / sqft, 2),
                        'total_cost': round(amount * 0.50, 2)
                    },
                    {
                        'name': 'Lighting Systems',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.50 / sqft, 2),
                        'total_cost': round(amount * 0.50, 2)
                    }
                ]
        
        elif trade == 'plumbing':
            if building_type == 'restaurant':
                return [
                    {
                        'name': 'Kitchen Plumbing & Grease Traps',
                        'quantity': round(sqft * 0.3, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.60 / (sqft * 0.3), 2),
                        'total_cost': round(amount * 0.60, 2)
                    },
                    {
                        'name': 'Restroom & Service Plumbing',
                        'quantity': round(sqft * 0.7, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.40 / (sqft * 0.7), 2),
                        'total_cost': round(amount * 0.40, 2)
                    }
                ]
            elif building_type == 'healthcare':
                return [
                    {
                        'name': 'Medical Gas & Vacuum',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.40 / sqft, 2),
                        'total_cost': round(amount * 0.40, 2)
                    },
                    {
                        'name': 'Special Drainage & Waste',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.30 / sqft, 2),
                        'total_cost': round(amount * 0.30, 2)
                    },
                    {
                        'name': 'Domestic Water Systems',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.30 / sqft, 2),
                        'total_cost': round(amount * 0.30, 2)
                    }
                ]
            else:
                fixtures = sqft / 500
                return [
                    {
                        'name': 'Plumbing Fixtures',
                        'quantity': round(fixtures, 0),
                        'unit': 'EA',
                        'unit_cost': round(amount * 0.40 / fixtures, 2),
                        'total_cost': round(amount * 0.40, 2)
                    },
                    {
                        'name': 'Piping & Distribution',
                        'quantity': round(sqft, 0),
                        'unit': 'SF',
                        'unit_cost': round(amount * 0.60 / sqft, 2),
                        'total_cost': round(amount * 0.60, 2)
                    }
                ]
        
        elif trade == 'finishes':
            return [
                {
                    'name': 'Flooring',
                    'quantity': round(sqft, 0),
                    'unit': 'SF',
                    'unit_cost': round(amount * 0.35 / sqft, 2),
                    'total_cost': round(amount * 0.35, 2)
                },
                {
                    'name': 'Wall Finishes',
                    'quantity': round(sqft * 3, 0),  # Wall area estimate
                    'unit': 'SF',
                    'unit_cost': round(amount * 0.25 / (sqft * 3), 2),
                    'total_cost': round(amount * 0.25, 2)
                },
                {
                    'name': 'Ceilings',
                    'quantity': round(sqft, 0),
                    'unit': 'SF',
                    'unit_cost': round(amount * 0.20 / sqft, 2),
                    'total_cost': round(amount * 0.20, 2)
                },
                {
                    'name': 'Millwork & Specialties',
                    'quantity': 1,
                    'unit': 'LS',
                    'unit_cost': round(amount * 0.20, 2),
                    'total_cost': round(amount * 0.20, 2)
                }
            ]
        
        else:
            # Generic system breakdown
            return [{
                'name': f'{trade.capitalize()} Systems',
                'quantity': round(sqft, 0),
                'unit': 'SF',
                'unit_cost': round(amount / sqft, 2),
                'total_cost': round(amount, 2)
            }]

# Create singleton instance
engine = CleanEngineV2()

# Export for easy use
def calculate_scope(request_data: dict) -> dict:
    """Convenience function for API integration"""
    request = CalculationRequest(
        building_type=request_data['building_type'],
        building_subtype=request_data['building_subtype'],
        square_footage=request_data['square_footage'],
        location=request_data['location'],
        features=request_data.get('features', []),
        num_floors=request_data.get('num_floors', 1),
        finish_level=request_data.get('finish_level', 'standard'),
        project_classification=request_data.get('project_classification', 'ground_up'),
        project_description=request_data.get('project_description'),
        project_name=request_data.get('project_name')
    )
    return engine.calculate(request)