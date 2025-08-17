"""
Central configuration for all building types, subtypes, and base costs.
Based on real-world construction costs (2024 data).
"""

BUILDING_TYPES_CONFIG = {
    'restaurant': {
        'display_name': 'Restaurant/Food Service',
        'subtypes': {
            'qsr': {
                'name': 'Quick Service (QSR)',
                'base_cost': 275,
                'equipment_cost': 75,
                'typical_floors': 1,
                'keywords': ['qsr', 'quick service', 'fast food', 'drive through', 'drive-through']
            },
            'fast_casual': {
                'name': 'Fast Casual',
                'base_cost': 325,
                'equipment_cost': 75,
                'typical_floors': 1,
                'keywords': ['fast casual', 'counter service', 'chipotle', 'panera']
            },
            'casual_dining': {
                'name': 'Casual Dining',
                'base_cost': 350,
                'equipment_cost': 75,
                'typical_floors': 1,
                'keywords': ['casual dining', 'sit down', 'family restaurant']
            },
            'fine_dining': {
                'name': 'Fine Dining',
                'base_cost': 450,
                'equipment_cost': 100,
                'typical_floors': 1,
                'keywords': ['fine dining', 'upscale', 'high end restaurant', 'steakhouse']
            }
        }
    },
    
    'healthcare': {
        'display_name': 'Healthcare Facilities',
        'subtypes': {
            'hospital': {
                'name': 'Hospital',
                'base_cost': 950,
                'equipment_cost': 200,
                'typical_floors': 5,
                'keywords': ['hospital', 'medical center', 'emergency', 'trauma center']
            },
            'medical_office': {
                'name': 'Medical Office Building',
                'base_cost': 280,
                'equipment_cost': 50,
                'typical_floors': 3,
                'keywords': ['medical office', 'mob', 'clinic', 'outpatient']
            },
            'urgent_care': {
                'name': 'Urgent Care',
                'base_cost': 350,
                'equipment_cost': 100,
                'typical_floors': 1,
                'keywords': ['urgent care', 'walk in clinic', 'immediate care']
            },
            'surgery_center': {
                'name': 'Ambulatory Surgery Center',
                'base_cost': 650,
                'equipment_cost': 150,
                'typical_floors': 1,
                'keywords': ['surgery center', 'asc', 'ambulatory', 'surgical center']
            },
            'dental_office': {
                'name': 'Dental Office',
                'base_cost': 325,
                'equipment_cost': 125,
                'typical_floors': 1,
                'keywords': ['dental', 'dentist', 'orthodontist']
            }
        }
    },
    
    'residential': {
        'display_name': 'Multifamily Residential',
        'subtypes': {
            'luxury_apartments': {
                'name': 'Class A / Luxury Apartments',
                'base_cost': 185,
                'equipment_cost': 40,  # Appliances, fixtures
                'typical_floors': 4,
                'keywords': ['luxury apartment', 'class a', 'high end apartment']
            },
            'market_rate_apartments': {
                'name': 'Class B / Market Rate',
                'base_cost': 145,
                'equipment_cost': 25,
                'typical_floors': 3,
                'keywords': ['apartment', 'multifamily', 'market rate']
            },
            'affordable_housing': {
                'name': 'Affordable Housing',
                'base_cost': 120,
                'equipment_cost': 15,
                'typical_floors': 3,
                'keywords': ['affordable housing', 'workforce housing', 'section 8', 'lihtc']
            },
            'student_housing': {
                'name': 'Student Housing',
                'base_cost': 165,
                'equipment_cost': 20,
                'typical_floors': 4,
                'keywords': ['student housing', 'dormitory', 'student apartment']
            },
            'condominiums': {
                'name': 'Condominiums',
                'base_cost': 195,
                'equipment_cost': 35,
                'typical_floors': 6,
                'keywords': ['condo', 'condominium', 'owned apartment']
            }
        }
    },
    
    'office': {
        'display_name': 'Office Buildings',
        'subtypes': {
            'class_a_office': {
                'name': 'Class A Office',
                'base_cost': 325,
                'equipment_cost': 25,
                'typical_floors': 10,
                'keywords': ['class a office', 'premium office', 'corporate headquarters']
            },
            'class_b_office': {
                'name': 'Class B Office',
                'base_cost': 225,
                'equipment_cost': 15,
                'typical_floors': 5,
                'keywords': ['class b office', 'standard office', 'professional building']
            },
            'class_c_office': {
                'name': 'Class C Office',
                'base_cost': 165,
                'equipment_cost': 10,
                'typical_floors': 3,
                'keywords': ['class c office', 'basic office']
            },
            'tech_office': {
                'name': 'Tech/Creative Office',
                'base_cost': 425,
                'equipment_cost': 50,
                'typical_floors': 4,
                'keywords': ['tech office', 'creative office', 'startup', 'open office']
            },
            'medical_office': {
                'name': 'Medical Office',
                'base_cost': 280,
                'equipment_cost': 50,
                'typical_floors': 3,
                'keywords': ['medical office', 'dental office', 'clinic']
            }
        }
    },
    
    'industrial': {
        'display_name': 'Industrial Buildings',
        'subtypes': {
            'warehouse': {
                'name': 'Warehouse/Distribution',
                'base_cost': 75,
                'equipment_cost': 10,
                'typical_floors': 1,
                'keywords': ['warehouse', 'distribution center', 'storage']
            },
            'manufacturing': {
                'name': 'Manufacturing',
                'base_cost': 110,
                'equipment_cost': 15,
                'typical_floors': 1,
                'keywords': ['manufacturing', 'factory', 'production facility']
            },
            'flex_space': {
                'name': 'Flex/Light Industrial',
                'base_cost': 95,
                'equipment_cost': 15,
                'typical_floors': 1,
                'keywords': ['flex space', 'light industrial', 'workshop']
            },
            'cold_storage': {
                'name': 'Cold Storage',
                'base_cost': 175,
                'equipment_cost': 25,
                'typical_floors': 1,
                'keywords': ['cold storage', 'freezer', 'refrigerated warehouse']
            },
            'data_center': {
                'name': 'Data Center',
                'base_cost': 850,
                'equipment_cost': 350,  # Servers, cooling
                'typical_floors': 1,
                'keywords': ['data center', 'server farm', 'colocation']
            }
        }
    },
    
    'retail': {
        'display_name': 'Retail',
        'subtypes': {
            'big_box': {
                'name': 'Big Box Retail',
                'base_cost': 135,
                'equipment_cost': 15,
                'typical_floors': 1,
                'keywords': ['big box', 'walmart', 'target', 'home depot']
            },
            'strip_center': {
                'name': 'Strip Center',
                'base_cost': 185,
                'equipment_cost': 15,
                'typical_floors': 1,
                'keywords': ['strip mall', 'strip center', 'retail center']
            },
            'mall_retail': {
                'name': 'Mall Retail',
                'base_cost': 225,
                'equipment_cost': 25,
                'typical_floors': 1,
                'keywords': ['mall store', 'anchor store', 'department store']
            },
            'boutique_retail': {
                'name': 'Boutique/High-End',
                'base_cost': 325,
                'equipment_cost': 25,
                'typical_floors': 1,
                'keywords': ['boutique', 'luxury retail', 'flagship store']
            },
            'grocery': {
                'name': 'Grocery Store',
                'base_cost': 245,
                'equipment_cost': 30,
                'typical_floors': 1,
                'keywords': ['grocery', 'supermarket', 'food store']
            },
            'convenience_store': {
                'name': 'Convenience Store',
                'base_cost': 285,
                'equipment_cost': 40,
                'typical_floors': 1,
                'keywords': ['convenience store', 'gas station', 'c-store', '7-eleven']
            }
        }
    },
    
    'education': {
        'display_name': 'Educational Facilities',
        'subtypes': {
            'elementary_school': {
                'name': 'Elementary School',
                'base_cost': 275,
                'equipment_cost': 25,
                'typical_floors': 2,
                'keywords': ['elementary school', 'primary school', 'grade school']
            },
            'middle_school': {
                'name': 'Middle School',
                'base_cost': 285,
                'equipment_cost': 30,
                'typical_floors': 2,
                'keywords': ['middle school', 'junior high']
            },
            'high_school': {
                'name': 'High School',
                'base_cost': 325,
                'equipment_cost': 35,
                'typical_floors': 3,
                'keywords': ['high school', 'secondary school']
            },
            'university': {
                'name': 'University/College',
                'base_cost': 385,
                'equipment_cost': 45,
                'typical_floors': 4,
                'keywords': ['university', 'college', 'higher education']
            },
            'vocational_school': {
                'name': 'Vocational/Technical',
                'base_cost': 295,
                'equipment_cost': 50,
                'typical_floors': 2,
                'keywords': ['vocational', 'technical school', 'trade school']
            },
            'daycare': {
                'name': 'Daycare/Preschool',
                'base_cost': 225,
                'equipment_cost': 20,
                'typical_floors': 1,
                'keywords': ['daycare', 'preschool', 'childcare', 'kindergarten']
            }
        }
    },
    
    'hospitality': {
        'display_name': 'Hospitality',
        'subtypes': {
            'luxury_hotel': {
                'name': 'Luxury/5-Star Hotel',
                'base_cost': 425,
                'equipment_cost': 75,
                'typical_floors': 20,
                'keywords': ['luxury hotel', '5 star', 'five star', 'resort']
            },
            'full_service_hotel': {
                'name': 'Full Service Hotel',
                'base_cost': 325,
                'equipment_cost': 50,
                'typical_floors': 10,
                'keywords': ['full service hotel', 'marriott', 'hilton', 'convention hotel']
            },
            'limited_service_hotel': {
                'name': 'Limited Service Hotel',
                'base_cost': 225,
                'equipment_cost': 35,
                'typical_floors': 4,
                'keywords': ['limited service', 'hampton inn', 'holiday inn express']
            },
            'economy_hotel': {
                'name': 'Economy Hotel',
                'base_cost': 165,
                'equipment_cost': 25,
                'typical_floors': 3,
                'keywords': ['economy hotel', 'motel', 'budget hotel', 'motel 6']
            },
            'boutique_hotel': {
                'name': 'Boutique Hotel',
                'base_cost': 385,
                'equipment_cost': 60,
                'typical_floors': 6,
                'keywords': ['boutique hotel', 'design hotel', 'lifestyle hotel']
            }
        }
    },
    
    'senior_living': {
        'display_name': 'Senior Living',
        'subtypes': {
            'independent_living': {
                'name': 'Independent Living',
                'base_cost': 185,
                'equipment_cost': 30,
                'typical_floors': 3,
                'keywords': ['independent living', 'senior apartments', '55+']
            },
            'assisted_living': {
                'name': 'Assisted Living',
                'base_cost': 245,
                'equipment_cost': 40,
                'typical_floors': 3,
                'keywords': ['assisted living', 'alf', 'senior care']
            },
            'memory_care': {
                'name': 'Memory Care',
                'base_cost': 285,
                'equipment_cost': 45,
                'typical_floors': 2,
                'keywords': ['memory care', 'dementia care', 'alzheimer']
            },
            'skilled_nursing': {
                'name': 'Skilled Nursing',
                'base_cost': 325,
                'equipment_cost': 60,
                'typical_floors': 2,
                'keywords': ['skilled nursing', 'nursing home', 'snf']
            }
        }
    },
    
    'mixed_use': {
        'display_name': 'Mixed Use',
        'subtypes': {
            'retail_residential': {
                'name': 'Retail + Residential',
                'base_cost': 245,
                'equipment_cost': 35,
                'typical_floors': 5,
                'keywords': ['mixed use', 'retail residential', 'live work']
            },
            'office_residential': {
                'name': 'Office + Residential',
                'base_cost': 265,
                'equipment_cost': 30,
                'typical_floors': 8,
                'keywords': ['office residential', 'mixed use office']
            },
            'hotel_retail': {
                'name': 'Hotel + Retail',
                'base_cost': 285,
                'equipment_cost': 45,
                'typical_floors': 12,
                'keywords': ['hotel retail', 'mixed use hotel']
            },
            'full_mixed': {
                'name': 'Retail + Office + Residential',
                'base_cost': 275,
                'equipment_cost': 40,
                'typical_floors': 15,
                'keywords': ['full mixed use', 'urban mixed', 'tod']
            }
        }
    },
    
    'specialty': {
        'display_name': 'Specialty Buildings',
        'subtypes': {
            'laboratory': {
                'name': 'Laboratory/Research',
                'base_cost': 525,
                'equipment_cost': 175,
                'typical_floors': 3,
                'keywords': ['laboratory', 'lab', 'research facility', 'r&d']
            },
            'clean_room': {
                'name': 'Clean Room Facility',
                'base_cost': 750,
                'equipment_cost': 250,
                'typical_floors': 2,
                'keywords': ['clean room', 'semiconductor', 'pharma manufacturing']
            },
            'sports_facility': {
                'name': 'Sports/Recreation',
                'base_cost': 225,
                'equipment_cost': 50,
                'typical_floors': 1,
                'keywords': ['gym', 'sports facility', 'recreation center', 'ymca']
            },
            'theater': {
                'name': 'Theater/Performance',
                'base_cost': 385,
                'equipment_cost': 75,
                'typical_floors': 1,
                'keywords': ['theater', 'cinema', 'performing arts', 'auditorium']
            },
            'parking_garage': {
                'name': 'Parking Garage',
                'base_cost': 65,
                'equipment_cost': 5,
                'typical_floors': 5,
                'keywords': ['parking garage', 'parking structure', 'deck']
            },
            'religious': {
                'name': 'Religious/Worship',
                'base_cost': 245,
                'equipment_cost': 25,
                'typical_floors': 1,
                'keywords': ['church', 'mosque', 'synagogue', 'temple', 'worship']
            }
        }
    }
}

