"""
Market-specific healthcare construction costs
Based on RSMeans 2024 Q3 data + regional healthcare construction indices
Includes Tennessee Certificate of Need and NH licensing requirements
"""

from typing import Dict, Any

HEALTHCARE_MARKET_COSTS = {
    'nashville_tn': {
        'region_name': 'Nashville Metro',
        'regional_multiplier': 1.02,
        'labor_adjustment': 1.03,
        'material_adjustment': 0.98,
        
        # Certificate of Need requirements affect costs
        'certificate_of_need': True,
        'con_threshold': 2000000,  # Projects over $2M need CON
        'con_cost_impact': 1.05,   # 5% increase for CON compliance
        
        # Facility type base CONSTRUCTION costs (equipment added separately)
        'facility_costs_per_sf': {
            'general_hospital': 850,  # Construction only (+$150-300 equipment)
            'pediatric_hospital': 875,  # Construction only
            'psychiatric_hospital': 650,  # Construction only
            'rehabilitation_hospital': 700,  # Construction only
            'critical_access_hospital': 750,  # Construction only
            'ambulatory_surgery_center': 550,  # Construction only (+$200-300 equipment)
            'imaging_center': 500,  # Construction only (+$150-250 equipment)
            'cancer_center': 800,  # Construction only (+$200-400 equipment)
            'dialysis_center': 450,  # Construction only (+$100-150 equipment)
            'birthing_center': 650,  # Construction only
            'urgent_care': 350,  # Construction only
            'community_health_center': 320,  # Construction only
            'medical_office': 320,  # Construction only (+$10-30 equipment)
            'dental_clinic': 300,  # Construction only (+$50-100 equipment)
            'eye_clinic': 325,  # Construction only
            'skilled_nursing_facility': 275,  # Construction only
            'assisted_living': 250  # Construction only
        },
        
        # Special space premiums (added to base)
        'special_space_costs': {
            'operating_room': 1200,  # per SF for OR space
            'emergency_dept': 550,
            'icu': 750,
            'clean_room': 850,
            'isolation_room': 650,
            'mri_suite': 900,
            'ct_suite': 700,
            'xray_suite': 500,
            'cath_lab': 950,
            'linear_accelerator': 1500,
            'pharmacy_usp_797': 450,
            'laboratory_clia': 400,
            'morgue': 350,
            'kitchen_commercial': 300,
            'data_center': 800,
            'helicopter_pad': 2000
        },
        
        # Trade cost percentages for healthcare
        'trade_percentages': {
            'site_work': 0.08,
            'structural': 0.14,
            'mechanical': 0.32,  # Higher for healthcare
            'electrical': 0.20,  # Higher for healthcare
            'plumbing': 0.12,   # Medical gas included
            'finishes': 0.08,    # Lower - more MEP
            'general_conditions': 0.06
        }
    },
    
    'franklin_tn': {
        'region_name': 'Franklin/Williamson County',
        'regional_multiplier': 1.03,
        'labor_adjustment': 1.04,
        'material_adjustment': 0.98,
        'certificate_of_need': True,
        'con_threshold': 2000000,
        'con_cost_impact': 1.05,
        
        # Costs similar to Nashville with slight premium - CONSTRUCTION ONLY
        'facility_costs_per_sf': {
            'general_hospital': 865,  # Construction only (+$150-300 equipment)
            'pediatric_hospital': 890,  # Construction only
            'psychiatric_hospital': 660,  # Construction only
            'rehabilitation_hospital': 710,  # Construction only
            'critical_access_hospital': 760,  # Construction only
            'ambulatory_surgery_center': 560,  # Construction only (+$200-300 equipment)
            'imaging_center': 510,  # Construction only (+$150-250 equipment)
            'cancer_center': 815,  # Construction only (+$200-400 equipment)
            'dialysis_center': 460,  # Construction only (+$100-150 equipment)
            'birthing_center': 660,  # Construction only
            'urgent_care': 360,  # Construction only
            'community_health_center': 330,  # Construction only
            'medical_office': 330,  # Construction only (+$10-30 equipment)
            'dental_clinic': 310,  # Construction only (+$50-100 equipment)
            'eye_clinic': 335,  # Construction only
            'skilled_nursing_facility': 285,  # Construction only
            'assisted_living': 240
        },
        
        # Use Nashville's special space costs
        'special_space_costs': 'inherit:nashville_tn',
        'trade_percentages': 'inherit:nashville_tn'
    },
    
    'murfreesboro_tn': {
        'region_name': 'Murfreesboro/Rutherford County',
        'regional_multiplier': 1.01,
        'labor_adjustment': 1.02,
        'material_adjustment': 0.98,
        'certificate_of_need': True,
        'con_threshold': 2000000,
        'con_cost_impact': 1.05,
        
        'facility_costs_per_sf': {
            'general_hospital': 455,
            'pediatric_hospital': 480,
            'psychiatric_hospital': 355,
            'rehabilitation_hospital': 380,
            'critical_access_hospital': 405,
            'ambulatory_surgery_center': 430,
            'imaging_center': 380,
            'cancer_center': 455,
            'dialysis_center': 330,
            'birthing_center': 410,
            'urgent_care': 330,
            'community_health_center': 280,
            'medical_office': 280,
            'dental_clinic': 305,
            'eye_clinic': 330,
            'skilled_nursing_facility': 255,
            'assisted_living': 230
        },
        
        'special_space_costs': 'inherit:nashville_tn',
        'trade_percentages': 'inherit:nashville_tn'
    },
    
    'manchester_nh': {
        'region_name': 'Manchester/Southern NH',
        'regional_multiplier': 0.99,
        'labor_adjustment': 1.05,  # Higher labor costs in NH
        'material_adjustment': 1.02,  # Higher material transport costs
        
        # NH has different regulatory environment
        'certificate_of_need': False,  # NH repealed CON
        'state_licensing_premium': 1.02,  # State licensing adds 2%
        
        'facility_costs_per_sf': {
            'general_hospital': 450,
            'pediatric_hospital': 475,
            'psychiatric_hospital': 350,
            'rehabilitation_hospital': 375,
            'critical_access_hospital': 400,
            'ambulatory_surgery_center': 425,
            'imaging_center': 375,
            'cancer_center': 450,
            'dialysis_center': 325,
            'birthing_center': 400,
            'urgent_care': 325,
            'community_health_center': 275,
            'medical_office': 275,
            'dental_clinic': 300,
            'eye_clinic': 325,
            'skilled_nursing_facility': 250,
            'assisted_living': 225
        },
        
        'special_space_costs': {
            'operating_room': 1150,
            'emergency_dept': 525,
            'icu': 725,
            'clean_room': 825,
            'isolation_room': 625,
            'mri_suite': 875,
            'ct_suite': 675,
            'xray_suite': 475,
            'cath_lab': 925,
            'linear_accelerator': 1450,
            'pharmacy_usp_797': 425,
            'laboratory_clia': 375,
            'morgue': 325,
            'kitchen_commercial': 275,
            'data_center': 775,
            'helicopter_pad': 1950
        },
        
        'trade_percentages': {
            'site_work': 0.09,  # Winter conditions
            'structural': 0.15,  # Snow loads
            'mechanical': 0.31,
            'electrical': 0.19,
            'plumbing': 0.11,
            'finishes': 0.09,
            'general_conditions': 0.06
        }
    },
    
    'nashua_nh': {
        'region_name': 'Nashua/Hillsborough County',
        'regional_multiplier': 0.98,
        'labor_adjustment': 1.04,
        'material_adjustment': 1.02,
        'certificate_of_need': False,
        'state_licensing_premium': 1.02,
        
        'facility_costs_per_sf': {
            'general_hospital': 445,
            'pediatric_hospital': 470,
            'psychiatric_hospital': 345,
            'rehabilitation_hospital': 370,
            'critical_access_hospital': 395,
            'ambulatory_surgery_center': 420,
            'imaging_center': 370,
            'cancer_center': 445,
            'dialysis_center': 320,
            'birthing_center': 395,
            'urgent_care': 320,
            'community_health_center': 270,
            'medical_office': 270,
            'dental_clinic': 295,
            'eye_clinic': 320,
            'skilled_nursing_facility': 245,
            'assisted_living': 220
        },
        
        'special_space_costs': 'inherit:manchester_nh',
        'trade_percentages': 'inherit:manchester_nh'
    },
    
    'concord_nh': {
        'region_name': 'Concord/Capital Region',
        'regional_multiplier': 0.97,
        'labor_adjustment': 1.03,
        'material_adjustment': 1.03,
        'certificate_of_need': False,
        'state_licensing_premium': 1.02,
        
        'facility_costs_per_sf': {
            'general_hospital': 440,
            'pediatric_hospital': 465,
            'psychiatric_hospital': 340,
            'rehabilitation_hospital': 365,
            'critical_access_hospital': 390,
            'ambulatory_surgery_center': 415,
            'imaging_center': 365,
            'cancer_center': 440,
            'dialysis_center': 315,
            'birthing_center': 390,
            'urgent_care': 315,
            'community_health_center': 265,
            'medical_office': 265,
            'dental_clinic': 290,
            'eye_clinic': 315,
            'skilled_nursing_facility': 240,
            'assisted_living': 215
        },
        
        'special_space_costs': 'inherit:manchester_nh',
        'trade_percentages': 'inherit:manchester_nh'
    }
}

