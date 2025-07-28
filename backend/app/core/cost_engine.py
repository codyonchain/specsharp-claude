"""
Cost Calculation Engine with Building Type Specifications

This module implements a proper cost calculation hierarchy:
1. Base Material Cost → 2. Building Type Adjustments → 3. Regional Multipliers
"""
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
import re
from app.core.floor_parser import needs_elevator, calculate_elevator_count
from app.core.confidence_calculator import ConfidenceCalculator


@dataclass
class ScopeItem:
    """Represents a single scope item with quantity and unit"""
    name: str
    quantity: float
    unit: str
    unit_cost: float = 0.0
    total_cost: float = 0.0
    note: str = ""
    category: str = ""
    confidence_score: int = 95
    confidence_label: str = "High"
    confidence_factors: Dict[str, Any] = field(default_factory=dict)


# Building Type Specifications define material quantities per building type
BUILDING_TYPE_SPECIFICATIONS = {
    "commercial": {
        "structural": {
            "steel_frame_weight": 10,  # lbs/SF
            "concrete_slab_thickness": 6,  # inches
            "foundation_depth": 4,  # feet
            "column_spacing": 30,  # feet
        },
        "mechanical": {
            "hvac_tons_per_sf": 400,  # 1 ton per 400 SF
            "ductwork_gauge": 24,
            "vav_boxes_per_sf": 800,  # 1 per 800 SF
            "exhaust_fans_per_sf": 5000,  # 1 per 5000 SF
        },
        "electrical": {
            "watts_per_sf": 5,
            "panel_amps": 400,
            "outlets_per_sf": 125,  # 1 per 125 SF
            "lighting_fc": 30,  # foot-candles
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.1,
            "pipe_size_main": 2,  # inches
            "occupants_per_sf": 100,  # 1 per 100 SF
        }
    },
    "educational": {
        "structural": {
            "steel_frame_weight": 14,  # lbs/SF - longer spans for classrooms
            "concrete_slab_thickness": 8,  # inches - higher loads
            "foundation_depth": 5,  # feet - multi-story capable
            "column_spacing": 40,  # feet - open classrooms
        },
        "mechanical": {
            "hvac_tons_per_sf": 300,  # 1 ton per 300 SF - higher ventilation
            "ductwork_gauge": 22,  # heavier gauge
            "vav_boxes_per_sf": 600,  # 1 per 600 SF - more zones
            "exhaust_fans_per_sf": 3000,  # labs and cafeteria
        },
        "electrical": {
            "watts_per_sf": 8,  # higher for technology
            "panel_amps": 800,
            "outlets_per_sf": 75,  # 1 per 75 SF - computer labs
            "data_drops_per_sf": 150,  # 1 per 150 SF
            "lighting_fc": 50,  # higher for classrooms
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.15,  # more restrooms
            "pipe_size_main": 3,  # inches - cafeteria needs
            "drinking_fountains_per_floor": 4,
            "occupants_per_sf": 50,  # 1 per 50 SF - higher density
        }
    },
    "warehouse": {
        "structural": {
            "steel_frame_weight": 8,  # lbs/SF - simple frame
            "concrete_slab_thickness": 8,  # inches - forklift traffic
            "foundation_depth": 3,  # feet
            "column_spacing": 50,  # feet - clear spans
        },
        "mechanical": {
            "hvac_tons_per_sf": 600,  # 1 ton per 600 SF - minimal
            "ductwork_gauge": 26,
            "unit_heaters": True,  # instead of VAV
            "exhaust_fans_per_sf": 10000,
        },
        "electrical": {
            "watts_per_sf": 2,
            "panel_amps": 400,
            "outlets_per_sf": 1000,  # 1 per 1000 SF
            "high_bay_lighting": True,
            "lighting_fc": 20,  # lower requirements
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.05,  # minimal
            "pipe_size_main": 1.5,  # inches
            "occupants_per_sf": 500,  # 1 per 500 SF - low density
        }
    },
    "healthcare": {
        "structural": {
            "steel_frame_weight": 16,  # lbs/SF - heavy equipment
            "concrete_slab_thickness": 10,  # inches - equipment loads
            "foundation_depth": 6,  # feet - vibration isolation
            "column_spacing": 25,  # feet - equipment access
        },
        "mechanical": {
            "hvac_tons_per_sf": 250,  # 1 ton per 250 SF - critical environments
            "ductwork_gauge": 20,  # hospital grade
            "vav_boxes_per_sf": 400,  # precise control
            "exhaust_fans_per_sf": 2000,  # isolation rooms
            "medical_gas": True,
        },
        "electrical": {
            "watts_per_sf": 10,  # medical equipment
            "panel_amps": 1200,
            "outlets_per_sf": 50,  # 1 per 50 SF - equipment
            "emergency_power": True,
            "lighting_fc": 70,  # surgical requirements
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.2,  # patient rooms
            "pipe_size_main": 4,  # inches
            "medical_gas_outlets_per_bed": 6,
            "occupants_per_sf": 200,  # includes patients
        }
    },
    "office": {
        "structural": {
            "steel_frame_weight": 10,  # lbs/SF
            "concrete_slab_thickness": 5,  # inches
            "foundation_depth": 4,  # feet
            "column_spacing": 30,  # feet
        },
        "mechanical": {
            "hvac_tons_per_sf": 350,  # 1 ton per 350 SF
            "ductwork_gauge": 24,
            "vav_boxes_per_sf": 600,  # 1 per 600 SF
            "exhaust_fans_per_sf": 5000,
        },
        "electrical": {
            "watts_per_sf": 6,
            "panel_amps": 600,
            "outlets_per_sf": 100,  # 1 per 100 SF
            "data_drops_per_sf": 100,  # 1 per 100 SF
            "lighting_fc": 40,
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.1,
            "pipe_size_main": 2,  # inches
            "occupants_per_sf": 150,  # 1 per 150 SF
        }
    },
    "restaurant": {
        "structural": {
            "steel_frame_weight": 12,  # lbs/SF - kitchen equipment
            "concrete_slab_thickness": 8,  # inches - kitchen loads
            "foundation_depth": 4,  # feet
            "column_spacing": 25,  # feet - dining flexibility
            "grease_interceptor_pad": True,
        },
        "mechanical": {
            "hvac_tons_per_sf": 200,  # 1 ton per 200 SF - kitchen heat
            "ductwork_gauge": 22,  # grease-rated
            "makeup_air_cfm_per_sf": 1.5,  # kitchen ventilation
            "exhaust_hoods": True,
            "exhaust_fans_per_sf": 2000,
        },
        "electrical": {
            "watts_per_sf": 12,  # kitchen equipment
            "panel_amps": 800,
            "outlets_per_sf": 60,  # 1 per 60 SF - equipment
            "kitchen_equipment_circuits": True,
            "lighting_fc": 50,
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.15,
            "pipe_size_main": 3,  # inches
            "grease_interceptor": True,
            "floor_drains_per_sf": 200,  # 1 per 200 SF in kitchen
            "gas_piping": True,
            "occupants_per_sf": 15,  # 1 per 15 SF - dining density
        }
    },
    "multi_family_residential": {
        "structural": {
            "steel_frame_weight": 9,  # lbs/SF - wood frame common
            "concrete_slab_thickness": 5,  # inches - standard residential
            "foundation_depth": 4,  # feet
            "column_spacing": 20,  # feet - unit layout constraints
            "demising_walls": True,  # fire-rated between units
        },
        "mechanical": {
            "hvac_tons_per_sf": 450,  # 1 ton per 450 SF - individual units
            "ductwork_gauge": 26,  # lighter residential grade
            "individual_units": True,  # split systems per unit
            "exhaust_fans_per_sf": 500,  # bathroom/kitchen per unit
            "dryer_vents_per_unit": 1,
        },
        "electrical": {
            "watts_per_sf": 4,  # residential loads
            "panel_amps": 200,  # per unit
            "outlets_per_sf": 80,  # 1 per 80 SF - residential density
            "individual_meters": True,
            "lighting_fc": 30,  # residential requirements
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.5,  # full bathroom per unit
            "pipe_size_main": 3,  # inches - multiple units
            "water_heater_per_unit": True,
            "washer_connections_per_unit": 1,
            "occupants_per_sf": 400,  # 2.5 per 1000 SF unit average
        }
    },
    "industrial": {
        "structural": {
            "steel_frame_weight": 12,  # lbs/SF - heavier for crane loads
            "concrete_slab_thickness": 10,  # inches - for equipment
            "foundation_depth": 6,  # feet - deeper for vibration
            "column_spacing": 60,  # feet - clear spans for operations
            "crane_capable": True,
        },
        "mechanical": {
            "hvac_tons_per_sf": 500,  # 1 ton per 500 SF - less comfort cooling
            "ductwork_gauge": 20,  # heavier industrial grade
            "process_piping": True,
            "compressed_air": True,
            "dust_collection": True,
            "exhaust_fans_per_sf": 2000,  # industrial ventilation
        },
        "electrical": {
            "watts_per_sf": 15,  # 3x office for machinery
            "panel_amps": 2000,  # high capacity
            "voltage": "480V",  # industrial voltage
            "motor_control_centers": True,
            "outlets_per_sf": 500,  # 1 per 500 SF
            "lighting_fc": 30,  # task lighting requirements
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.05,  # minimal fixtures
            "pipe_size_main": 2,  # inches
            "process_water": True,
            "floor_drains_per_sf": 1000,  # 1 per 1000 SF
            "occupants_per_sf": 1000,  # 1 per 1000 SF - low density
        }
    },
    "hospitality": {
        "structural": {
            "steel_frame_weight": 11,  # lbs/SF - between office and residential
            "concrete_slab_thickness": 6,  # inches - standard floors
            "foundation_depth": 4,  # feet
            "column_spacing": 25,  # feet - room layout constraints
            "demising_walls": True,  # sound-rated between rooms
        },
        "mechanical": {
            "hvac_tons_per_sf": 350,  # 1 ton per 350 SF - individual room control
            "ductwork_gauge": 24,  # standard commercial
            "individual_units": True,  # PTAC or VRF per room
            "exhaust_fans_per_sf": 450,  # per room bathroom
            "laundry_exhaust": True,
            "kitchen_exhaust": True,
        },
        "electrical": {
            "watts_per_sf": 7,  # moderate for guest rooms + common areas
            "panel_amps": 1000,  # large service for all rooms
            "outlets_per_sf": 100,  # multiple per room
            "card_key_system": True,
            "emergency_lighting": True,
            "lighting_fc": 35,  # comfortable ambient lighting
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.75,  # 3 fixtures per room average
            "pipe_size_main": 4,  # inches - high demand
            "hot_water_recirc": True,
            "laundry_equipment": True,
            "occupants_per_sf": 225,  # ~2 per 450 SF room
        }
    },
    "retail": {
        "structural": {
            "steel_frame_weight": 10,  # lbs/SF - standard commercial frame
            "concrete_slab_thickness": 6,  # inches - standard retail
            "foundation_depth": 4,  # feet
            "column_spacing": 40,  # feet - open retail space
            "storefront_system": True,  # aluminum and glass
        },
        "mechanical": {
            "hvac_tons_per_sf": 350,  # 1 ton per 350 SF - high occupancy
            "ductwork_gauge": 24,  # standard commercial
            "vav_boxes_per_sf": 1000,  # 1 per 1000 SF - open spaces
            "exhaust_fans_per_sf": 5000,  # minimal exhaust
            "make_up_air": True,  # for retail spaces
        },
        "electrical": {
            "watts_per_sf": 8,  # high for display lighting
            "panel_amps": 800,  # varies by size
            "outlets_per_sf": 200,  # 1 per 200 SF
            "track_lighting": True,  # retail display
            "signage_power": True,  # exterior signage
            "lighting_fc": 50,  # bright retail lighting
        },
        "plumbing": {
            "fixture_units_per_occupant": 0.08,  # minimal restrooms
            "pipe_size_main": 2,  # inches
            "floor_drains_per_sf": 5000,  # service areas only
            "occupants_per_sf": 60,  # 1 per 60 SF - retail density
        }
    }
}

