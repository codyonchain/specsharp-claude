"""
Master configuration for all building types.
Single source of truth that combines construction costs, owner metrics, and NLP patterns.
This replaces: building_types_config.py, owner_metrics_config.py, and NLP detection logic.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ============================================================================
# ENUMS
# ============================================================================

class BuildingType(Enum):
    """All building types in the system"""
    HEALTHCARE = "healthcare"
    MULTIFAMILY = "multifamily"
    OFFICE = "office"
    RETAIL = "retail"
    INDUSTRIAL = "industrial"
    HOSPITALITY = "hospitality"
    EDUCATIONAL = "educational"
    CIVIC = "civic"
    RECREATION = "recreation"
    MIXED_USE = "mixed_use"
    PARKING = "parking"
    RESTAURANT = "restaurant"
    SPECIALTY = "specialty"
    # Note: RELIGIOUS excluded per requirements (13 types total)

class ProjectClass(Enum):
    """Project classification types"""
    GROUND_UP = "ground_up"
    ADDITION = "addition"
    RENOVATION = "renovation"
    TENANT_IMPROVEMENT = "tenant_improvement"

class OwnershipType(Enum):
    """Ownership types for financing calculations"""
    FOR_PROFIT = "for_profit"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"
    PPP = "public_private_partnership"

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TradeBreakdown:
    """Trade cost percentages"""
    structural: float
    mechanical: float
    electrical: float
    plumbing: float
    finishes: float

@dataclass
class SoftCosts:
    """Owner soft cost rates"""
    design_fees: float
    permits: float
    legal: float
    financing: float
    contingency: float
    testing: float
    construction_management: float
    startup: float

@dataclass
class FinancingTerms:
    """Financing parameters for ownership types"""
    debt_ratio: float
    debt_rate: float
    equity_ratio: float
    philanthropy_ratio: float = 0.0
    grants_ratio: float = 0.0
    target_dscr: float = 1.25
    target_roi: float = 0.08

@dataclass
class NLPConfig:
    """NLP detection configuration"""
    keywords: List[str]
    priority: int  # Higher = check first
    incompatible_classes: List[ProjectClass]
    confidence_threshold: float = 0.7

@dataclass
class BuildingConfig:
    """Complete configuration for a building subtype"""
    # Display
    display_name: str
    
    # Construction costs
    base_cost_per_sf: float
    cost_range: Tuple[float, float]
    equipment_cost_per_sf: float
    typical_floors: int
    
    # Trade breakdown
    trades: TradeBreakdown
    
    # Owner costs
    soft_costs: SoftCosts
    
    # Financing options
    ownership_types: Dict[OwnershipType, FinancingTerms]
    
    # NLP detection
    nlp: NLPConfig
    
    # Regional multipliers (base = Nashville = 1.0)
    regional_multipliers: Dict[str, float]
    
    # Special features that add cost
    special_features: Optional[Dict[str, float]] = None

# ============================================================================
# MASTER CONFIGURATION
# ============================================================================

MASTER_CONFIG = {
    # ------------------------------------------------------------------------
    # HEALTHCARE
    # ------------------------------------------------------------------------
    BuildingType.HEALTHCARE: {
        'hospital': BuildingConfig(
            display_name='Hospital',
            base_cost_per_sf=1150,
            cost_range=(1050, 1250),
            equipment_cost_per_sf=200,
            typical_floors=5,
            
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.35,  # High for healthcare
                electrical=0.15,
                plumbing=0.18,
                finishes=0.10
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.025,
                legal=0.02,
                financing=0.03,
                contingency=0.10,
                testing=0.015,
                construction_management=0.04,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.068,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.08
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.04,  # Tax-exempt bonds
                    equity_ratio=0.10,
                    philanthropy_ratio=0.10,
                    grants_ratio=0.05,
                    target_dscr=1.15,
                    target_roi=0.03
                ),
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.40,
                    debt_rate=0.035,
                    equity_ratio=0.30,
                    grants_ratio=0.30,
                    target_dscr=1.10,
                    target_roi=0.0  # Break-even OK
                )
            },
            
            nlp=NLPConfig(
                keywords=['hospital', 'emergency', 'operating room', 'OR', 'ICU', 
                         'beds', 'surgical', 'medical center', 'trauma', 'acute care'],
                priority=1,  # Highest priority
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.96,
                'Memphis': 0.94,
                'Knoxville': 0.93,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.20,
                'Miami': 1.10
            },
            
            special_features={
                'emergency_department': 50,  # $/SF additional
                'surgical_suite': 100,
                'mri_suite': 80,
                'cathlab': 90,
                'pharmacy': 40
            }
        ),
        
        'medical_office': BuildingConfig(
            display_name='Medical Office Building',
            base_cost_per_sf=425,
            cost_range=(375, 475),
            equipment_cost_per_sf=75,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.28,
                electrical=0.12,
                plumbing=0.15,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.065,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.09
                )
            },
            
            nlp=NLPConfig(
                keywords=['medical office', 'MOB', 'physician', 'doctor office', 
                         'clinic', 'outpatient', 'medical suite', 'practice'],
                priority=2,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.96,
                'Memphis': 0.94,
                'New York': 1.30,
                'San Francisco': 1.35
            }
        ),
        
        'urgent_care': BuildingConfig(
            display_name='Urgent Care Center',
            base_cost_per_sf=385,
            cost_range=(350, 420),
            equipment_cost_per_sf=65,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.26,
                electrical=0.12,
                plumbing=0.14,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.065,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['urgent care', 'walk-in clinic', 'immediate care', 
                         'express care', 'quick care'],
                priority=3,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.25,
                'San Francisco': 1.30
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # MULTIFAMILY
    # ------------------------------------------------------------------------
    BuildingType.MULTIFAMILY: {
        'luxury_apartments': BuildingConfig(
            display_name='Class A / Luxury Apartments',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=25,  # Appliances, fixtures
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.22,
                electrical=0.12,
                plumbing=0.18,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.005,
                construction_management=0.03,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.055,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['luxury apartment', 'class a', 'high-end apartment', 
                         'luxury multifamily', 'upscale apartment', 'premium apartment'],
                priority=5,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Miami': 1.20
            },
            
            special_features={
                'rooftop_amenity': 35,
                'pool': 25,
                'fitness_center': 20,
                'parking_garage': 45,
                'concierge': 15
            }
        ),
        
        'market_rate_apartments': BuildingConfig(
            display_name='Class B / Market Rate Apartments',
            base_cost_per_sf=145,
            cost_range=(130, 160),
            equipment_cost_per_sf=15,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.30,
                mechanical=0.20,
                electrical=0.12,
                plumbing=0.18,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.045,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.07,
                testing=0.005,
                construction_management=0.025,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.20,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['apartment', 'multifamily', 'market rate', 'class b',
                         'rental housing', 'apartment complex'],
                priority=6,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.40,
                'San Francisco': 1.45
            }
        ),
        
        'affordable_housing': BuildingConfig(
            display_name='Affordable Housing',
            base_cost_per_sf=120,
            cost_range=(110, 130),
            equipment_cost_per_sf=10,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.32,
                mechanical=0.18,
                electrical=0.12,
                plumbing=0.18,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.02,  # Higher for compliance
                financing=0.02,  # Often subsidized
                contingency=0.06,
                testing=0.005,
                construction_management=0.025,
                startup=0.005
            ),
            
            ownership_types={
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.50,
                    debt_rate=0.04,  # Tax-exempt bonds
                    equity_ratio=0.10,
                    philanthropy_ratio=0.15,
                    grants_ratio=0.25,  # LIHTC, etc.
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['affordable housing', 'workforce housing', 'section 8',
                         'LIHTC', 'low income', 'subsidized housing'],
                priority=7,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.88,
                'Memphis': 0.86,
                'New York': 1.35,
                'San Francisco': 1.40
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # OFFICE
    # ------------------------------------------------------------------------
    BuildingType.OFFICE: {
        'class_a': BuildingConfig(
            display_name='Class A Office',
            base_cost_per_sf=225,
            cost_range=(200, 250),
            equipment_cost_per_sf=15,
            typical_floors=10,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.25,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.06,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.08
                )
            },
            
            nlp=NLPConfig(
                keywords=['class a office', 'corporate headquarters', 'tower',
                         'high-rise office', 'premium office'],
                priority=8,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.92,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25
            }
        ),
        
        'class_b': BuildingConfig(
            display_name='Class B Office',
            base_cost_per_sf=175,
            cost_range=(150, 200),
            equipment_cost_per_sf=10,
            typical_floors=5,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.22,
                electrical=0.14,
                plumbing=0.11,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.72,
                    debt_rate=0.062,
                    equity_ratio=0.28,
                    target_dscr=1.20,
                    target_roi=0.09
                )
            },
            
            nlp=NLPConfig(
                keywords=['office', 'office building', 'class b',
                         'commercial office', 'professional building'],
                priority=9,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.90,
                'New York': 1.40,
                'San Francisco': 1.45
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # RETAIL
    # ------------------------------------------------------------------------
    BuildingType.RETAIL: {
        'shopping_center': BuildingConfig(
            display_name='Shopping Center',
            base_cost_per_sf=150,
            cost_range=(125, 175),
            equipment_cost_per_sf=5,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.30,
                mechanical=0.20,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.07,
                testing=0.005,
                construction_management=0.025,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.058,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['shopping center', 'retail center', 'strip mall',
                         'strip center', 'plaza', 'shopping plaza'],
                priority=10,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40
            }
        ),
        
        'big_box': BuildingConfig(
            display_name='Big Box Retail',
            base_cost_per_sf=125,
            cost_range=(100, 150),
            equipment_cost_per_sf=3,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.35,
                mechanical=0.18,
                electrical=0.14,
                plumbing=0.08,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.06,
                testing=0.005,
                construction_management=0.02,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.72,
                    debt_rate=0.06,
                    equity_ratio=0.28,
                    target_dscr=1.20,
                    target_roi=0.09
                )
            },
            
            nlp=NLPConfig(
                keywords=['big box', 'anchor tenant', 'department store',
                         'superstore', 'warehouse retail'],
                priority=11,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.30,
                'San Francisco': 1.35
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # RESTAURANT
    # ------------------------------------------------------------------------
    BuildingType.RESTAURANT: {
        'quick_service': BuildingConfig(
            display_name='Quick Service Restaurant',
            base_cost_per_sf=300,
            cost_range=(250, 350),
            equipment_cost_per_sf=25,  # Kitchen equipment mostly in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.28,
                electrical=0.15,
                plumbing=0.15,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,      # 5% - simpler design than complex buildings
                permits=0.015,         # 1.5%
                legal=0.005,           # 0.5%
                financing=0.02,        # 2% - shorter construction period
                contingency=0.05,      # 5% - well-understood building type
                testing=0.005,         # 0.5% - kitchen equipment testing
                construction_management=0.025,  # 2.5%
                startup=0.01           # 1% - training, initial inventory
            ),  # Total: 18% soft costs
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['fast food', 'quick service', 'QSR', 'drive through',
                         'fast casual', 'takeout'],
                priority=12,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.35,
                'San Francisco': 1.40
            }
        ),
        
        'full_service': BuildingConfig(
            display_name='Full Service Restaurant',
            base_cost_per_sf=385,  # Optimized for industry standards ($450-500/SF total)
            cost_range=(350, 425),
            equipment_cost_per_sf=25,  # Optimized - kitchen equipment mostly in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.20,
                mechanical=0.30,
                electrical=0.16,
                plumbing=0.14,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,      # 5% - simpler design than complex buildings
                permits=0.015,         # 1.5%
                legal=0.005,           # 0.5%
                financing=0.02,        # 2% - shorter construction period
                contingency=0.05,      # 5% - well-understood building type
                testing=0.005,         # 0.5% - kitchen equipment testing
                construction_management=0.025,  # 2.5%
                startup=0.01           # 1% - training, initial inventory
            ),  # Total: 18% soft costs
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.068,
                    equity_ratio=0.40,
                    target_dscr=1.30,
                    target_roi=0.15
                )
            },
            
            nlp=NLPConfig(
                keywords=['restaurant', 'dining', 'sit-down', 'full service',
                         'casual dining', 'family restaurant'],
                priority=13,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.40,
                'San Francisco': 1.45
            }
        ),
        
        'bar_tavern': BuildingConfig(
            display_name='Bar/Tavern',
            base_cost_per_sf=350,  # Adjusted to industry standard
            cost_range=(325, 375),
            equipment_cost_per_sf=25,  # Bar equipment included in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.25,
                electrical=0.18,
                plumbing=0.15,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,      # 5% - simpler design than complex buildings
                permits=0.02,          # 2% - includes liquor license
                legal=0.01,            # 1% - includes liquor license legal
                financing=0.02,        # 2% - shorter construction period
                contingency=0.05,      # 5% - well-understood building type
                testing=0.005,         # 0.5% - bar equipment testing
                construction_management=0.025,  # 2.5%
                startup=0.01           # 1% - training, initial inventory
            ),  # Total: 19% soft costs (slightly higher for liquor licensing)
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.14
                )
            },
            
            nlp=NLPConfig(
                keywords=['bar', 'tavern', 'pub', 'lounge', 'nightclub', 
                         'cocktail bar', 'sports bar', 'brewpub'],
                priority=13,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42
            }
        ),
        
        'cafe': BuildingConfig(
            display_name='Cafe/Coffee Shop',
            base_cost_per_sf=300,  # Adjusted to industry standard
            cost_range=(275, 325),
            equipment_cost_per_sf=20,  # Coffee equipment mostly in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.23,
                mechanical=0.22,
                electrical=0.16,
                plumbing=0.14,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.045,     # 4.5% - simpler cafe design
                permits=0.015,         # 1.5%
                legal=0.005,           # 0.5%
                financing=0.02,        # 2% - shorter construction period
                contingency=0.045,     # 4.5% - simple, well-understood
                testing=0.005,         # 0.5% - coffee equipment testing
                construction_management=0.02,   # 2%
                startup=0.01           # 1% - training, initial inventory
            ),  # Total: 16% soft costs (lower for simpler cafes)
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.063,
                    equity_ratio=0.32,
                    target_dscr=1.22,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['cafe', 'coffee shop', 'coffee house', 'espresso bar',
                         'coffee bar', 'bakery cafe', 'tea shop'],
                priority=12,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.35,
                'San Francisco': 1.40
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # INDUSTRIAL
    # ------------------------------------------------------------------------
    BuildingType.INDUSTRIAL: {
        'warehouse': BuildingConfig(
            display_name='Warehouse',
            base_cost_per_sf=85,
            cost_range=(70, 100),
            equipment_cost_per_sf=5,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.35,  # Large clear spans
                mechanical=0.15,  # Minimal HVAC
                electrical=0.12,
                plumbing=0.08,   # Minimal plumbing
                finishes=0.30
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.01,
                financing=0.025,
                contingency=0.06,
                testing=0.005,
                construction_management=0.02,
                startup=0.005
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['warehouse', 'storage', 'distribution', 'logistics', 
                         'fulfillment center', 'bulk storage'],
                priority=14,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.25,
                'San Francisco': 1.30,
                'Chicago': 1.10,
                'Miami': 1.05
            }
        ),
        
        'distribution_center': BuildingConfig(
            display_name='Distribution Center',
            base_cost_per_sf=95,
            cost_range=(80, 110),
            equipment_cost_per_sf=8,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.33,
                mechanical=0.17,  # More HVAC than warehouse
                electrical=0.13,
                plumbing=0.09,
                finishes=0.28
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.045,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.065,
                testing=0.005,
                construction_management=0.025,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['distribution center', 'distribution', 'DC', 'cross-dock',
                         'sorting facility', 'hub'],
                priority=15,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,  # Memphis is distribution hub
                'New York': 1.28,
                'San Francisco': 1.32,
                'Chicago': 1.12,
                'Miami': 1.06
            },
            
            special_features={
                'automated_sorting': 25,
                'refrigerated_area': 35,
                'loading_docks': 15
            }
        ),
        
        'manufacturing': BuildingConfig(
            display_name='Manufacturing Facility',
            base_cost_per_sf=125,
            cost_range=(100, 150),
            equipment_cost_per_sf=35,  # Process equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.25,  # Heavy mechanical
                electrical=0.18,  # Heavy power
                plumbing=0.12,
                finishes=0.17
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['manufacturing', 'factory', 'production', 'plant',
                         'assembly', 'fabrication', 'processing'],
                priority=16,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.08
            },
            
            special_features={
                'clean_room': 75,
                'heavy_power': 40,
                'crane_bays': 30,
                'compressed_air': 20
            }
        ),
        
        'flex_space': BuildingConfig(
            display_name='Flex Space',
            base_cost_per_sf=110,
            cost_range=(95, 125),
            equipment_cost_per_sf=10,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.30,
                mechanical=0.20,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.25  # Better finishes for office portion
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.07,
                testing=0.005,
                construction_management=0.025,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.72,
                    debt_rate=0.060,
                    equity_ratio=0.28,
                    target_dscr=1.22,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['flex space', 'flex', 'warehouse office', 'light industrial',
                         'r&d space', 'tech space'],
                priority=17,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.30,
                'San Francisco': 1.35,
                'Chicago': 1.12,
                'Miami': 1.07
            }
        ),
        
        'cold_storage': BuildingConfig(
            display_name='Cold Storage Facility',
            base_cost_per_sf=175,
            cost_range=(150, 200),
            equipment_cost_per_sf=45,  # Refrigeration equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.35,  # Heavy refrigeration
                electrical=0.18,  # High power for refrigeration
                plumbing=0.10,
                finishes=0.12
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.015,  # More testing for systems
                construction_management=0.03,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['cold storage', 'freezer', 'refrigerated', 'frozen storage',
                         'cooler', 'cold chain'],
                priority=18,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.32,
                'San Francisco': 1.38,
                'Chicago': 1.15,
                'Miami': 1.10
            },
            
            special_features={
                'blast_freezer': 50,
                'multiple_temp_zones': 30,
                'automated_retrieval': 40
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # HOSPITALITY
    # ------------------------------------------------------------------------
    BuildingType.HOSPITALITY: {
        'full_service_hotel': BuildingConfig(
            display_name='Full Service Hotel',
            base_cost_per_sf=325,
            cost_range=(275, 375),
            equipment_cost_per_sf=45,  # FF&E
            typical_floors=8,
            
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.26,
                electrical=0.14,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.02,
                financing=0.035,
                contingency=0.09,
                testing=0.01,
                construction_management=0.035,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.30,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['hotel', 'full service hotel', 'convention hotel',
                         'resort hotel', 'luxury hotel'],
                priority=19,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.20
            },
            
            special_features={
                'ballroom': 50,
                'restaurant': 75,
                'spa': 60,
                'conference_center': 45,
                'rooftop_bar': 55
            }
        ),
        
        'limited_service_hotel': BuildingConfig(
            display_name='Limited Service Hotel',
            base_cost_per_sf=225,
            cost_range=(200, 250),
            equipment_cost_per_sf=25,
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.24,
                electrical=0.13,
                plumbing=0.17,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.03,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['limited service', 'select service', 'express hotel',
                         'budget hotel', 'economy hotel'],
                priority=20,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.20,
                'Miami': 1.15
            },
            
            special_features={
                'breakfast_area': 20,
                'fitness_center': 15,
                'business_center': 10,
                'pool': 25
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # EDUCATIONAL
    # ------------------------------------------------------------------------
    BuildingType.EDUCATIONAL: {
        'elementary_school': BuildingConfig(
            display_name='Elementary School',
            base_cost_per_sf=285,
            cost_range=(260, 310),
            equipment_cost_per_sf=25,  # Classroom equipment, playground
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.24,  # Good ventilation crucial
                electrical=0.13,
                plumbing=0.15,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.035,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,  # Municipal bonds
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.15,
                    target_roi=0.0  # Public good
                )
            },
            
            nlp=NLPConfig(
                keywords=['elementary school', 'primary school', 'grade school',
                         'K-5', 'K-6', 'elementary'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.18,
                'Miami': 1.10
            },
            
            special_features={
                'gymnasium': 35,
                'cafeteria': 30,
                'playground': 20,
                'computer_lab': 25,
                'library': 25
            }
        ),
        
        'middle_school': BuildingConfig(
            display_name='Middle School',
            base_cost_per_sf=295,
            cost_range=(270, 320),
            equipment_cost_per_sf=30,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.25,
                electrical=0.14,
                plumbing=0.15,
                finishes=0.19
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.035,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['middle school', 'junior high', 'intermediate school',
                         'grades 6-8', 'grades 7-9'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.18,
                'Miami': 1.10
            },
            
            special_features={
                'gymnasium': 40,
                'cafeteria': 30,
                'science_labs': 35,
                'computer_lab': 25,
                'auditorium': 45,
                'athletic_field': 30
            }
        ),
        
        'high_school': BuildingConfig(
            display_name='High School',
            base_cost_per_sf=315,
            cost_range=(290, 340),
            equipment_cost_per_sf=35,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.26,  # Labs need ventilation
                electrical=0.15,
                plumbing=0.15,
                finishes=0.18
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.075,
                permits=0.022,
                legal=0.015,
                financing=0.025,
                contingency=0.085,
                testing=0.012,
                construction_management=0.04,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['high school', 'secondary school', 'senior high',
                         'grades 9-12', 'preparatory school'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.20,
                'Miami': 1.12
            },
            
            special_features={
                'stadium': 60,
                'field_house': 50,
                'performing_arts_center': 55,
                'science_labs': 40,
                'vocational_shops': 45,
                'media_center': 30
            }
        ),
        
        'university': BuildingConfig(
            display_name='University Building',
            base_cost_per_sf=375,
            cost_range=(325, 425),
            equipment_cost_per_sf=50,  # Lab equipment, technology
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.28,  # Complex systems
                electrical=0.16,
                plumbing=0.14,
                finishes=0.17
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.025,
                legal=0.02,
                financing=0.03,
                contingency=0.09,
                testing=0.015,
                construction_management=0.04,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.045,  # Tax-exempt bonds
                    equity_ratio=0.15,
                    philanthropy_ratio=0.20,  # Donations
                    grants_ratio=0.05,
                    target_dscr=1.20,
                    target_roi=0.0
                ),
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.08
                )
            },
            
            nlp=NLPConfig(
                keywords=['university', 'college', 'academic building', 'campus',
                         'lecture hall', 'classroom building', 'higher education'],
                priority=24,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.42,
                'San Francisco': 1.48,
                'Chicago': 1.22,
                'Miami': 1.15
            },
            
            special_features={
                'lecture_hall': 45,
                'research_lab': 75,
                'clean_room': 100,
                'library': 40,
                'student_center': 35
            }
        ),
        
        'community_college': BuildingConfig(
            display_name='Community College',
            base_cost_per_sf=295,
            cost_range=(270, 320),
            equipment_cost_per_sf=30,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.25,
                electrical=0.14,
                plumbing=0.14,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.075,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,
                    equity_ratio=0.25,
                    grants_ratio=0.10,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['community college', 'junior college', 'technical college',
                         'vocational school', 'trade school'],
                priority=25,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.08
            },
            
            special_features={
                'vocational_lab': 40,
                'computer_lab': 25,
                'library': 20,
                'student_services': 15
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # MIXED_USE
    # ------------------------------------------------------------------------
    BuildingType.MIXED_USE: {
        'retail_residential': BuildingConfig(
            display_name='Retail with Residential Above',
            base_cost_per_sf=225,
            cost_range=(200, 250),
            equipment_cost_per_sf=20,
            typical_floors=5,  # 1 retail + 4 residential
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.23,
                electrical=0.14,
                plumbing=0.17,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.018,
                financing=0.03,
                contingency=0.08,
                testing=0.008,
                construction_management=0.03,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.72,
                    debt_rate=0.058,
                    equity_ratio=0.28,
                    target_dscr=1.25,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['mixed use', 'retail residential', 'shops with apartments',
                         'ground floor retail', 'live work'],
                priority=26,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.18
            },
            
            special_features={
                'rooftop_deck': 30,
                'parking_podium': 40,
                'retail_plaza': 25
            }
        ),
        
        'office_residential': BuildingConfig(
            display_name='Office with Residential',
            base_cost_per_sf=245,
            cost_range=(220, 270),
            equipment_cost_per_sf=18,
            typical_floors=8,  # 3 office + 5 residential
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.24,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.065,
                permits=0.025,
                legal=0.018,
                financing=0.03,
                contingency=0.085,
                testing=0.01,
                construction_management=0.032,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.060,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['office residential', 'mixed use tower', 'office with housing',
                         'work live', 'commercial residential'],
                priority=27,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.48,
                'San Francisco': 1.52,
                'Chicago': 1.28,
                'Miami': 1.20
            },
            
            special_features={
                'amenity_deck': 35,
                'business_center': 20,
                'conference_facility': 30
            }
        ),
        
        'hotel_retail': BuildingConfig(
            display_name='Hotel with Retail',
            base_cost_per_sf=295,
            cost_range=(270, 320),
            equipment_cost_per_sf=35,
            typical_floors=10,
            
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.25,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.02,
                financing=0.032,
                contingency=0.09,
                testing=0.01,
                construction_management=0.035,
                startup=0.018
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.062,
                    equity_ratio=0.32,
                    target_dscr=1.28,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['hotel retail', 'hotel with shops', 'hospitality mixed use',
                         'hotel complex', 'resort retail'],
                priority=28,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.22
            },
            
            special_features={
                'conference_center': 45,
                'restaurant': 50,
                'spa': 55,
                'retail_arcade': 30
            }
        ),
        
        'urban_mixed': BuildingConfig(
            display_name='Urban Mixed Use',
            base_cost_per_sf=265,
            cost_range=(240, 290),
            equipment_cost_per_sf=25,
            typical_floors=12,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.24,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.028,
                legal=0.02,
                financing=0.032,
                contingency=0.09,
                testing=0.012,
                construction_management=0.035,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.060,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['urban mixed', 'mixed use development', 'multi-use',
                         'live work play', 'vertical mixed'],
                priority=29,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.48,
                'San Francisco': 1.55,
                'Chicago': 1.30,
                'Miami': 1.22
            },
            
            special_features={
                'public_plaza': 40,
                'green_roof': 35,
                'parking_structure': 45,
                'transit_connection': 30
            }
        ),
        
        'transit_oriented': BuildingConfig(
            display_name='Transit-Oriented Development',
            base_cost_per_sf=275,
            cost_range=(250, 300),
            equipment_cost_per_sf=22,
            typical_floors=8,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.23,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.21
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.03,
                legal=0.022,
                financing=0.032,
                contingency=0.09,
                testing=0.012,
                construction_management=0.035,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.058,
                    equity_ratio=0.32,
                    target_dscr=1.25,
                    target_roi=0.12
                ),
                OwnershipType.PPP: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.045,
                    equity_ratio=0.20,
                    grants_ratio=0.20,  # Transit grants
                    target_dscr=1.20,
                    target_roi=0.08
                )
            },
            
            nlp=NLPConfig(
                keywords=['TOD', 'transit oriented', 'transit development', 'station area',
                         'transit village', 'metro development'],
                priority=30,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,  # No transit
                'Memphis': 0.93,
                'New York': 1.50,  # High transit value
                'San Francisco': 1.55,
                'Chicago': 1.35,
                'Miami': 1.20
            },
            
            special_features={
                'transit_plaza': 35,
                'bike_facility': 20,
                'pedestrian_bridge': 45,
                'public_art': 15
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # SPECIALTY
    # ------------------------------------------------------------------------
    BuildingType.SPECIALTY: {
        'data_center': BuildingConfig(
            display_name='Data Center',
            base_cost_per_sf=1200,  # Very high due to infrastructure
            cost_range=(1000, 1400),
            equipment_cost_per_sf=400,  # Servers, cooling, UPS
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.15,
                mechanical=0.40,  # Massive cooling requirements
                electrical=0.30,  # Redundant power systems
                plumbing=0.05,
                finishes=0.10
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.03,
                legal=0.02,
                financing=0.04,
                contingency=0.10,
                testing=0.02,  # Critical testing
                construction_management=0.04,
                startup=0.03
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.065,
                    equity_ratio=0.40,
                    target_dscr=1.35,
                    target_roi=0.15
                )
            },
            
            nlp=NLPConfig(
                keywords=['data center', 'server farm', 'colocation', 'colo',
                         'cloud facility', 'computing center', 'tier 3', 'tier 4'],
                priority=31,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT, ProjectClass.RENOVATION]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.25,  # Less premium for data centers
                'San Francisco': 1.30,
                'Chicago': 1.15,
                'Miami': 1.10
            },
            
            special_features={
                'tier_4_certification': 200,
                'redundant_power': 150,
                'security_system': 75,
                'fiber_connectivity': 100
            }
        ),
        
        'laboratory': BuildingConfig(
            display_name='Laboratory / Research Facility',
            base_cost_per_sf=450,
            cost_range=(400, 500),
            equipment_cost_per_sf=125,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.32,  # Specialized ventilation
                electrical=0.18,
                plumbing=0.16,  # Gas, water, waste systems
                finishes=0.12
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.09,
                permits=0.03,
                legal=0.02,
                financing=0.035,
                contingency=0.10,
                testing=0.02,
                construction_management=0.04,
                startup=0.025
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.12
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.045,
                    equity_ratio=0.10,
                    grants_ratio=0.20,  # Research grants
                    target_dscr=1.20,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['laboratory', 'lab', 'research facility', 'R&D',
                         'biotech', 'clean room', 'research center', 'testing facility'],
                priority=32,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.40,
                'San Francisco': 1.45,  # Biotech hub
                'Chicago': 1.20,
                'Miami': 1.12
            },
            
            special_features={
                'clean_room': 150,
                'fume_hoods': 75,
                'biosafety_level_3': 200,
                'vibration_isolation': 100,
                'emergency_shower': 25
            }
        ),
        
        'self_storage': BuildingConfig(
            display_name='Self Storage Facility',
            base_cost_per_sf=65,
            cost_range=(55, 75),
            equipment_cost_per_sf=5,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.35,
                mechanical=0.12,  # Minimal HVAC
                electrical=0.13,
                plumbing=0.05,   # Minimal plumbing
                finishes=0.35
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.06,
                testing=0.005,
                construction_management=0.02,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['self storage', 'storage facility', 'mini storage',
                         'storage units', 'public storage', 'boat storage', 'RV storage'],
                priority=33,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.30,
                'San Francisco': 1.35,
                'Chicago': 1.10,
                'Miami': 1.05
            },
            
            special_features={
                'climate_control': 20,
                'vehicle_storage': 15,
                'security_system': 10,
                'automated_access': 12
            }
        ),
        
        'car_dealership': BuildingConfig(
            display_name='Car Dealership',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=15,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.20,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.27  # Showroom finishes
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.028,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.22,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['car dealership', 'auto dealership', 'vehicle showroom',
                         'car showroom', 'auto mall', 'dealership'],
                priority=34,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.10
            },
            
            special_features={
                'service_center': 45,
                'detail_bay': 25,
                'parts_warehouse': 20,
                'car_wash': 30
            }
        ),
        
        'broadcast_facility': BuildingConfig(
            display_name='Broadcast / Studio Facility',
            base_cost_per_sf=325,
            cost_range=(300, 350),
            equipment_cost_per_sf=75,  # Studio equipment
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.26,  # Sound isolation HVAC
                electrical=0.20,  # High power for equipment
                plumbing=0.10,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.018,
                financing=0.03,
                contingency=0.08,
                testing=0.015,
                construction_management=0.03,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['broadcast', 'studio', 'television station', 'radio station',
                         'recording studio', 'production facility', 'soundstage'],
                priority=35,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,  # Music city
                'Manchester': 0.92,
                'Memphis': 0.94,
                'New York': 1.45,
                'San Francisco': 1.40,
                'Chicago': 1.20,
                'Miami': 1.15
            },
            
            special_features={
                'sound_stage': 60,
                'control_room': 45,
                'green_screen': 30,
                'acoustic_treatment': 40,
                'broadcast_tower': 100
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # CIVIC
    # ------------------------------------------------------------------------
    BuildingType.CIVIC: {
        'government_building': BuildingConfig(
            display_name='Government Building',
            base_cost_per_sf=265,
            cost_range=(240, 290),
            equipment_cost_per_sf=20,
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.23,
                electrical=0.14,
                plumbing=0.14,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.015,  # Government project
                legal=0.02,
                financing=0.02,
                contingency=0.08,
                testing=0.01,
                construction_management=0.035,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,  # Municipal bonds
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['city hall', 'courthouse', 'federal building', 'state building',
                         'municipal building', 'government center', 'capitol', 'administration'],
                priority=36,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.20,
                'Miami': 1.12
            },
            
            special_features={
                'council_chambers': 40,
                'secure_area': 35,
                'public_plaza': 25,
                'records_vault': 30
            }
        ),
        
        'public_safety': BuildingConfig(
            display_name='Public Safety Facility',
            base_cost_per_sf=285,
            cost_range=(260, 310),
            equipment_cost_per_sf=35,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.28,  # Hardened structure
                mechanical=0.24,
                electrical=0.16,  # Emergency power
                plumbing=0.14,
                finishes=0.18
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.015,
                legal=0.018,
                financing=0.02,
                contingency=0.085,
                testing=0.012,
                construction_management=0.035,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['fire station', 'police station', 'sheriff', 'emergency services',
                         'dispatch center', '911 center', 'EOC', 'public safety'],
                priority=37,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.22,
                'Miami': 1.15
            },
            
            special_features={
                'apparatus_bay': 45,
                'dispatch_center': 50,
                'training_tower': 40,
                'emergency_generator': 35,
                'sally_port': 30
            }
        ),
        
        'library': BuildingConfig(
            display_name='Public Library',
            base_cost_per_sf=275,
            cost_range=(250, 300),
            equipment_cost_per_sf=25,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.24,
                electrical=0.15,
                plumbing=0.12,
                finishes=0.23
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.015,
                legal=0.015,
                financing=0.02,
                contingency=0.075,
                testing=0.01,
                construction_management=0.03,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.15,
                    grants_ratio=0.10,  # Library grants
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['library', 'public library', 'branch library', 'main library',
                         'media center', 'learning center'],
                priority=38,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.20,
                'Miami': 1.10
            },
            
            special_features={
                'reading_room': 20,
                'computer_lab': 25,
                'childrens_area': 20,
                'meeting_rooms': 15,
                'archives': 30
            }
        ),
        
        'community_center': BuildingConfig(
            display_name='Community Center',
            base_cost_per_sf=245,
            cost_range=(220, 270),
            equipment_cost_per_sf=20,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.23,
                electrical=0.13,
                plumbing=0.15,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.015,
                legal=0.015,
                financing=0.02,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    grants_ratio=0.10,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.045,
                    equity_ratio=0.15,
                    philanthropy_ratio=0.15,
                    grants_ratio=0.10,
                    target_dscr=1.10,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['community center', 'rec center', 'senior center', 'youth center',
                         'cultural center', 'civic center', 'activity center'],
                priority=39,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.18,
                'Miami': 1.08
            },
            
            special_features={
                'gymnasium': 35,
                'kitchen': 25,
                'multipurpose_room': 20,
                'fitness_center': 20,
                'outdoor_pavilion': 15
            }
        ),
        
        'courthouse': BuildingConfig(
            display_name='Courthouse',
            base_cost_per_sf=325,
            cost_range=(300, 350),
            equipment_cost_per_sf=30,
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.28,  # Security requirements
                mechanical=0.24,
                electrical=0.16,
                plumbing=0.13,
                finishes=0.19
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.015,
                legal=0.025,
                financing=0.025,
                contingency=0.09,
                testing=0.012,
                construction_management=0.04,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['courthouse', 'court house', 'justice center', 'judicial center',
                         'court building', 'federal court', 'district court'],
                priority=40,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.42,
                'San Francisco': 1.45,
                'Chicago': 1.25,
                'Miami': 1.18
            },
            
            special_features={
                'courtroom': 50,
                'jury_room': 25,
                'holding_cells': 40,
                'judges_chambers': 30,
                'security_screening': 35
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # RECREATION
    # ------------------------------------------------------------------------
    BuildingType.RECREATION: {
        'fitness_center': BuildingConfig(
            display_name='Fitness Center / Gym',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=35,  # Exercise equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.25,  # Heavy HVAC for workout areas
                electrical=0.14,
                plumbing=0.15,  # Showers, pools
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['gym', 'fitness center', 'health club', 'workout',
                         'YMCA', 'athletic club', 'crossfit', 'wellness center'],
                priority=41,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.12
            },
            
            special_features={
                'pool': 45,
                'basketball_court': 30,
                'group_fitness': 20,
                'spa_area': 35,
                'juice_bar': 15
            }
        ),
        
        'sports_complex': BuildingConfig(
            display_name='Sports Complex',
            base_cost_per_sf=225,
            cost_range=(200, 250),
            equipment_cost_per_sf=25,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.28,  # Large spans
                mechanical=0.23,
                electrical=0.14,
                plumbing=0.13,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.022,
                legal=0.015,
                financing=0.028,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.25,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.062,
                    equity_ratio=0.32,
                    target_dscr=1.25,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['sports complex', 'athletic complex', 'field house',
                         'sports center', 'recreation complex', 'sportsplex'],
                priority=42,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.20,
                'Miami': 1.15
            },
            
            special_features={
                'indoor_track': 35,
                'multiple_courts': 40,
                'weight_room': 25,
                'locker_complex': 30,
                'concessions': 20
            }
        ),
        
        'aquatic_center': BuildingConfig(
            display_name='Aquatic Center',
            base_cost_per_sf=325,
            cost_range=(300, 350),
            equipment_cost_per_sf=45,  # Pool equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.30,  # Heavy HVAC and dehumidification
                electrical=0.15,
                plumbing=0.18,  # Pool systems
                finishes=0.12
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.09,
                testing=0.015,  # Water quality systems
                construction_management=0.035,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.25,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.045,
                    equity_ratio=0.15,
                    grants_ratio=0.15,
                    target_dscr=1.10,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['aquatic center', 'natatorium', 'swimming pool', 'pool',
                         'water park', 'swim center', 'aquatics'],
                priority=43,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.22,
                'Miami': 1.10  # Outdoor pools more common
            },
            
            special_features={
                'competition_pool': 60,
                'diving_well': 50,
                'lazy_river': 40,
                'water_slides': 45,
                'therapy_pool': 35
            }
        ),
        
        'recreation_center': BuildingConfig(
            display_name='Recreation Center',
            base_cost_per_sf=215,
            cost_range=(190, 240),
            equipment_cost_per_sf=20,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.24,
                electrical=0.13,
                plumbing=0.14,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.075,
                testing=0.008,
                construction_management=0.03,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    grants_ratio=0.05,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.045,
                    equity_ratio=0.15,
                    philanthropy_ratio=0.10,
                    grants_ratio=0.10,
                    target_dscr=1.10,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['rec center', 'recreation center', 'community recreation',
                         'activity center', 'parks and rec', 'leisure center'],
                priority=44,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.18,
                'Miami': 1.08
            },
            
            special_features={
                'gymnasium': 30,
                'game_room': 15,
                'craft_room': 12,
                'dance_studio': 20,
                'outdoor_courts': 25
            }
        ),
        
        'stadium': BuildingConfig(
            display_name='Stadium / Arena',
            base_cost_per_sf=425,
            cost_range=(375, 475),
            equipment_cost_per_sf=55,  # Scoreboards, sound, lighting
            typical_floors=4,  # Multiple levels of seating
            
            trades=TradeBreakdown(
                structural=0.32,  # Major structural for seating
                mechanical=0.22,
                electrical=0.18,  # Field lighting, displays
                plumbing=0.13,
                finishes=0.15
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.03,
                legal=0.025,
                financing=0.035,
                contingency=0.10,
                testing=0.012,
                construction_management=0.04,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.038,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.0
                ),
                OwnershipType.PPP: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.045,
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.25,
                    target_roi=0.06
                )
            },
            
            nlp=NLPConfig(
                keywords=['stadium', 'arena', 'coliseum', 'ballpark', 'football stadium',
                         'baseball stadium', 'soccer stadium', 'sports venue'],
                priority=45,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT, ProjectClass.RENOVATION]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.93,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.28,
                'Miami': 1.20
            },
            
            special_features={
                'luxury_boxes': 75,
                'club_level': 50,
                'press_box': 40,
                'video_board': 100,
                'retractable_roof': 200
            }
        )
    },
    
    # ------------------------------------------------------------------------
    # PARKING
    # ------------------------------------------------------------------------
    BuildingType.PARKING: {
        'surface_parking': BuildingConfig(
            display_name='Surface Parking Lot',
            base_cost_per_sf=18,  # Very low - just paving
            cost_range=(15, 21),
            equipment_cost_per_sf=2,  # Lighting, gates
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.60,  # Paving, grading
                mechanical=0.02,  # Minimal
                electrical=0.18,  # Lighting
                plumbing=0.05,   # Drainage
                finishes=0.15    # Striping, signage
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.03,
                permits=0.015,
                legal=0.01,
                financing=0.02,
                contingency=0.05,
                testing=0.005,
                construction_management=0.015,
                startup=0.005
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.30,
                    target_roi=0.15
                )
            },
            
            nlp=NLPConfig(
                keywords=['parking lot', 'surface parking', 'parking', 'surface lot',
                         'park and ride', 'parking area'],
                priority=46,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.25,
                'San Francisco': 1.30,
                'Chicago': 1.10,
                'Miami': 1.05
            },
            
            special_features={
                'covered_parking': 25,
                'valet_booth': 15,
                'ev_charging': 10,
                'security_system': 8
            }
        ),
        
        'parking_garage': BuildingConfig(
            display_name='Parking Garage',
            base_cost_per_sf=65,
            cost_range=(55, 75),
            equipment_cost_per_sf=8,  # Gates, equipment
            typical_floors=5,
            
            trades=TradeBreakdown(
                structural=0.45,  # Heavy concrete structure
                mechanical=0.08,  # Ventilation
                electrical=0.15,  # Lighting, controls
                plumbing=0.07,   # Minimal
                finishes=0.25    # Coatings, striping
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.06,
                testing=0.008,
                construction_management=0.02,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.12
                ),
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['parking garage', 'parking structure', 'parking deck',
                         'parkade', 'parking ramp', 'multi-level parking'],
                priority=47,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.20,
                'Miami': 1.10
            },
            
            special_features={
                'automated_system': 45,
                'ev_charging': 12,
                'car_wash': 25,
                'retail_space': 30,
                'green_roof': 20
            }
        ),
        
        'underground_parking': BuildingConfig(
            display_name='Underground Parking',
            base_cost_per_sf=125,  # Expensive excavation
            cost_range=(110, 140),
            equipment_cost_per_sf=12,
            typical_floors=2,  # Below grade levels
            
            trades=TradeBreakdown(
                structural=0.40,  # Major excavation and structure
                mechanical=0.15,  # Ventilation critical
                electrical=0.15,
                plumbing=0.10,   # Drainage, pumps
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.012,  # Waterproofing tests
                construction_management=0.03,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.22,
                    target_roi=0.10
                )
            },
            
            nlp=NLPConfig(
                keywords=['underground parking', 'subterranean parking', 'basement parking',
                         'below grade parking', 'underground garage'],
                priority=48,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.45,  # High land value
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.05  # Water table issues
            },
            
            special_features={
                'waterproofing': 35,
                'sump_pumps': 20,
                'vehicle_lifts': 30,
                'security_booth': 15,
                'ventilation_upgrade': 25
            }
        ),
        
        'automated_parking': BuildingConfig(
            display_name='Automated Parking System',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=65,  # Automated systems
            typical_floors=6,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.30,  # Automated systems
                electrical=0.25,  # Controls and power
                plumbing=0.05,
                finishes=0.15
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.03,
                legal=0.02,
                financing=0.035,
                contingency=0.10,
                testing=0.02,  # System testing
                construction_management=0.04,
                startup=0.025  # System commissioning
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['automated parking', 'robotic parking', 'mechanical parking',
                         'puzzle parking', 'stack parking', 'tower parking'],
                priority=49,
                incompatible_classes=[ProjectClass.RENOVATION, ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.40,  # Space premium
                'San Francisco': 1.45,
                'Chicago': 1.22,
                'Miami': 1.15
            },
            
            special_features={
                'retrieval_speed': 40,
                'redundant_systems': 35,
                'valet_interface': 20,
                'ev_charging_integration': 15
            }
        )
    }
}

# ============================================================================
# MULTIPLIERS
# ============================================================================

PROJECT_CLASS_MULTIPLIERS = {
    ProjectClass.GROUND_UP: 1.00,
    ProjectClass.ADDITION: 1.15,
    ProjectClass.RENOVATION: 1.35,
    ProjectClass.TENANT_IMPROVEMENT: 0.65
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_building_config(building_type: BuildingType, subtype: str) -> Optional[BuildingConfig]:
    """Get configuration for a specific building type and subtype"""
    if building_type in MASTER_CONFIG:
        return MASTER_CONFIG[building_type].get(subtype)
    return None

def get_all_subtypes(building_type: BuildingType) -> List[str]:
    """Get all subtypes for a building type"""
    if building_type in MASTER_CONFIG:
        return list(MASTER_CONFIG[building_type].keys())
    return []

def validate_project_class(building_type: BuildingType, subtype: str, 
                          project_class: ProjectClass) -> ProjectClass:
    """Validate and correct project classification if incompatible"""
    config = get_building_config(building_type, subtype)
    if config and project_class in config.nlp.incompatible_classes:
        return ProjectClass.GROUND_UP  # Default to ground-up if incompatible
    return project_class

def get_trade_breakdown(building_type: BuildingType, subtype: str) -> Optional[TradeBreakdown]:
    """Get trade breakdown for a building type"""
    config = get_building_config(building_type, subtype)
    return config.trades if config else None

def get_soft_costs(building_type: BuildingType, subtype: str) -> Optional[SoftCosts]:
    """Get soft costs for a building type"""
    config = get_building_config(building_type, subtype)
    return config.soft_costs if config else None

def get_regional_multiplier(building_type: BuildingType, subtype: str, city: str) -> float:
    """Get regional cost multiplier for a city"""
    config = get_building_config(building_type, subtype)
    if config:
        # Try exact match first
        if city in config.regional_multipliers:
            return config.regional_multipliers[city]
        # Try case-insensitive match
        for key, value in config.regional_multipliers.items():
            if key.lower() == city.lower():
                return value
    return 1.0  # Default to Nashville baseline

def get_base_cost(building_type: BuildingType, subtype: str) -> float:
    """Get base construction cost per square foot"""
    config = get_building_config(building_type, subtype)
    return config.base_cost_per_sf if config else 250.0  # Default to office cost

def get_equipment_cost(building_type: BuildingType, subtype: str) -> float:
    """Get equipment cost per square foot"""
    config = get_building_config(building_type, subtype)
    return config.equipment_cost_per_sf if config else 0.0

def get_special_feature_cost(building_type: BuildingType, subtype: str, feature: str) -> float:
    """Get additional cost for special features"""
    config = get_building_config(building_type, subtype)
    if config and config.special_features:
        return config.special_features.get(feature, 0.0)
    return 0.0

def get_financing_terms(building_type: BuildingType, subtype: str, 
                       ownership: OwnershipType) -> Optional[FinancingTerms]:
    """Get financing terms for a specific ownership type"""
    config = get_building_config(building_type, subtype)
    if config:
        return config.ownership_types.get(ownership)
    return None

# ============================================================================
# NLP DETECTION HELPERS
# ============================================================================

def get_nlp_keywords_by_priority() -> List[Tuple[BuildingType, str, NLPConfig]]:
    """Get all NLP configurations sorted by priority for detection"""
    configs = []
    for building_type, subtypes in MASTER_CONFIG.items():
        for subtype, config in subtypes.items():
            configs.append((building_type, subtype, config.nlp))
    
    # Sort by priority (higher first)
    configs.sort(key=lambda x: x[2].priority, reverse=True)
    return configs

def detect_building_type(description: str) -> Optional[Tuple[BuildingType, str]]:
    """Simple keyword-based building type detection"""
    description_lower = description.lower()
    
    for building_type, subtype, nlp_config in get_nlp_keywords_by_priority():
        for keyword in nlp_config.keywords:
            if keyword.lower() in description_lower:
                return (building_type, subtype)
    
    return None  # No match found

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate that all configurations are complete and consistent"""
    errors = []
    
    for building_type, subtypes in MASTER_CONFIG.items():
        for subtype, config in subtypes.items():
            # Check trade percentages sum to 1.0
            trade_sum = (config.trades.structural + config.trades.mechanical + 
                        config.trades.electrical + config.trades.plumbing + 
                        config.trades.finishes)
            if abs(trade_sum - 1.0) > 0.01:
                errors.append(f"{building_type.value}/{subtype}: Trade percentages sum to {trade_sum:.2f}, not 1.0")
            
            # Check at least one ownership type exists
            if not config.ownership_types:
                errors.append(f"{building_type.value}/{subtype}: No ownership types defined")
            
            # Check financing ratios sum correctly
            for ownership, terms in config.ownership_types.items():
                ratio_sum = (terms.debt_ratio + terms.equity_ratio + 
                           terms.philanthropy_ratio + terms.grants_ratio)
                if abs(ratio_sum - 1.0) > 0.01:
                    errors.append(f"{building_type.value}/{subtype}/{ownership.value}: "
                                f"Financing ratios sum to {ratio_sum:.2f}, not 1.0")
    
    return errors

# Run validation on import
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration validation passed")