# Regional cost multipliers (applied to base_cost only, not equipment)
REGIONAL_MULTIPLIERS = {
    # Southeast
    'nashville': 1.02,
    'atlanta': 1.05,
    'birmingham': 0.95,
    'charlotte': 1.03,
    'miami': 1.08,
    'orlando': 0.98,
    'tampa': 0.99,
    
    # Tennessee Cities
    'franklin': 1.03,
    'murfreesboro': 1.01,
    'memphis': 0.98,
    'knoxville': 0.97,
    'chattanooga': 0.96,
    
    # Northeast
    'new york': 1.45,
    'manhattan': 1.50,
    'brooklyn': 1.40,
    'boston': 1.38,
    'philadelphia': 1.25,
    'manchester': 0.98,
    'portsmouth': 1.01,
    'concord': 0.97,
    'nashua': 0.98,
    
    # West
    'san francisco': 1.48,
    'los angeles': 1.35,
    'san diego': 1.30,
    'seattle': 1.28,
    'portland': 1.15,
    'denver': 1.12,
    'phoenix': 0.95,
    'las vegas': 1.08,
    'salt lake city': 1.02,
    
    # Midwest
    'chicago': 1.22,
    'detroit': 1.08,
    'minneapolis': 1.15,
    'kansas city': 0.98,
    'milwaukee': 1.05,
    'indianapolis': 0.96,
    'columbus': 0.97,
    'cincinnati': 0.99,
    'cleveland': 1.02,
    'st louis': 1.00,
    
    # Southwest/Texas
    'austin': 1.08,
    'dallas': 1.05,
    'houston': 1.06,
    'san antonio': 0.98,
    'fort worth': 1.02,
    
    # Default
    'default': 1.00
}