# Base Unit Costs (national average per unit)
BASE_UNIT_COSTS = {
    # Structural
    "steel_frame_per_lb": 2.50,
    "concrete_per_cy": 150.00,
    "rebar_per_ton": 1200.00,
    
    # Mechanical
    "hvac_ton": 1500.00,
    "ductwork_per_lb": 6.00,
    "vav_box": 850.00,
    "exhaust_fan_1000cfm": 2500.00,
    "makeup_air_unit_per_cfm": 12.00,
    
    # Electrical
    "panel_per_amp": 25.00,
    "outlet": 125.00,
    "data_drop": 250.00,
    "lighting_per_sf": 4.50,
    
    # Plumbing
    "fixture_unit": 450.00,
    "pipe_per_lf": {"1.5": 35, "2": 45, "3": 65, "4": 85},
    "floor_drain": 650.00,
    "grease_interceptor": 15000.00,
    
    # Elevators (updated costs)
    "passenger_elevator": 75000.00,  # Standard commercial
    "passenger_elevator_ada": 85000.00,  # ADA school-rated
    "passenger_elevator_hospital": 125000.00,  # Hospital gurney size
    "service_elevator": 150000.00,  # Freight/service
    "passenger_elevator_traction": 250000.00,  # High-rise traction
    
    # Industrial Equipment
    "compressed_air_system": 45000.00,  # 100 HP system
    "dust_collection_system": 35000.00,  # 10,000 CFM
    "process_piping_per_lf": 85.00,  # Stainless steel
    "motor_control_center": 75000.00,  # 480V MCC
    "crane_rail_per_lf": 450.00,  # 10-ton capacity
    "loading_dock_equipment": 25000.00,  # Per door
    "industrial_exhaust_fan": 8500.00,  # 10,000 CFM
    
    # Clean Room / Pharma
    "hepa_filter_unit": 5500.00,  # Per unit
    "clean_room_ahu": 125000.00,  # 10,000 CFM
    "epoxy_flooring_per_sf": 8.50,  # Seamless
    
    # Food Processing
    "washdown_station": 3500.00,  # Stainless steel
    "floor_coating_per_sf": 6.50,  # USDA approved
    "insulated_panel_per_sf": 18.00,  # Walk-in cooler
    
    # Data Center
    "ups_system_per_kw": 1200.00,  # Uninterruptible power
    "crac_unit": 45000.00,  # Computer room AC
    "raised_floor_per_sf": 15.00,  # Access flooring
    
    # Hospitality Equipment
    "ptac_unit": 1200.00,  # Per room HVAC unit
    "vrf_system_per_ton": 2500.00,  # Variable refrigerant flow
    "card_key_system_per_door": 350.00,  # Electronic lock system
    "guest_room_bathroom_package": 4500.00,  # Complete bathroom fixtures
    "commercial_laundry_washer": 12000.00,  # Industrial size
    "commercial_laundry_dryer": 8000.00,  # Industrial size
    "ffe_per_room": 12000.00,  # Furniture, fixtures & equipment
    
    # Retail Equipment
    "storefront_system_per_lf": 450.00,  # Aluminum and glass storefront
    "automatic_doors": 8500.00,  # Per pair
    "refrigeration_rack_system": 125000.00,  # Grocery store system
    "walk_in_cooler_per_sf": 185.00,  # Insulated box with refrigeration
    "display_case_lf": 1200.00,  # Refrigerated display cases
    "pos_system": 5500.00,  # Point of sale terminal
    "security_system_retail": 15000.00,  # EAS tags, cameras
    "loading_dock_retail": 12000.00,  # Dock leveler and door
    "demising_wall_per_lf": 85.00,  # Between tenant spaces
    "tenant_electrical_panel": 8500.00,  # Sub-panel for tenant
}

# Building Complexity Factors (installation difficulty, not quantity)
BUILDING_COMPLEXITY_FACTORS = {
    "commercial": {
        "structural": 1.0,
        "mechanical": 1.0,
        "electrical": 1.0,
        "plumbing": 1.0,
        "finishes": 1.0,
    },
    "educational": {
        "structural": 1.1,  # more complex connections
        "mechanical": 1.2,  # zone control complexity
        "electrical": 1.15,  # technology integration
        "plumbing": 1.1,  # multiple restroom cores
        "finishes": 1.3,  # durability requirements
    },
    "warehouse": {
        "structural": 0.9,  # simpler connections
        "mechanical": 0.8,  # basic systems
        "electrical": 0.85,  # simple distribution
        "plumbing": 0.7,  # minimal fixtures
        "finishes": 0.6,  # basic finishes
    },
    "healthcare": {
        "structural": 1.2,  # seismic and vibration
        "mechanical": 1.4,  # medical gas, controls
        "electrical": 1.3,  # emergency systems
        "plumbing": 1.3,  # medical gas integration
        "finishes": 1.4,  # infection control
    },
    "office": {
        "structural": 1.0,
        "mechanical": 1.1,  # tenant flexibility
        "electrical": 1.1,  # high data density
        "plumbing": 1.0,
        "finishes": 1.2,  # professional appearance
    },
    "restaurant": {
        "structural": 1.1,  # equipment support
        "mechanical": 1.3,  # kitchen exhaust complexity
        "electrical": 1.2,  # kitchen equipment
        "plumbing": 1.2,  # grease management
        "finishes": 1.1,  # durability
    },
    "multi_family_residential": {
        "structural": 0.95,  # repetitive unit layout
        "mechanical": 0.9,  # standardized systems
        "electrical": 0.95,  # repetitive wiring
        "plumbing": 0.9,  # stacked plumbing
        "finishes": 1.0,  # standard residential
    },
    "industrial": {
        "structural": 1.15,  # heavy equipment support
        "mechanical": 1.25,  # process systems complexity
        "electrical": 1.3,  # motor controls and power
        "plumbing": 1.1,  # process piping
        "finishes": 0.7,  # minimal finishes
    },
    "hospitality": {
        "structural": 1.05,  # standard with sound isolation
        "mechanical": 1.15,  # individual room systems
        "electrical": 1.2,  # card key and room controls
        "plumbing": 1.15,  # multiple bathrooms
        "finishes": 1.25,  # guest experience quality
    },
    "retail": {
        "structural": 1.0,  # standard construction
        "mechanical": 1.05,  # simple distribution
        "electrical": 1.1,  # display lighting complexity
        "plumbing": 0.85,  # minimal fixtures
        "finishes": 1.15,  # retail quality finishes
    }
}

