"""
Owner view calculation engine.
Handles soft costs, department allocations, and ROI calculations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .owner_metrics_config import OWNER_METRICS_CONFIG
import logging

logger = logging.getLogger(__name__)


class OwnerViewEngine:
    """
    Engine for calculating owner-specific metrics.
    Uses configuration from owner_metrics_config.py.
    """
    
    def __init__(self, building_type: str, subtype: str):
        """
        Initialize engine with specific building configuration.
        
        Args:
            building_type: Main building category (e.g., 'healthcare')
            subtype: Specific subtype (e.g., 'hospital')
        """
        self.building_type = building_type
        self.subtype = subtype
        
        # Try to load configuration
        try:
            if building_type not in OWNER_METRICS_CONFIG:
                raise KeyError(f"Building type '{building_type}' not configured")
            
            if subtype not in OWNER_METRICS_CONFIG[building_type]:
                raise KeyError(f"Subtype '{subtype}' not configured for {building_type}")
                
            self.config = OWNER_METRICS_CONFIG[building_type][subtype]
            logger.info(f"Loaded config for {building_type}/{subtype}")
            
        except KeyError as e:
            logger.warning(f"Configuration not found: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """
        Provide default configuration when specific config is missing.
        These are conservative estimates.
        """
        return {
            'soft_costs': {
                'design_engineering': 0.06,        # 6% default
                'permits_legal': 0.02,              # 2% default
                'furniture_fixtures': 0.05,         # 5% default
                'construction_contingency': 0.10,   # 10% standard
                'owner_contingency': 0.05,          # 5% standard
                'financing_costs': 0.025,           # 2.5% default
                'insurance_bonds': 0.01             # 1% default
            },
            'department_allocations': {
                'general': {
                    'percent_of_area': 1.0,
                    'trade_allocations': {
                        'structural': 1.0,
                        'mechanical': 1.0,
                        'electrical': 1.0,
                        'plumbing': 1.0,
                        'finishes': 1.0
                    },
                    'includes': ['All Areas']
                }
            },
            'roi_metrics': {}              # Will be added later
        }
    
    def calculate_soft_costs(self, construction_cost: float) -> Dict[str, Any]:
        """
        Calculate all soft costs based on construction cost.
        
        Args:
            construction_cost: Base construction cost from contractor view
            
        Returns:
            Dictionary containing:
            - Individual soft costs with amounts and percentages
            - Subtotal of all soft costs
            - Total project cost (construction + soft costs)
        """
        if construction_cost <= 0:
            raise ValueError("Construction cost must be positive")
        
        result = {
            'construction_cost': construction_cost,
            'soft_costs_breakdown': {},
            'soft_costs_subtotal': 0,
            'total_project_cost': 0,
            'soft_costs_percentage': 0
        }
        
        # Get soft costs configuration
        soft_costs_config = self.config.get('soft_costs', {})
        
        # Calculate each soft cost
        for cost_type, percentage in soft_costs_config.items():
            amount = construction_cost * percentage
            
            # Format the name for display
            display_name = cost_type.replace('_', ' ').title()
            
            result['soft_costs_breakdown'][display_name] = {
                'amount': round(amount, 2),
                'percentage': percentage * 100,
                'description': self._get_cost_description(cost_type)
            }
            
            result['soft_costs_subtotal'] += amount
        
        # Calculate totals
        result['soft_costs_subtotal'] = round(result['soft_costs_subtotal'], 2)
        result['total_project_cost'] = round(construction_cost + result['soft_costs_subtotal'], 2)
        
        # Calculate soft costs as percentage of construction
        if construction_cost > 0:
            result['soft_costs_percentage'] = round(
                (result['soft_costs_subtotal'] / construction_cost) * 100, 
                1
            )
        
        logger.info(f"Calculated soft costs for {self.building_type}/{self.subtype}: "
                   f"Construction: ${construction_cost:,.0f}, "
                   f"Soft Costs: ${result['soft_costs_subtotal']:,.0f} ({result['soft_costs_percentage']}%), "
                   f"Total: ${result['total_project_cost']:,.0f}")
        
        return result
    
    def _get_cost_description(self, cost_type: str) -> str:
        """
        Provide descriptions for each soft cost type.
        """
        descriptions = {
            'design_engineering': 'Architectural and engineering design fees',
            'permits_legal': 'Building permits and legal fees',
            'medical_equipment': 'Medical equipment and specialized systems',
            'furniture_fixtures': 'Furniture, fixtures, and equipment (FF&E)',
            'construction_contingency': 'General contractor contingency',
            'owner_contingency': 'Owner contingency reserve',
            'financing_costs': 'Construction loan interest and fees',
            'insurance_bonds': 'Insurance and performance bonds',
            'commissioning': 'Building commissioning and testing',
            'specialized_therapy_equipment': 'Specialized therapy and rehab equipment',
            'technology': 'IT and AV equipment',
            'playground_equipment': 'Playground and outdoor equipment',
            'athletic_equipment': 'Athletic and sports equipment'
        }
        return descriptions.get(cost_type, 'Project soft cost')
    
    def calculate_department_allocation(self, trade_breakdown: Dict[str, float]) -> Dict[str, Any]:
        """
        Maps trade costs to business departments (Clinical, Support, Infrastructure, etc.)
        
        Args:
            trade_breakdown: Dictionary with trade costs like:
            {
                "structural": 5000000,
                "mechanical": 7000000,
                "electrical": 3000000,
                "plumbing": 4400000,
                "finishes": 1600000
            }
        
        Returns dictionary like:
            {
                "departments": {
                    "clinical": {
                        "amount": 12600000,
                        "percentage": 0.60,
                        "trades": {
                            "mechanical": 5600000,
                            "electrical": 2400000,
                            "plumbing": 3520000,
                            "finishes": 1080000
                        }
                    },
                    "support": {
                        "amount": 4200000,
                        "percentage": 0.20,
                        "trades": {...}
                    },
                    "infrastructure": {
                        "amount": 4200000,
                        "percentage": 0.20,
                        "trades": {...}
                    }
                },
                "total_allocated": 21000000
            }
        """
        if not trade_breakdown:
            raise ValueError("Trade breakdown cannot be empty")
        
        # Get department allocations from config
        dept_config = self.config.get('department_allocations', {})
        
        if not dept_config:
            # If no department config, return all as general
            total = sum(trade_breakdown.values())
            return {
                'departments': {
                    'general': {
                        'amount': round(total, 2),
                        'percentage': 1.0,
                        'trades': {k: round(v, 2) for k, v in trade_breakdown.items()},
                        'includes': ['All Areas']
                    }
                },
                'total_allocated': round(total, 2)
            }
        
        result = {
            'departments': {},
            'total_allocated': 0
        }
        
        # Calculate total construction cost from trades
        total_construction = sum(trade_breakdown.values())
        
        # Process each department
        for dept_name, dept_data in dept_config.items():
            dept_result = {
                'amount': 0,
                'percentage': dept_data.get('percent_of_area', 0),
                'trades': {},
                'includes': dept_data.get('includes', [])
            }
            
            # Get trade allocations for this department
            trade_allocs = dept_data.get('trade_allocations', {})
            
            # Calculate each trade's contribution to this department
            for trade_name, trade_cost in trade_breakdown.items():
                # Get allocation percentage for this trade to this department
                allocation_pct = trade_allocs.get(trade_name, 0)
                
                # Calculate amount allocated to this department
                allocated_amount = trade_cost * allocation_pct
                
                dept_result['trades'][trade_name] = round(allocated_amount, 2)
                dept_result['amount'] += allocated_amount
            
            dept_result['amount'] = round(dept_result['amount'], 2)
            result['departments'][dept_name] = dept_result
            result['total_allocated'] += dept_result['amount']
        
        result['total_allocated'] = round(result['total_allocated'], 2)
        
        # Log allocation summary
        logger.info(f"Department allocation for {self.building_type}/{self.subtype}:")
        for dept_name, dept_data in result['departments'].items():
            logger.info(f"  {dept_name}: ${dept_data['amount']:,.0f} "
                       f"({dept_data['percentage']:.0%} of area)")
        
        return result
    
    def calculate_unit_metrics(self, total_project_cost: float, square_footage: float) -> Dict[str, Any]:
        """
        Calculate per-unit metrics based on building type
        
        Args:
            total_project_cost: Total project cost including soft costs
            square_footage: Total building square footage
            
        Returns:
            {
                "unit_type": "beds",  # or "units", "students", "rooms"
                "unit_count": 150,
                "cost_per_unit": 970000,
                "revenue_per_unit": 500000,  # annual
                "metrics_basis": "150 beds at 200,000 SF hospital"
            }
        """
        if square_footage <= 0:
            raise ValueError("Square footage must be positive")
        if total_project_cost <= 0:
            raise ValueError("Total project cost must be positive")
        
        # Get ROI metrics from config
        roi_config = self.config.get('roi_metrics', {})
        
        if not roi_config:
            # Default metrics if not configured
            return {
                'unit_type': 'sqft',
                'unit_count': square_footage,
                'cost_per_unit': total_project_cost / square_footage,
                'revenue_per_unit': 0,
                'metrics_basis': f'{square_footage:,.0f} SF building'
            }
        
        # Get unit type and calculation method
        unit_type = roi_config.get('unit_type', 'sqft')
        units_per_sqft = roi_config.get('units_per_sqft', 1)
        
        # Calculate unit count
        if unit_type == 'sqft':
            unit_count = square_footage
        else:
            # For beds, visits, etc. - use the ratio
            unit_count = square_footage / units_per_sqft if units_per_sqft > 0 else 0
        
        # Calculate cost per unit
        cost_per_unit = total_project_cost / unit_count if unit_count > 0 else 0
        
        # Get revenue assumptions
        if 'revenue_per_unit_day' in roi_config:
            # Daily revenue (hospitals, hotels)
            revenue_per_unit = roi_config['revenue_per_unit_day'] * 365
        elif 'revenue_per_unit_month' in roi_config:
            # Monthly revenue (offices, apartments)
            revenue_per_unit = roi_config['revenue_per_unit_month'] * 12
        else:
            revenue_per_unit = 0
        
        # Create metrics basis description
        if unit_type == 'beds':
            metrics_basis = f"{unit_count:.0f} beds at {square_footage:,.0f} SF ({units_per_sqft:.0f} SF/bed)"
        elif unit_type == 'visits':
            metrics_basis = f"{unit_count:.1f} daily visit capacity at {square_footage:,.0f} SF"
        elif unit_type == 'sqft':
            metrics_basis = f"{square_footage:,.0f} SF rentable area"
        else:
            metrics_basis = f"{unit_count:.0f} {unit_type} at {square_footage:,.0f} SF"
        
        return {
            'unit_type': unit_type,
            'unit_count': round(unit_count, 2),
            'cost_per_unit': round(cost_per_unit, 2),
            'revenue_per_unit': round(revenue_per_unit, 2),
            'metrics_basis': metrics_basis
        }
    
    def calculate_roi_metrics(self, total_project_cost: float, square_footage: float, ownership_type: str = 'for_profit') -> Dict[str, Any]:
        """Calculate ROI, payback period, and financial metrics with ownership type consideration"""
        
        try:
            # Get ROI config
            config = self.config.get('roi_metrics', {})
            
            # Get ownership type config if available
            ownership_configs = self.config.get('ownership_types', {})
            ownership_config = ownership_configs.get(ownership_type, {})
            
            # Use ownership-specific financing if available
            if ownership_config:
                financing = ownership_config.get('financing', {})
                debt_ratio = financing.get('debt_ratio', 0.65)
                debt_rate = financing.get('debt_rate', 0.068)
                philanthropy = financing.get('philanthropy_ratio', 0)
                grants = financing.get('grants_ratio', 0)
                public_funding = financing.get('public_funding_ratio', 0)
                system_funding = financing.get('system_funding_ratio', 0)
            else:
                debt_ratio = 0.65
                debt_rate = 0.068
                philanthropy = 0
                grants = 0
                public_funding = 0
                system_funding = 0
            
            # Calculate effective capital needed (after philanthropy/grants/public funding)
            effective_capital = total_project_cost * (1 - philanthropy - grants - public_funding - system_funding)
            
            # Calculate unit count based on type
            unit_type = config.get('unit_type', 'beds')
            units_per_sf = config.get('units_per_sf', 0.00075)
            
            if unit_type == 'sf':
                unit_count = square_footage
            else:
                unit_count = square_footage * units_per_sf
            
            # Calculate revenue based on type
            revenue_per_unit = config.get('revenue_per_unit', 500000)
            occupancy_rate = config.get('occupancy_rate', 0.85)
            
            if unit_type == 'visits_per_day':
                # For urgent care - visits per day model
                daily_visits = unit_count
                annual_operating_days = config.get('annual_operating_days', 365)
                annual_visits = daily_visits * annual_operating_days * occupancy_rate
                annual_revenue = annual_visits * revenue_per_unit
            else:
                # For beds, exam rooms, or SF-based
                annual_revenue = unit_count * revenue_per_unit * occupancy_rate
            
            # Calculate operating metrics
            operating_margin = config.get('operating_margin', 0.15)
            annual_net_income = annual_revenue * operating_margin
            
            # Calculate ROI and payback
            roi_percentage = (annual_net_income / total_project_cost) * 100 if total_project_cost > 0 else 0
            payback_period_years = total_project_cost / annual_net_income if annual_net_income > 0 else 999
            
            # Calculate 10-year NPV at 8% discount rate
            npv_10_year = self._calculate_simple_npv(
                total_project_cost, 
                annual_net_income, 
                years=10, 
                discount_rate=0.08
            )
            
            # Calculate break-even occupancy
            if annual_revenue > 0:
                fixed_costs = annual_revenue * (1 - operating_margin)
                break_even_revenue = fixed_costs / (1 - operating_margin)
                break_even_occupancy = (break_even_revenue / (unit_count * revenue_per_unit)) if (unit_count * revenue_per_unit) > 0 else 0
                break_even_occupancy = min(break_even_occupancy, 1.0)  # Cap at 100%
            else:
                break_even_occupancy = 0.85
            
            # Calculate DSCR (Debt Service Coverage Ratio) with appropriate debt service
            debt_amount = effective_capital * debt_ratio
            annual_debt_service = debt_amount * debt_rate
            dscr = annual_net_income / annual_debt_service if annual_debt_service > 0 else 0
            
            # Get target metrics for this ownership type
            target_metrics = ownership_config.get('target_metrics', {}) if ownership_config else {}
            
            return {
                "unit_metrics": {
                    "unit_type": unit_type,
                    "unit_count": round(unit_count, 0),
                    "cost_per_unit": total_project_cost / unit_count if unit_count > 0 else 0,
                    "revenue_per_unit": revenue_per_unit,
                    "annual_revenue": annual_revenue
                },
                "financial_metrics": {
                    "total_project_cost": total_project_cost,
                    "annual_revenue": annual_revenue,
                    "operating_margin": operating_margin,
                    "annual_net_income": annual_net_income,
                    "roi_percentage": roi_percentage,
                    "payback_period_years": payback_period_years,
                    "10_year_npv": npv_10_year,
                    "break_even_occupancy": break_even_occupancy,
                    "dscr": dscr,
                    "annual_debt_service": annual_debt_service
                },
                "assumptions": {
                    "occupancy_rate": occupancy_rate,
                    "revenue_per_unit": revenue_per_unit,
                    "operating_margin": operating_margin,
                    "discount_rate": 0.08,
                    "ltv_ratio": debt_ratio,
                    "interest_rate": debt_rate
                },
                "ownership_context": {
                    "type": ownership_type,
                    "label": ownership_config.get('label', 'For-Profit') if ownership_config else 'For-Profit',
                    "effective_capital": effective_capital,
                    "philanthropy_amount": total_project_cost * philanthropy,
                    "grants_amount": total_project_cost * grants,
                    "public_funding_amount": total_project_cost * public_funding,
                    "system_funding_amount": total_project_cost * system_funding,
                    "debt_rate_used": debt_rate,
                    "target_metrics": target_metrics
                },
                "investment_status": self._determine_investment_status(
                    roi_percentage, 
                    dscr, 
                    payback_period_years,
                    target_metrics
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating ROI metrics: {str(e)}")
            return self._get_default_roi_metrics(total_project_cost, square_footage)
    
    def _determine_investment_status(self, roi: float, dscr: float, payback_years: float, target_metrics: dict = None) -> dict:
        """Determine if investment meets criteria"""
        
        # Use ownership-specific targets if available, otherwise defaults
        if target_metrics:
            roi_target = target_metrics.get('roi_target', 8.0)
            dscr_target = target_metrics.get('dscr_target', 1.25)
            margin_target = target_metrics.get('operating_margin_target', 0.20)
        else:
            roi_target = 8.0
            dscr_target = 1.25
            margin_target = 0.20
        
        # Define thresholds
        status = {
            'overall': 'red',  # Default to red
            'roi_status': 'red',
            'dscr_status': 'red',
            'payback_status': 'red',
            'recommendation': ''
        }
        
        # Check ROI (using ownership-specific target)
        if roi >= roi_target:
            status['roi_status'] = 'green'
        elif roi >= roi_target * 0.75:
            status['roi_status'] = 'yellow'
        else:
            status['roi_status'] = 'red'
        
        # Check DSCR (using ownership-specific target)
        if dscr >= dscr_target:
            status['dscr_status'] = 'green'
        elif dscr >= dscr_target * 0.88:
            status['dscr_status'] = 'yellow'
        else:
            status['dscr_status'] = 'red'
        
        # Check Payback (Target: <20 years)
        if payback_years <= 20:
            status['payback_status'] = 'green'
        elif payback_years <= 25:
            status['payback_status'] = 'yellow'
        else:
            status['payback_status'] = 'red'
        
        # Determine overall status
        green_count = sum(1 for s in [status['roi_status'], status['dscr_status'], status['payback_status']] if s == 'green')
        red_count = sum(1 for s in [status['roi_status'], status['dscr_status'], status['payback_status']] if s == 'red')
        
        if green_count == 3:
            status['overall'] = 'green'
            status['recommendation'] = 'Project meets all investment criteria. Proceed with financing.'
        elif red_count >= 2:
            status['overall'] = 'red'
            status['recommendation'] = 'Project does not meet investment criteria. Consider value engineering or operational improvements.'
        else:
            status['overall'] = 'yellow'
            status['recommendation'] = 'Project is marginal. Review assumptions and consider optimization strategies.'
        
        return status
    
    def _get_default_roi_metrics(self, total_project_cost: float, square_footage: float) -> dict:
        """Return default ROI metrics if calculation fails"""
        return {
            "unit_metrics": {
                "unit_type": "beds",
                "unit_count": 150,
                "cost_per_unit": total_project_cost / 150,
                "revenue_per_unit": 650000,
                "annual_revenue": 82875000
            },
            "financial_metrics": {
                "total_project_cost": total_project_cost,
                "annual_revenue": 82875000,
                "operating_margin": 0.20,
                "annual_net_income": 16575000,
                "roi_percentage": (16575000 / total_project_cost * 100) if total_project_cost > 0 else 0,
                "payback_period_years": total_project_cost / 16575000 if total_project_cost > 0 else 999,
                "10_year_npv": -total_project_cost / 2,
                "break_even_occupancy": 0.85,
                "dscr": 0.8,
                "annual_debt_service": 19584000
            },
            "assumptions": {
                "occupancy_rate": 0.85,
                "revenue_per_unit": 650000,
                "operating_margin": 0.20,
                "discount_rate": 0.08,
                "ltv_ratio": 0.65,
                "interest_rate": 0.068
            },
            "investment_status": {
                'overall': 'yellow',
                'roi_status': 'yellow',
                'dscr_status': 'red',
                'payback_status': 'yellow',
                'recommendation': 'Unable to calculate precise metrics. Review inputs and assumptions.'
            }
        }
    
    def _calculate_simple_npv(self, initial_investment: float, annual_cash_flow: float, 
                             years: int = 10, discount_rate: float = 0.08) -> float:
        """
        Helper to calculate Net Present Value
        
        Args:
            initial_investment: Initial investment amount (positive value)
            annual_cash_flow: Annual cash flow
            years: Number of years to calculate
            discount_rate: Discount rate (e.g., 0.08 for 8%)
            
        Returns:
            Net present value
        """
        npv = -initial_investment
        for year in range(1, years + 1):
            npv += annual_cash_flow / ((1 + discount_rate) ** year)
        return npv


class OwnerViewOrchestrator:
    """Orchestrates all owner view calculations and returns complete data structure"""
    
    def __init__(self, building_type: str, subtype: str):
        self.building_type = building_type
        self.subtype = subtype
        self.engine = OwnerViewEngine(building_type, subtype)
    
    def get_complete_owner_view(self, construction_cost: float, square_footage: float, 
                                trade_breakdown: Dict[str, float] = None,
                                ownership_type: str = 'for_profit') -> Dict[str, Any]:
        """
        Generate complete owner view data
        
        Args:
            construction_cost: Hard construction costs
            square_footage: Total building square footage
            trade_breakdown: Optional trade cost breakdown for department allocation
                           If not provided, will use default percentages
            ownership_type: Type of ownership (for_profit, non_profit, government, etc.)
        
        Returns complete owner view data structure for UI
        """
        
        # 1. Calculate soft costs
        soft_costs = self.engine.calculate_soft_costs(construction_cost)
        total_project_cost = soft_costs['total_project_cost']
        
        # 2. Get trade breakdown if not provided
        if not trade_breakdown:
            # Use default trade percentages for building type
            trade_breakdown = self._get_default_trade_breakdown(construction_cost)
        
        # 3. Calculate department allocation
        department_allocation = self.engine.calculate_department_allocation(trade_breakdown)
        
        # 4. Calculate ROI metrics with ownership type
        roi_metrics = self.engine.calculate_roi_metrics(total_project_cost, square_footage, ownership_type)
        
        # 5. Combine into complete view
        return {
            "project_summary": {
                "building_type": self.building_type,
                "subtype": self.subtype,
                "square_footage": square_footage,
                "construction_cost": construction_cost,
                "cost_per_sqft": round(construction_cost / square_footage, 2) if square_footage > 0 else 0,
                "total_project_cost": total_project_cost,
                "total_cost_per_sqft": round(total_project_cost / square_footage, 2) if square_footage > 0 else 0
            },
            "soft_costs": soft_costs,
            "department_allocation": department_allocation,
            "roi_analysis": roi_metrics,
            "trade_breakdown": {k: round(v, 2) for k, v in trade_breakdown.items()},
            "view_type": "owner",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_default_trade_breakdown(self, construction_cost: float) -> Dict[str, float]:
        """Generate default trade breakdown based on building type"""
        
        # Healthcare default percentages
        if self.building_type == "healthcare":
            if self.subtype == "hospital":
                percentages = {
                    "structural": 0.14,
                    "mechanical": 0.38,  # High for hospitals
                    "electrical": 0.22,
                    "plumbing": 0.15,   # Includes medical gas
                    "finishes": 0.11
                }
            elif self.subtype == "medical_office":
                percentages = {
                    "structural": 0.20,
                    "mechanical": 0.30,
                    "electrical": 0.20,
                    "plumbing": 0.12,
                    "finishes": 0.18
                }
            else:
                # Generic healthcare
                percentages = {
                    "structural": 0.18,
                    "mechanical": 0.35,
                    "electrical": 0.20,
                    "plumbing": 0.15,
                    "finishes": 0.12
                }
        else:
            # Generic default
            percentages = {
                "structural": 0.30,
                "mechanical": 0.25,
                "electrical": 0.15,
                "plumbing": 0.15,
                "finishes": 0.15
            }
        
        return {
            trade: construction_cost * pct 
            for trade, pct in percentages.items()
        }


# Temporary test function - remove after testing
def test_soft_costs():
    """
    Test the soft costs calculation with sample data.
    """
    print("\n" + "="*50)
    print("Testing Owner View Engine - Soft Costs")
    print("="*50)
    
    # Test cases
    test_cases = [
        ('healthcare', 'hospital', 100_000_000),
        ('healthcare', 'medical_office', 10_000_000),
        ('healthcare', 'urgent_care', 5_000_000),
        ('invalid', 'invalid', 1_000_000),  # Test default config
    ]
    
    for building_type, subtype, construction_cost in test_cases:
        print(f"\nTest: {building_type}/{subtype} - Construction: ${construction_cost:,.0f}")
        print("-" * 40)
        
        try:
            engine = OwnerViewEngine(building_type, subtype)
            result = engine.calculate_soft_costs(construction_cost)
            
            print(f"Soft Costs Breakdown:")
            for cost_type, details in result['soft_costs_breakdown'].items():
                print(f"  {cost_type}: ${details['amount']:,.0f} ({details['percentage']:.1f}%)")
            
            print(f"\nSummary:")
            print(f"  Construction Cost: ${result['construction_cost']:,.0f}")
            print(f"  Soft Costs Total: ${result['soft_costs_subtotal']:,.0f} "
                  f"({result['soft_costs_percentage']:.1f}% of construction)")
            print(f"  Total Project Cost: ${result['total_project_cost']:,.0f}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "="*50)
    print("Testing Complete")
    print("="*50)


def test_department_allocation():
    """
    Test the department allocation calculation with sample data.
    """
    print("\n" + "="*50)
    print("Testing Owner View Engine - Department Allocation")
    print("="*50)
    
    # Test hospital allocation
    engine = OwnerViewEngine("healthcare", "hospital")
    
    # Sample trade breakdown (realistic percentages for hospital)
    trade_breakdown = {
        "structural": 25_000_000,  # 25% of construction
        "mechanical": 35_000_000,  # 35% - high for hospitals
        "electrical": 15_000_000,  # 15%
        "plumbing": 20_000_000,   # 20% - includes medical gas
        "finishes": 5_000_000     # 5% - lower for hospitals
    }
    
    result = engine.calculate_department_allocation(trade_breakdown)
    
    print("\nDepartment Allocation for Hospital:")
    print("=" * 50)
    total_construction = sum(trade_breakdown.values())
    print(f"Total Construction Cost: ${total_construction:,.0f}")
    print("\nTrade Breakdown Input:")
    for trade, amount in trade_breakdown.items():
        pct = (amount / total_construction) * 100
        print(f"  {trade.title()}: ${amount:,.0f} ({pct:.0f}%)")
    
    print("\nDepartment Allocations:")
    for dept, data in result["departments"].items():
        print(f"\n{dept.title()} Department:")
        print(f"  Area Coverage: {data['percentage']:.0%}")
        print(f"  Total Cost: ${data['amount']:,.0f}")
        if data['amount'] > 0:
            dept_pct = (data['amount'] / total_construction) * 100
            print(f"  Percentage of Total: {dept_pct:.1f}%")
        print(f"  Includes: {', '.join(data['includes'])}")
        print(f"  Trade Breakdown:")
        for trade, amount in data['trades'].items():
            if amount > 0:
                print(f"    {trade.title()}: ${amount:,.0f}")
    
    print(f"\nTotal Allocated: ${result['total_allocated']:,.0f}")
    
    # Verify allocation adds up
    allocation_pct = (result['total_allocated'] / total_construction) * 100
    print(f"Allocation Coverage: {allocation_pct:.1f}%")
    
    # Test other healthcare subtypes
    print("\n" + "-"*50)
    print("Testing Other Healthcare Subtypes:")
    print("-"*50)
    
    subtypes = ['medical_office', 'urgent_care', 'rehabilitation_center']
    for subtype in subtypes:
        engine = OwnerViewEngine("healthcare", subtype)
        result = engine.calculate_department_allocation(trade_breakdown)
        
        print(f"\n{subtype.replace('_', ' ').title()}:")
        for dept, data in result["departments"].items():
            print(f"  {dept.title()}: ${data['amount']:,.0f} ({data['percentage']:.0%} of area)")
    
    # Test with missing config (should use default)
    print("\n" + "-"*50)
    print("Testing Default Config (invalid building type):")
    print("-"*50)
    
    engine = OwnerViewEngine("invalid", "invalid")
    result = engine.calculate_department_allocation(trade_breakdown)
    
    for dept, data in result["departments"].items():
        print(f"  {dept.title()}: ${data['amount']:,.0f} ({data['percentage']:.0%} of area)")


def test_roi_calculations():
    """
    Test the ROI calculation methods with sample data.
    """
    print("\n" + "="*50)
    print("Testing Owner View Engine - ROI Calculations")
    print("="*50)
    
    # Test hospital ROI
    construction_cost = 100_000_000
    engine = OwnerViewEngine("healthcare", "hospital")
    
    # Get soft costs for total project cost
    soft_costs = engine.calculate_soft_costs(construction_cost)
    total_project_cost = soft_costs['total_project_cost']
    
    # Calculate ROI
    roi_metrics = engine.calculate_roi_metrics(total_project_cost, 200_000)  # 200k SF
    
    print(f"\nHospital ROI Analysis:")
    print(f"  Building: 200,000 SF Hospital")
    print(f"  Construction Cost: ${construction_cost:,.0f}")
    print(f"  Total Project Cost: ${total_project_cost:,.0f}")
    print(f"\nUnit Metrics:")
    print(f"  Unit Type: {roi_metrics['unit_metrics']['unit_type']}")
    print(f"  Unit Count: {roi_metrics['unit_metrics']['unit_count']:.0f}")
    print(f"  Cost per {roi_metrics['unit_metrics']['unit_type']}: ${roi_metrics['unit_metrics']['cost_per_unit']:,.0f}")
    print(f"  Metrics Basis: {roi_metrics['unit_metrics']['metrics_basis']}")
    print(f"\nFinancial Metrics:")
    print(f"  Annual Revenue: ${roi_metrics['financial_metrics']['annual_revenue']:,.0f}")
    print(f"  Operating Margin: {roi_metrics['financial_metrics']['operating_margin']:.1%}")
    print(f"  Annual Net Income: ${roi_metrics['financial_metrics']['annual_net_income']:,.0f}")
    print(f"  ROI: {roi_metrics['financial_metrics']['roi_percentage']:.1f}%")
    if roi_metrics['financial_metrics']['payback_period_years']:
        print(f"  Payback Period: {roi_metrics['financial_metrics']['payback_period_years']:.1f} years")
    print(f"  10-Year NPV @ {roi_metrics['assumptions']['discount_rate']:.0%}: ${roi_metrics['financial_metrics']['10_year_npv']:,.0f}")
    print(f"  Break-Even Occupancy: {roi_metrics['financial_metrics']['break_even_occupancy']:.1%}")
    print(f"\nAssumptions:")
    print(f"  Occupancy Rate: {roi_metrics['assumptions']['occupancy_rate']:.0%}")
    print(f"  Revenue per Unit: ${roi_metrics['assumptions']['revenue_per_unit']:,.0f}/year")
    
    # Test medical office
    print("\n" + "-"*50)
    construction_cost = 10_000_000
    engine = OwnerViewEngine("healthcare", "medical_office")
    soft_costs = engine.calculate_soft_costs(construction_cost)
    total_project_cost = soft_costs['total_project_cost']
    
    roi_metrics = engine.calculate_roi_metrics(total_project_cost, 25_000)  # 25k SF
    
    print(f"\nMedical Office ROI Analysis:")
    print(f"  Building: 25,000 SF Medical Office")
    print(f"  Construction Cost: ${construction_cost:,.0f}")
    print(f"  Total Project Cost: ${total_project_cost:,.0f}")
    print(f"\nUnit Metrics:")
    print(f"  Unit Type: {roi_metrics['unit_metrics']['unit_type']}")
    print(f"  Metrics Basis: {roi_metrics['unit_metrics']['metrics_basis']}")
    print(f"\nFinancial Metrics:")
    print(f"  Annual Revenue: ${roi_metrics['financial_metrics']['annual_revenue']:,.0f}")
    print(f"  Annual Net Income: ${roi_metrics['financial_metrics']['annual_net_income']:,.0f}")
    print(f"  ROI: {roi_metrics['financial_metrics']['roi_percentage']:.1f}%")
    if roi_metrics['financial_metrics']['payback_period_years']:
        print(f"  Payback Period: {roi_metrics['financial_metrics']['payback_period_years']:.1f} years")
    print(f"  10-Year NPV @ {roi_metrics['assumptions']['discount_rate']:.0%}: ${roi_metrics['financial_metrics']['10_year_npv']:,.0f}")
    
    # Test urgent care
    print("\n" + "-"*50)
    construction_cost = 5_000_000
    engine = OwnerViewEngine("healthcare", "urgent_care")
    soft_costs = engine.calculate_soft_costs(construction_cost)
    total_project_cost = soft_costs['total_project_cost']
    
    roi_metrics = engine.calculate_roi_metrics(total_project_cost, 8_000)  # 8k SF
    
    print(f"\nUrgent Care ROI Analysis:")
    print(f"  Building: 8,000 SF Urgent Care")
    print(f"  Total Project Cost: ${total_project_cost:,.0f}")
    print(f"  Unit Type: {roi_metrics['unit_metrics']['unit_type']} ({roi_metrics['unit_metrics']['unit_count']:.1f})")
    print(f"  ROI: {roi_metrics['financial_metrics']['roi_percentage']:.1f}%")
    if roi_metrics['financial_metrics']['payback_period_years']:
        print(f"  Payback Period: {roi_metrics['financial_metrics']['payback_period_years']:.1f} years")
    
    print("\n" + "="*50)
    print("ROI Testing Complete")
    print("="*50)


def test_orchestrator():
    """
    Test the OwnerViewOrchestrator that combines all calculations
    """
    print("\n" + "="*50)
    print("Testing Owner View Orchestrator")
    print("="*50)
    
    orchestrator = OwnerViewOrchestrator("healthcare", "hospital")
    
    # Get complete owner view
    owner_view = orchestrator.get_complete_owner_view(
        construction_cost=100_000_000,
        square_footage=200_000
    )
    
    print("\nComplete Owner View Structure:")
    print(f"  Project Summary:")
    print(f"    Building: {owner_view['project_summary']['subtype']}")
    print(f"    Square Footage: {owner_view['project_summary']['square_footage']:,.0f} SF")
    print(f"    Construction Cost: ${owner_view['project_summary']['construction_cost']:,.0f}")
    print(f"    Construction $/SF: ${owner_view['project_summary']['cost_per_sqft']:,.2f}")
    print(f"    Total Project Cost: ${owner_view['project_summary']['total_project_cost']:,.0f}")
    print(f"    Total $/SF: ${owner_view['project_summary']['total_cost_per_sqft']:,.2f}")
    
    print(f"\n  Soft Costs:")
    print(f"    Total Soft Costs: ${owner_view['soft_costs']['soft_costs_subtotal']:,.0f}")
    print(f"    Soft Cost %: {owner_view['soft_costs']['soft_costs_percentage']:.1f}%")
    
    print(f"\n  Department Allocation:")
    print(f"    Number of Departments: {len(owner_view['department_allocation']['departments'])}")
    for dept_name, dept_data in owner_view['department_allocation']['departments'].items():
        print(f"    {dept_name.title()}: ${dept_data['amount']:,.0f} ({dept_data['percentage']:.0%} area)")
    
    print(f"\n  ROI Analysis:")
    print(f"    Unit Type: {owner_view['roi_analysis']['unit_metrics']['unit_type']}")
    print(f"    Unit Count: {owner_view['roi_analysis']['unit_metrics']['unit_count']:.0f}")
    print(f"    Annual Revenue: ${owner_view['roi_analysis']['financial_metrics']['annual_revenue']:,.0f}")
    print(f"    ROI: {owner_view['roi_analysis']['financial_metrics']['roi_percentage']:.1f}%")
    if owner_view['roi_analysis']['financial_metrics']['payback_period_years']:
        print(f"    Payback Period: {owner_view['roi_analysis']['financial_metrics']['payback_period_years']:.1f} years")
    
    print(f"\n  Trade Breakdown (Default):")
    for trade, amount in owner_view['trade_breakdown'].items():
        print(f"    {trade.title()}: ${amount:,.0f}")
    
    print(f"\n  Metadata:")
    print(f"    View Type: {owner_view['view_type']}")
    print(f"    Timestamp: {owner_view['timestamp'][:19]}")
    
    # Test with custom trade breakdown
    print("\n" + "-"*50)
    print("Testing with Custom Trade Breakdown:")
    print("-"*50)
    
    custom_trades = {
        "structural": 20_000_000,
        "mechanical": 40_000_000,
        "electrical": 20_000_000,
        "plumbing": 15_000_000,
        "finishes": 5_000_000
    }
    
    owner_view_custom = orchestrator.get_complete_owner_view(
        construction_cost=100_000_000,
        square_footage=200_000,
        trade_breakdown=custom_trades
    )
    
    print(f"\n  Custom Trade Breakdown:")
    for trade, amount in custom_trades.items():
        print(f"    {trade.title()}: ${amount:,.0f}")
    
    print(f"\n  Department Allocation with Custom Trades:")
    for dept_name, dept_data in owner_view_custom['department_allocation']['departments'].items():
        print(f"    {dept_name.title()}: ${dept_data['amount']:,.0f}")
    
    print("\n✅ Orchestrator working - returns complete owner view data")
    print("="*50)


if __name__ == "__main__":
    # Run test when file is executed directly
    test_soft_costs()
    test_department_allocation()
    test_roi_calculations()
    test_orchestrator()