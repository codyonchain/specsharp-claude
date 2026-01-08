"""
Clean Scope Engine - Deterministic, transparent construction cost calculations
No legacy code, no branching confusion, just pure calculations.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ScopeRequest:
    """Clean request structure for scope generation"""
    building_type: str
    building_subtype: str
    square_footage: float
    location: str
    num_floors: int = 1
    features: List[str] = None
    finish_level: str = 'standard'
    project_classification: str = 'ground_up'
    project_name: str = 'New Project'

class CleanScopeEngine:
    """
    Clean, deterministic scope calculation engine.
    No legacy code, no branching, just pure calculation.
    """
    
    def __init__(self):
        self.building_features = self._initialize_building_features()
        self.regional_multipliers = self._initialize_regional_multipliers()
        self.trade_percentages = self._initialize_trade_percentages()
        self.base_costs = self._initialize_base_costs()
        self.equipment_costs = self._initialize_equipment_costs()
    
    def _initialize_building_features(self) -> Dict[str, Dict[str, float]]:
        """Initialize building feature costs per square foot"""
        return {
            'education': {
                'gymnasium': 25,
                'science_labs': 20,
                'auditorium': 35,
                'cafeteria': 15,
                'athletic_field': 10,
                'library': 12,
                'computer_lab': 18
            },
            'healthcare': {
                'emergency_department': 50,
                'operating_rooms': 75,
                'mri_suite': 40,
                'ct_scanner': 35,
                'icu': 60,
                'nicu': 65,
                'catheterization_lab': 55,
                'pharmacy': 20,
                'laboratory': 30
            },
            'restaurant': {
                'drive_through': 25,
                'outdoor_seating': 15,
                'bar': 20,
                'private_dining': 10,
                'catering_kitchen': 30,
                'wine_cellar': 15
            },
            'hospitality': {
                'spa': 40,
                'conference_center': 25,
                'rooftop_bar': 35,
                'fitness_center': 20,
                'pool': 30,
                'restaurant': 25
            },
            'office': {
                'data_center': 50,
                'trading_floor': 60,
                'executive_suite': 30,
                'fitness_center': 20,
                'cafeteria': 15,
                'conference_center': 25
            },
            'industrial': {
                'clean_room': 100,
                'cold_storage': 75,
                'loading_docks': 15,
                'crane_systems': 40,
                'hazmat_storage': 50
            }
        }
    
    def _initialize_regional_multipliers(self) -> Dict[str, float]:
        """Initialize regional cost multipliers based on RSMeans 2024 Q2 data"""
        return {
            # Northeast
            'Boston, MA': 1.18,
            'New York, NY': 1.28,
            'Philadelphia, PA': 1.10,
            'Manchester, NH': 1.00,
            'Nashua, NH': 0.98,
            'Concord, NH': 0.97,
            'Hartford, CT': 1.08,
            
            # Southeast
            'Nashville, TN': 1.03,
            'Franklin, TN': 1.03,
            'Murfreesboro, TN': 1.01,
            'Memphis, TN': 0.98,
            'Atlanta, GA': 1.00,
            'Miami, FL': 1.05,
            'Charlotte, NC': 0.98,
            'Orlando, FL': 1.02,
            
            # Midwest
            'Chicago, IL': 1.12,
            'Detroit, MI': 1.05,
            'Minneapolis, MN': 1.08,
            'Columbus, OH': 0.98,
            'Milwaukee, WI': 1.05,
            
            # Southwest
            'Dallas, TX': 0.95,
            'Houston, TX': 0.97,
            'Phoenix, AZ': 0.95,
            'Austin, TX': 1.02,
            'San Antonio, TX': 0.94,
            
            # West
            'San Francisco, CA': 1.35,
            'Los Angeles, CA': 1.20,
            'San Diego, CA': 1.15,
            'Seattle, WA': 1.15,
            'Denver, CO': 1.05,
            'Portland, OR': 1.10,
            'Las Vegas, NV': 1.02,
            
            # Default
            'default': 1.00
        }
    
    def _initialize_trade_percentages(self) -> Dict[str, Dict[str, float]]:
        """Initialize trade percentage allocations by building type"""
        return {
            'education': {
                'structural': 0.30,
                'mechanical': 0.32,
                'electrical': 0.08,
                'plumbing': 0.22,
                'finishes': 0.08
            },
            'healthcare': {
                'structural': 0.25,
                'mechanical': 0.35,  # Higher for ventilation
                'electrical': 0.15,  # Higher for equipment
                'plumbing': 0.20,   # Medical gas, drainage
                'finishes': 0.05    # Medical-grade finishes
            },
            'restaurant': {
                'structural': 0.20,
                'mechanical': 0.25,  # Kitchen ventilation
                'electrical': 0.15,
                'plumbing': 0.30,   # Kitchen plumbing
                'finishes': 0.10
            },
            'office': {
                'structural': 0.35,
                'mechanical': 0.25,
                'electrical': 0.15,
                'plumbing': 0.10,
                'finishes': 0.15
            },
            'industrial': {
                'structural': 0.45,  # Heavy structure
                'mechanical': 0.20,
                'electrical': 0.20,
                'plumbing': 0.05,
                'finishes': 0.10
            },
            'hospitality': {
                'structural': 0.30,
                'mechanical': 0.25,
                'electrical': 0.12,
                'plumbing': 0.18,
                'finishes': 0.15   # Higher finishes
            },
            'residential': {
                'structural': 0.35,
                'mechanical': 0.20,
                'electrical': 0.10,
                'plumbing': 0.15,
                'finishes': 0.20   # Higher finishes
            },
            'retail': {
                'structural': 0.30,
                'mechanical': 0.20,
                'electrical': 0.15,
                'plumbing': 0.10,
                'finishes': 0.25   # Retail finishes
            },
            'default': {
                'structural': 0.30,
                'mechanical': 0.25,
                'electrical': 0.15,
                'plumbing': 0.15,
                'finishes': 0.15
            }
        }
    
    def _initialize_base_costs(self) -> Dict[str, Dict[str, float]]:
        """Initialize base construction costs per square foot"""
        return {
            'education': {
                'elementary_school': 275,
                'middle_school': 285,
                'high_school': 325,
                'university': 385,
                'vocational_school': 295,
                'daycare': 225
            },
            'healthcare': {
                'hospital': 950,
                'medical_office': 280,
                'urgent_care': 350,
                'surgery_center': 650,
                'dental_office': 325,
                'imaging_center': 475,
                'outpatient_clinic': 400,
                'senior_care': 285
            },
            'restaurant': {
                'qsr': 275,
                'fast_casual': 325,
                'casual_dining': 350,
                'fine_dining': 450,
                'full_service': 375  # Default
            },
            'office': {
                'class_a_office': 325,
                'class_b_office': 225,
                'class_c_office': 165,
                'tech_office': 425,
                'medical_office': 280
            },
            'industrial': {
                'warehouse': 75,
                'manufacturing': 110,
                'flex_space': 95,
                'cold_storage': 175,
                'data_center': 850
            },
            'retail': {
                'big_box': 135,
                'strip_center': 185,
                'mall_retail': 225,
                'boutique_retail': 325,
                'grocery': 245,
                'convenience_store': 285
            },
            'hospitality': {
                'luxury_hotel': 425,
                'full_service_hotel': 325,
                'limited_service_hotel': 225,
                'economy_hotel': 165,
                'boutique_hotel': 385
            },
            'residential': {
                'luxury_apartments': 185,
                'market_rate_apartments': 145,
                'affordable_housing': 120,
                'student_housing': 165,
                'condominiums': 195
            }
        }
    
    def _initialize_equipment_costs(self) -> Dict[str, Dict[str, float]]:
        """Initialize equipment costs per square foot"""
        return {
            'education': {
                'elementary_school': 25,
                'middle_school': 30,
                'high_school': 35,
                'university': 45,
                'vocational_school': 50,
                'daycare': 20
            },
            'healthcare': {
                'hospital': 200,
                'medical_office': 50,
                'urgent_care': 100,
                'surgery_center': 150,
                'dental_office': 125,
                'imaging_center': 175,
                'outpatient_clinic': 75,
                'senior_care': 40
            },
            'restaurant': {
                'qsr': 75,
                'fast_casual': 75,
                'casual_dining': 75,
                'fine_dining': 100,
                'full_service': 85
            },
            'office': {
                'class_a_office': 25,
                'class_b_office': 15,
                'class_c_office': 10,
                'tech_office': 50,
                'medical_office': 50
            },
            'industrial': {
                'warehouse': 10,
                'manufacturing': 15,
                'flex_space': 15,
                'cold_storage': 25,
                'data_center': 350
            },
            'retail': {
                'big_box': 15,
                'strip_center': 15,
                'mall_retail': 25,
                'boutique_retail': 25,
                'grocery': 30,
                'convenience_store': 40
            },
            'hospitality': {
                'luxury_hotel': 75,
                'full_service_hotel': 50,
                'limited_service_hotel': 35,
                'economy_hotel': 25,
                'boutique_hotel': 60
            },
            'residential': {
                'luxury_apartments': 40,
                'market_rate_apartments': 25,
                'affordable_housing': 15,
                'student_housing': 20,
                'condominiums': 35
            }
        }
    
    def calculate(self, request: ScopeRequest) -> Dict:
        """
        Main calculation method - single path, fully transparent
        """
        # Step 1: Get base costs
        base_cost = self._get_base_cost(request.building_type, request.building_subtype)
        equipment_cost = self._get_equipment_cost(request.building_type, request.building_subtype)
        
        # Step 2: Add features
        feature_cost = self._calculate_features(request.building_type, request.features or [])
        
        # Step 3: Sum construction cost
        construction_cost = base_cost + equipment_cost + feature_cost
        
        # Step 4: Apply multipliers
        regional_mult = self._get_regional_multiplier(request.location)
        finish_mult = self._get_finish_multiplier(request.finish_level)
        classification_mult = self._get_classification_multiplier(request.project_classification)
        
        # Step 5: Calculate final cost per SF
        cost_per_sqft = construction_cost * regional_mult * finish_mult * classification_mult
        
        # Step 6: Calculate totals
        subtotal = cost_per_sqft * request.square_footage
        contingency = subtotal * 0.10
        total_cost = subtotal + contingency
        
        # Step 7: Generate categories breakdown
        categories = self._generate_categories(
            subtotal, 
            request.building_type,
            request.square_footage,
            request.num_floors
        )
        
        # Step 8: Build response
        return {
            'project_id': self._generate_project_id(),
            'project_name': request.project_name,
            'building_type': request.building_type,
            'building_subtype': request.building_subtype,
            'square_footage': request.square_footage,
            'location': request.location,
            'num_floors': request.num_floors,
            'cost_per_sqft': round(cost_per_sqft, 2),
            'subtotal': round(subtotal, 2),
            'contingency_amount': round(contingency, 2),
            'contingency_percentage': 10,
            'total_cost': round(total_cost, 2),
            'categories': categories,
            'calculation_breakdown': {
                'base_cost': base_cost,
                'equipment_cost': equipment_cost,
                'feature_cost': feature_cost,
                'construction_total': construction_cost,
                'multipliers': {
                    'regional': regional_mult,
                    'finish_level': finish_mult,
                    'classification': classification_mult,
                    'combined': regional_mult * finish_mult * classification_mult
                },
                'formula': f"({base_cost} + {equipment_cost} + {feature_cost}) × {regional_mult:.2f} × {finish_mult} × {classification_mult} = ${cost_per_sqft:.2f}/SF"
            },
            'confidence_score': 95  # Always high confidence with deterministic calculation
        }
    
    def _get_base_cost(self, building_type: str, subtype: str) -> float:
        """Get base construction cost from config"""
        costs = self.base_costs.get(building_type, {})
        return costs.get(subtype, 200)  # Default to $200/SF if not found
    
    def _get_equipment_cost(self, building_type: str, subtype: str) -> float:
        """Get equipment cost from config"""
        equipment = self.equipment_costs.get(building_type, {})
        return equipment.get(subtype, 0)
    
    def _calculate_features(self, building_type: str, features: List[str]) -> float:
        """Calculate additional cost from features"""
        if not features:
            return 0
        
        feature_costs = self.building_features.get(building_type, {})
        total_feature_cost = sum(
            feature_costs.get(feature.lower().replace(' ', '_'), 0) 
            for feature in features
        )
        return total_feature_cost
    
    def _get_regional_multiplier(self, location: str) -> float:
        """Get regional cost multiplier"""
        if not location:
            return 1.0
        
        # Try exact match first
        for city, multiplier in self.regional_multipliers.items():
            if city.lower() in location.lower():
                return multiplier
        
        # Extract state and try state-level defaults
        state_defaults = {
            'NH': 0.99,  # New Hampshire average
            'TN': 1.01,  # Tennessee average
            'MA': 1.18,  # Massachusetts average
            'CA': 1.25,  # California average
            'TX': 0.96,  # Texas average
            'NY': 1.28,  # New York average
            'FL': 1.03,  # Florida average
            'IL': 1.12,  # Illinois average
        }
        
        for state_code, default_mult in state_defaults.items():
            if f', {state_code}' in location or f',{state_code}' in location:
                return default_mult
        
        return self.regional_multipliers.get('default', 1.0)
    
    def _get_finish_multiplier(self, finish_level: str) -> float:
        """Get finish level multiplier"""
        multipliers = {
            'basic': 0.85,
            'standard': 1.00,
            'premium': 1.25,
            'luxury': 1.50
        }
        return multipliers.get(finish_level.lower(), 1.0)
    
    def _get_classification_multiplier(self, classification: str) -> float:
        """Get project classification multiplier"""
        multipliers = {
            'ground_up': 1.00,
            'addition': 1.15,
            'renovation': 1.35,
            'tenant_improvement': 1.20
        }
        return multipliers.get(classification.lower(), 1.0)
    
    def _generate_categories(self, subtotal: float, building_type: str, 
                            square_footage: float, num_floors: int) -> List[Dict]:
        """Generate detailed category breakdown"""
        percentages = self.trade_percentages.get(
            building_type, 
            self.trade_percentages['default']
        )
        
        categories = []
        
        # Structural
        structural_amount = subtotal * percentages['structural']
        categories.append({
            'name': 'Structural',
            'amount': round(structural_amount, 2),
            'percentage': percentages['structural'] * 100,
            'systems': self._generate_structural_systems(
                structural_amount, square_footage, num_floors
            )
        })
        
        # Mechanical
        mechanical_amount = subtotal * percentages['mechanical']
        categories.append({
            'name': 'Mechanical',
            'amount': round(mechanical_amount, 2),
            'percentage': percentages['mechanical'] * 100,
            'systems': self._generate_mechanical_systems(
                mechanical_amount, square_footage, building_type
            )
        })
        
        # Electrical
        electrical_amount = subtotal * percentages['electrical']
        categories.append({
            'name': 'Electrical',
            'amount': round(electrical_amount, 2),
            'percentage': percentages['electrical'] * 100,
            'systems': self._generate_electrical_systems(
                electrical_amount, square_footage
            )
        })
        
        # Plumbing
        plumbing_amount = subtotal * percentages['plumbing']
        categories.append({
            'name': 'Plumbing',
            'amount': round(plumbing_amount, 2),
            'percentage': percentages['plumbing'] * 100,
            'systems': self._generate_plumbing_systems(
                plumbing_amount, square_footage, building_type
            )
        })
        
        # Finishes
        finishes_amount = subtotal * percentages['finishes']
        categories.append({
            'name': 'Finishes',
            'amount': round(finishes_amount, 2),
            'percentage': percentages['finishes'] * 100,
            'systems': self._generate_finishes_systems(
                finishes_amount, square_footage
            )
        })
        
        # General Conditions (always 10% of construction)
        gc_amount = subtotal * 0.10
        categories.append({
            'name': 'General Conditions',
            'amount': round(gc_amount, 2),
            'percentage': 10,
            'systems': self._generate_gc_systems(gc_amount)
        })
        
        return categories
    
    def _generate_structural_systems(self, total: float, sqft: float, floors: int) -> List[Dict]:
        """Generate structural systems breakdown"""
        roof_sqft = sqft / floors if floors > 0 else sqft
        
        return [
            {
                'name': 'Foundation/Slab',
                'quantity': sqft / floors if floors > 0 else sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.30 / (sqft / floors if floors > 0 else sqft), 2),
                'total_cost': round(total * 0.30, 2)
            },
            {
                'name': 'Structural Frame',
                'quantity': sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.40 / sqft, 2),
                'total_cost': round(total * 0.40, 2)
            },
            {
                'name': 'Roof Structure',
                'quantity': roof_sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.20 / roof_sqft, 2),
                'total_cost': round(total * 0.20, 2)
            },
            {
                'name': 'Miscellaneous Steel',
                'quantity': sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.10 / sqft, 2),
                'total_cost': round(total * 0.10, 2)
            }
        ]
    
    def _generate_mechanical_systems(self, total: float, sqft: float, building_type: str) -> List[Dict]:
        """Generate mechanical systems based on building type"""
        if building_type == 'education':
            return [
                {
                    'name': 'Classroom Unit Ventilators',
                    'quantity': sqft / 1000,
                    'unit': 'tons',
                    'unit_cost': round(total * 0.40 / (sqft / 1000), 2),
                    'total_cost': round(total * 0.40, 2)
                },
                {
                    'name': 'Gymnasium HVAC System',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.20, 2),
                    'total_cost': round(total * 0.20, 2)
                },
                {
                    'name': 'Ventilation & Ductwork',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.25 / sqft, 2),
                    'total_cost': round(total * 0.25, 2)
                },
                {
                    'name': 'Controls & BMS',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.15, 2),
                    'total_cost': round(total * 0.15, 2)
                }
            ]
        elif building_type == 'healthcare':
            return [
                {
                    'name': 'Medical Gas System',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.15 / sqft, 2),
                    'total_cost': round(total * 0.15, 2)
                },
                {
                    'name': 'HVAC with HEPA Filtration',
                    'quantity': sqft / 300,
                    'unit': 'tons',
                    'unit_cost': round(total * 0.45 / (sqft / 300), 2),
                    'total_cost': round(total * 0.45, 2)
                },
                {
                    'name': 'Exhaust & Ventilation',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.25 / sqft, 2),
                    'total_cost': round(total * 0.25, 2)
                },
                {
                    'name': 'Controls & Monitoring',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.15, 2),
                    'total_cost': round(total * 0.15, 2)
                }
            ]
        elif building_type == 'restaurant':
            return [
                {
                    'name': 'Kitchen Exhaust Hood System',
                    'quantity': sqft * 0.3,  # Kitchen is ~30% of restaurant
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.35 / (sqft * 0.3), 2),
                    'total_cost': round(total * 0.35, 2)
                },
                {
                    'name': 'Make-up Air Unit',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.20, 2),
                    'total_cost': round(total * 0.20, 2)
                },
                {
                    'name': 'Dining Area HVAC',
                    'quantity': sqft / 400,
                    'unit': 'tons',
                    'unit_cost': round(total * 0.30 / (sqft / 400), 2),
                    'total_cost': round(total * 0.30, 2)
                },
                {
                    'name': 'Walk-in Cooler/Freezer',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.15, 2),
                    'total_cost': round(total * 0.15, 2)
                }
            ]
        else:
            # Generic mechanical
            return [
                {
                    'name': 'HVAC Equipment',
                    'quantity': sqft / 400,
                    'unit': 'tons',
                    'unit_cost': round(total * 0.50 / (sqft / 400), 2),
                    'total_cost': round(total * 0.50, 2)
                },
                {
                    'name': 'Ductwork & Distribution',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.35 / sqft, 2),
                    'total_cost': round(total * 0.35, 2)
                },
                {
                    'name': 'Controls',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.15, 2),
                    'total_cost': round(total * 0.15, 2)
                }
            ]
    
    def _generate_electrical_systems(self, total: float, sqft: float) -> List[Dict]:
        """Generate electrical systems breakdown"""
        return [
            {
                'name': 'Main Distribution Panel',
                'quantity': 1,
                'unit': 'system',
                'unit_cost': round(total * 0.15, 2),
                'total_cost': round(total * 0.15, 2)
            },
            {
                'name': 'Lighting Systems',
                'quantity': sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.35 / sqft, 2),
                'total_cost': round(total * 0.35, 2)
            },
            {
                'name': 'Power Distribution',
                'quantity': sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.30 / sqft, 2),
                'total_cost': round(total * 0.30, 2)
            },
            {
                'name': 'Emergency/Backup Power',
                'quantity': 1,
                'unit': 'system',
                'unit_cost': round(total * 0.10, 2),
                'total_cost': round(total * 0.10, 2)
            },
            {
                'name': 'Fire Alarm System',
                'quantity': sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.10 / sqft, 2),
                'total_cost': round(total * 0.10, 2)
            }
        ]
    
    def _generate_plumbing_systems(self, total: float, sqft: float, building_type: str) -> List[Dict]:
        """Generate plumbing systems based on building type"""
        if building_type == 'restaurant':
            return [
                {
                    'name': 'Kitchen Plumbing & Fixtures',
                    'quantity': sqft * 0.3,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.40 / (sqft * 0.3), 2),
                    'total_cost': round(total * 0.40, 2)
                },
                {
                    'name': 'Grease Interceptor System',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.20, 2),
                    'total_cost': round(total * 0.20, 2)
                },
                {
                    'name': 'Restroom Fixtures',
                    'quantity': sqft / 500,
                    'unit': 'fixtures',
                    'unit_cost': round(total * 0.25 / (sqft / 500), 2),
                    'total_cost': round(total * 0.25, 2)
                },
                {
                    'name': 'Water Heater System',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.15, 2),
                    'total_cost': round(total * 0.15, 2)
                }
            ]
        elif building_type == 'healthcare':
            return [
                {
                    'name': 'Medical Gas Piping',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.30 / sqft, 2),
                    'total_cost': round(total * 0.30, 2)
                },
                {
                    'name': 'Specialized Drainage',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.25 / sqft, 2),
                    'total_cost': round(total * 0.25, 2)
                },
                {
                    'name': 'Fixtures & Equipment',
                    'quantity': sqft / 200,
                    'unit': 'fixtures',
                    'unit_cost': round(total * 0.30 / (sqft / 200), 2),
                    'total_cost': round(total * 0.30, 2)
                },
                {
                    'name': 'Water Treatment',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.15, 2),
                    'total_cost': round(total * 0.15, 2)
                }
            ]
        else:
            return [
                {
                    'name': 'Water Distribution',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.30 / sqft, 2),
                    'total_cost': round(total * 0.30, 2)
                },
                {
                    'name': 'Drainage System',
                    'quantity': sqft,
                    'unit': 'sqft',
                    'unit_cost': round(total * 0.30 / sqft, 2),
                    'total_cost': round(total * 0.30, 2)
                },
                {
                    'name': 'Fixtures',
                    'quantity': sqft / 1000,
                    'unit': 'fixtures',
                    'unit_cost': round(total * 0.30 / (sqft / 1000), 2),
                    'total_cost': round(total * 0.30, 2)
                },
                {
                    'name': 'Water Heater',
                    'quantity': 1,
                    'unit': 'system',
                    'unit_cost': round(total * 0.10, 2),
                    'total_cost': round(total * 0.10, 2)
                }
            ]
    
    def _generate_finishes_systems(self, total: float, sqft: float) -> List[Dict]:
        """Generate finishes systems breakdown"""
        return [
            {
                'name': 'Flooring',
                'quantity': sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.35 / sqft, 2),
                'total_cost': round(total * 0.35, 2)
            },
            {
                'name': 'Wall Finishes',
                'quantity': sqft * 3,  # Wall area is ~3x floor area
                'unit': 'sqft',
                'unit_cost': round(total * 0.25 / (sqft * 3), 2),
                'total_cost': round(total * 0.25, 2)
            },
            {
                'name': 'Ceiling Systems',
                'quantity': sqft,
                'unit': 'sqft',
                'unit_cost': round(total * 0.20 / sqft, 2),
                'total_cost': round(total * 0.20, 2)
            },
            {
                'name': 'Doors & Hardware',
                'quantity': sqft / 500,
                'unit': 'doors',
                'unit_cost': round(total * 0.10 / (sqft / 500), 2),
                'total_cost': round(total * 0.10, 2)
            },
            {
                'name': 'Specialties & Accessories',
                'quantity': 1,
                'unit': 'lot',
                'unit_cost': round(total * 0.10, 2),
                'total_cost': round(total * 0.10, 2)
            }
        ]
    
    def _generate_gc_systems(self, total: float) -> List[Dict]:
        """Generate general conditions breakdown"""
        return [
            {
                'name': 'Project Management & Supervision',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': round(total * 0.30, 2),
                'total_cost': round(total * 0.30, 2)
            },
            {
                'name': 'Temporary Facilities & Equipment',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': round(total * 0.20, 2),
                'total_cost': round(total * 0.20, 2)
            },
            {
                'name': 'Insurance & Bonds',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': round(total * 0.25, 2),
                'total_cost': round(total * 0.25, 2)
            },
            {
                'name': 'Permits & Fees',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': round(total * 0.15, 2),
                'total_cost': round(total * 0.15, 2)
            },
            {
                'name': 'Project Closeout & Commissioning',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': round(total * 0.10, 2),
                'total_cost': round(total * 0.10, 2)
            }
        ]
    
    def _generate_project_id(self) -> str:
        """Generate unique project ID"""
        return str(uuid.uuid4())[:8]

# Create singleton instance
engine = CleanScopeEngine()