"""Building type configuration service with service levels and features"""
from typing import Dict, List, Optional, Any
from enum import Enum


# Restaurant-specific item categorization rules
RESTAURANT_ITEM_CATEGORIZATION = {
    'mechanical': {
        'keywords': [
            'exhaust', 'hood', 'ventilation', 'make_up_air', 'makeup_air',
            'walk_in', 'walkin', 'cooler', 'freezer', 'refrigeration',
            'hvac', 'rtu', 'rooftop_unit', 'ductwork', 'duct',
            'ansul', 'fire_suppression', 'kitchen_exhaust', 'cfm',
            'air_conditioning', 'heating', 'cooling', 'condenser',
            'compressor', 'evaporator', 'air_handler', 'vav', 'thermostat'
        ],
        'exact_items': [
            'Type I Exhaust Hood System',
            'Make-up Air Unit',
            'Make-up Air Unit - Kitchen',
            'Walk-in Cooler',
            'Walk-in Freezer',
            'Walk-in Cooler (8x10)',
            'Walk-in Freezer (6x8)',
            'Kitchen Ventilation System',
            'Rooftop HVAC Unit',
            'Restaurant RTU - High Efficiency',
            'Ansul Fire Suppression System',
            'Kitchen Exhaust Ductwork - Stainless',
            'Dining Area Ductwork',
            'Refrigeration Compressor/Condenser Units'
        ]
    },
    'electrical': {
        'keywords': [
            'power', 'electrical', 'circuit', 'panel', 'breaker',
            'lighting', 'emergency', 'exit', 'outlet', 'receptacle',
            'disconnect', 'transformer', 'generator', 'ups',
            'fire_alarm', 'security', 'data', 'communications',
            'kitchen_equipment_power', 'hood_controls', 'shunt_trip',
            'voltage', 'amp', 'wire', 'conduit', 'junction'
        ],
        'exact_items': [
            'Kitchen Equipment Electrical Connections',
            'Hood Control Panel',
            'Emergency Shutoff System',
            'Kitchen Equipment Circuits',
            'Main Distribution Panel - 200A',
            'Kitchen Equipment Power',
            'Restaurant - Branch Panels & Feeders',
            'Restaurant - Conduit & Wire',
            'Restaurant - Grounding & Bonding'
        ]
    },
    'plumbing': {
        'keywords': [
            'grease', 'interceptor', 'trap', 'drain', 'floor_drain',
            'sink', 'faucet', 'water', 'gas', 'piping', 'pipe',
            'sprinkler', 'backflow', 'preventer', 'pre_rinse',
            'disposal', 'dishwasher', 'ice_machine', 'sewer',
            'waste', 'vent', 'fixture', 'valve', 'pump'
        ],
        'exact_items': [
            'Grease Interceptor - 1000 Gal',
            'Kitchen Floor Drains - Heavy Duty',
            'Pre-Rinse Spray Assembly',
            'Gas Piping to Kitchen Equipment',
            'Kitchen Equipment Connections',
            'Cast Iron Waste Pipe - 3"',
            'Cast Iron Waste Pipe - 4"',
            'PVC Waste Pipe - 2"',
            'Copper Water Pipe - 1"',
            'Copper Water Pipe - 3/4"',
            'Copper Water Pipe - 2"',
            'Pipe Insulation - Fiberglass'
        ]
    },
    'finishes': {
        'keywords': [
            'equipment', 'furnishing', 'furniture', 'fixture',
            'millwork', 'countertop', 'flooring', 'ceiling',
            'wall_covering', 'painting', 'tile', 'booth',
            'table', 'chair', 'bar', 'pos', 'menu_board',
            'decoration', 'finish', 'surface', 'coating'
        ],
        'exact_items': [
            'Kitchen Equipment Package',
            'Dining Room Furniture',
            'Bar Equipment',
            'POS System',
            'Flooring',
            'Wall Finishes',
            'Ceiling'
        ]
    },
    'structural': {
        'keywords': [
            'foundation', 'slab', 'frame', 'structural', 'steel',
            'concrete', 'rebar', 'beam', 'column', 'joist',
            'deck', 'roof', 'load', 'bearing', 'footing'
        ],
        'exact_items': [
            'Foundation/Slab',
            'Structural Frame',
            'Roof Structure'
        ]
    }
}