# Regional Multipliers (DO NOT MODIFY - applies to final costs)
REGIONAL_MULTIPLIERS = {
    "TX": {
        "structural": 0.95,
        "mechanical": 0.97,
        "electrical": 0.96,
        "plumbing": 0.95,
        "finishes": 0.94
    },
    "NH": {
        "structural": 1.15,
        "mechanical": 1.12,
        "electrical": 1.14,
        "plumbing": 1.13,
        "finishes": 1.10
    },
    "NY": {
        "structural": 1.25,
        "mechanical": 1.22,
        "electrical": 1.24,
        "plumbing": 1.23,
        "finishes": 1.20
    },
    "CA": {
        "structural": 1.20,
        "mechanical": 1.18,
        "electrical": 1.19,
        "plumbing": 1.18,
        "finishes": 1.15
    },
    "FL": {
        "structural": 1.02,
        "mechanical": 1.00,
        "electrical": 1.01,
        "plumbing": 1.00,
        "finishes": 0.98
    },
    "IL": {
        "structural": 1.10,
        "mechanical": 1.08,
        "electrical": 1.09,
        "plumbing": 1.08,
        "finishes": 1.05
    },
    "WA": {
        "structural": 1.12,
        "mechanical": 1.10,
        "electrical": 1.11,
        "plumbing": 1.10,
        "finishes": 1.08
    },
    "GA": {
        "structural": 0.98,
        "mechanical": 0.96,
        "electrical": 0.97,
        "plumbing": 0.96,
        "finishes": 0.95
    },
    "PA": {
        "structural": 1.08,
        "mechanical": 1.06,
        "electrical": 1.07,
        "plumbing": 1.06,
        "finishes": 1.04
    },
    "AZ": {
        "structural": 1.00,
        "mechanical": 0.98,
        "electrical": 0.99,
        "plumbing": 0.98,
        "finishes": 0.97
    }
}


def calculate_quantities(specs: Dict[str, Any], square_footage: float) -> Dict[str, float]:
    """Calculate material quantities based on building specifications"""
    quantities = {}
    
    # Structural quantities
    if "steel_frame_weight" in specs:
        quantities["steel_frame_lbs"] = specs["steel_frame_weight"] * square_footage
    
    if "concrete_slab_thickness" in specs:
        # Convert thickness in inches to cubic yards
        slab_volume_cf = square_footage * (specs["concrete_slab_thickness"] / 12)
        quantities["concrete_cy"] = slab_volume_cf / 27
        
        # Estimate rebar at 0.5% of concrete volume
        quantities["rebar_tons"] = (slab_volume_cf * 150 * 0.005) / 2000  # 150 lb/cf concrete
    
    # Mechanical quantities
    if "hvac_tons_per_sf" in specs:
        quantities["hvac_tons"] = square_footage / specs["hvac_tons_per_sf"]
    
    if "vav_boxes_per_sf" in specs:
        quantities["vav_boxes"] = square_footage / specs["vav_boxes_per_sf"]
    
    if "exhaust_fans_per_sf" in specs:
        quantities["exhaust_fans"] = square_footage / specs["exhaust_fans_per_sf"]
    
    # Electrical quantities
    if "outlets_per_sf" in specs:
        quantities["outlets"] = square_footage / specs["outlets_per_sf"]
    
    if "data_drops_per_sf" in specs:
        quantities["data_drops"] = square_footage / specs.get("data_drops_per_sf", float('inf'))
    
    if "panel_amps" in specs:
        quantities["panel_amps"] = specs["panel_amps"]
    
    # Plumbing quantities
    if "fixture_units_per_occupant" in specs and "occupants_per_sf" in specs:
        occupants = square_footage / specs["occupants_per_sf"]
        quantities["fixture_units"] = occupants * specs["fixture_units_per_occupant"]
    
    if "floor_drains_per_sf" in specs:
        quantities["floor_drains"] = square_footage / specs.get("floor_drains_per_sf", float('inf'))
    
    return quantities


