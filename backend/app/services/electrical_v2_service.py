"""
Electrical Cost Calculation Engine V2
Implements realistic, industry-standard electrical pricing with:
- Space-type-aware calculations
- Regional cost adjustments
- Comprehensive scope coverage
- Accurate fixture densities
- Validation and warnings
"""
from typing import Dict, List, Any, Tuple, Optional
import math
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SpaceType(Enum):
    """Define standard space types with electrical characteristics"""
    WAREHOUSE = "warehouse"
    OFFICE = "office"
    RETAIL = "retail"
    RESTAURANT = "restaurant"
    HEALTHCARE = "healthcare"
    LIGHT_INDUSTRIAL = "light_industrial"
    DATA_CENTER = "data_center"
    RESIDENTIAL = "residential"


class CostTier(Enum):
    """Regional cost tiers"""
    TIER_1_HIGHEST = 1  # SF, LA, NYC, Boston, Seattle
    TIER_2_HIGH = 2     # San Diego, Sacramento, Portland, Denver, Austin
    TIER_3_MODERATE = 3 # Phoenix, Dallas, Atlanta, Chicago
    TIER_4_LOWER = 4    # Kansas City, Memphis, Oklahoma City, Rural


class ElectricalV2Service:
    """Modern electrical cost calculation service with industry-standard pricing"""
    
    def __init__(self):
        # Space type base rates ($/SF) - Calibrated for 2025 California construction
        self.space_type_rates = {
            SpaceType.WAREHOUSE: {
                'base_min': 5.00,
                'base_max': 6.50,
                'typical': 5.75,  # Warehouse electrical
                'lighting_density': 600,  # Adjusted - 1 per 600 SF
                'receptacle_density': 1500,  # Adjusted receptacles
                'circuit_density': 2000,  # Adjusted circuits
                'data_density': 4000,  # Adjusted data
                'lighting_watts_per_sf': 0.9,
                'panel_density': 15000,
                'emergency_density': 3000,  # 1 per 3000 SF
                'exit_density': 3500  # 1 per 3500 SF
            },
            SpaceType.OFFICE: {
                'base_min': 14.00,
                'base_max': 18.00,
                'typical': 16.00,  # Office electrical density
                'lighting_density': 100,  # Adjusted - 1 per 100 SF
                'receptacle_density': 125,  # 8 per 1000 SF
                'circuit_density': 800,
                'data_density': 150,  # Adjusted data drops
                'lighting_watts_per_sf': 1.5,
                'panel_density': 10000,
                'emergency_density': 1200,  # 1 per 1200 SF
                'task_lighting_factor': 0.15  # 15% additional for task lighting
            },
            SpaceType.RETAIL: {
                'base_min': 8.00,
                'base_max': 14.00,
                'typical': 11.00,
                'lighting_density': 100,  # High lighting for merchandise
                'receptacle_density': 250,
                'circuit_density': 1000,
                'data_density': 500,
                'lighting_watts_per_sf': 1.8,
                'panel_density': 12000,
                'track_lighting_adder': 2.50  # $/SF additional
            },
            SpaceType.RESTAURANT: {
                'base_min': 20.00,
                'base_max': 35.00,
                'typical': 28.00,
                'lighting_density': 80,
                'receptacle_density': 100,
                'circuit_density': 400,  # Heavy equipment needs
                'data_density': 300,
                'lighting_watts_per_sf': 2.0,
                'panel_density': 5000,
                'kitchen_equipment_adder': 8.00  # $/SF for kitchen areas
            },
            SpaceType.HEALTHCARE: {
                'base_min': 25.00,
                'base_max': 40.00,
                'typical': 32.00,
                'lighting_density': 80,
                'receptacle_density': 60,  # Very high density
                'circuit_density': 300,
                'data_density': 100,
                'lighting_watts_per_sf': 2.2,
                'panel_density': 5000,
                'emergency_power_adder': 5.00,
                'isolated_ground_adder': 3.00
            },
            SpaceType.LIGHT_INDUSTRIAL: {
                'base_min': 6.00,
                'base_max': 10.00,
                'typical': 8.00,
                'lighting_density': 600,
                'receptacle_density': 800,
                'circuit_density': 1500,
                'data_density': 2000,
                'lighting_watts_per_sf': 1.0,
                'panel_density': 12000
            }
        }
        
        # California 2025 Prevailing Wage Rates
        self.california_labor_rates = {
            'journeyman_base': 95,  # $/hour base wage
            'benefits_burden': 0.75,  # 75% burden for benefits/taxes
            'total_hourly': 166.25,  # $95 × 1.75
            'apprentice_base': 57,  # 60% of journeyman
            'foreman_base': 110,  # 115% of journeyman
            'productivity_factor': 0.85  # Urban CA productivity adjustment
        }
        
        # Regional cost multipliers
        self.regional_multipliers = {
            # California regions
            'san francisco': CostTier.TIER_1_HIGHEST,
            'san francisco bay area': CostTier.TIER_1_HIGHEST,
            'los angeles': CostTier.TIER_1_HIGHEST,
            'california': CostTier.TIER_1_HIGHEST,  # Default CA to Tier 1
            'san diego': CostTier.TIER_2_HIGH,
            'sacramento': CostTier.TIER_2_HIGH,
            
            # Other Tier 1 cities
            'new york': CostTier.TIER_1_HIGHEST,
            'new york city': CostTier.TIER_1_HIGHEST,
            'boston': CostTier.TIER_1_HIGHEST,
            'seattle': CostTier.TIER_1_HIGHEST,
            
            # Tier 2 cities
            'portland': CostTier.TIER_2_HIGH,
            'denver': CostTier.TIER_2_HIGH,
            'austin': CostTier.TIER_2_HIGH,
            'washington dc': CostTier.TIER_2_HIGH,
            
            # Tier 3 cities
            'phoenix': CostTier.TIER_3_MODERATE,
            'dallas': CostTier.TIER_3_MODERATE,
            'atlanta': CostTier.TIER_3_MODERATE,
            'chicago': CostTier.TIER_3_MODERATE,
            'houston': CostTier.TIER_3_MODERATE,
            
            # Tier 4 cities
            'kansas city': CostTier.TIER_4_LOWER,
            'memphis': CostTier.TIER_4_LOWER,
            'oklahoma city': CostTier.TIER_4_LOWER,
            'omaha': CostTier.TIER_4_LOWER
        }
        
        # Cost tier multipliers - Further reduced to hit target
        self.tier_multipliers = {
            CostTier.TIER_1_HIGHEST: 1.15,  # 15% premium
            CostTier.TIER_2_HIGH: 1.08,     # 8% premium
            CostTier.TIER_3_MODERATE: 1.00,  # Base
            CostTier.TIER_4_LOWER: 0.94     # 6% discount
        }
        
        # Service sizing thresholds and costs - 2025 California market rates
        self.service_sizing = [
            {'max_sf': 10000, 'amps': 200, 'base_cost': 25000, 'cost_range': (22000, 28000)},
            {'max_sf': 25000, 'amps': 400, 'base_cost': 45000, 'cost_range': (40000, 50000)},
            {'max_sf': 50000, 'amps': 800, 'base_cost': 65000, 'cost_range': (60000, 70000)},
            {'max_sf': 100000, 'amps': 1200, 'base_cost': 110000, 'cost_range': (100000, 125000)},
            {'max_sf': 200000, 'amps': 1600, 'base_cost': 160000, 'cost_range': (145000, 180000)},
            {'max_sf': float('inf'), 'amps': 2000, 'base_cost': 220000, 'cost_range': (200000, 250000)}
        ]
        
        # Fixture costs (installed) - Adjusted for realistic pricing
        self.fixture_costs = {
            'high_bay_led_150w': {'cost': 475, 'range': (425, 525)},
            'troffer_2x4_led': {'cost': 195, 'range': (175, 215)},
            'troffer_2x2_led': {'cost': 210, 'range': (190, 230)},
            'track_lighting_per_lf': {'cost': 85, 'range': (75, 95)},
            'decorative_pendant': {'cost': 325, 'range': (290, 360)},
            'wall_pack_led': {'cost': 425, 'range': (385, 465)},
            'pole_light_25ft': {'cost': 2800, 'range': (2500, 3100)},
            'emergency_light': {'cost': 295, 'range': (270, 320)},
            'exit_sign': {'cost': 245, 'range': (220, 270)},
            'under_cabinet_led': {'cost': 75, 'range': (65, 85)}  # per LF
        }
        
        # Power distribution costs - Adjusted for market rates
        self.distribution_costs = {
            'panel_200a': {'cost': 4500, 'range': (4000, 5000)},
            'transformer_75kva': {'cost': 7000, 'range': (6000, 8000)},
            'circuit_20a': {'cost': 1150, 'range': (1000, 1300)},
            'receptacle_standard': {'cost': 155, 'range': (140, 170)},
            'receptacle_gfci': {'cost': 205, 'range': (185, 225)},
            'receptacle_dedicated': {'cost': 355, 'range': (320, 390)},
            'data_drop_cat6': {'cost': 395, 'range': (355, 435)},
            'data_drop_cat6a': {'cost': 475, 'range': (435, 515)},
            'junction_box': {'cost': 75, 'range': (65, 85)},
            'disconnect_60a': {'cost': 550, 'range': (500, 600)}
        }
        
        # Special systems costs - Optimized for target range
        self.special_systems = {
            'generator_per_kw': {'cost': 1000, 'range': (850, 1150)},
            'ups_per_kva': {'cost': 700, 'range': (600, 800)},
            'lighting_controls_per_sf': {'cost': 0.85, 'range': (0.70, 1.00)},
            'solar_ready_per_sf': {'cost': 0.50, 'range': (0.40, 0.60)},
            'ev_charging_roughin': {'cost': 1800, 'range': (1600, 2000)},
            'ev_charging_full': {'cost': 3500, 'range': (3000, 4000)},
            'fire_alarm_per_sf': {'cost': 1.00, 'range': (0.85, 1.15)},
            'emergency_power_per_sf': {'cost': 0.50, 'range': (0.40, 0.60)},
            'arc_fault_per_sf': {'cost': 0.35, 'range': (0.30, 0.40)},
            'surge_protection': {'cost': 2200, 'range': (2000, 2400)},
            'building_automation_per_sf': {'cost': 0.60, 'range': (0.50, 0.70)}
        }
        
        # California-specific requirements
        self.california_requirements = {
            'title_24_lighting_controls': True,
            'solar_ready': True,
            'ev_charging_min_spaces': 0.10,  # 10% of parking spaces
            'demand_response': True
        }
    
    def calculate_electrical_cost(self, project_data: Dict) -> Dict[str, Any]:
        """Calculate comprehensive electrical costs with space-type awareness"""
        
        # Extract project parameters - check both root and request_data
        request_data = project_data.get('request_data', {})
        total_sf = project_data.get('square_footage', 0) or request_data.get('square_footage', 0)
        location = project_data.get('location', '') or request_data.get('location', '')
        location = location.lower() if location else ''
        building_mix = project_data.get('building_mix', {}) or request_data.get('building_mix', {})
        special_requirements = project_data.get('special_requirements', '') or request_data.get('special_requirements', '')
        quality_level = project_data.get('quality_level', 'standard') or request_data.get('quality_level', 'standard')
        
        logger.error(f"[ELECTRICAL V2] Calculating for {total_sf} SF in {location}")
        logger.error(f"[ELECTRICAL V2] Building mix: {building_mix}")
        logger.error(f"[ELECTRICAL V2] Request data keys: {list(request_data.keys())}")
        
        # Normalize building mix
        if not building_mix:
            building_mix = {'office': 1.0}
        
        # Get regional multiplier
        regional_tier = self._get_regional_tier(location)
        regional_multiplier = self.tier_multipliers[regional_tier]
        
        # Calculate space-by-space costs
        space_calculations = []
        total_base_cost = 0
        
        for space_type_str, percentage in building_mix.items():
            if percentage <= 0:
                continue
                
            space_sf = total_sf * percentage
            space_type = self._map_space_type(space_type_str)
            space_data = self.space_type_rates.get(space_type, self.space_type_rates[SpaceType.OFFICE])
            
            # Calculate base electrical cost for this space type
            base_rate = space_data['typical']
            if quality_level == 'economy':
                base_rate = space_data['base_min']
            elif quality_level == 'premium':
                base_rate = space_data['base_max']
            
            space_base_cost = space_sf * base_rate
            total_base_cost += space_base_cost
            
            # Calculate fixtures and devices
            fixtures_data = self._calculate_fixtures_for_space(space_sf, space_type, space_data)
            
            space_calculations.append({
                'type': space_type_str,
                'area': space_sf,
                'percentage': percentage * 100,
                'base_rate': base_rate,
                'base_cost': space_base_cost,
                'fixtures': fixtures_data
            })
        
        # Calculate service and distribution
        service_data = self._calculate_service_distribution(total_sf, building_mix)
        
        # Calculate special systems
        special_systems = self._calculate_special_systems(total_sf, location, special_requirements)
        
        # Apply regional multiplier
        subtotal_before_regional = total_base_cost + service_data['total'] + special_systems['total']
        regional_adjustment = subtotal_before_regional * (regional_multiplier - 1.0)
        
        # Calculate totals
        subtotal = subtotal_before_regional + regional_adjustment
        contingency_rate = 0.10  # 10% standard
        contingency = subtotal * contingency_rate
        total = subtotal + contingency
        
        # Log the calculation for debugging
        logger.error(f"[ELECTRICAL V2] Base cost: ${total_base_cost:,.2f}")
        logger.error(f"[ELECTRICAL V2] Service cost: ${service_data['total']:,.2f}")
        logger.error(f"[ELECTRICAL V2] Special systems: ${special_systems['total']:,.2f}")
        logger.error(f"[ELECTRICAL V2] Regional multiplier: {regional_multiplier}")
        logger.error(f"[ELECTRICAL V2] Total with contingency: ${total:,.2f}")
        
        # Generate detailed breakdown
        breakdown = self._generate_detailed_breakdown(
            project_data, space_calculations, service_data, special_systems,
            regional_tier, regional_multiplier, subtotal, contingency, total
        )
        
        # Perform validation
        validations = self._validate_costs(total, total_sf, building_mix)
        
        return {
            'space_calculations': space_calculations,
            'service_distribution': service_data,
            'special_systems': special_systems,
            'base_cost': total_base_cost,
            'raw_subtotal': subtotal_before_regional,  # Raw cost without regional
            'regional_tier': regional_tier.name,
            'regional_multiplier': regional_multiplier,
            'regional_adjustment': regional_adjustment,
            'subtotal': subtotal,
            'contingency_rate': contingency_rate,
            'contingency': contingency,
            'total': total,
            'cost_per_sf': total / total_sf if total_sf > 0 else 0,
            'breakdown': breakdown,
            'validations': validations,
            'calculation_date': datetime.now().isoformat()
        }
    
    def _map_space_type(self, space_type_str: str) -> SpaceType:
        """Map string space type to enum"""
        mapping = {
            'warehouse': SpaceType.WAREHOUSE,
            'office': SpaceType.OFFICE,
            'retail': SpaceType.RETAIL,
            'restaurant': SpaceType.RESTAURANT,
            'healthcare': SpaceType.HEALTHCARE,
            'light_industrial': SpaceType.LIGHT_INDUSTRIAL,
            'industrial': SpaceType.WAREHOUSE,
            'medical': SpaceType.HEALTHCARE
        }
        return mapping.get(space_type_str.lower(), SpaceType.OFFICE)
    
    def _get_regional_tier(self, location: str) -> CostTier:
        """Determine cost tier from location"""
        location_lower = location.lower()
        
        # Check exact matches first
        if location_lower in self.regional_multipliers:
            return self.regional_multipliers[location_lower]
        
        # Check partial matches
        for key, tier in self.regional_multipliers.items():
            if key in location_lower or location_lower in key:
                return tier
        
        # Default to moderate
        return CostTier.TIER_3_MODERATE
    
    def _calculate_fixtures_for_space(self, space_sf: float, space_type: SpaceType, 
                                    space_data: Dict) -> Dict[str, Any]:
        """Calculate fixtures and devices for a specific space type"""
        
        fixtures = []
        total_fixture_cost = 0
        
        # Calculate lighting fixtures
        num_fixtures = max(1, math.ceil(space_sf / space_data['lighting_density']))
        
        if space_type == SpaceType.WAREHOUSE:
            fixture_type = 'high_bay_led_150w'
            fixture_cost = self.fixture_costs[fixture_type]['cost']
            total_cost = num_fixtures * fixture_cost
            fixtures.append({
                'type': 'LED High Bay 150W',
                'quantity': num_fixtures,
                'unit_cost': fixture_cost,
                'total_cost': total_cost
            })
            total_fixture_cost += total_cost
            
        elif space_type in [SpaceType.OFFICE, SpaceType.HEALTHCARE]:
            fixture_type = 'troffer_2x4_led'
            fixture_cost = self.fixture_costs[fixture_type]['cost']
            total_cost = num_fixtures * fixture_cost
            fixtures.append({
                'type': '2x4 LED Troffer',
                'quantity': num_fixtures,
                'unit_cost': fixture_cost,
                'total_cost': total_cost
            })
            total_fixture_cost += total_cost
            
            # Add task lighting for office spaces (20% additional)
            if space_type == SpaceType.OFFICE and 'task_lighting_factor' in space_data:
                task_lf = space_sf * 0.02  # 2% of SF in linear feet
                task_cost = task_lf * self.fixture_costs.get('under_cabinet_led', {'cost': 85})['cost']
                fixtures.append({
                    'type': 'Under Cabinet/Task LED',
                    'quantity': task_lf,
                    'unit_cost': self.fixture_costs.get('under_cabinet_led', {'cost': 85})['cost'],
                    'total_cost': task_cost,
                    'unit': 'LF'
                })
                total_fixture_cost += task_cost
            
        elif space_type == SpaceType.RETAIL:
            # Mix of track and decorative
            track_lf = space_sf * 0.05  # 5% of SF in linear feet of track
            track_cost = track_lf * self.fixture_costs['track_lighting_per_lf']['cost']
            fixtures.append({
                'type': 'Track Lighting',
                'quantity': track_lf,
                'unit_cost': self.fixture_costs['track_lighting_per_lf']['cost'],
                'total_cost': track_cost,
                'unit': 'LF'
            })
            total_fixture_cost += track_cost
            
            # Some decorative fixtures
            num_decorative = max(1, math.ceil(space_sf / 500))
            decorative_cost = num_decorative * self.fixture_costs['decorative_pendant']['cost']
            fixtures.append({
                'type': 'Decorative Pendant',
                'quantity': num_decorative,
                'unit_cost': self.fixture_costs['decorative_pendant']['cost'],
                'total_cost': decorative_cost
            })
            total_fixture_cost += decorative_cost
        
        # Calculate receptacles
        num_receptacles = max(1, math.ceil(space_sf / space_data['receptacle_density']))
        receptacle_cost = num_receptacles * self.distribution_costs['receptacle_standard']['cost']
        
        # Calculate circuits
        num_circuits = max(1, math.ceil(space_sf / space_data['circuit_density']))
        circuit_cost = num_circuits * self.distribution_costs['circuit_20a']['cost']
        
        # Calculate data drops
        num_data = max(1, math.ceil(space_sf / space_data['data_density']))
        data_cost = num_data * self.distribution_costs['data_drop_cat6']['cost']
        
        return {
            'fixtures': fixtures,
            'fixture_cost': total_fixture_cost,
            'receptacles': num_receptacles,
            'receptacle_cost': receptacle_cost,
            'circuits': num_circuits,
            'circuit_cost': circuit_cost,
            'data_drops': num_data,
            'data_cost': data_cost,
            'total': total_fixture_cost + receptacle_cost + circuit_cost + data_cost
        }
    
    def _calculate_service_distribution(self, total_sf: float, building_mix: Dict) -> Dict[str, Any]:
        """Calculate service entrance and distribution equipment"""
        
        # Determine service size
        service_info = None
        for threshold in self.service_sizing:
            if total_sf <= threshold['max_sf']:
                service_info = threshold
                break
        
        if not service_info:
            service_info = self.service_sizing[-1]
        
        # Calculate number of distribution panels needed
        # Higher panel density for complex buildings
        avg_panel_density = 12000  # Average SF per panel
        if 'office' in building_mix and building_mix['office'] > 0.5:
            avg_panel_density = 10000
        elif 'healthcare' in building_mix or 'restaurant' in building_mix:
            avg_panel_density = 8000
            
        num_panels = max(2, math.ceil(total_sf / avg_panel_density))
        panel_cost = num_panels * self.distribution_costs['panel_200a']['cost']
        
        # Transformer needs (for larger buildings)
        transformer_cost = 0
        if total_sf > 25000:
            num_transformers = math.ceil(total_sf / 50000)
            transformer_cost = num_transformers * self.distribution_costs['transformer_75kva']['cost']
        
        return {
            'service_amps': service_info['amps'],
            'service_cost': service_info['base_cost'],
            'num_panels': num_panels,
            'panel_cost': panel_cost,
            'transformer_cost': transformer_cost,
            'total': service_info['base_cost'] + panel_cost + transformer_cost
        }
    
    def _calculate_special_systems(self, total_sf: float, location: str, 
                                 special_requirements: str) -> Dict[str, Any]:
        """Calculate special systems and code requirements"""
        
        systems = []
        total_cost = 0
        
        # Fire alarm system (required for all commercial)
        fire_alarm_cost = total_sf * self.special_systems['fire_alarm_per_sf']['cost']
        systems.append({
            'name': 'Fire Alarm System',
            'cost': fire_alarm_cost,
            'calculation': f"${self.special_systems['fire_alarm_per_sf']['cost']}/SF × {total_sf:,.0f} SF"
        })
        total_cost += fire_alarm_cost
        
        # California-specific requirements
        if 'california' in location.lower() or 'ca' in location.lower():
            # Title 24 lighting controls
            controls_cost = total_sf * self.special_systems['lighting_controls_per_sf']['cost']
            systems.append({
                'name': 'Title 24 Lighting Controls',
                'cost': controls_cost,
                'calculation': f"${self.special_systems['lighting_controls_per_sf']['cost']}/SF × {total_sf:,.0f} SF"
            })
            total_cost += controls_cost
            
            # Solar ready infrastructure
            solar_cost = total_sf * self.special_systems['solar_ready_per_sf']['cost']
            systems.append({
                'name': 'Solar Ready Infrastructure',
                'cost': solar_cost,
                'calculation': f"${self.special_systems['solar_ready_per_sf']['cost']}/SF × {total_sf:,.0f} SF"
            })
            total_cost += solar_cost
            
            # EV charging rough-in (estimate parking spaces)
            parking_spaces = math.ceil(total_sf / 300)  # Rough estimate
            ev_spaces = max(2, math.ceil(parking_spaces * 0.1))
            ev_cost = ev_spaces * self.special_systems['ev_charging_roughin']['cost']
            systems.append({
                'name': f'EV Charging Rough-in ({ev_spaces} spaces)',
                'cost': ev_cost,
                'calculation': f"{ev_spaces} spaces × ${self.special_systems['ev_charging_roughin']['cost']}/space"
            })
            total_cost += ev_cost
        
        # Emergency/Life Safety with enhanced requirements
        emergency_cost = total_sf * self.special_systems['emergency_power_per_sf']['cost']
        systems.append({
            'name': 'Emergency/Life Safety System',
            'cost': emergency_cost,
            'calculation': f"${self.special_systems['emergency_power_per_sf']['cost']}/SF × {total_sf:,.0f} SF"
        })
        total_cost += emergency_cost
        
        # Arc fault protection (NEC requirement)
        arc_fault_cost = total_sf * self.special_systems['arc_fault_per_sf']['cost']
        systems.append({
            'name': 'Arc Fault Circuit Protection',
            'cost': arc_fault_cost,
            'calculation': f"${self.special_systems['arc_fault_per_sf']['cost']}/SF × {total_sf:,.0f} SF"
        })
        total_cost += arc_fault_cost
        
        # Surge protection for main service
        systems.append({
            'name': 'Whole Building Surge Protection',
            'cost': self.special_systems['surge_protection']['cost'],
            'calculation': "Type 1 & 2 surge protective devices"
        })
        total_cost += self.special_systems['surge_protection']['cost']
        
        # Check for generator requirements
        if 'generator' in special_requirements.lower() or 'backup power' in special_requirements.lower():
            # Size generator at 30W/SF for critical loads
            generator_kw = math.ceil(total_sf * 30 / 1000)
            generator_cost = generator_kw * self.special_systems['generator_per_kw']['cost']
            systems.append({
                'name': f'Emergency Generator ({generator_kw}kW)',
                'cost': generator_cost,
                'calculation': f"{generator_kw}kW × ${self.special_systems['generator_per_kw']['cost']}/kW"
            })
            total_cost += generator_cost
        
        return {
            'systems': systems,
            'total': total_cost
        }
    
    def _generate_detailed_breakdown(self, project_data: Dict, space_calculations: List[Dict],
                                   service_data: Dict, special_systems: Dict,
                                   regional_tier: CostTier, regional_multiplier: float,
                                   subtotal: float, contingency: float, total: float) -> str:
        """Generate detailed cost breakdown report"""
        
        request_data = project_data.get('request_data', {})
        total_sf = request_data.get('square_footage', 0) or project_data.get('square_footage', 0)
        location = project_data.get('location', 'Not specified')
        
        breakdown = f"""ELECTRICAL COST BREAKDOWN
{'=' * 60}
Building: {total_sf:,} SF {project_data.get('project_type', 'Mixed-Use')}
Location: {location} ({regional_tier.name.replace('_', ' ').title()} - {regional_multiplier:.2f}x multiplier)

SPACE ANALYSIS:
"""
        
        for space in space_calculations:
            breakdown += f"- {space['type'].title()}: {space['area']:,.0f} SF ({space['percentage']:.0f}%) @ ${space['base_rate']:.2f}/SF base = ${space['base_cost']:,.2f}\n"
        
        breakdown += f"\nBASE SYSTEMS:"
        breakdown += f"\n- Service & Distribution ({service_data['service_amps']}A): ${service_data['service_cost']:,.2f}"
        breakdown += f"\n- Distribution Panels ({service_data['num_panels']}): ${service_data['panel_cost']:,.2f}"
        if service_data['transformer_cost'] > 0:
            breakdown += f"\n- Transformers: ${service_data['transformer_cost']:,.2f}"
        
        breakdown += f"\n\nFIXTURES & DEVICES:"
        total_fixtures_cost = 0
        for space in space_calculations:
            if space['fixtures']['fixtures']:
                breakdown += f"\n{space['type'].title()}:"
                for fixture in space['fixtures']['fixtures']:
                    unit = fixture.get('unit', 'EA')
                    breakdown += f"\n  - {fixture['type']} ({fixture['quantity']:.0f} {unit}): ${fixture['total_cost']:,.2f}"
                total_fixtures_cost += space['fixtures']['fixture_cost']
        
        breakdown += f"\n\nSPECIAL SYSTEMS:"
        for system in special_systems['systems']:
            breakdown += f"\n- {system['name']}: ${system['cost']:,.2f}"
            breakdown += f"\n  ({system['calculation']})"
        
        breakdown += f"\n\nCOST SUMMARY:"
        breakdown += f"\n- Base Systems & Labor: ${subtotal / regional_multiplier:,.2f}"
        breakdown += f"\n- Regional Adjustment ({regional_tier.name}): ${subtotal - (subtotal / regional_multiplier):,.2f}"
        breakdown += f"\n- Subtotal: ${subtotal:,.2f}"
        breakdown += f"\n- Contingency (10%): ${contingency:,.2f}"
        breakdown += f"\n\nTOTAL ELECTRICAL: ${total:,.2f}"
        if total_sf > 0:
            breakdown += f"\nCost per SF: ${total / total_sf:.2f}"
        else:
            breakdown += f"\nCost per SF: N/A (0 SF)"
        
        return breakdown
    
    def _validate_costs(self, total: float, total_sf: float, building_mix: Dict) -> List[Dict[str, str]]:
        """Validate calculated costs against expected ranges"""
        
        validations = []
        cost_per_sf = total / total_sf if total_sf > 0 else 0
        
        # Determine expected range based on building mix
        min_expected = 0
        max_expected = 0
        
        for space_type_str, percentage in building_mix.items():
            space_type = self._map_space_type(space_type_str)
            space_data = self.space_type_rates.get(space_type, self.space_type_rates[SpaceType.OFFICE])
            min_expected += space_data['base_min'] * percentage
            max_expected += space_data['base_max'] * percentage
        
        # Adjust for typical multipliers and contingency
        min_expected *= 1.1  # 10% contingency
        max_expected *= 1.5  # Regional premium + contingency
        
        if cost_per_sf < min_expected:
            validations.append({
                'type': 'warning',
                'message': f'Total cost/SF (${cost_per_sf:.2f}) is below expected range (${min_expected:.2f}-${max_expected:.2f})'
            })
        elif cost_per_sf > max_expected:
            validations.append({
                'type': 'warning',  
                'message': f'Total cost/SF (${cost_per_sf:.2f}) is above expected range (${min_expected:.2f}-${max_expected:.2f})'
            })
        else:
            validations.append({
                'type': 'success',
                'message': f'Total cost/SF (${cost_per_sf:.2f}) is within expected range (${min_expected:.2f}-${max_expected:.2f})'
            })
        
        # Check service sizing
        expected_service = None
        for threshold in self.service_sizing:
            if total_sf <= threshold['max_sf']:
                expected_service = threshold['amps']
                break
        
        if expected_service:
            validations.append({
                'type': 'info',
                'message': f'Service size ({expected_service}A) is appropriate for {total_sf:,} SF building'
            })
        
        return validations


# Create service instance
electrical_v2_service = ElectricalV2Service()