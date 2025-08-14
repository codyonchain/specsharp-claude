"""
Healthcare Facility Cost Calculation Service
Provides accurate cost estimates for hospitals, medical centers, and healthcare facilities
Integrates classifier with market-specific costs
"""
from typing import Dict, Tuple, Optional, List, Any
import re
import logging
from app.services.healthcare_classifier import HealthcareFacilityClassifier
from app.data.healthcare_market_costs import (
    get_market_costs, 
    calculate_equipment_cost,
    MEDICAL_EQUIPMENT_COSTS
)

logger = logging.getLogger(__name__)


class HealthcareFacilityType:
    """Healthcare facility types with base costs"""
    HOSPITAL = "hospital"
    SURGICAL_CENTER = "surgical_center"
    MEDICAL_CENTER = "medical_center"
    OUTPATIENT_CLINIC = "outpatient_clinic"
    URGENT_CARE = "urgent_care"
    MEDICAL_OFFICE = "medical_office"
    DENTAL_OFFICE = "dental_office"
    REHABILITATION = "rehabilitation"
    NURSING_HOME = "nursing_home"
    IMAGING_CENTER = "imaging_center"


# Base CONSTRUCTION costs per square foot (equipment calculated separately)
HEALTHCARE_BASE_COSTS = {
    # Full Hospitals (construction only - equipment adds $150-300/SF)
    HealthcareFacilityType.HOSPITAL: 850,  # Construction only
    HealthcareFacilityType.MEDICAL_CENTER: 750,  # Construction only
    
    # Specialized Facilities (equipment adds $200-300/SF for surgical)
    HealthcareFacilityType.SURGICAL_CENTER: 550,  # Construction only
    HealthcareFacilityType.IMAGING_CENTER: 500,  # Construction only
    
    # Outpatient Facilities
    HealthcareFacilityType.OUTPATIENT_CLINIC: 380,  # Construction only
    HealthcareFacilityType.URGENT_CARE: 350,  # Construction only
    HealthcareFacilityType.REHABILITATION: 325,  # Construction only
    
    # Medical Offices (equipment adds $10-30/SF)
    HealthcareFacilityType.MEDICAL_OFFICE: 320,  # Construction only
    HealthcareFacilityType.DENTAL_OFFICE: 300,  # Construction only
    
    # Residential Care
    HealthcareFacilityType.NURSING_HOME: 275,  # Construction only
}


# Keywords for identifying healthcare facility types from descriptions
HEALTHCARE_KEYWORDS = {
    HealthcareFacilityType.HOSPITAL: [
        'hospital', 'medical center', 'health center', 'healthcare center',
        'trauma center', 'emergency', 'emergency room', 'emergency department',
        'acute care', 'inpatient', 'icu', 'intensive care', 'critical care',
        'nicu', 'pediatric hospital', 'children\'s hospital', 'maternity'
    ],
    HealthcareFacilityType.SURGICAL_CENTER: [
        'surgical center', 'surgery center', 'operating room', 'operating suite',
        'ambulatory surgery', 'outpatient surgery', 'asc', 'or suite',
        'procedure room', 'endoscopy', 'cath lab', 'catheterization'
    ],
    HealthcareFacilityType.IMAGING_CENTER: [
        'imaging center', 'radiology', 'mri center', 'ct scan', 'x-ray',
        'diagnostic imaging', 'pet scan', 'mammography', 'ultrasound center'
    ],
    HealthcareFacilityType.OUTPATIENT_CLINIC: [
        'outpatient clinic', 'outpatient center', 'ambulatory care',
        'clinic', 'health clinic', 'community clinic', 'walk-in clinic'
    ],
    HealthcareFacilityType.URGENT_CARE: [
        'urgent care', 'immediate care', 'express care', 'walk-in care',
        'minor emergency', 'after hours clinic'
    ],
    HealthcareFacilityType.MEDICAL_OFFICE: [
        'medical office', 'doctor office', 'physician office', 'medical building',
        'primary care', 'family medicine', 'internal medicine', 'pediatrics',
        'specialty clinic', 'cardiology', 'oncology', 'neurology', 'orthopedic'
    ],
    HealthcareFacilityType.DENTAL_OFFICE: [
        'dental', 'dentist', 'orthodontic', 'oral surgery', 'endodontic',
        'periodontic', 'dental clinic'
    ],
    HealthcareFacilityType.REHABILITATION: [
        'rehabilitation', 'rehab center', 'physical therapy', 'pt clinic',
        'occupational therapy', 'speech therapy', 'recovery center'
    ],
    HealthcareFacilityType.NURSING_HOME: [
        'nursing home', 'assisted living', 'senior living', 'memory care',
        'long term care', 'skilled nursing', 'elder care', 'retirement home'
    ]
}