# Medical equipment costs (same across markets, adjusted for shipping)
MEDICAL_EQUIPMENT_COSTS = {
    'imaging': {
        'mri_1_5t': {
            'base_cost': 1500000,
            'installation': 250000,
            'shielding': 150000,
            'total_typical': 1900000
        },
        'mri_3t': {
            'base_cost': 2500000,
            'installation': 300000,
            'shielding': 200000,
            'total_typical': 3000000
        },
        'ct_64_slice': {
            'base_cost': 800000,
            'installation': 150000,
            'shielding': 50000,
            'total_typical': 1000000
        },
        'ct_128_slice': {
            'base_cost': 1500000,
            'installation': 200000,
            'shielding': 100000,
            'total_typical': 1800000
        },
        'xray_digital': {
            'base_cost': 200000,
            'installation': 40000,
            'shielding': 10000,
            'total_typical': 250000
        },
        'fluoroscopy': {
            'base_cost': 400000,
            'installation': 75000,
            'shielding': 25000,
            'total_typical': 500000
        },
        'mammography': {
            'base_cost': 300000,
            'installation': 50000,
            'shielding': 25000,
            'total_typical': 375000
        },
        'ultrasound': {
            'base_cost': 150000,
            'installation': 10000,
            'shielding': 0,
            'total_typical': 160000
        }
    },
    
    'surgical': {
        'or_basic_setup': {
            'surgical_lights': 75000,
            'or_table': 100000,
            'anesthesia_machine': 50000,
            'surgical_booms': 125000,
            'integration_system': 150000,
            'monitors': 50000,
            'instruments_basic': 150000,
            'total_typical': 700000
        },
        'or_cardiac': {
            'includes_basic': 700000,
            'c_arm': 500000,
            'perfusion_system': 150000,
            'specialized_instruments': 200000,
            'total_typical': 1550000
        },
        'or_neuro': {
            'includes_basic': 700000,
            'microscope': 400000,
            'navigation_system': 300000,
            'specialized_instruments': 150000,
            'total_typical': 1550000
        },
        'or_orthopedic': {
            'includes_basic': 700000,
            'c_arm': 300000,
            'arthroscopy_tower': 150000,
            'power_tools': 100000,
            'total_typical': 1250000
        }
    },
    
    'emergency': {
        'trauma_bay': {
            'monitors': 50000,
            'crash_cart': 25000,
            'ultrasound': 80000,
            'defibrillator': 30000,
            'ventilator': 25000,
            'total_typical': 210000
        },
        'resuscitation_room': {
            'monitors': 75000,
            'crash_cart': 25000,
            'defibrillator': 30000,
            'ventilator': 35000,
            'infusion_pumps': 20000,
            'total_typical': 185000
        }
    },
    
    'icu': {
        'icu_bed_setup': {
            'bed': 25000,
            'monitors': 50000,
            'ventilator': 35000,
            'infusion_pumps': 15000,
            'total_per_bed': 125000
        }
    },
    
    'laboratory': {
        'clinical_lab_basic': {
            'chemistry_analyzer': 150000,
            'hematology_analyzer': 100000,
            'coagulation_analyzer': 50000,
            'urinalysis': 30000,
            'centrifuges': 20000,
            'refrigeration': 30000,
            'microscopes': 20000,
            'total_typical': 400000
        },
        'pathology_lab': {
            'includes_basic': 400000,
            'histology_equipment': 200000,
            'cryostat': 50000,
            'tissue_processor': 75000,
            'total_typical': 725000
        }
    },
    
    'dental': {
        'operatory_basic': {
            'dental_chair': 25000,
            'delivery_system': 15000,
            'xray_intraoral': 8000,
            'instruments': 5000,
            'total_per_operatory': 53000
        },
        'operatory_surgical': {
            'surgical_chair': 35000,
            'surgical_delivery': 25000,
            'surgical_light': 15000,
            'instruments': 10000,
            'total_per_operatory': 85000
        }
    }
}