def get_regional_multiplier(location: str) -> float:
    """
    Get the regional cost multiplier for a location.
    Checks for exact match first, then partial match.
    """
    if not location:
        return REGIONAL_MULTIPLIERS['default']
    
    location_lower = location.lower()
    
    # Check for exact city match
    for city, multiplier in REGIONAL_MULTIPLIERS.items():
        if city in location_lower:
            return multiplier
    
    # Check for state matches
    state_multipliers = {
        'tennessee': 1.00,
        ', tn': 1.00,
        'new york': 1.35,
        ', ny': 1.35,
        'california': 1.30,
        ', ca': 1.30,
        'texas': 1.02,
        ', tx': 1.02,
        'florida': 1.02,
        ', fl': 1.02,
        'massachusetts': 1.25,
        ', ma': 1.25,
        'illinois': 1.15,
        ', il': 1.15,
    }
    
    for state, multiplier in state_multipliers.items():
        if state in location_lower:
            return multiplier
    
    return REGIONAL_MULTIPLIERS['default']

# Special features cost additions (per square foot)
SPECIAL_FEATURES_COSTS = {
    'education': {
        'gymnasium': 25,
        'auditorium': 35,
        'science_labs': 20,
        'library': 15,
        'cafeteria': 12,
        'computer_lab': 18
    },
    'healthcare': {
        'emergency_department': 50,
        'operating_rooms': 75,
        'medical_imaging': 45,
        'laboratory': 30,
        'icu': 65,
        'pharmacy': 25,
        'medical_gas': 20
    },
    'specialty': {
        'clean_room': 100,
        'server_room': 80,
        'high_security': 35,
        'cold_storage': 40,
        'loading_dock': 15
    },
    'hospitality': {
        'pool': 60,
        'spa': 45,
        'conference_rooms': 20,
        'restaurant': 35,
        'fitness_center': 25
    },
    'office': {
        'executive_suite': 30,
        'conference_rooms': 20,
        'fitness_center': 25,
        'cafeteria': 15,
        'data_center': 75
    },
    'retail': {
        'food_court': 25,
        'anchor_store': 15,
        'escalators': 40,
        'loading_dock': 12
    }
}

