"""
Owner metrics configuration for healthcare building types.
This config drives soft costs, department allocations, and ROI calculations.
"""

OWNER_METRICS_CONFIG = {
    'healthcare': {
        'hospital': {
            'soft_costs': {
                # As percentages of construction cost
                'design_engineering': 0.08,      # 8% - Complex medical design
                'permits_legal': 0.02,           # 2% - Standard permits
                'medical_equipment': 0.12,       # 12% - Expensive medical equipment
                'furniture_fixtures': 0.03,      # 3% - Non-medical FF&E
                'construction_contingency': 0.10,# 10% - GC contingency
                'owner_contingency': 0.05,       # 5% - Owner reserve
                'financing_costs': 0.03,         # 3% - Based on 18-month build
                'insurance_bonds': 0.015,        # 1.5% - Standard for healthcare
                'commissioning': 0.01            # 1% - Critical for hospitals
            },
            'department_allocations': {
                'clinical': {
                    'percent_of_area': 0.60,     # 60% of total area
                    'trade_allocations': {
                        # How much of each trade serves this department
                        'structural': 0.60,
                        'mechanical': 0.70,      # Heavy HVAC for ORs/ICUs
                        'electrical': 0.65,       # Medical equipment power
                        'plumbing': 0.60,        # Medical gas systems
                        'finishes': 0.50         # Clinical finishes
                    },
                    'includes': ['Patient Rooms', 'Operating Rooms', 'ICU', 'Emergency', 'Imaging', 'Labs', 'Pharmacy']
                },
                'support': {
                    'percent_of_area': 0.30,
                    'trade_allocations': {
                        'structural': 0.30,
                        'mechanical': 0.20,
                        'electrical': 0.20,
                        'plumbing': 0.30,
                        'finishes': 0.35
                    },
                    'includes': ['Admin Offices', 'Waiting Areas', 'Cafeteria', 'Gift Shop', 'Chapel', 'Storage', 'Corridors']
                },
                'infrastructure': {
                    'percent_of_area': 0.10,
                    'trade_allocations': {
                        'structural': 0.10,
                        'mechanical': 0.10,      # Central plant
                        'electrical': 0.15,       # Main electrical rooms
                        'plumbing': 0.10,
                        'finishes': 0.15
                    },
                    'includes': ['Mechanical Rooms', 'Electrical Rooms', 'IT/Data Centers', 'Loading Dock', 'Service Areas']
                }
            },
            'roi_metrics': {
                'unit_type': 'beds',
                'units_per_sf': 0.00075,          # Industry standard: ~1,333 SF per bed
                'revenue_per_unit': 650000,       # $650K annual revenue per bed
                'occupancy_rate': 0.85,           # 85% target occupancy
                'operating_margin': 0.20,         # 20% EBITDA margin for well-run hospital
                'revenue_type': 'annual',
                'expense_ratio': 0.80,            # Operating expenses are 80% of revenue
                'discount_rate': 0.08             # 8% discount rate for NPV
            },
            'ownership_types': {
                'for_profit': {
                    'label': 'For-Profit Hospital',
                    'financing': {
                        'debt_ratio': 0.65,
                        'debt_rate': 0.068,
                        'equity_ratio': 0.35
                    },
                    'target_metrics': {
                        'roi_target': 8.0,
                        'dscr_target': 1.25,
                        'operating_margin_target': 0.20
                    }
                },
                'non_profit': {
                    'label': 'Non-Profit Hospital (Most Common)',
                    'financing': {
                        'debt_ratio': 0.75,
                        'debt_rate': 0.04,  # Tax-exempt bonds
                        'philanthropy_ratio': 0.15,
                        'grants_ratio': 0.10
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.03,
                        'dscr_target': 1.15,
                        'days_cash_target': 180
                    }
                },
                'government': {
                    'label': 'Government/Public Hospital',
                    'financing': {
                        'public_funding_ratio': 0.60,
                        'bond_ratio': 0.40,
                        'debt_rate': 0.035
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.00,  # Break-even is OK
                        'community_benefit_target': True
                    }
                }
            }
        },
        
        'medical_office': {
            'soft_costs': {
                'design_engineering': 0.06,      # 6% - Simpler than hospital
                'permits_legal': 0.015,          # 1.5% - Easier permitting
                'medical_equipment': 0.05,       # 5% - Basic medical equipment
                'furniture_fixtures': 0.04,      # 4% - Office furniture
                'construction_contingency': 0.10,
                'owner_contingency': 0.05,
                'financing_costs': 0.02,         # 2% - 12-month build
                'insurance_bonds': 0.01
            },
            'department_allocations': {
                'clinical': {
                    'percent_of_area': 0.70,
                    'trade_allocations': {
                        'structural': 0.70,
                        'mechanical': 0.70,
                        'electrical': 0.70,
                        'plumbing': 0.65,
                        'finishes': 0.70
                    },
                    'includes': ['Exam Rooms', 'Procedure Rooms', 'Lab', 'X-Ray', 'Nursing Stations']
                },
                'support': {
                    'percent_of_area': 0.25,
                    'trade_allocations': {
                        'structural': 0.25,
                        'mechanical': 0.25,
                        'electrical': 0.25,
                        'plumbing': 0.30,
                        'finishes': 0.25
                    },
                    'includes': ['Reception', 'Waiting', 'Admin', 'Records', 'Staff Break Room']
                },
                'infrastructure': {
                    'percent_of_area': 0.05,
                    'trade_allocations': {
                        'structural': 0.05,
                        'mechanical': 0.05,
                        'electrical': 0.05,
                        'plumbing': 0.05,
                        'finishes': 0.05
                    },
                    'includes': ['IT Room', 'Storage', 'Mechanical']
                }
            },
            'roi_metrics': {
                'unit_type': 'sf',
                'units_per_sf': 1.0,              # Revenue calculated per SF
                'revenue_per_unit': 45,           # $45/SF annual rent (NNN)
                'occupancy_rate': 0.92,           # 92% occupancy
                'operating_margin': 0.35,         # Higher margin due to NNN lease structure
                'revenue_type': 'annual',
                'expense_ratio': 0.65,
                'discount_rate': 0.07
            },
            'ownership_types': {
                'for_profit': {
                    'label': 'For-Profit Medical Office',
                    'financing': {
                        'debt_ratio': 0.70,
                        'debt_rate': 0.065,
                        'equity_ratio': 0.30
                    },
                    'target_metrics': {
                        'roi_target': 7.5,
                        'dscr_target': 1.20,
                        'operating_margin_target': 0.35
                    }
                },
                'non_profit': {
                    'label': 'Hospital-Owned Medical Office',
                    'financing': {
                        'debt_ratio': 0.80,
                        'debt_rate': 0.045,  # Tax-exempt if part of hospital system
                        'system_funding_ratio': 0.20
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.15,
                        'dscr_target': 1.10
                    }
                },
                'reit': {
                    'label': 'REIT-Owned Medical Office',
                    'financing': {
                        'debt_ratio': 0.60,
                        'debt_rate': 0.055,
                        'equity_ratio': 0.40
                    },
                    'target_metrics': {
                        'cap_rate_target': 0.065,
                        'dscr_target': 1.35,
                        'ffo_yield_target': 0.07
                    }
                }
            }
        },
        
        'outpatient_clinic': {
            'soft_costs': {
                'design_engineering': 0.065,
                'permits_legal': 0.02,
                'medical_equipment': 0.08,       # More equipment than office
                'furniture_fixtures': 0.035,
                'construction_contingency': 0.10,
                'owner_contingency': 0.05,
                'financing_costs': 0.025,
                'insurance_bonds': 0.012
            },
            'department_allocations': {
                'clinical': {
                    'percent_of_area': 0.65,
                    'trade_allocations': {
                        'structural': 0.65,
                        'mechanical': 0.68,
                        'electrical': 0.67,
                        'plumbing': 0.63,
                        'finishes': 0.60
                    },
                    'includes': ['Treatment Rooms', 'Minor Procedure Rooms', 'Recovery', 'Imaging']
                },
                'support': {
                    'percent_of_area': 0.28,
                    'trade_allocations': {
                        'structural': 0.28,
                        'mechanical': 0.25,
                        'electrical': 0.26,
                        'plumbing': 0.30,
                        'finishes': 0.32
                    },
                    'includes': ['Reception', 'Waiting', 'Consultation', 'Admin']
                },
                'infrastructure': {
                    'percent_of_area': 0.07,
                    'trade_allocations': {
                        'structural': 0.07,
                        'mechanical': 0.07,
                        'electrical': 0.07,
                        'plumbing': 0.07,
                        'finishes': 0.08
                    },
                    'includes': ['Mechanical', 'Electrical', 'Storage']
                }
            },
            'roi_metrics': {
                'unit_type': 'exam_rooms',
                'units_per_sf': 0.001,            # 1 exam room per 1,000 SF
                'revenue_per_unit': 400000,       # $400K per exam room annually
                'occupancy_rate': 0.80,
                'operating_margin': 0.22,
                'revenue_type': 'annual',
                'expense_ratio': 0.78,
                'discount_rate': 0.075
            },
            'ownership_types': {
                'for_profit': {
                    'label': 'For-Profit Outpatient Clinic',
                    'financing': {
                        'debt_ratio': 0.65,
                        'debt_rate': 0.065,
                        'equity_ratio': 0.35
                    },
                    'target_metrics': {
                        'roi_target': 7.5,
                        'dscr_target': 1.20,
                        'operating_margin_target': 0.22
                    }
                },
                'non_profit': {
                    'label': 'Community Health Center',
                    'financing': {
                        'debt_ratio': 0.50,
                        'debt_rate': 0.04,  # Tax-exempt bonds
                        'grants_ratio': 0.30,  # HRSA and other grants
                        'philanthropy_ratio': 0.20
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.05,
                        'dscr_target': 1.10,
                        'community_benefit_target': True
                    }
                },
                'hospital_owned': {
                    'label': 'Hospital System Clinic',
                    'financing': {
                        'debt_ratio': 0.70,
                        'debt_rate': 0.045,
                        'system_funding_ratio': 0.30
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.15,
                        'dscr_target': 1.15
                    }
                }
            }
        },
        
        'urgent_care': {
            'soft_costs': {
                'design_engineering': 0.055,
                'permits_legal': 0.015,
                'medical_equipment': 0.07,
                'furniture_fixtures': 0.03,
                'construction_contingency': 0.10,
                'owner_contingency': 0.05,
                'financing_costs': 0.02,         # Quick 10-month build
                'insurance_bonds': 0.01
            },
            'department_allocations': {
                'clinical': {
                    'percent_of_area': 0.68,
                    'trade_allocations': {
                        'structural': 0.68,
                        'mechanical': 0.65,
                        'electrical': 0.70,
                        'plumbing': 0.60,
                        'finishes': 0.65
                    },
                    'includes': ['Exam Rooms', 'Triage', 'X-Ray', 'Lab', 'Treatment']
                },
                'support': {
                    'percent_of_area': 0.27,
                    'trade_allocations': {
                        'structural': 0.27,
                        'mechanical': 0.30,
                        'electrical': 0.25,
                        'plumbing': 0.35,
                        'finishes': 0.30
                    },
                    'includes': ['Reception', 'Waiting', 'Admin', 'Staff Areas']
                },
                'infrastructure': {
                    'percent_of_area': 0.05,
                    'trade_allocations': {
                        'structural': 0.05,
                        'mechanical': 0.05,
                        'electrical': 0.05,
                        'plumbing': 0.05,
                        'finishes': 0.05
                    },
                    'includes': ['Mechanical', 'Storage', 'IT']
                }
            },
            'roi_metrics': {
                'unit_type': 'visits_per_day',
                'units_per_sf': 0.005,            # 40 visits/day for 8,000 SF facility
                'revenue_per_unit': 150,          # $150 per visit
                'daily_visits': 40,               # Base daily capacity
                'annual_operating_days': 365,
                'occupancy_rate': 0.75,           # 75% of capacity
                'operating_margin': 0.25,         # 25% EBITDA margin
                'revenue_type': 'per_visit',
                'expense_ratio': 0.75,
                'discount_rate': 0.08
            },
            'ownership_types': {
                'for_profit': {
                    'label': 'For-Profit Urgent Care',
                    'financing': {
                        'debt_ratio': 0.60,
                        'debt_rate': 0.065,
                        'equity_ratio': 0.40
                    },
                    'target_metrics': {
                        'roi_target': 8.0,
                        'dscr_target': 1.25,
                        'operating_margin_target': 0.25
                    }
                },
                'hospital_owned': {
                    'label': 'Hospital System Urgent Care',
                    'financing': {
                        'debt_ratio': 0.70,
                        'debt_rate': 0.045,
                        'system_funding_ratio': 0.30
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.18,
                        'dscr_target': 1.15
                    }
                },
                'franchise': {
                    'label': 'Franchise Urgent Care',
                    'financing': {
                        'debt_ratio': 0.55,
                        'debt_rate': 0.07,  # Higher rate due to franchise risk
                        'franchise_fee': 0.06,  # 6% of revenue
                        'equity_ratio': 0.45
                    },
                    'target_metrics': {
                        'roi_target': 9.0,
                        'dscr_target': 1.30,
                        'operating_margin_target': 0.20  # Lower due to franchise fees
                    }
                }
            }
        },
        
        'rehabilitation_center': {
            'soft_costs': {
                'design_engineering': 0.07,
                'permits_legal': 0.02,
                'medical_equipment': 0.10,       # Therapy equipment
                'furniture_fixtures': 0.04,
                'construction_contingency': 0.10,
                'owner_contingency': 0.05,
                'financing_costs': 0.025,
                'insurance_bonds': 0.012,
                'specialized_therapy_equipment': 0.03  # Additional therapy equipment
            },
            'department_allocations': {
                'clinical': {
                    'percent_of_area': 0.55,
                    'trade_allocations': {
                        'structural': 0.55,
                        'mechanical': 0.60,
                        'electrical': 0.58,
                        'plumbing': 0.55,
                        'finishes': 0.50
                    },
                    'includes': ['Therapy Gyms', 'Treatment Rooms', 'Hydrotherapy', 'Patient Rooms']
                },
                'support': {
                    'percent_of_area': 0.35,
                    'trade_allocations': {
                        'structural': 0.35,
                        'mechanical': 0.32,
                        'electrical': 0.32,
                        'plumbing': 0.38,
                        'finishes': 0.40
                    },
                    'includes': ['Admin', 'Dining', 'Recreation', 'Family Areas']
                },
                'infrastructure': {
                    'percent_of_area': 0.10,
                    'trade_allocations': {
                        'structural': 0.10,
                        'mechanical': 0.08,
                        'electrical': 0.10,
                        'plumbing': 0.07,
                        'finishes': 0.10
                    },
                    'includes': ['Mechanical', 'Laundry', 'Storage', 'Service']
                }
            },
            'roi_metrics': {
                'unit_type': 'beds',
                'units_per_sf': 0.0005,          # 1 bed per 2,000 SF (more space needed)
                'revenue_per_unit': 450000,       # $450K per bed (lower than acute care)
                'occupancy_rate': 0.90,           # Higher occupancy for rehab
                'operating_margin': 0.18,
                'revenue_type': 'annual',
                'expense_ratio': 0.82,
                'discount_rate': 0.075
            },
            'ownership_types': {
                'for_profit': {
                    'label': 'For-Profit Rehab Center',
                    'financing': {
                        'debt_ratio': 0.65,
                        'debt_rate': 0.065,
                        'equity_ratio': 0.35
                    },
                    'target_metrics': {
                        'roi_target': 7.5,
                        'dscr_target': 1.20,
                        'operating_margin_target': 0.18
                    }
                },
                'non_profit': {
                    'label': 'Non-Profit Rehab Center',
                    'financing': {
                        'debt_ratio': 0.70,
                        'debt_rate': 0.04,  # Tax-exempt bonds
                        'philanthropy_ratio': 0.20,
                        'grants_ratio': 0.10
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.08,
                        'dscr_target': 1.10,
                        'days_cash_target': 120
                    }
                },
                'hospital_owned': {
                    'label': 'Hospital System Rehab',
                    'financing': {
                        'debt_ratio': 0.75,
                        'debt_rate': 0.045,
                        'system_funding_ratio': 0.25
                    },
                    'target_metrics': {
                        'operating_margin_target': 0.12,
                        'dscr_target': 1.15
                    }
                }
            }
        }
    }
}