def extract_number_before_keyword(description: str, keywords: List[str]) -> Optional[int]:
    """Extract number immediately before specific keywords in description"""
    if not description:
        return None
    
    description_lower = description.lower()
    
    for keyword in keywords:
        # Patterns like "6 operating rooms", "10 OR", "4 surgery"
        patterns = [
            rf'(\d+)\s+{keyword}',
            rf'(\d+)\s*{keyword}',
            rf'(\d+)-{keyword}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description_lower)
            if match:
                return int(match.group(1))
    
    return None


def add_building_specific_mechanical_items(scope_items: List[ScopeItem], building_type: str, 
                                         square_footage: float, floors: int, 
                                         description: str = "") -> List[ScopeItem]:
    """Add detailed mechanical items specific to building type"""
    
    # Create a copy to avoid modifying the original
    items = scope_items.copy()
    
    # ELEVATORS FOR ALL MULTI-STORY BUILDINGS
    if floors > 1:
        if building_type == 'healthcare':
            # Hospital elevators
            patient_elevators = max(3, int(square_footage / 50000))
            service_elevators = max(1, int(square_footage / 100000))
            
            items.extend([
                ScopeItem(
                    name='Patient Elevator - Gurney Size (5000 lb, 5\'8"x8\')',
                    quantity=patient_elevators,
                    unit='EA',
                    unit_cost=125000,
                    total_cost=patient_elevators * 125000,
                    category='Mechanical',
                    note=f'Hospital-size cab, {floors} stops, bed transport capable'
                ),
                ScopeItem(
                    name='Service/Freight Elevator (6000 lb)',
                    quantity=service_elevators,
                    unit='EA',
                    unit_cost=150000,
                    total_cost=service_elevators * 150000,
                    category='Mechanical',
                    note=f'For equipment and supplies, {floors} stops'
                )
            ])
        
        elif building_type == 'educational':
            # School elevators (ADA compliant)
            elevators_needed = max(1, int(square_footage / 75000))
            items.append(ScopeItem(
                name='Passenger Elevator - ADA Compliant (3500 lb)',
                quantity=elevators_needed,
                unit='EA',
                unit_cost=85000,
                total_cost=elevators_needed * 85000,
                category='Mechanical',
                note=f'School-rated with key control, {floors} stops'
            ))
        
        else:  # Commercial, office, mixed-use
            elevators_needed = max(1, int(square_footage / 50000))
            items.append(ScopeItem(
                name='Passenger Elevator (3500 lb)',
                quantity=elevators_needed,
                unit='EA',
                unit_cost=75000,
                total_cost=elevators_needed * 75000,
                category='Mechanical',
                note=f'Standard commercial, {floors} stops'
            ))
    
    # HEALTHCARE-SPECIFIC MECHANICAL
    if building_type == 'healthcare':
        # Extract OR count from description if mentioned
        or_count = extract_number_before_keyword(description, ['operating room', 'or', 'surgery'])
        or_count = or_count or max(4, int(square_footage / 50000))  # Default estimate
        
        items.extend([
            ScopeItem(
                name='Operating Room AHU - 100% Outside Air',
                quantity=or_count,
                unit='EA',
                unit_cost=45000,
                total_cost=or_count * 45000,
                category='Mechanical',
                note='HEPA filtration, laminar flow, 20-25 air changes/hr'
            ),
            ScopeItem(
                name='Laboratory Exhaust System',
                quantity=max(25, int(square_footage / 4000)),
                unit='hoods',
                unit_cost=3500,
                total_cost=max(25, int(square_footage / 4000)) * 3500,
                category='Mechanical',
                note='Variable volume fume hood exhaust'
            ),
            ScopeItem(
                name='Pharmacy Clean Room AHU',
                quantity=1,
                unit='LS',
                unit_cost=35000,
                total_cost=35000,
                category='Mechanical',
                note='USP 797/800 compliant, HEPA filtered'
            ),
            ScopeItem(
                name='Kitchen Exhaust Hood System',
                quantity=1,
                unit='LS',
                unit_cost=45000,
                total_cost=45000,
                category='Mechanical',
                note='Commercial kitchen with make-up air'
            ),
            ScopeItem(
                name='Emergency Dept Isolation Exhaust',
                quantity=10,
                unit='rooms',
                unit_cost=8500,
                total_cost=10 * 8500,
                category='Mechanical',
                note='Negative pressure, dedicated exhaust'
            )
        ])
    
    # EDUCATIONAL-SPECIFIC MECHANICAL
    elif building_type == 'educational':
        has_gym = 'gym' in description.lower() or 'gymnasium' in description.lower()
        has_cafeteria = 'cafeteria' in description.lower()
        
        if has_gym:
            items.append(ScopeItem(
                name='Gymnasium HVAC Unit',
                quantity=2,
                unit='EA',
                unit_cost=65000,
                total_cost=2 * 65000,
                category='Mechanical',
                note='High-volume air handling for assembly space'
            ))
        
        if has_cafeteria:
            items.append(ScopeItem(
                name='Kitchen Hood & Exhaust System',
                quantity=1,
                unit='LS',
                unit_cost=35000,
                total_cost=35000,
                category='Mechanical',
                note='School kitchen ventilation with make-up air'
            ))
        
        # Science lab exhaust
        items.append(ScopeItem(
            name='Science Lab Exhaust System',
            quantity=max(4, int(square_footage / 15000)),
            unit='labs',
            unit_cost=12000,
            total_cost=max(4, int(square_footage / 15000)) * 12000,
            category='Mechanical',
            note='Fume hoods and general exhaust'
        ))
    
    # RESTAURANT-SPECIFIC MECHANICAL
    elif building_type == 'restaurant':
        kitchen_sf = square_footage * 0.3  # Typical 30% for kitchen
        
        items.extend([
            ScopeItem(
                name='Kitchen Hood System - Type I',
                quantity=max(2, int(kitchen_sf / 500)),
                unit='EA',
                unit_cost=18000,
                total_cost=max(2, int(kitchen_sf / 500)) * 18000,
                category='Mechanical',
                note='Grease-rated with fire suppression'
            ),
            ScopeItem(
                name='Kitchen Make-up Air Unit',
                quantity=max(1, int(kitchen_sf / 1000)),
                unit='EA',
                unit_cost=22000,
                total_cost=max(1, int(kitchen_sf / 1000)) * 22000,
                category='Mechanical',
                note='Tempered make-up air, interlocked with hoods'
            ),
            ScopeItem(
                name='Walk-in Cooler/Freezer Package',
                quantity=1,
                unit='LS',
                unit_cost=45000,
                total_cost=45000,
                category='Mechanical',
                note='Includes refrigeration and controls'
            ),
            ScopeItem(
                name='Dining Area Split Systems',
                quantity=max(4, int(square_footage / 2000)),
                unit='EA',
                unit_cost=8500,
                total_cost=max(4, int(square_footage / 2000)) * 8500,
                category='Mechanical',
                note='Separate zones for comfort control'
            )
        ])
    
    # MULTI-FAMILY RESIDENTIAL-SPECIFIC MECHANICAL
    elif building_type == 'multi_family_residential':
        # Unit mix data if available
        unit_count = max(10, int(square_footage / 1000))  # Default 1000 SF per unit
        
        # Individual HVAC units per apartment
        items.append(ScopeItem(
            name='Split System Heat Pump - Per Unit',
            quantity=unit_count,
            unit='EA',
            unit_cost=4500,
            total_cost=unit_count * 4500,
            category='Mechanical',
            note='Individual unit HVAC systems'
        ))
        
        # Common area HVAC
        common_area_sf = square_footage * 0.15  # 15% common areas
        common_hvac_tons = common_area_sf / 400
        items.append(ScopeItem(
            name='Common Area HVAC System',
            quantity=common_hvac_tons,
            unit='tons',
            unit_cost=2000,
            total_cost=common_hvac_tons * 2000,
            category='Mechanical',
            note='Corridors, lobby, amenity spaces'
        ))
        
        # Exhaust fans for bathrooms and kitchens
        items.append(ScopeItem(
            name='Bathroom/Kitchen Exhaust Fans',
            quantity=unit_count * 2,  # 2 per unit average
            unit='EA',
            unit_cost=350,
            total_cost=unit_count * 2 * 350,
            category='Mechanical',
            note='Code-required ventilation'
        ))
        
        # Dryer vents
        items.append(ScopeItem(
            name='Dryer Vent Systems',
            quantity=unit_count,
            unit='EA',
            unit_cost=450,
            total_cost=unit_count * 450,
            category='Mechanical',
            note='Individual dryer venting to exterior'
        ))
        
        # If multi-story, add elevators
        if floors > 2:
            elevators_needed = max(1, int(unit_count / 50))  # 1 per 50 units
            items.append(ScopeItem(
                name='Passenger Elevator - Residential',
                quantity=elevators_needed,
                unit='EA',
                unit_cost=75000,
                total_cost=elevators_needed * 75000,
                category='Mechanical',
                note=f'Residential duty, {floors} stops'
            ))
    
    # INDUSTRIAL-SPECIFIC MECHANICAL
    elif building_type == 'industrial':
        # Base industrial systems
        items.extend([
            ScopeItem(
                name='Compressed Air System - 100 HP',
                quantity=1,
                unit='LS',
                unit_cost=45000,
                total_cost=45000,
                category='Mechanical',
                note='Rotary screw compressor with dryer and receiver'
            ),
            ScopeItem(
                name='Dust Collection System',
                quantity=max(1, int(square_footage / 25000)),
                unit='EA',
                unit_cost=35000,
                total_cost=max(1, int(square_footage / 25000)) * 35000,
                category='Mechanical',
                note='10,000 CFM baghouse system'
            ),
            ScopeItem(
                name='Industrial Exhaust Fans',
                quantity=max(4, int(square_footage / 10000)),
                unit='EA',
                unit_cost=8500,
                total_cost=max(4, int(square_footage / 10000)) * 8500,
                category='Mechanical',
                note='Wall-mounted, 10,000 CFM each'
            ),
            ScopeItem(
                name='Loading Dock Equipment',
                quantity=max(2, int(square_footage / 50000)),
                unit='doors',
                unit_cost=25000,
                total_cost=max(2, int(square_footage / 50000)) * 25000,
                category='Mechanical',
                note='Dock levelers, seals, and bumpers'
            )
        ])
        
        # Process piping
        process_piping_lf = square_footage * 0.3  # 0.3 LF/SF average
        items.append(ScopeItem(
            name='Process Piping - Stainless Steel',
            quantity=process_piping_lf,
            unit='LF',
            unit_cost=85,
            total_cost=process_piping_lf * 85,
            category='Mechanical',
            note='Schedule 10 SS for process utilities'
        ))
        
        # Check for specialized industrial types
        description_lower = description.lower()
        
        # Clean room / Pharmaceutical
        if any(term in description_lower for term in ['clean', 'pharma', 'pharmaceutical', 'biotech']):
            clean_room_sf = square_footage * 0.3  # Assume 30% is clean space
            hepa_units = int(clean_room_sf / 400)  # 1 per 400 SF
            
            items.extend([
                ScopeItem(
                    name='Clean Room AHU - Class 10000',
                    quantity=max(2, int(clean_room_sf / 5000)),
                    unit='EA',
                    unit_cost=125000,
                    total_cost=max(2, int(clean_room_sf / 5000)) * 125000,
                    category='Mechanical',
                    note='100% outside air, HEPA filtration'
                ),
                ScopeItem(
                    name='HEPA Filter Fan Units',
                    quantity=hepa_units,
                    unit='EA',
                    unit_cost=5500,
                    total_cost=hepa_units * 5500,
                    category='Mechanical',
                    note='Ceiling-mounted, 2x4 units'
                ),
                ScopeItem(
                    name='Epoxy Floor Coating',
                    quantity=clean_room_sf,
                    unit='SF',
                    unit_cost=8.50,
                    total_cost=clean_room_sf * 8.50,
                    category='Finishes',
                    note='Seamless, chemical-resistant'
                )
            ])
        
        # Food & Beverage Processing
        elif any(term in description_lower for term in ['food', 'beverage', 'brewery', 'bottling', 'processing']):
            process_area_sf = square_footage * 0.5  # 50% process area
            
            items.extend([
                ScopeItem(
                    name='Washdown Stations',
                    quantity=max(4, int(process_area_sf / 5000)),
                    unit='EA',
                    unit_cost=3500,
                    total_cost=max(4, int(process_area_sf / 5000)) * 3500,
                    category='Plumbing',
                    note='Stainless steel with hose reels'
                ),
                ScopeItem(
                    name='USDA-Approved Floor Coating',
                    quantity=process_area_sf,
                    unit='SF',
                    unit_cost=6.50,
                    total_cost=process_area_sf * 6.50,
                    category='Finishes',
                    note='Slip-resistant, antimicrobial'
                ),
                ScopeItem(
                    name='Insulated Metal Panels',
                    quantity=process_area_sf * 0.2,  # For coolers/freezers
                    unit='SF',
                    unit_cost=18,
                    total_cost=process_area_sf * 0.2 * 18,
                    category='Structural',
                    note='4" panels for cold storage areas'
                ),
                ScopeItem(
                    name='Refrigeration Systems',
                    quantity=max(2, int(process_area_sf / 10000)),
                    unit='systems',
                    unit_cost=65000,
                    total_cost=max(2, int(process_area_sf / 10000)) * 65000,
                    category='Mechanical',
                    note='Walk-in cooler/freezer packages'
                )
            ])
        
        # Data Center
        elif 'data center' in description_lower or 'server' in description_lower:
            it_load_kw = square_footage * 0.1  # 100W/SF IT load
            
            items.extend([
                ScopeItem(
                    name='UPS System',
                    quantity=it_load_kw,
                    unit='kW',
                    unit_cost=1200,
                    total_cost=it_load_kw * 1200,
                    category='Electrical',
                    note='N+1 redundancy, 15-minute runtime'
                ),
                ScopeItem(
                    name='Computer Room AC Units (CRAC)',
                    quantity=max(4, int(it_load_kw / 100)),
                    unit='EA',
                    unit_cost=45000,
                    total_cost=max(4, int(it_load_kw / 100)) * 45000,
                    category='Mechanical',
                    note='DX cooling with humidification'
                ),
                ScopeItem(
                    name='Raised Access Floor',
                    quantity=square_footage * 0.8,  # 80% of space
                    unit='SF',
                    unit_cost=15,
                    total_cost=square_footage * 0.8 * 15,
                    category='Finishes',
                    note='24" height for airflow and cabling'
                ),
                ScopeItem(
                    name='Fire Suppression - FM200',
                    quantity=square_footage * 0.8,
                    unit='SF',
                    unit_cost=12,
                    total_cost=square_footage * 0.8 * 12,
                    category='Mechanical',
                    note='Clean agent system for IT spaces'
                )
            ])
        
        # Add crane if mentioned or large facility
        if 'crane' in description_lower or square_footage > 50000:
            crane_length = square_footage / (floors or 1) / 100  # Approximate bay length
            items.append(ScopeItem(
                name='Bridge Crane System - 10 Ton',
                quantity=crane_length,
                unit='LF',
                unit_cost=450,
                total_cost=crane_length * 450,
                category='Mechanical',
                note='Including runway beams and controls'
            ))
    
    # HOSPITALITY-SPECIFIC MECHANICAL
    elif building_type == 'hospitality':
        # Extract room count from description
        room_count = extract_number_before_keyword(description, ['room', 'rooms', 'guest room', 'guest rooms'])
        
        # If no room count found, estimate based on square footage (450 SF per room average)
        if not room_count:
            room_count = max(50, int(square_footage / 450))
        
        # Individual room HVAC
        items.append(ScopeItem(
            name='PTAC Units - Guest Room HVAC',
            quantity=room_count,
            unit='EA',
            unit_cost=1200,
            total_cost=room_count * 1200,
            category='Mechanical',
            note='Packaged terminal air conditioner per room'
        ))
        
        # Common area HVAC
        common_area_sf = square_footage * 0.25  # 25% common areas
        common_hvac_tons = common_area_sf / 400
        items.append(ScopeItem(
            name='Common Area HVAC System',
            quantity=common_hvac_tons,
            unit='tons',
            unit_cost=2000,
            total_cost=common_hvac_tons * 2000,
            category='Mechanical',
            note='Lobby, corridors, conference, restaurant'
        ))
        
        # Commercial kitchen exhaust
        kitchen_sf = square_footage * 0.05  # 5% for kitchen
        items.extend([
            ScopeItem(
                name='Kitchen Hood System - Type I',
                quantity=max(2, int(kitchen_sf / 300)),
                unit='EA',
                unit_cost=18000,
                total_cost=max(2, int(kitchen_sf / 300)) * 18000,
                category='Mechanical',
                note='Commercial kitchen with fire suppression'
            ),
            ScopeItem(
                name='Kitchen Make-up Air Unit',
                quantity=1,
                unit='LS',
                unit_cost=25000,
                total_cost=25000,
                category='Mechanical',
                note='Tempered make-up air for kitchen exhaust'
            )
        ])
        
        # Laundry facility
        items.extend([
            ScopeItem(
                name='Commercial Laundry Equipment',
                quantity=max(4, int(room_count / 50)),
                unit='sets',
                unit_cost=20000,
                total_cost=max(4, int(room_count / 50)) * 20000,
                category='Mechanical',
                note='Washer/dryer sets for guest laundry'
            ),
            ScopeItem(
                name='Laundry Exhaust System',
                quantity=max(2, int(room_count / 100)),
                unit='EA',
                unit_cost=4500,
                total_cost=max(2, int(room_count / 100)) * 4500,
                category='Mechanical',
                note='Dryer exhaust and ventilation'
            )
        ])
        
        # Pool/spa equipment if mentioned
        if any(term in description.lower() for term in ['pool', 'spa', 'swimming']):
            items.extend([
                ScopeItem(
                    name='Pool HVAC Dehumidification',
                    quantity=1,
                    unit='system',
                    unit_cost=65000,
                    total_cost=65000,
                    category='Mechanical',
                    note='Natatorium dehumidification system'
                ),
                ScopeItem(
                    name='Pool Equipment Package',
                    quantity=1,
                    unit='LS',
                    unit_cost=45000,
                    total_cost=45000,
                    category='Mechanical',
                    note='Pumps, filters, heaters, chemical systems'
                )
            ])
        
        # Bathroom exhaust fans
        items.append(ScopeItem(
            name='Guest Room Bathroom Exhaust',
            quantity=room_count,
            unit='EA',
            unit_cost=450,
            total_cost=room_count * 450,
            category='Mechanical',
            note='Low-noise bathroom ventilation'
        ))
        
        # Elevators for multi-story hotels
        if floors > 2:
            elevators_needed = max(2, int(room_count / 75))  # 1 per 75 rooms
            items.append(ScopeItem(
                name='Passenger Elevator - Hotel Service',
                quantity=elevators_needed,
                unit='EA',
                unit_cost=85000,
                total_cost=elevators_needed * 85000,
                category='Mechanical',
                note=f'Guest elevators, {floors} stops'
            ))
            
            # Service elevator for larger hotels
            if room_count > 100:
                items.append(ScopeItem(
                    name='Service/Freight Elevator',
                    quantity=1,
                    unit='EA',
                    unit_cost=150000,
                    total_cost=150000,
                    category='Mechanical',
                    note=f'For housekeeping and supplies, {floors} stops'
                ))
    
    # RETAIL-SPECIFIC MECHANICAL
    elif building_type == 'retail':
        # Determine retail subtype from description
        description_lower = description.lower()
        
        # Grocery store - heavy refrigeration
        if any(term in description_lower for term in ['grocery', 'supermarket', 'food market']):
            items.extend([
                ScopeItem(
                    name='Refrigeration Rack System',
                    quantity=1,
                    unit='system',
                    unit_cost=125000,
                    total_cost=125000,
                    category='Mechanical',
                    note='Central rack system for all refrigeration'
                ),
                ScopeItem(
                    name='Walk-in Coolers/Freezers',
                    quantity=max(4, int(square_footage / 10000)),
                    unit='EA',
                    unit_cost=35000,
                    total_cost=max(4, int(square_footage / 10000)) * 35000,
                    category='Mechanical',
                    note='Produce, dairy, meat, frozen storage'
                ),
                ScopeItem(
                    name='Refrigerated Display Cases',
                    quantity=max(20, int(square_footage / 500)),
                    unit='sections',
                    unit_cost=8500,
                    total_cost=max(20, int(square_footage / 500)) * 8500,
                    category='Mechanical',
                    note='Open and closed refrigerated displays'
                ),
                ScopeItem(
                    name='Specialty HVAC for Refrigeration',
                    quantity=square_footage / 300,  # More cooling needed
                    unit='tons',
                    unit_cost=2200,
                    total_cost=(square_footage / 300) * 2200,
                    category='Mechanical',
                    note='Additional cooling for refrigeration heat'
                )
            ])
        
        # Shopping mall - complex systems
        elif 'mall' in description_lower and 'strip' not in description_lower:
            items.extend([
                ScopeItem(
                    name='Central Plant Equipment',
                    quantity=square_footage / 250,
                    unit='tons',
                    unit_cost=2500,
                    total_cost=(square_footage / 250) * 2500,
                    category='Mechanical',
                    note='Mall central cooling/heating plant'
                ),
                ScopeItem(
                    name='Mall Common Area HVAC',
                    quantity=square_footage * 0.2 / 400,  # 20% common area
                    unit='tons',
                    unit_cost=2000,
                    total_cost=(square_footage * 0.2 / 400) * 2000,
                    category='Mechanical',
                    note='Corridors, courts, restrooms'
                ),
                ScopeItem(
                    name='Smoke Evacuation System',
                    quantity=max(4, int(square_footage / 50000)),
                    unit='zones',
                    unit_cost=35000,
                    total_cost=max(4, int(square_footage / 50000)) * 35000,
                    category='Mechanical',
                    note='Code-required smoke control'
                )
            ])
            
            # Escalators for multi-level malls
            if floors > 1:
                escalator_count = max(2, (floors - 1) * 2)  # Up and down per floor
                items.append(ScopeItem(
                    name='Escalators',
                    quantity=escalator_count,
                    unit='EA',
                    unit_cost=250000,
                    total_cost=escalator_count * 250000,
                    category='Mechanical',
                    note='Heavy-duty commercial escalators'
                ))
        
        # Big box retail - warehouse-like
        elif any(term in description_lower for term in ['big box', 'anchor', 'department store']):
            items.extend([
                ScopeItem(
                    name='Rooftop Units - High Capacity',
                    quantity=max(4, int(square_footage / 12500)),
                    unit='EA',
                    unit_cost=45000,
                    total_cost=max(4, int(square_footage / 12500)) * 45000,
                    category='Mechanical',
                    note='Large RTUs for open retail space'
                ),
                ScopeItem(
                    name='Loading Dock Equipment',
                    quantity=max(2, int(square_footage / 25000)),
                    unit='docks',
                    unit_cost=12000,
                    total_cost=max(2, int(square_footage / 25000)) * 12000,
                    category='Mechanical',
                    note='Dock levelers and seals'
                ),
                ScopeItem(
                    name='Warehouse-style Exhaust Fans',
                    quantity=max(4, int(square_footage / 15000)),
                    unit='EA',
                    unit_cost=6500,
                    total_cost=max(4, int(square_footage / 15000)) * 6500,
                    category='Mechanical',
                    note='Large diameter exhaust fans'
                )
            ])
        
        # Strip center - individual tenant systems
        elif any(term in description_lower for term in ['strip', 'neighborhood center', 'inline']):
            tenant_count = max(4, int(square_footage / 2500))  # Avg 2500 SF per tenant
            
            items.extend([
                ScopeItem(
                    name='Tenant HVAC Units',
                    quantity=tenant_count,
                    unit='units',
                    unit_cost=12000,
                    total_cost=tenant_count * 12000,
                    category='Mechanical',
                    note='Individual RTUs per tenant space'
                ),
                ScopeItem(
                    name='Tenant Exhaust Systems',
                    quantity=tenant_count,
                    unit='EA',
                    unit_cost=3500,
                    total_cost=tenant_count * 3500,
                    category='Mechanical',
                    note='Restroom and general exhaust'
                ),
                ScopeItem(
                    name='Gas Service to Tenants',
                    quantity=tenant_count * 0.3,  # 30% need gas
                    unit='meters',
                    unit_cost=2500,
                    total_cost=tenant_count * 0.3 * 2500,
                    category='Mechanical',
                    note='For restaurant tenants'
                )
            ])
        
        # General retail HVAC
        else:
            items.append(ScopeItem(
                name='Retail HVAC System',
                quantity=square_footage / 350,
                unit='tons',
                unit_cost=1800,
                total_cost=(square_footage / 350) * 1800,
                category='Mechanical',
                note='Standard retail cooling/heating'
            ))
        
        # Common retail mechanical items
        items.extend([
            ScopeItem(
                name='Make-up Air Units',
                quantity=max(1, int(square_footage / 20000)),
                unit='EA',
                unit_cost=18000,
                total_cost=max(1, int(square_footage / 20000)) * 18000,
                category='Mechanical',
                note='Code-required ventilation air'
            ),
            ScopeItem(
                name='Energy Management System',
                quantity=1,
                unit='LS',
                unit_cost=25000 + square_footage * 0.5,
                total_cost=25000 + square_footage * 0.5,
                category='Mechanical',
                note='BMS for HVAC control and monitoring'
            )
        ])
        
        # Elevators for multi-story retail
        if floors > 1:
            if 'mall' in description_lower:
                # Malls need more elevators
                elevator_count = max(2, int(square_footage / 40000))
                items.append(ScopeItem(
                    name='Passenger Elevators - Glass Cab',
                    quantity=elevator_count,
                    unit='EA',
                    unit_cost=125000,
                    total_cost=elevator_count * 125000,
                    category='Mechanical',
                    note=f'Scenic elevators, {floors} stops'
                ))
            else:
                # Standard retail elevators
                elevator_count = max(1, int(square_footage / 50000))
                items.append(ScopeItem(
                    name='Passenger Elevator',
                    quantity=elevator_count,
                    unit='EA',
                    unit_cost=75000,
                    total_cost=elevator_count * 75000,
                    category='Mechanical',
                    note=f'Standard commercial, {floors} stops'
                ))
            
            # Service elevator for larger retail
            if square_footage > 50000:
                items.append(ScopeItem(
                    name='Freight Elevator',
                    quantity=1,
                    unit='EA',
                    unit_cost=150000,
                    total_cost=150000,
                    category='Mechanical',
                    note=f'For merchandise movement, {floors} stops'
                ))
    
    return items


def calculate_trade_cost(trade: str, building_type: str, square_footage: float, region: str, floors: int = 1, location: str = "") -> Tuple[float, List[ScopeItem]]:
    """
    Calculate trade cost with proper hierarchy:
    1. Base material cost from specifications
    2. Building type complexity adjustment
    3. Regional multiplier
    
    Returns: (total_cost, list_of_scope_items)
    """
    
    # Get building type specifications
    if building_type not in BUILDING_TYPE_SPECIFICATIONS:
        building_type = "commercial"  # default
    
    specs = BUILDING_TYPE_SPECIFICATIONS[building_type].get(trade, {})
    
    # Step 1: Calculate base material quantities
    quantities = calculate_quantities(specs, square_footage)
    
    # Step 2: Apply base unit costs
    base_cost = 0
    scope_items = []
    
    if trade == "structural":
        if "steel_frame_lbs" in quantities:
            cost = quantities["steel_frame_lbs"] * BASE_UNIT_COSTS["steel_frame_per_lb"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name=f"Structural Steel Frame ({specs['steel_frame_weight']} lbs/SF)",
                quantity=quantities["steel_frame_lbs"],
                unit="lbs",
                unit_cost=BASE_UNIT_COSTS["steel_frame_per_lb"],
                total_cost=cost,
                category="Structural"
            ))
        
        if "concrete_cy" in quantities:
            cost = quantities["concrete_cy"] * BASE_UNIT_COSTS["concrete_per_cy"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name=f"Concrete Slab ({specs['concrete_slab_thickness']}\" thick)",
                quantity=quantities["concrete_cy"],
                unit="CY",
                unit_cost=BASE_UNIT_COSTS["concrete_per_cy"],
                total_cost=cost,
                category="Structural"
            ))
        
        if "rebar_tons" in quantities:
            cost = quantities["rebar_tons"] * BASE_UNIT_COSTS["rebar_per_ton"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name="Reinforcing Steel",
                quantity=quantities["rebar_tons"],
                unit="tons",
                unit_cost=BASE_UNIT_COSTS["rebar_per_ton"],
                total_cost=cost,
                category="Structural"
            ))
    
    elif trade == "mechanical":
        if "hvac_tons" in quantities:
            cost = quantities["hvac_tons"] * BASE_UNIT_COSTS["hvac_ton"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name=f"HVAC Equipment ({specs['hvac_tons_per_sf']} SF/ton)",
                quantity=quantities["hvac_tons"],
                unit="tons",
                unit_cost=BASE_UNIT_COSTS["hvac_ton"],
                total_cost=cost,
                category="Mechanical"
            ))
        
        if "vav_boxes" in quantities:
            cost = quantities["vav_boxes"] * BASE_UNIT_COSTS["vav_box"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name="VAV Boxes",
                quantity=quantities["vav_boxes"],
                unit="EA",
                unit_cost=BASE_UNIT_COSTS["vav_box"],
                total_cost=cost,
                category="Mechanical"
            ))
        
        # Add ductwork estimate
        ductwork_lbs = square_footage * 2.5  # 2.5 lbs/SF average
        cost = ductwork_lbs * BASE_UNIT_COSTS["ductwork_per_lb"]
        base_cost += cost
        scope_items.append(ScopeItem(
            name=f"Ductwork ({specs['ductwork_gauge']} gauge)",
            quantity=ductwork_lbs,
            unit="lbs",
            unit_cost=BASE_UNIT_COSTS["ductwork_per_lb"],
            total_cost=cost,
            category="Mechanical"
        ))
        
        # Add exhaust fans for all building types
        if "exhaust_fans" in quantities:
            fan_cost = quantities["exhaust_fans"] * BASE_UNIT_COSTS["exhaust_fan_1000cfm"]
            base_cost += fan_cost
            scope_items.append(ScopeItem(
                name="General Exhaust Fans",
                quantity=quantities["exhaust_fans"],
                unit="EA",
                unit_cost=BASE_UNIT_COSTS["exhaust_fan_1000cfm"],
                total_cost=fan_cost,
                category="Mechanical",
                note="Restroom and general area exhaust"
            ))
        
        # Add controls and thermostats
        control_zones = max(4, square_footage / 2000)
        control_cost = control_zones * 850
        base_cost += control_cost
        scope_items.append(ScopeItem(
            name="HVAC Controls & Thermostats",
            quantity=control_zones,
            unit="zones",
            unit_cost=850,
            total_cost=control_cost,
            category="Mechanical",
            note="Programmable thermostats with zone control"
        ))
        
        # Add hydronic piping if specified
        if building_type in ["healthcare", "educational", "office"] and square_footage > 20000:
            hydronic_lf = square_footage * 0.3  # 0.3 LF/SF for hot/chilled water
            hydronic_cost = hydronic_lf * 55
            base_cost += hydronic_cost
            scope_items.append(ScopeItem(
                name="Hydronic Piping System",
                quantity=hydronic_lf,
                unit="LF",
                unit_cost=55,
                total_cost=hydronic_cost,
                category="Mechanical",
                note="Chilled/hot water distribution piping"
            ))
        
        # Add elevator mechanical components if needed
        if needs_elevator(floors, building_type, square_footage):
            elevator_dict = calculate_elevator_count(floors, building_type, square_footage)
            
            for elevator_type, count in elevator_dict.items():
                if elevator_type == "passenger_elevators":
                    # Elevator machine room ventilation
                    vent_cost = count * 3500  # Per elevator machine room
                    base_cost += vent_cost
                    scope_items.append(ScopeItem(
                        name=f"Elevator Machine Room Ventilation ({count} elevators)",
                        quantity=count,
                        unit="EA",
                        unit_cost=3500,
                        total_cost=vent_cost,
                        category="Mechanical",
                        note="Dedicated exhaust and supply for machine rooms"
                    ))
                    
                    # Shaft ventilation
                    shaft_vent_cost = count * 2500 * floors
                    base_cost += shaft_vent_cost
                    scope_items.append(ScopeItem(
                        name=f"Elevator Shaft Ventilation ({count} shafts)",
                        quantity=count * floors,
                        unit="FLOOR",
                        unit_cost=2500,
                        total_cost=shaft_vent_cost,
                        category="Mechanical",
                        note="Code-required shaft ventilation"
                    ))
    
    elif trade == "electrical":
        if "panel_amps" in quantities:
            cost = quantities["panel_amps"] * BASE_UNIT_COSTS["panel_per_amp"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name=f"Main Distribution Panel ({specs['panel_amps']}A)",
                quantity=1,
                unit="EA",
                unit_cost=cost,
                total_cost=cost,
                category="Electrical"
            ))
        
        if "outlets" in quantities:
            cost = quantities["outlets"] * BASE_UNIT_COSTS["outlet"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name="Electrical Outlets",
                quantity=quantities["outlets"],
                unit="EA",
                unit_cost=BASE_UNIT_COSTS["outlet"],
                total_cost=cost,
                category="Electrical"
            ))
        
        # Add data drops for educational buildings
        if "data_drops" in quantities:
            cost = quantities["data_drops"] * BASE_UNIT_COSTS["data_drop"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name="Data/Communication Drops",
                quantity=quantities["data_drops"],
                unit="EA",
                unit_cost=BASE_UNIT_COSTS["data_drop"],
                total_cost=cost,
                category="Electrical",
                note="Cat6 cabling for classrooms"
            ))
        
        # Lighting based on foot-candles requirement
        lighting_cost = square_footage * BASE_UNIT_COSTS["lighting_per_sf"]
        base_cost += lighting_cost
        scope_items.append(ScopeItem(
            name=f"Lighting System ({specs.get('lighting_fc', 30)} FC)",
            quantity=square_footage,
            unit="SF",
            unit_cost=BASE_UNIT_COSTS["lighting_per_sf"],
            total_cost=lighting_cost,
            category="Electrical"
        ))
        
        # Add industrial-specific electrical items
        if building_type == "industrial":
            # Motor Control Centers
            if specs.get("motor_control_centers"):
                mcc_count = max(1, int(square_footage / 50000))
                mcc_cost = mcc_count * BASE_UNIT_COSTS["motor_control_center"]
                base_cost += mcc_cost
                scope_items.append(ScopeItem(
                    name="Motor Control Center - 480V",
                    quantity=mcc_count,
                    unit="EA",
                    unit_cost=BASE_UNIT_COSTS["motor_control_center"],
                    total_cost=mcc_cost,
                    category="Electrical",
                    note="VFDs, starters, and controls"
                ))
            
            # Industrial power distribution
            transformer_kva = square_footage * specs.get("watts_per_sf", 15) / 1000 * 1.25  # 25% safety factor
            transformer_count = max(1, int(transformer_kva / 1500))  # 1500 kVA units
            transformer_cost = transformer_count * 85000
            base_cost += transformer_cost
            scope_items.append(ScopeItem(
                name="Transformer - 1500 kVA",
                quantity=transformer_count,
                unit="EA",
                unit_cost=85000,
                total_cost=transformer_cost,
                category="Electrical",
                note="13.8kV to 480V step-down"
            ))
            
            # High bay lighting
            if specs.get("high_bay_lighting"):
                highbay_fixtures = int(square_footage / 200)  # 1 per 200 SF
                highbay_cost = highbay_fixtures * 850
                base_cost += highbay_cost
                scope_items.append(ScopeItem(
                    name="LED High Bay Fixtures",
                    quantity=highbay_fixtures,
                    unit="EA",
                    unit_cost=850,
                    total_cost=highbay_cost,
                    category="Electrical",
                    note="400W LED, 50,000 lumens"
                ))
        
        # Add elevator electrical components if needed
        if needs_elevator(floors, building_type, square_footage):
            elevator_dict = calculate_elevator_count(floors, building_type, square_footage)
            
            total_elevators = sum(elevator_dict.values())
            
            # Elevator power feeds
            power_cost = total_elevators * 8500  # 3-phase power per elevator
            base_cost += power_cost
            scope_items.append(ScopeItem(
                name=f"Elevator Power Feeds ({total_elevators} elevators)",
                quantity=total_elevators,
                unit="EA",
                unit_cost=8500,
                total_cost=power_cost,
                category="Electrical",
                note="3-phase 480V power with disconnect"
            ))
            
            # Elevator controls and lighting
            controls_cost = total_elevators * 4500  # Controls, cab lighting, emergency power
            base_cost += controls_cost
            scope_items.append(ScopeItem(
                name="Elevator Controls & Emergency Power",
                quantity=total_elevators,
                unit="EA",
                unit_cost=4500,
                total_cost=controls_cost,
                category="Electrical",
                note="Cab controls, lighting, emergency lowering"
            ))
            
            # Fire alarm integration
            fire_alarm_cost = total_elevators * 2500
            base_cost += fire_alarm_cost
            scope_items.append(ScopeItem(
                name="Elevator Fire Alarm Integration",
                quantity=total_elevators,
                unit="EA",
                unit_cost=2500,
                total_cost=fire_alarm_cost,
                category="Electrical",
                note="Recall, firefighter operation, shaft detectors"
            ))
    
    elif trade == "plumbing":
        if "fixture_units" in quantities:
            cost = quantities["fixture_units"] * BASE_UNIT_COSTS["fixture_unit"]
            base_cost += cost
            scope_items.append(ScopeItem(
                name="Plumbing Fixtures",
                quantity=quantities["fixture_units"],
                unit="FU",
                unit_cost=BASE_UNIT_COSTS["fixture_unit"],
                total_cost=cost,
                category="Plumbing"
            ))
        
        # Piping estimate
        pipe_size = str(specs.get("pipe_size_main", 2))
        pipe_lf = square_footage * 0.5  # 0.5 LF per SF average
        pipe_cost = pipe_lf * BASE_UNIT_COSTS["pipe_per_lf"].get(pipe_size, 45)
        base_cost += pipe_cost
        scope_items.append(ScopeItem(
            name=f"Water Piping ({pipe_size}\" main)",
            quantity=pipe_lf,
            unit="LF",
            unit_cost=BASE_UNIT_COSTS["pipe_per_lf"].get(pipe_size, 45),
            total_cost=pipe_cost,
            category="Plumbing"
        ))
    
    # Step 3: Apply building complexity factor
    complexity_factor = BUILDING_COMPLEXITY_FACTORS.get(building_type, {}).get(trade, 1.0)
    adjusted_cost = base_cost * complexity_factor
    
    # Step 4: Apply regional multiplier
    regional_multiplier = REGIONAL_MULTIPLIERS.get(region, {}).get(trade, 1.0)
    final_cost = adjusted_cost * regional_multiplier
    
    # Update scope items with adjusted costs
    for item in scope_items:
        item.total_cost = item.total_cost * complexity_factor * regional_multiplier
        if item.quantity > 0:
            item.unit_cost = item.total_cost / item.quantity
    
    # Apply confidence scores to all items
    scope_items = ConfidenceCalculator.apply_confidence_to_items(
        scope_items=scope_items,
        building_type=building_type,
        square_footage=square_footage,
        region=region,
        location=location
    )
    
    return final_cost, scope_items