# Trade breakdown percentages for different healthcare facility types
HEALTHCARE_TRADE_BREAKDOWNS = {
    HealthcareFacilityType.HOSPITAL: {
        'structural': 0.15,      # Heavy structural for equipment, vibration isolation
        'mechanical': 0.35,      # Complex HVAC, medical gas, pneumatic tubes
        'electrical': 0.20,      # Redundant power, emergency systems, medical equipment
        'plumbing': 0.15,        # Medical gas, special drainage, dialysis
        'finishes': 0.08,        # Medical-grade finishes, cleanable surfaces
        'general_conditions': 0.07
    },
    HealthcareFacilityType.SURGICAL_CENTER: {
        'structural': 0.12,
        'mechanical': 0.38,      # OR requires precise HVAC control
        'electrical': 0.18,      # OR lighting, equipment power
        'plumbing': 0.14,        # Medical gas, special fixtures
        'finishes': 0.10,        # OR-grade finishes
        'general_conditions': 0.08
    },
    HealthcareFacilityType.IMAGING_CENTER: {
        'structural': 0.18,      # Heavy shielding for MRI/CT
        'mechanical': 0.30,      # Precise temperature control
        'electrical': 0.22,      # High power for imaging equipment
        'plumbing': 0.10,
        'finishes': 0.12,
        'general_conditions': 0.08
    },
    HealthcareFacilityType.OUTPATIENT_CLINIC: {
        'structural': 0.12,
        'mechanical': 0.28,      # Enhanced ventilation
        'electrical': 0.15,
        'plumbing': 0.12,        # Exam room sinks
        'finishes': 0.20,        # Better finishes for patient experience
        'general_conditions': 0.13
    },
    HealthcareFacilityType.MEDICAL_OFFICE: {
        'structural': 0.12,
        'mechanical': 0.25,      # Standard medical HVAC
        'electrical': 0.14,
        'plumbing': 0.11,
        'finishes': 0.25,        # Professional finishes
        'general_conditions': 0.13
    }
}