def get_market_costs(location: str) -> Dict[str, Any]:
    """
    Get market-specific costs for a location
    """
    location_lower = location.lower()
    
    # Check each market
    for market, data in HEALTHCARE_MARKET_COSTS.items():
        if market.split('_')[0] in location_lower:
            # Handle inheritance
            if isinstance(data.get('special_space_costs'), str) and data['special_space_costs'].startswith('inherit:'):
                parent = data['special_space_costs'].split(':')[1]
                data['special_space_costs'] = HEALTHCARE_MARKET_COSTS[parent]['special_space_costs']
            
            if isinstance(data.get('trade_percentages'), str) and data['trade_percentages'].startswith('inherit:'):
                parent = data['trade_percentages'].split(':')[1]
                data['trade_percentages'] = HEALTHCARE_MARKET_COSTS[parent]['trade_percentages']
            
            return data
    
    # Default to Nashville if not found
    return HEALTHCARE_MARKET_COSTS['nashville_tn']

def calculate_equipment_cost(equipment_list: list, market: str = 'nashville_tn') -> int:
    """
    Calculate total equipment cost with market adjustments
    """
    total = 0
    
    # Market shipping/installation adjustments
    shipping_multipliers = {
        'nashville_tn': 1.0,
        'franklin_tn': 1.0,
        'murfreesboro_tn': 1.0,
        'manchester_nh': 1.05,  # 5% more for NH shipping
        'nashua_nh': 1.05,
        'concord_nh': 1.06
    }
    
    multiplier = shipping_multipliers.get(market, 1.0)
    
    for equipment_type in equipment_list:
        # Find equipment in categories
        for category, items in MEDICAL_EQUIPMENT_COSTS.items():
            if equipment_type in items:
                cost = items[equipment_type].get('total_typical', 0)
                total += int(cost * multiplier)
                break
    
    return total