def get_special_features_cost(building_type: str, features: list) -> float:
    """Calculate additional cost per sqft for special features"""
    if not features or building_type not in SPECIAL_FEATURES_COSTS:
        return 0.0
    
    feature_costs = SPECIAL_FEATURES_COSTS[building_type]
    total_feature_cost = 0.0
    
    for feature in features:
        if feature.lower() in feature_costs:
            total_feature_cost += feature_costs[feature.lower()]
    
    return total_feature_cost

# Trade breakdown percentages by building type
TRADE_PERCENTAGES = {
    'healthcare': {
        'site_work': 0.08,
        'foundations': 0.06,
        'structural': 0.14,
        'envelope': 0.08,
        'roofing': 0.03,
        'mechanical': 0.30,  # Higher for hospitals (medical gas, specialized HVAC)
        'electrical': 0.18,  # Higher for medical equipment
        'plumbing': 0.12,   # Medical gas, specialized drainage
        'finishes': 0.10,   # Medical-grade finishes
        'equipment': 0.05,   # Built-in medical equipment
        'vertical_transport': 0.03,
        'fire_protection': 0.03
    },
    'restaurant': {
        'site_work': 0.10,
        'foundations': 0.05,
        'structural': 0.10,
        'envelope': 0.08,
        'roofing': 0.04,
        'mechanical': 0.25,  # Kitchen ventilation
        'electrical': 0.20,  # Kitchen equipment power
        'plumbing': 0.15,   # Grease traps, floor drains
        'finishes': 0.25,   # Dining area finishes
        'equipment': 0.08,   # Kitchen equipment (partial)
        'fire_protection': 0.05  # Kitchen suppression
    },
    'residential': {
        'site_work': 0.06,
        'foundations': 0.07,
        'structural': 0.18,
        'envelope': 0.12,
        'roofing': 0.05,
        'windows_doors': 0.06,
        'mechanical': 0.08,
        'electrical': 0.08,
        'plumbing': 0.08,
        'finishes': 0.35,   # Higher for residential
        'appliances': 0.02,
        'vertical_transport': 0.02
    },
    'office': {
        'site_work': 0.08,
        'foundations': 0.06,
        'structural': 0.18,
        'envelope': 0.12,
        'roofing': 0.04,
        'mechanical': 0.15,
        'electrical': 0.12,
        'plumbing': 0.08,
        'finishes': 0.25,
        'vertical_transport': 0.03,
        'fire_protection': 0.02
    },
    'industrial': {
        'site_work': 0.12,
        'foundations': 0.08,
        'structural': 0.25,  # Heavy structure
        'envelope': 0.15,
        'roofing': 0.06,
        'mechanical': 0.10,
        'electrical': 0.08,
        'plumbing': 0.04,
        'finishes': 0.05,   # Minimal finishes
        'equipment': 0.04,
        'fire_protection': 0.03
    },
    'retail': {
        'site_work': 0.10,
        'foundations': 0.05,
        'structural': 0.15,
        'envelope': 0.10,
        'roofing': 0.05,
        'storefront': 0.08,
        'mechanical': 0.12,
        'electrical': 0.10,
        'plumbing': 0.06,
        'finishes': 0.30,
        'fire_protection': 0.02
    },
    'default': {
        'site_work': 0.08,
        'foundations': 0.06,
        'structural': 0.18,
        'envelope': 0.10,
        'roofing': 0.04,
        'mechanical': 0.15,
        'electrical': 0.12,
        'plumbing': 0.08,
        'finishes': 0.25,
        'equipment': 0.02,
        'fire_protection': 0.02
    }
}

def get_trade_percentages(building_type: str) -> dict:
    """Get trade breakdown percentages for a building type"""
    return TRADE_PERCENTAGES.get(building_type, TRADE_PERCENTAGES['default'])