class HealthcareCostService:
    """Service for calculating healthcare facility costs"""
    
    def __init__(self):
        self.base_costs = HEALTHCARE_BASE_COSTS
        self.keywords = HEALTHCARE_KEYWORDS
        self.trade_breakdowns = HEALTHCARE_TRADE_BREAKDOWNS
        self.classifier = HealthcareFacilityClassifier()
    
    def determine_facility_type(self, description: str, occupancy_type: str = None) -> HealthcareFacilityType:
        """
        Determine the healthcare facility type from description
        
        Args:
            description: Natural language project description
            occupancy_type: Explicit occupancy type if provided
            
        Returns:
            HealthcareFacilityType enum value
        """
        if not description:
            # Default based on occupancy type
            if occupancy_type and 'hospital' in occupancy_type.lower():
                return HealthcareFacilityType.HOSPITAL
            return HealthcareFacilityType.MEDICAL_OFFICE
        
        description_lower = description.lower()
        
        # Check each facility type's keywords
        for facility_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    logger.info(f"Healthcare type detected: {facility_type} (matched '{keyword}')")
                    return facility_type
        
        # Default based on common terms
        if any(term in description_lower for term in ['healthcare', 'medical', 'health']):
            return HealthcareFacilityType.MEDICAL_OFFICE
        
        return HealthcareFacilityType.MEDICAL_OFFICE
    
    def get_base_cost(self, facility_type: HealthcareFacilityType) -> float:
        """Get base cost per square foot for facility type"""
        return self.base_costs.get(facility_type, 425)  # Default to general medical
    
    def get_healthcare_cost(self, 
                           description: str,
                           occupancy_type: str = None,
                           square_footage: float = 0) -> Dict[str, any]:
        """
        Calculate healthcare facility cost based on type and description
        
        Args:
            description: Natural language project description
            occupancy_type: Explicit occupancy type if provided
            square_footage: Building square footage
            
        Returns:
            Dictionary with cost details
        """
        # Determine facility type
        facility_type = self.determine_facility_type(description, occupancy_type)
        
        # Get base cost
        base_cost = self.get_base_cost(facility_type)
        
        # Parse additional features from description
        features = self.parse_healthcare_features(description)
        
        # Adjust base cost for features
        adjusted_cost = base_cost
        
        # Add cost for specific features
        if features.get('has_emergency'):
            adjusted_cost += 50  # Emergency department adds significant cost
        
        if features.get('has_surgery'):
            adjusted_cost += 75  # OR suites are expensive
        
        if features.get('has_imaging'):
            adjusted_cost += 40  # Imaging equipment and shielding
        
        if features.get('has_lab'):
            adjusted_cost += 25  # Laboratory space
        
        if features.get('is_specialty'):
            adjusted_cost += 30  # Specialized equipment and finishes
        
        # Adjust for bed count if applicable
        bed_count = features.get('bed_count', 0)
        if bed_count > 0:
            if bed_count < 50:
                adjusted_cost *= 0.95  # Small hospitals are slightly cheaper per SF
            elif bed_count > 200:
                adjusted_cost *= 1.05  # Large hospitals have more complexity
        
        return {
            'facility_type': facility_type,
            'base_cost_per_sf': base_cost,
            'adjusted_cost_per_sf': adjusted_cost,
            'features': features,
            'trade_breakdown': self.trade_breakdowns.get(
                facility_type, 
                self.trade_breakdowns[HealthcareFacilityType.MEDICAL_OFFICE]
            ),
            'complexity': self.get_complexity_level(facility_type),
            'confidence_score': self.calculate_confidence(facility_type, features)
        }
    
    def parse_healthcare_features(self, description: str) -> Dict[str, any]:
        """Parse healthcare-specific features from description"""
        if not description:
            return {}
        
        description_lower = description.lower()
        
        features = {
            'has_emergency': any(term in description_lower for term in [
                'emergency', 'er', 'emergency room', 'emergency department',
                'trauma', 'urgent'
            ]),
            'has_surgery': any(term in description_lower for term in [
                'surgery', 'surgical', 'operating room', 'or suite',
                'procedure room', 'operating theater', 'operating theatre'
            ]),
            'has_imaging': any(term in description_lower for term in [
                'mri', 'ct scan', 'ct', 'x-ray', 'xray', 'radiology',
                'imaging', 'pet scan', 'mammography', 'ultrasound'
            ]),
            'has_lab': any(term in description_lower for term in [
                'laboratory', 'lab', 'pathology', 'blood work', 'testing'
            ]),
            'is_specialty': any(term in description_lower for term in [
                'cancer', 'cardiac', 'heart', 'nicu', 'pediatric', 'children',
                'maternity', 'oncology', 'cardiology', 'neurology', 'orthopedic'
            ]),
            'has_pharmacy': any(term in description_lower for term in [
                'pharmacy', 'medication', 'drug'
            ]),
            'bed_count': self.extract_bed_count(description_lower)
        }
        
        return features
    
    def extract_bed_count(self, text: str) -> int:
        """Extract bed count from text"""
        patterns = [
            r'(\d+)[\s-]?bed',
            r'(\d+)[\s-]?patient[\s-]?room',
            r'(\d+)[\s-]?room[\s-]?(?:medical|hospital)',
            r'(\d+)[\s-]?room[\s-]?facility'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return 0
    
    def get_complexity_level(self, facility_type: HealthcareFacilityType) -> str:
        """Get complexity level for facility type"""
        high_complexity = [
            HealthcareFacilityType.HOSPITAL,
            HealthcareFacilityType.MEDICAL_CENTER,
            HealthcareFacilityType.SURGICAL_CENTER
        ]
        
        medium_complexity = [
            HealthcareFacilityType.IMAGING_CENTER,
            HealthcareFacilityType.OUTPATIENT_CLINIC,
            HealthcareFacilityType.URGENT_CARE
        ]
        
        if facility_type in high_complexity:
            return 'high'
        elif facility_type in medium_complexity:
            return 'medium'
        else:
            return 'standard'
    
    def calculate_confidence(self, facility_type: HealthcareFacilityType, features: Dict) -> int:
        """Calculate confidence score for estimate"""
        # Start with base confidence
        confidence = 85
        
        # Higher confidence for simpler facilities
        if facility_type in [HealthcareFacilityType.MEDICAL_OFFICE, 
                            HealthcareFacilityType.DENTAL_OFFICE]:
            confidence += 10
        
        # Lower confidence for complex facilities
        if facility_type == HealthcareFacilityType.HOSPITAL:
            confidence -= 10
        
        # Adjust based on features
        complex_features = ['has_emergency', 'has_surgery', 'has_imaging']
        complex_count = sum(1 for f in complex_features if features.get(f))
        
        if complex_count >= 2:
            confidence -= 5
        
        return max(70, min(95, confidence))
    
    def get_healthcare_addition_multiplier(self, facility_type: HealthcareFacilityType) -> float:
        """
        Get multiplier for healthcare additions
        Healthcare additions are more complex than standard commercial
        """
        if facility_type in [HealthcareFacilityType.HOSPITAL, 
                            HealthcareFacilityType.MEDICAL_CENTER]:
            return 1.25  # 25% premium for hospital additions
        elif facility_type in [HealthcareFacilityType.SURGICAL_CENTER,
                              HealthcareFacilityType.IMAGING_CENTER]:
            return 1.20  # 20% premium for specialized facility additions
        else:
            return 1.15  # Standard 15% premium for other healthcare additions
    
    def calculate_healthcare_costs_v2(
        self, 
        description: str, 
        square_feet: int, 
        location: str
    ) -> Dict[str, Any]:
        """
        Calculate complete healthcare facility costs using Phase 2 market-specific data
        
        Args:
            description: Natural language project description
            square_feet: Building square footage
            location: Project location (e.g., "Nashville, TN")
            
        Returns:
            Dictionary with comprehensive cost breakdown
        """
        # Classify the facility using the new classifier
        classification = self.classifier.classify_healthcare_facility(description)
        
        # Get market-specific costs
        market_data = get_market_costs(location)
        
        # Get base construction cost
        facility_type = classification['facility_type']
        base_cost_per_sf = market_data['facility_costs_per_sf'].get(
            facility_type, 
            275  # Default
        )
        
        # Note: The base_cost_per_sf from market data already includes typical complexity
        # Only apply additional complexity if significantly above normal (>1.2x)
        complexity_mult = classification['complexity_multiplier']
        if complexity_mult > 1.2:
            # Apply only the excess complexity
            base_cost_per_sf *= (1 + (complexity_mult - 1.0) * 0.3)  # Dampen the multiplier
        
        # Apply regional multiplier
        base_cost_per_sf *= market_data['regional_multiplier']
        
        # Calculate special space costs
        special_space_cost = 0
        special_spaces = classification['special_spaces']
        special_costs = market_data['special_space_costs']
        
        for space in special_spaces:
            # Estimate SF for special spaces (rough approximation)
            if space == 'operating_room':
                space_sf = min(600 * 2, square_feet * 0.1)  # 2 ORs or 10% max
            elif space == 'mri_suite':
                space_sf = 800
            elif space == 'ct_suite':
                space_sf = 600
            elif space == 'emergency_dept':
                space_sf = square_feet * 0.15  # 15% for ED
            elif space == 'icu':
                space_sf = square_feet * 0.1   # 10% for ICU
            else:
                space_sf = 400  # Default special space
            
            cost_per_sf = special_costs.get(space, 0)
            special_space_cost += cost_per_sf * space_sf
        
        # The base_cost_per_sf (after multipliers) IS the total construction cost per SF
        # Trade percentages show the BREAKDOWN, not additional multipliers
        # First, calculate the construction subtotal INCLUDING special spaces
        construction_cost_per_sf = base_cost_per_sf + (special_space_cost / square_feet)
        construction_subtotal = construction_cost_per_sf * square_feet
        
        # Now break down the total into trades (percentages should sum to 100%)
        trade_pct = market_data['trade_percentages']
        
        # Calculate base trade allocation (before special spaces)
        base_trade_total = base_cost_per_sf * square_feet
        trades = {
            'site_work': base_trade_total * trade_pct['site_work'],
            'structural': base_trade_total * trade_pct['structural'],
            'mechanical': base_trade_total * trade_pct['mechanical'],
            'electrical': base_trade_total * trade_pct['electrical'],
            'plumbing': base_trade_total * trade_pct['plumbing'],
            'finishes': base_trade_total * trade_pct['finishes'],
            'general_conditions': base_trade_total * trade_pct['general_conditions']
        }
        
        # Add special space premium to mechanical/electrical
        trades['mechanical'] += special_space_cost * 0.6
        trades['electrical'] += special_space_cost * 0.4
        
        # Apply compliance premiums (CON adds cost but not 5% of entire project)
        if market_data.get('certificate_of_need') and construction_subtotal > market_data.get('con_threshold', 0):
            # CON compliance adds fixed costs, not percentage of total
            # Typical CON costs: legal, consultants, delays = ~$500k-1M for large projects
            con_cost = min(1000000, construction_subtotal * 0.005)  # 0.5% max or $1M
            construction_subtotal += con_cost
        
        if market_data.get('state_licensing_premium'):
            construction_subtotal *= market_data.get('state_licensing_premium', 1.0)
        
        # Add contingency
        contingency = construction_subtotal * 0.10
        construction_total = construction_subtotal + contingency
        
        # Calculate equipment costs
        equipment_items = []
        equipment_total = 0
        
        for equipment_key, equipment_data in classification['equipment_needs'].items():
            equipment_items.append({
                'name': equipment_data['type'],
                'cost': equipment_data['typical_cost'],
                'requires_shielding': equipment_data.get('requires_shielding', False)
            })
            equipment_total += equipment_data['typical_cost']
        
        # Project totals
        project_total_with_equipment = construction_total + equipment_total
        
        # Add the calculated base_cost_per_sf to classification for reference
        classification['base_cost_per_sf'] = base_cost_per_sf
        
        return {
            'facility_type': facility_type,
            'classification': classification,
            'market': market_data['region_name'],
            'square_feet': square_feet,
            'regional_multiplier': market_data['regional_multiplier'],
            
            # Construction costs
            'construction': {
                'base_cost_per_sf': base_cost_per_sf,
                'trades': trades,
                'special_spaces_premium': special_space_cost,
                'subtotal': construction_subtotal,
                'contingency': contingency,
                'total': construction_total,
                'cost_per_sf': construction_total / square_feet
            },
            
            # Equipment costs (separate)
            'equipment': {
                'items': equipment_items,
                'total': equipment_total,
                'cost_per_sf': equipment_total / square_feet if square_feet > 0 else 0
            },
            
            # Combined totals
            'project_total': {
                'construction_only': construction_total,
                'equipment_only': equipment_total,
                'all_in_total': project_total_with_equipment,
                'all_in_cost_per_sf': project_total_with_equipment / square_feet
            },
            
            # Compliance and special requirements
            'compliance': classification['compliance_requirements'],
            'special_spaces': special_spaces
        }


# Initialize global service instance
healthcare_cost_service = HealthcareCostService()