class ServiceLevel(str, Enum):
    # Restaurant service levels
    QUICK_SERVICE = "quick_service"
    CASUAL_DINING = "casual_dining"
    FULL_SERVICE = "full_service"
    FINE_DINING = "fine_dining"
    
    # Hospital service levels (future)
    OUTPATIENT_CLINIC = "outpatient_clinic"
    COMMUNITY_HOSPITAL = "community_hospital"
    REGIONAL_MEDICAL_CENTER = "regional_medical_center"
    TEACHING_HOSPITAL = "teaching_hospital"
    
    # School service levels (future)
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    UNIVERSITY = "university"


class BuildingFeature:
    def __init__(self, key: str, label: str, cost_per_sqft: float, description: str):
        self.key = key
        self.label = label
        self.cost_per_sqft = cost_per_sqft
        self.description = description


class BuildingTypeConfig:
    def __init__(
        self,
        building_type: str,
        service_levels: List[ServiceLevel],
        features: Dict[str, BuildingFeature],
        trade_allocations: Dict[str, Dict[str, float]],
        base_costs: Dict[str, Dict[str, float]]
    ):
        self.building_type = building_type
        self.service_levels = service_levels
        self.features = features
        self.trade_allocations = trade_allocations
        self.base_costs = base_costs


class BuildingTypeService:
    def __init__(self):
        self.building_configs = self._initialize_building_configs()
        self._validate_allocations()
        
    def _initialize_building_configs(self) -> Dict[str, BuildingTypeConfig]:
        """Initialize all building type configurations"""
        return {
            'restaurant': self._get_restaurant_config(),
            'hospital': self._get_hospital_config(),
            'school': self._get_school_config()
        }
    
    def _get_restaurant_config(self) -> BuildingTypeConfig:
        """Get restaurant configuration with service levels and features"""
        service_levels = [
            ServiceLevel.QUICK_SERVICE,
            ServiceLevel.CASUAL_DINING,
            ServiceLevel.FULL_SERVICE,
            ServiceLevel.FINE_DINING
        ]
        
        features = {
            'commercial_kitchen': BuildingFeature(
                key='commercial_kitchen',
                label='Full Commercial Kitchen',
                cost_per_sqft=75,
                description='Professional cooking equipment, hoods, ventilation'
            ),
            'full_bar': BuildingFeature(
                key='full_bar',
                label='Full Bar Service',
                cost_per_sqft=35,
                description='Bar equipment, draft systems, storage'
            ),
            'outdoor_dining': BuildingFeature(
                key='outdoor_dining',
                label='Outdoor Dining/Patio',
                cost_per_sqft=15,
                description='Patio construction, outdoor furniture'
            ),
            'premium_finishes': BuildingFeature(
                key='premium_finishes',
                label='Premium Interior Finishes',
                cost_per_sqft=50,
                description='High-end materials, custom millwork'
            ),
            'wine_cellar': BuildingFeature(
                key='wine_cellar',
                label='Wine Cellar/Storage',
                cost_per_sqft=25,
                description='Climate-controlled storage'
            ),
            'drive_thru': BuildingFeature(
                key='drive_thru',
                label='Drive-Thru Window',
                cost_per_sqft=20,
                description='Drive-thru lane, window, equipment'
            )
        }
        
        trade_allocations = {
            'quick_service': {
                'structural': 0.12,
                'mechanical': 0.18,
                'electrical': 0.15,
                'plumbing': 0.15,
                'finishes': 0.30,  # Includes kitchen equipment
                'general_conditions': 0.10
            },
            'casual_dining': {
                'structural': 0.11,
                'mechanical': 0.20,
                'electrical': 0.16,
                'plumbing': 0.17,
                'finishes': 0.26,
                'general_conditions': 0.10
            },
            'full_service': {
                'structural': 0.10,      # 10%
                'mechanical': 0.22,      # 22% - MUST BE 0.22
                'electrical': 0.175,     # 17.5%
                'plumbing': 0.175,      # 17.5%
                'finishes': 0.25,       # 25%
                'general_conditions': 0.08  # 8% - REDUCED
            },
            'fine_dining': {
                'structural': 0.08,
                'mechanical': 0.23,
                'electrical': 0.18,
                'plumbing': 0.19,  # Increased for extensive kitchen plumbing
                'finishes': 0.27,  # Adjusted for balance
                'general_conditions': 0.05
            }
        }
        
        # Base costs by state and service level
        base_costs = {
            'NH': {
                'quick_service': 225,
                'casual_dining': 300,
                'full_service': 400,
                'fine_dining': 525
            },
            'MA': {
                'quick_service': 250,
                'casual_dining': 325,
                'full_service': 425,
                'fine_dining': 550
            },
            'NY': {
                'quick_service': 275,
                'casual_dining': 350,
                'full_service': 450,
                'fine_dining': 600
            },
            'CA': {
                'quick_service': 300,
                'casual_dining': 375,
                'full_service': 475,
                'fine_dining': 625
            },
            # Default for other states
            'default': {
                'quick_service': 225,
                'casual_dining': 300,
                'full_service': 400,
                'fine_dining': 525
            }
        }
        
        return BuildingTypeConfig(
            building_type='restaurant',
            service_levels=service_levels,
            features=features,
            trade_allocations=trade_allocations,
            base_costs=base_costs
        )
    
    def _get_hospital_config(self) -> BuildingTypeConfig:
        """Placeholder for hospital configuration"""
        service_levels = [
            ServiceLevel.OUTPATIENT_CLINIC,
            ServiceLevel.COMMUNITY_HOSPITAL,
            ServiceLevel.REGIONAL_MEDICAL_CENTER,
            ServiceLevel.TEACHING_HOSPITAL
        ]
        
        features = {}  # To be implemented
        
        trade_allocations = {
            'outpatient_clinic': {
                'structural': 0.15,
                'mechanical': 0.25,
                'electrical': 0.20,
                'plumbing': 0.15,
                'finishes': 0.20,
                'general_conditions': 0.05
            },
            # Add other service levels
        }
        
        base_costs = {
            'default': {
                'outpatient_clinic': 300,
                'community_hospital': 450,
                'regional_medical_center': 600,
                'teaching_hospital': 750
            }
        }
        
        return BuildingTypeConfig(
            building_type='hospital',
            service_levels=service_levels,
            features=features,
            trade_allocations=trade_allocations,
            base_costs=base_costs
        )
    
    def _get_school_config(self) -> BuildingTypeConfig:
        """Placeholder for school configuration"""
        service_levels = [
            ServiceLevel.ELEMENTARY,
            ServiceLevel.MIDDLE_SCHOOL,
            ServiceLevel.HIGH_SCHOOL,
            ServiceLevel.UNIVERSITY
        ]
        
        features = {}  # To be implemented
        
        trade_allocations = {
            'elementary': {
                'structural': 0.20,
                'mechanical': 0.20,
                'electrical': 0.15,
                'plumbing': 0.10,
                'finishes': 0.25,
                'general_conditions': 0.10
            },
            # Add other service levels
        }
        
        base_costs = {
            'default': {
                'elementary': 200,
                'middle_school': 225,
                'high_school': 275,
                'university': 350
            }
        }
        
        return BuildingTypeConfig(
            building_type='school',
            service_levels=service_levels,
            features=features,
            trade_allocations=trade_allocations,
            base_costs=base_costs
        )
    
    def get_building_config(self, building_type: str) -> Optional[BuildingTypeConfig]:
        """Get configuration for a specific building type"""
        return self.building_configs.get(building_type)
    
    def get_base_cost(self, building_type: str, state: str, service_level: str) -> float:
        """Get base cost per square foot for a building type, state, and service level"""
        config = self.get_building_config(building_type)
        if not config:
            return 0
        
        # Try to get state-specific costs, fall back to default
        state_costs = config.base_costs.get(state.upper(), config.base_costs.get('default', {}))
        return state_costs.get(service_level, 0)
    
    def get_trade_allocations(self, building_type: str, service_level: str) -> Dict[str, float]:
        """Get trade allocation percentages for a building type and service level"""
        config = self.get_building_config(building_type)
        if not config:
            return {}
        
        return config.trade_allocations.get(service_level, {})
    
    def calculate_feature_costs(self, building_type: str, features: List[str], square_footage: float) -> float:
        """Calculate additional costs based on selected features"""
        config = self.get_building_config(building_type)
        if not config:
            return 0
        
        total_feature_cost = 0
        for feature_key in features:
            if feature_key in config.features:
                feature = config.features[feature_key]
                total_feature_cost += feature.cost_per_sqft * square_footage
        
        return total_feature_cost
    
    def categorize_item_for_restaurant(self, item_name: str) -> str:
        """Categorize restaurant items to correct trades based on comprehensive rules"""
        # First check exact item matches
        for trade, config in RESTAURANT_ITEM_CATEGORIZATION.items():
            if item_name in config.get('exact_items', []):
                return trade
        
        # Then check keywords
        item_lower = item_name.lower()
        for trade, config in RESTAURANT_ITEM_CATEGORIZATION.items():
            for keyword in config.get('keywords', []):
                # Replace underscores in keywords with spaces for matching
                keyword_normalized = keyword.replace('_', ' ')
                if keyword_normalized in item_lower:
                    return trade
        
        # Check for general conditions keywords
        gc_keywords = [
            'general conditions', 'gc', 'overhead', 'supervision', 'temporary', 
            'permit', 'insurance', 'bond', 'mobilization', 'cleanup', 'dumpster',
            'safety', 'testing', 'commissioning', 'as-built', 'warranty',
            'project management', 'superintendent'
        ]
        if any(keyword in item_lower for keyword in gc_keywords):
            return 'general_conditions'
        
        # Default to general_conditions for unmatched items
        return 'general_conditions'
    
    def categorize_line_item(self, item_name: str, building_type: str) -> str:
        """Properly categorize line items based on building type"""
        if building_type == 'restaurant':
            return self.categorize_item_for_restaurant(item_name)
                
        # Default categorization for non-restaurant or unmatched items
        # Check for standard categorizations
        item_lower = item_name.lower()
        if any(word in item_lower for word in ['structural', 'frame', 'foundation', 'roof', 'steel']):
            return 'structural'
        elif any(word in item_lower for word in ['hvac', 'heating', 'cooling', 'ventilation', 'duct']):
            return 'mechanical'
        elif any(word in item_lower for word in ['electrical', 'power', 'lighting', 'panel']):
            return 'electrical'
        elif any(word in item_lower for word in ['plumbing', 'pipe', 'drain', 'water', 'sewer']):
            return 'plumbing'
        elif any(word in item_lower for word in ['floor', 'wall', 'ceiling', 'paint', 'finish']):
            return 'finishes'
        
        return 'general_conditions'
    
    def _validate_allocations(self):
        """Validate that all trade allocations sum to 1.0"""
        for building_type, config in self.building_configs.items():
            for service_type, allocations in config.trade_allocations.items():
                total = sum(allocations.values())
                if not (0.99 <= total <= 1.01):
                    raise ValueError(f"{building_type} {service_type} allocations sum to {total}, not 1.0")


# Singleton instance
building_type_service = BuildingTypeService()