def add_building_specific_items(building_type: str, scope_items: List[ScopeItem], square_footage: float, floors: int = 1, description: str = "") -> List[ScopeItem]:
    """Add building-type specific scope items"""
    
    additional_items = []
    
    # Note: Elevators are now handled in the mechanical section through add_building_specific_mechanical_items
    
    if building_type == "educational":
        additional_items.extend([
            ScopeItem(
                name="Enhanced Fire Alarm System",
                quantity=1,
                unit="system",
                unit_cost=square_footage * 2.5,
                total_cost=square_footage * 2.5,
                note="Classroom notification systems",
                category="Electrical"
            ),
            ScopeItem(
                name="Security System",
                quantity=square_footage/500,
                unit="cameras",
                unit_cost=1200,
                total_cost=(square_footage/500) * 1200,
                note="1 camera per 500 SF coverage",
                category="Electrical"
            ),
            ScopeItem(
                name="Drinking Fountains",
                quantity=max(4, square_footage/5000),
                unit="EA",
                unit_cost=2500,
                total_cost=max(4, square_footage/5000) * 2500,
                note="ADA compliant dual-height fountains",
                category="Plumbing"
            ),
        ])
    
    elif building_type == "warehouse":
        additional_items.extend([
            ScopeItem(
                name="Loading Dock Equipment",
                quantity=max(1, square_footage/5000),
                unit="doors",
                unit_cost=8500,
                total_cost=max(1, square_footage/5000) * 8500,
                note="1 dock door per 5000 SF",
                category="Structural"
            ),
            ScopeItem(
                name="High Bay LED Lighting",
                quantity=square_footage/150,
                unit="fixtures",
                unit_cost=450,
                total_cost=(square_footage/150) * 450,
                note="30W LED high bay fixtures",
                category="Electrical"
            ),
            ScopeItem(
                name="Unit Heaters",
                quantity=square_footage/2500,
                unit="EA",
                unit_cost=2800,
                total_cost=(square_footage/2500) * 2800,
                note="Gas-fired unit heaters",
                category="Mechanical"
            ),
        ])
    
    elif building_type == "healthcare":
        additional_items.extend([
            ScopeItem(
                name="Medical Gas System",
                quantity=square_footage/100,
                unit="outlets",
                unit_cost=850,
                total_cost=(square_footage/100) * 850,
                note="O2, vacuum, medical air outlets",
                category="Plumbing"
            ),
            ScopeItem(
                name="Emergency Power System",
                quantity=square_footage * 0.004,
                unit="kW",
                unit_cost=1500,
                total_cost=(square_footage * 0.004) * 1500,
                note="Life safety and critical branch",
                category="Electrical"
            ),
            ScopeItem(
                name="Isolation Room Exhaust",
                quantity=square_footage/2000,
                unit="rooms",
                unit_cost=12000,
                total_cost=(square_footage/2000) * 12000,
                note="Negative pressure rooms",
                category="Mechanical"
            ),
        ])
    
    elif building_type == "restaurant":
        additional_items.extend([
            ScopeItem(
                name="Kitchen Hood System",
                quantity=square_footage * 0.3 / 50,  # 1 per 50 SF of kitchen
                unit="LF",
                unit_cost=850,
                total_cost=(square_footage * 0.3 / 50) * 850,
                note="Type I grease hood with fire suppression",
                category="Mechanical"
            ),
            ScopeItem(
                name="Grease Interceptor",
                quantity=1,
                unit="EA",
                unit_cost=15000,
                total_cost=15000,
                note="1000 gallon exterior interceptor",
                category="Plumbing"
            ),
            ScopeItem(
                name="Walk-in Cooler/Freezer",
                quantity=2,
                unit="EA",
                unit_cost=12000,
                total_cost=24000,
                note="Pre-fab insulated boxes",
                category="Mechanical"
            ),
            ScopeItem(
                name="Gas Piping for Kitchen",
                quantity=square_footage * 0.3,
                unit="SF",
                unit_cost=12,
                total_cost=(square_footage * 0.3) * 12,
                note="Kitchen equipment gas supply",
                category="Plumbing"
            ),
        ])
    
    elif building_type == "office":
        additional_items.extend([
            ScopeItem(
                name="Data/Communication Infrastructure",
                quantity=square_footage/100,
                unit="drops",
                unit_cost=250,
                total_cost=(square_footage/100) * 250,
                note="Cat6 cabling to workstations",
                category="Electrical"
            ),
            ScopeItem(
                name="Conference Room AV",
                quantity=square_footage/2000,
                unit="rooms",
                unit_cost=8500,
                total_cost=(square_footage/2000) * 8500,
                note="Display, audio, video conferencing",
                category="Electrical"
            ),
        ])
    
    elif building_type == "hospitality":
        # Extract room count from description
        room_count_match = re.search(r'(\d+)\s*(?:room|rooms|guest room|guest rooms)', description.lower()) if description else None
        room_count = int(room_count_match.group(1)) if room_count_match else max(50, int(square_footage / 450))
        
        additional_items.extend([
            ScopeItem(
                name="Card Key Access System",
                quantity=room_count,
                unit="doors",
                unit_cost=350,
                total_cost=room_count * 350,
                note="Electronic door locks with card readers",
                category="Electrical"
            ),
            ScopeItem(
                name="Guest Room Bathroom Packages",
                quantity=room_count,
                unit="EA",
                unit_cost=4500,
                total_cost=room_count * 4500,
                note="Complete bathroom fixture sets",
                category="Plumbing"
            ),
            ScopeItem(
                name="Hot Water Recirculation System",
                quantity=1,
                unit="system",
                unit_cost=25000,
                total_cost=25000,
                note="Continuous hot water for guest comfort",
                category="Plumbing"
            ),
            ScopeItem(
                name="Emergency Lighting & Exit Signs",
                quantity=square_footage/1000,
                unit="EA",
                unit_cost=450,
                total_cost=(square_footage/1000) * 450,
                note="Code-required emergency egress lighting",
                category="Electrical"
            ),
            ScopeItem(
                name="FF&E Package",
                quantity=room_count,
                unit="rooms",
                unit_cost=12000,
                total_cost=room_count * 12000,
                note="Furniture, fixtures & equipment per room",
                category="Finishes"
            ),
            ScopeItem(
                name="Guest Room Electrical Package",
                quantity=room_count,
                unit="rooms",
                unit_cost=2500,
                total_cost=room_count * 2500,
                note="Outlets, USB charging, lighting controls",
                category="Electrical"
            ),
            ScopeItem(
                name="Fire Alarm System - Hospitality",
                quantity=1,
                unit="system",
                unit_cost=square_footage * 3.5,
                total_cost=square_footage * 3.5,
                note="Voice evacuation and room notification",
                category="Electrical"
            ),
            ScopeItem(
                name="Telecommunications Infrastructure",
                quantity=room_count,
                unit="rooms",
                unit_cost=850,
                total_cost=room_count * 850,
                note="WiFi, phone, cable TV per room",
                category="Electrical"
            )
        ])
    
    elif building_type == "retail":
        # Extract retail subtype from description
        description_lower = description.lower() if description else ""
        
        # Common retail items
        additional_items.extend([
            ScopeItem(
                name="Storefront System",
                quantity=square_footage / 100,  # Perimeter footage estimate
                unit="LF",
                unit_cost=450,
                total_cost=(square_footage / 100) * 450,
                note="Aluminum and glass storefront",
                category="Structural"
            ),
            ScopeItem(
                name="Automatic Entry Doors",
                quantity=max(1, int(square_footage / 15000)),
                unit="pairs",
                unit_cost=8500,
                total_cost=max(1, int(square_footage / 15000)) * 8500,
                note="Sensor-activated sliding doors",
                category="Structural"
            ),
            ScopeItem(
                name="Retail Security System",
                quantity=1,
                unit="system",
                unit_cost=15000 + square_footage * 0.25,
                total_cost=15000 + square_footage * 0.25,
                note="EAS tags, cameras, monitoring",
                category="Electrical"
            ),
            ScopeItem(
                name="Display Lighting",
                quantity=square_footage,
                unit="SF",
                unit_cost=8.50,
                total_cost=square_footage * 8.50,
                note="Track lighting and accent fixtures",
                category="Electrical"
            ),
            ScopeItem(
                name="Signage Power & Lighting",
                quantity=square_footage / 5000,
                unit="signs",
                unit_cost=3500,
                total_cost=(square_footage / 5000) * 3500,
                note="Exterior and interior signage",
                category="Electrical"
            ),
            ScopeItem(
                name="Point of Sale Systems",
                quantity=max(2, int(square_footage / 5000)),
                unit="terminals",
                unit_cost=5500,
                total_cost=max(2, int(square_footage / 5000)) * 5500,
                note="POS terminals with networking",
                category="Electrical"
            )
        ])
        
        # Grocery store specific
        if any(term in description_lower for term in ['grocery', 'supermarket']):
            additional_items.extend([
                ScopeItem(
                    name="Specialty Flooring - Grocery",
                    quantity=square_footage,
                    unit="SF",
                    unit_cost=12.50,
                    total_cost=square_footage * 12.50,
                    note="Sealed concrete, epoxy in prep areas",
                    category="Finishes"
                ),
                ScopeItem(
                    name="Deli/Bakery Equipment Package",
                    quantity=1,
                    unit="LS",
                    unit_cost=125000,
                    total_cost=125000,
                    note="Ovens, slicers, prep equipment",
                    category="Mechanical"
                ),
                ScopeItem(
                    name="Checkout Lane Equipment",
                    quantity=max(8, int(square_footage / 3000)),
                    unit="lanes",
                    unit_cost=25000,
                    total_cost=max(8, int(square_footage / 3000)) * 25000,
                    note="Conveyor, scanner, bagging area",
                    category="Finishes"
                )
            ])
        
        # Strip center specific
        elif any(term in description_lower for term in ['strip', 'neighborhood center']):
            tenant_count = max(4, int(square_footage / 2500))
            additional_items.extend([
                ScopeItem(
                    name="Demising Walls",
                    quantity=tenant_count * 50,  # 50 LF per tenant avg
                    unit="LF",
                    unit_cost=85,
                    total_cost=tenant_count * 50 * 85,
                    note="Fire-rated tenant separation walls",
                    category="Structural"
                ),
                ScopeItem(
                    name="Tenant Electrical Panels",
                    quantity=tenant_count,
                    unit="EA",
                    unit_cost=8500,
                    total_cost=tenant_count * 8500,
                    note="Individual metering per tenant",
                    category="Electrical"
                ),
                ScopeItem(
                    name="Tenant Improvement Allowance",
                    quantity=square_footage,
                    unit="SF",
                    unit_cost=35,
                    total_cost=square_footage * 35,
                    note="TI allowance for tenant buildout",
                    category="Finishes"
                )
            ])
        
        # Mall specific
        elif 'mall' in description_lower and 'strip' not in description_lower:
            additional_items.extend([
                ScopeItem(
                    name="Mall Common Area Finishes",
                    quantity=square_footage * 0.2,  # 20% common area
                    unit="SF",
                    unit_cost=85,
                    total_cost=square_footage * 0.2 * 85,
                    note="High-end flooring, ceilings, lighting",
                    category="Finishes"
                ),
                ScopeItem(
                    name="Mall Directories & Wayfinding",
                    quantity=max(4, int(square_footage / 50000)),
                    unit="EA",
                    unit_cost=15000,
                    total_cost=max(4, int(square_footage / 50000)) * 15000,
                    note="Digital directories and signage",
                    category="Finishes"
                ),
                ScopeItem(
                    name="Food Court Infrastructure",
                    quantity=1,
                    unit="LS",
                    unit_cost=250000,
                    total_cost=250000,
                    note="Grease traps, exhaust, utilities",
                    category="Mechanical"
                )
            ])
        
        # Big box specific
        elif any(term in description_lower for term in ['big box', 'anchor']):
            additional_items.extend([
                ScopeItem(
                    name="High Bay Racking Systems",
                    quantity=square_footage * 0.7,  # 70% of space
                    unit="SF",
                    unit_cost=18,
                    total_cost=square_footage * 0.7 * 18,
                    note="Steel storage racking",
                    category="Finishes"
                ),
                ScopeItem(
                    name="Loading Dock Doors",
                    quantity=max(3, int(square_footage / 20000)),
                    unit="EA",
                    unit_cost=8500,
                    total_cost=max(3, int(square_footage / 20000)) * 8500,
                    note="Overhead sectional doors",
                    category="Structural"
                )
            ])
    
    return additional_items