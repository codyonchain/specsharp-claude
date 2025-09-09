"""
The single engine that handles ALL calculations.
This replaces: engine.py, clean_engine_v2.py, cost_engine.py, 
clean_scope_engine.py, owner_view_engine.py, engine_selector.py
"""

from app.v2.config.master_config import (
    MASTER_CONFIG, 
    BuildingType, 
    ProjectClass,
    OwnershipType,
    PROJECT_CLASS_MULTIPLIERS,
    get_building_config,
    get_regional_multiplier,
    validate_project_class
)
# from app.v2.services.financial_analyzer import FinancialAnalyzer  # TODO: Implement this
from typing import Optional, Dict, Any, List
from dataclasses import asdict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UnifiedEngine:
    """
    One engine to rule them all.
    Single source of truth for all cost calculations.
    """
    
    def __init__(self):
        """Initialize the unified engine"""
        self.config = MASTER_CONFIG
        self.calculation_trace = []  # Track every calculation for debugging
        # self.financial_analyzer = FinancialAnalyzer()  # TODO: Add financial analyzer
        
    def calculate_project(self, 
                         building_type: BuildingType,
                         subtype: str,
                         square_footage: float,
                         location: str,
                         project_class: ProjectClass = ProjectClass.GROUND_UP,
                         floors: int = 1,
                         ownership_type: OwnershipType = OwnershipType.FOR_PROFIT,
                         special_features: List[str] = None) -> Dict[str, Any]:
        """
        The master calculation method.
        Everything goes through here.
        
        Args:
            building_type: Type from BuildingType enum
            subtype: Specific subtype (e.g., 'hospital', 'class_a')
            square_footage: Total square footage
            location: City/location for regional multiplier
            project_class: Ground-up, renovation, etc.
            floors: Number of floors
            ownership_type: For-profit, non-profit, etc.
            special_features: List of special features to add
            
        Returns:
            Comprehensive cost breakdown dictionary
        """
        
        # Clear trace for new calculation
        self.calculation_trace = []
        self._log_trace("Starting calculation", {
            'building_type': building_type.value,
            'subtype': subtype,
            'square_footage': square_footage,
            'location': location
        })
        
        # Get configuration
        building_config = get_building_config(building_type, subtype)
        if not building_config:
            raise ValueError(f"No configuration found for {building_type.value}/{subtype}")
        
        # Validate and adjust project class if incompatible
        original_class = project_class
        project_class = validate_project_class(building_type, subtype, project_class)
        if project_class != original_class:
            self._log_trace("Project class adjusted", {
                'original': original_class.value,
                'adjusted': project_class.value,
                'reason': 'Incompatible with building type'
            })
        
        # Base construction cost calculation
        base_cost_per_sf = building_config.base_cost_per_sf
        self._log_trace("Base cost retrieved", {'base_cost_per_sf': base_cost_per_sf})
        
        # Apply project class multiplier
        class_multiplier = PROJECT_CLASS_MULTIPLIERS[project_class]
        adjusted_cost_per_sf = base_cost_per_sf * class_multiplier
        self._log_trace("Project class multiplier applied", {
            'multiplier': class_multiplier,
            'adjusted_cost_per_sf': adjusted_cost_per_sf
        })
        
        # Apply regional multiplier
        regional_multiplier = get_regional_multiplier(building_type, subtype, location)
        final_cost_per_sf = adjusted_cost_per_sf * regional_multiplier
        self._log_trace("Regional multiplier applied", {
            'location': location,
            'multiplier': regional_multiplier,
            'final_cost_per_sf': final_cost_per_sf
        })
        
        # Calculate base construction cost
        construction_cost = final_cost_per_sf * square_footage
        
        # Calculate equipment cost
        equipment_cost = building_config.equipment_cost_per_sf * square_footage
        
        # Add special features if any
        special_features_cost = 0
        if special_features and building_config.special_features:
            for feature in special_features:
                if feature in building_config.special_features:
                    feature_cost = building_config.special_features[feature] * square_footage
                    special_features_cost += feature_cost
                    self._log_trace(f"Special feature added: {feature}", {
                        'cost_per_sf': building_config.special_features[feature],
                        'total_cost': feature_cost
                    })
        
        # Calculate trade breakdown
        trades = self._calculate_trades(construction_cost, building_config.trades)
        
        # Calculate soft costs
        soft_costs = self._calculate_soft_costs(construction_cost, building_config.soft_costs)
        
        # For healthcare facilities, equipment is a soft cost (medical equipment)
        # For other building types, it's part of hard costs
        if building_type == BuildingType.HEALTHCARE:
            soft_costs['medical_equipment'] = equipment_cost
            total_hard_costs = construction_cost + special_features_cost
            total_soft_costs = sum(soft_costs.values())
        else:
            total_hard_costs = construction_cost + equipment_cost + special_features_cost
            total_soft_costs = sum(soft_costs.values())
        
        total_project_cost = total_hard_costs + total_soft_costs
        
        # Validate restaurant costs are within reasonable ranges
        if building_type == BuildingType.RESTAURANT:
            cost_per_sf = total_project_cost / square_footage
            min_cost = 250  # Minimum reasonable restaurant cost
            max_cost = 700  # Maximum reasonable restaurant cost (except fine dining)
            
            if cost_per_sf < min_cost:
                self._log_trace(f"Restaurant cost too low: ${cost_per_sf:.0f}/SF, adjusting to minimum", {
                    'original_cost_per_sf': cost_per_sf,
                    'minimum': min_cost
                })
                # Adjust costs proportionally
                adjustment_factor = (min_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = min_cost * square_footage
            elif cost_per_sf > max_cost and subtype != 'fine_dining':
                self._log_trace(f"Restaurant cost too high: ${cost_per_sf:.0f}/SF, capping at maximum", {
                    'original_cost_per_sf': cost_per_sf,
                    'maximum': max_cost
                })
                # Cap costs proportionally
                adjustment_factor = (max_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = max_cost * square_footage
        
        # Calculate ownership/financing analysis with enhanced financial metrics
        ownership_analysis = None
        if ownership_type in building_config.ownership_types:
            # Get basic ownership metrics
            ownership_analysis = self._calculate_ownership(
                total_project_cost,
                building_config.ownership_types[ownership_type]
            )
            
            # Calculate comprehensive revenue analysis using master_config
            revenue_data = self.calculate_ownership_analysis({
                'building_type': building_type.value,
                'subtype': subtype,
                'square_footage': square_footage,
                'total_cost': total_project_cost,
                'subtotal': construction_cost,  # Construction cost before contingency
                'regional_multiplier': regional_multiplier
            })
            
            # Merge revenue analysis into ownership analysis
            if revenue_data and 'revenue_analysis' in revenue_data:
                ownership_analysis['revenue_analysis'] = revenue_data['revenue_analysis']
                ownership_analysis['return_metrics'].update(revenue_data['return_metrics'])
                ownership_analysis['roi_analysis'] = {
                    'financial_metrics': {
                        'annual_revenue': revenue_data['revenue_analysis']['annual_revenue'],
                        'operating_margin': revenue_data['revenue_analysis']['operating_margin'],
                        'net_income': revenue_data['revenue_analysis']['net_income']
                    }
                }
                # Add the new metrics from our enhanced analysis
                ownership_analysis['revenue_requirements'] = revenue_data.get('revenue_requirements', {})
                ownership_analysis['operational_efficiency'] = revenue_data.get('operational_efficiency', {})
                ownership_analysis['operational_metrics'] = revenue_data.get('operational_metrics', {})
        
        # Build comprehensive response - FLATTENED structure to match frontend expectations
        result = {
            'project_info': {
                'building_type': building_type.value,
                'subtype': subtype,
                'display_name': building_config.display_name,
                'project_class': project_class.value,
                'square_footage': square_footage,
                'location': location,
                'floors': floors,
                'typical_floors': building_config.typical_floors
            },
            # Flatten calculations to top level to match frontend CalculationResult interface
            'construction_costs': {
                'base_cost_per_sf': base_cost_per_sf,
                'class_multiplier': class_multiplier,
                'regional_multiplier': regional_multiplier,
                'final_cost_per_sf': final_cost_per_sf,
                'construction_total': construction_cost,
                'equipment_total': equipment_cost,
                'special_features_total': special_features_cost
            },
            'trade_breakdown': trades,
            'soft_costs': soft_costs,
            'totals': {
                'hard_costs': total_hard_costs,
                'soft_costs': total_soft_costs,
                'total_project_cost': total_project_cost,
                'cost_per_sf': total_project_cost / square_footage if square_footage > 0 else 0
            },
            'ownership_analysis': ownership_analysis,
            # Add revenue_analysis at top level for easy access
            'revenue_analysis': ownership_analysis.get('revenue_analysis', {}) if ownership_analysis else {},
            # Add revenue_requirements at top level for easy access
            'revenue_requirements': ownership_analysis.get('revenue_requirements', {}) if ownership_analysis else {},
            # Add roi_analysis at top level for frontend compatibility
            'roi_analysis': ownership_analysis.get('roi_analysis', {}) if ownership_analysis else {},
            # Add operational efficiency at top level
            'operational_efficiency': ownership_analysis.get('operational_efficiency', {}) if ownership_analysis else {},
            # Add department and operational metrics at top level for easy frontend access
            'department_allocation': ownership_analysis.get('department_allocation', []) if ownership_analysis else [],
            'operational_metrics': ownership_analysis.get('operational_metrics', {}) if ownership_analysis else {},
            'calculation_trace': self.calculation_trace,
            'timestamp': datetime.now().isoformat()
        }
        
        self._log_trace("Calculation complete", {
            'total_project_cost': total_project_cost,
            'cost_per_sf': total_project_cost / square_footage
        })
        
        return result
    
    def _calculate_trades(self, construction_cost: float, trades_config: Any) -> Dict[str, float]:
        """Calculate trade breakdown costs"""
        trades = {}
        trades_dict = asdict(trades_config)
        
        for trade, percentage in trades_dict.items():
            trades[trade] = construction_cost * percentage
            
        self._log_trace("Trade breakdown calculated", {
            'total': construction_cost,
            'trades': len(trades)
        })
        
        return trades
    
    def _calculate_soft_costs(self, construction_cost: float, soft_costs_config: Any) -> Dict[str, float]:
        """Calculate soft costs"""
        soft_costs = {}
        soft_costs_dict = asdict(soft_costs_config)
        
        for cost_type, rate in soft_costs_dict.items():
            soft_costs[cost_type] = construction_cost * rate
            
        self._log_trace("Soft costs calculated", {
            'base': construction_cost,
            'total_soft': sum(soft_costs.values())
        })
        
        return soft_costs
    
    def _calculate_ownership(self, total_cost: float, financing_terms: Any) -> Dict[str, Any]:
        """Calculate ownership/financing metrics"""
        
        # Calculate debt and equity
        debt_amount = total_cost * financing_terms.debt_ratio
        equity_amount = total_cost * financing_terms.equity_ratio
        philanthropy_amount = total_cost * financing_terms.philanthropy_ratio
        grants_amount = total_cost * financing_terms.grants_ratio
        
        # Calculate debt service
        annual_debt_service = debt_amount * financing_terms.debt_rate
        monthly_debt_service = annual_debt_service / 12
        
        # Calculate DSCR (simplified - would need NOI in real implementation)
        # For now, estimate NOI as 8% of project cost
        estimated_annual_noi = total_cost * 0.08
        dscr = estimated_annual_noi / annual_debt_service if annual_debt_service > 0 else 0
        
        result = {
            'financing_sources': {
                'debt_amount': debt_amount,
                'equity_amount': equity_amount,
                'philanthropy_amount': philanthropy_amount,
                'grants_amount': grants_amount,
                'total_sources': debt_amount + equity_amount + philanthropy_amount + grants_amount
            },
            'debt_metrics': {
                'debt_rate': financing_terms.debt_rate,
                'annual_debt_service': annual_debt_service,
                'monthly_debt_service': monthly_debt_service,
                'target_dscr': financing_terms.target_dscr,
                'calculated_dscr': dscr,
                'dscr_meets_target': dscr >= financing_terms.target_dscr
            },
            'return_metrics': {
                'target_roi': financing_terms.target_roi,
                'estimated_annual_noi': estimated_annual_noi,
                'cash_on_cash_return': (estimated_annual_noi - annual_debt_service) / equity_amount if equity_amount > 0 else 0
            }
        }
        
        self._log_trace("Ownership analysis calculated", {
            'total_project_cost': total_cost,
            'debt_ratio': financing_terms.debt_ratio,
            'dscr': dscr
        })
        
        return result
    
    def _log_trace(self, step: str, data: Dict[str, Any]):
        """Log calculation steps for debugging and transparency"""
        trace_entry = {
            'step': step,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.calculation_trace.append(trace_entry)
        logger.debug(f"Calculation trace: {step} - {data}")
    
    def calculate_comparison(self, 
                           scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate and compare multiple scenarios
        
        Args:
            scenarios: List of scenario dictionaries with calculation parameters
            
        Returns:
            Comparison results with all scenarios
        """
        results = []
        
        for i, scenario in enumerate(scenarios):
            try:
                # Convert string types to enums
                building_type = BuildingType(scenario['building_type'])
                project_class = ProjectClass(scenario.get('project_class', 'ground_up'))
                ownership_type = OwnershipType(scenario.get('ownership_type', 'for_profit'))
                
                # Calculate scenario
                result = self.calculate_project(
                    building_type=building_type,
                    subtype=scenario['subtype'],
                    square_footage=scenario['square_footage'],
                    location=scenario['location'],
                    project_class=project_class,
                    floors=scenario.get('floors', 1),
                    ownership_type=ownership_type,
                    special_features=scenario.get('special_features', [])
                )
                
                result['scenario_name'] = scenario.get('name', f'Scenario {i+1}')
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error calculating scenario {i+1}: {str(e)}")
                results.append({
                    'scenario_name': scenario.get('name', f'Scenario {i+1}'),
                    'error': str(e)
                })
        
        # Find best/worst scenarios
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            lowest_cost = min(valid_results, key=lambda x: x['totals']['total_project_cost'])
            highest_cost = max(valid_results, key=lambda x: x['totals']['total_project_cost'])
        else:
            lowest_cost = highest_cost = None
        
        return {
            'scenarios': results,
            'summary': {
                'total_scenarios': len(scenarios),
                'successful_calculations': len(valid_results),
                'lowest_cost_scenario': lowest_cost['scenario_name'] if lowest_cost else None,
                'highest_cost_scenario': highest_cost['scenario_name'] if highest_cost else None,
                'cost_range': {
                    'min': lowest_cost['totals']['total_project_cost'] if lowest_cost else 0,
                    'max': highest_cost['totals']['total_project_cost'] if highest_cost else 0
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_ownership_analysis(self, calculations: dict) -> dict:
        """Calculate ownership and revenue analysis using master_config data"""
        
        building_type = calculations.get('building_type')
        subtype = calculations.get('subtype')
        square_footage = calculations.get('square_footage', 0)
        total_cost = calculations.get('total_cost', 0)
        construction_cost = calculations.get('subtotal', 0)
        
        # Get the config for this building/subtype
        building_enum = self._get_building_enum(building_type)
        if not building_enum or building_enum not in MASTER_CONFIG:
            return self._empty_ownership_analysis()
        
        subtype_config = MASTER_CONFIG[building_enum].get(subtype)
        if not subtype_config:
            return self._empty_ownership_analysis()
        
        # Calculate quality factor based on actual vs base cost
        base_cost_psf = subtype_config.base_cost_per_sf
        actual_cost_psf = construction_cost / square_footage if square_footage > 0 else base_cost_psf
        quality_factor = pow(actual_cost_psf / base_cost_psf, 0.5) if base_cost_psf > 0 else 1.0
        
        # Determine if premium (>20% above base cost)
        is_premium = quality_factor > 1.2
        
        # Get occupancy and margin based on quality
        occupancy_rate = subtype_config.occupancy_rate_premium if is_premium else subtype_config.occupancy_rate_base
        operating_margin = subtype_config.operating_margin_premium if is_premium else subtype_config.operating_margin_base
        
        # Calculate revenue based on building type
        annual_revenue = self._calculate_revenue_by_type(
            building_enum, subtype_config, square_footage, quality_factor, occupancy_rate
        )
        
        # Apply regional multiplier if available
        regional_multiplier = calculations.get('regional_multiplier', 1.0)
        annual_revenue *= regional_multiplier
        
        # Calculate financial metrics
        net_income = annual_revenue * operating_margin
        
        # Calculate NPV using config discount_rate
        years = 10  # Standard projection period
        discount_rate = getattr(subtype_config, 'discount_rate', 0.08)
        
        npv = self.calculate_npv(
            initial_investment=total_cost,
            annual_cash_flow=net_income,
            years=years,
            discount_rate=discount_rate
        )
        
        # Calculate IRR
        irr = self.calculate_irr(
            initial_investment=total_cost,
            annual_cash_flow=net_income,
            years=years
        )
        
        # Calculate Revenue Requirements
        revenue_requirements = self.calculate_revenue_requirements(
            total_cost=total_cost,
            config=subtype_config,
            square_footage=square_footage
        )
        
        # Calculate Operational Efficiency
        operational_efficiency = self.calculate_operational_efficiency(
            revenue=annual_revenue,
            config=subtype_config
        )
        
        # Calculate payback period
        payback_period = round(total_cost / net_income, 1) if net_income > 0 else 999
        
        # Calculate display-ready operational metrics
        operational_metrics = self.calculate_operational_metrics_for_display(
            building_type=building_type,
            subtype=subtype,
            operational_efficiency=operational_efficiency,
            square_footage=square_footage,
            annual_revenue=annual_revenue,
            units=calculations.get('units', 0)
        )
        
        return {
            'revenue_analysis': {
                'annual_revenue': round(annual_revenue, 2),
                'revenue_per_sf': round(annual_revenue / square_footage, 2) if square_footage > 0 else 0,
                'operating_margin': operating_margin,
                'net_income': round(net_income, 2),
                'occupancy_rate': occupancy_rate,
                'quality_factor': round(quality_factor, 2),
                'is_premium': is_premium
            },
            'return_metrics': {
                'estimated_annual_noi': round(net_income, 2),
                'cash_on_cash_return': round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0,
                'cap_rate': round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0,
                'npv': npv,
                'irr': round(irr * 100, 2),  # Convert to percentage
                'payback_period': payback_period
            },
            'revenue_requirements': revenue_requirements,
            'operational_efficiency': operational_efficiency,  # Keep raw data
            'operational_metrics': operational_metrics  # ADD formatted display data
        }

    def _calculate_revenue_by_type(self, building_enum, config, square_footage, quality_factor, occupancy_rate):
        """Calculate revenue based on the specific building type's metrics"""
        
        # Healthcare - uses beds, visits, procedures, or scans
        if building_enum == BuildingType.HEALTHCARE:
            if hasattr(config, 'base_revenue_per_bed_annual') and config.base_revenue_per_bed_annual and hasattr(config, 'beds_per_sf') and config.beds_per_sf:
                beds = square_footage * config.beds_per_sf
                base_revenue = beds * config.base_revenue_per_bed_annual
            elif hasattr(config, 'base_revenue_per_visit') and config.base_revenue_per_visit and hasattr(config, 'visits_per_day') and config.visits_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_visits = config.visits_per_day * config.days_per_year
                base_revenue = annual_visits * config.base_revenue_per_visit
            elif hasattr(config, 'base_revenue_per_procedure') and config.base_revenue_per_procedure and hasattr(config, 'procedures_per_day') and config.procedures_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_procedures = config.procedures_per_day * config.days_per_year
                base_revenue = annual_procedures * config.base_revenue_per_procedure
            elif hasattr(config, 'base_revenue_per_scan') and config.base_revenue_per_scan and hasattr(config, 'scans_per_day') and config.scans_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_scans = config.scans_per_day * config.days_per_year
                base_revenue = annual_scans * config.base_revenue_per_scan
            elif hasattr(config, 'base_revenue_per_sf_annual') and config.base_revenue_per_sf_annual:
                base_revenue = square_footage * config.base_revenue_per_sf_annual
            else:
                # Fallback for healthcare with missing revenue config
                base_revenue = 0
        
        # Multifamily - uses monthly rent per unit
        elif building_enum == BuildingType.MULTIFAMILY:
            units = square_footage * config.units_per_sf
            monthly_rent = config.base_revenue_per_unit_monthly
            base_revenue = units * monthly_rent * 12
        
        # Hospitality - uses revenue per room
        elif building_enum == BuildingType.HOSPITALITY:
            rooms = square_footage * config.rooms_per_sf
            base_revenue = rooms * config.base_revenue_per_room_annual
        
        # Educational - uses revenue per student
        elif building_enum == BuildingType.EDUCATIONAL:
            students = square_footage * config.students_per_sf
            base_revenue = students * config.base_revenue_per_student_annual
        
        # Parking - uses revenue per space
        elif building_enum == BuildingType.PARKING:
            if hasattr(config, 'base_revenue_per_space_monthly'):
                spaces = square_footage * config.spaces_per_sf
                base_revenue = spaces * config.base_revenue_per_space_monthly * 12
            else:
                base_revenue = 0
        
        # Recreation - special handling for stadium
        elif building_enum == BuildingType.RECREATION:
            if hasattr(config, 'base_revenue_per_seat_annual'):
                seats = square_footage * config.seats_per_sf
                base_revenue = seats * config.base_revenue_per_seat_annual
            else:
                base_revenue = square_footage * config.base_revenue_per_sf_annual
        
        # Civic - no revenue (government funded)
        elif building_enum == BuildingType.CIVIC:
            return 0
        
        # Default - uses revenue per SF (Office, Retail, Restaurant, Industrial, etc.)
        else:
            base_revenue = square_footage * config.base_revenue_per_sf_annual
        
        # Apply quality factor and occupancy
        adjusted_revenue = base_revenue * quality_factor * occupancy_rate
        
        return adjusted_revenue

    def _get_building_enum(self, building_type_str: str):
        """Convert string building type to BuildingType enum"""
        type_map = {
            'healthcare': BuildingType.HEALTHCARE,
            'multifamily': BuildingType.MULTIFAMILY,
            'office': BuildingType.OFFICE,
            'retail': BuildingType.RETAIL,
            'restaurant': BuildingType.RESTAURANT,
            'industrial': BuildingType.INDUSTRIAL,
            'hospitality': BuildingType.HOSPITALITY,
            'educational': BuildingType.EDUCATIONAL,
            'mixed_use': BuildingType.MIXED_USE,
            'specialty': BuildingType.SPECIALTY,
            'civic': BuildingType.CIVIC,
            'recreation': BuildingType.RECREATION,
            'parking': BuildingType.PARKING
        }
        return type_map.get(building_type_str.lower())

    def _empty_ownership_analysis(self):
        """Return empty ownership analysis structure"""
        return {
            'revenue_analysis': {
                'annual_revenue': 0,
                'revenue_per_sf': 0,
                'operating_margin': 0,
                'net_income': 0,
                'occupancy_rate': 0,
                'quality_factor': 1.0,
                'is_premium': False
            },
            'return_metrics': {
                'estimated_annual_noi': 0,
                'cash_on_cash_return': 0,
                'cap_rate': 0,
                'npv': 0,
                'irr': 0,
                'payback_period': 999
            },
            'revenue_requirements': {
                'required_value': 0,
                'metric_name': 'Annual Revenue Required',
                'target_roi': 0,
                'operating_margin': 0,
                'break_even_revenue': 0,
                'required_monthly': 0
            },
            'operational_efficiency': {
                'total_expenses': 0,
                'operating_margin': 0,
                'efficiency_score': 0,
                'expense_ratio': 0
            }
        }
    
    def calculate_npv(self, initial_investment: float, annual_cash_flow: float, 
                      years: int, discount_rate: float) -> float:
        """Calculate Net Present Value using discount rate from config"""
        npv = -initial_investment
        for year in range(1, years + 1):
            npv += annual_cash_flow / ((1 + discount_rate) ** year)
        return round(npv, 2)

    def calculate_irr(self, initial_investment: float, annual_cash_flow: float, 
                      years: int = 10) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson approximation"""
        # Simple approximation for constant cash flows
        if annual_cash_flow <= 0 or initial_investment <= 0:
            return 0.0
        
        # Newton-Raphson method for IRR
        rate = 0.1  # Initial guess
        for _ in range(20):  # Max iterations
            npv = -initial_investment
            dnpv = 0
            for year in range(1, years + 1):
                npv += annual_cash_flow / ((1 + rate) ** year)
                dnpv -= year * annual_cash_flow / ((1 + rate) ** (year + 1))
            
            if abs(npv) < 0.01:  # Converged
                break
            
            rate = rate - npv / dnpv if dnpv != 0 else rate
        
        return round(rate, 4)

    def calculate_revenue_requirements(self, total_cost: float, config, square_footage: float) -> dict:
        """Calculate revenue needed to achieve target ROI from config"""
        target_roi = getattr(config, 'target_roi', 0.08)
        
        # Calculate required annual return
        required_annual_return = total_cost * target_roi
        
        # Calculate operating margin (1 - total expense ratio)
        total_expense_ratio = 0
        
        # Add all expense ratios from config
        expense_fields = [
            'labor_cost_ratio', 'utility_cost_ratio', 'maintenance_cost_ratio',
            'management_fee_ratio', 'insurance_cost_ratio', 'property_tax_ratio',
            'supply_cost_ratio', 'food_cost_ratio', 'beverage_cost_ratio',
            'franchise_fee_ratio', 'equipment_lease_ratio', 'marketing_ratio',
            'reserves_ratio', 'security_ratio', 'supplies_ratio',
            'floor_plan_interest_ratio', 'materials_ratio', 'program_costs_ratio',
            'equipment_ratio', 'chemicals_ratio', 'event_costs_ratio',
            'software_fees_ratio', 'other_expenses_ratio'
        ]
        
        for field in expense_fields:
            if hasattr(config, field):
                ratio = getattr(config, field)
                if ratio and ratio > 0:
                    total_expense_ratio += ratio
        
        operating_margin = 1 - total_expense_ratio
        
        # Required revenue to achieve target ROI
        required_revenue = required_annual_return / operating_margin if operating_margin > 0 else 0
        
        # Calculate market value based on typical revenue for this building type
        market_revenue_per_sf = getattr(config, 'base_revenue_per_sf_annual', 0)
        market_value = market_revenue_per_sf * square_footage if market_revenue_per_sf > 0 else 0
        
        # Calculate feasibility and gap
        feasibility = 'Feasible' if market_value >= required_revenue else 'Challenging'
        gap = market_value - required_revenue
        gap_percentage = (gap / required_revenue * 100) if required_revenue > 0 else 0
        
        return {
            'required_value': round(required_revenue, 2),
            'required_revenue_per_sf': round(required_revenue / square_footage, 2) if square_footage > 0 else 0,
            'metric_name': 'Annual Revenue Required',
            'target_roi': target_roi,
            'operating_margin': round(operating_margin, 3),
            'break_even_revenue': round(total_cost * 0.1, 2),  # Simple 10% of cost
            'required_monthly': round(required_revenue / 12, 2),
            'market_value': round(market_value, 2),  # ADD THIS
            'feasibility': feasibility,  # ADD THIS
            'gap': round(gap, 2),  # ADD THIS
            'gap_percentage': round(gap_percentage, 1)  # ADD THIS
        }

    def calculate_operational_metrics_for_display(self, building_type: str, subtype: str, 
                                                 operational_efficiency: dict, 
                                                 square_footage: float, 
                                                 annual_revenue: float, 
                                                 units: int = 0) -> dict:
        """
        Calculate display-ready operational metrics based on building type.
        Returns formatted metrics ready for frontend display.
        """
        
        # Base metrics all building types have
        operational_metrics = {
            'staffing': [],
            'revenue': {},
            'kpis': []
        }
        
        # Get data from operational_efficiency with safe defaults
        labor_cost = operational_efficiency.get('labor_cost', 0) or 0
        total_expenses = operational_efficiency.get('total_expenses', 0) or 0
        operating_margin = operational_efficiency.get('operating_margin', 0) or 0
        efficiency_score = operational_efficiency.get('efficiency_score', 0) or 0
        expense_ratio = operational_efficiency.get('expense_ratio', 0) or 0
        
        # Building-type specific metrics
        if building_type == 'restaurant':
            food_cost = operational_efficiency.get('food_cost', 0)
            beverage_cost = operational_efficiency.get('beverage_cost', 0)
            
            # Calculate restaurant-specific metrics
            food_cost_ratio = (food_cost / annual_revenue) if annual_revenue > 0 else 0
            labor_cost_ratio = (labor_cost / annual_revenue) if annual_revenue > 0 else 0
            prime_cost_ratio = food_cost_ratio + labor_cost_ratio
            
            operational_metrics['staffing'] = [
                {'label': 'Labor Cost', 'value': f'${labor_cost:,.0f}'},
                {'label': 'Labor % of Revenue', 'value': f'{labor_cost_ratio * 100:.1f}%'}
            ]
            
            operational_metrics['revenue'] = {
                'Food Cost': f'{food_cost_ratio * 100:.1f}%',
                'Beverage Cost': f'{(beverage_cost / annual_revenue * 100):.1f}%' if annual_revenue > 0 else '0%',
                'Labor Cost': f'{labor_cost_ratio * 100:.1f}%',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Food Cost Ratio',
                    'value': f'{food_cost_ratio * 100:.0f}%',
                    'color': 'green' if (food_cost_ratio or 0) < 0.28 else 'yellow' if (food_cost_ratio or 0) < 0.32 else 'red'
                },
                {
                    'label': 'Prime Cost',
                    'value': f'{prime_cost_ratio * 100:.0f}%',
                    'color': 'green' if (prime_cost_ratio or 0) < 0.60 else 'yellow' if (prime_cost_ratio or 0) < 0.65 else 'red'
                },
                {
                    'label': 'Efficiency',
                    'value': f'{efficiency_score:.0f}%',
                    'color': 'green' if (efficiency_score or 0) > 15 else 'yellow' if (efficiency_score or 0) > 10 else 'red'
                }
            ]
            
        elif building_type == 'healthcare':
            # Healthcare calculations based on industry standards
            beds = round(square_footage / 600)  # Industry standard: ~600 SF per bed
            nursing_fte = round(labor_cost * 0.4 / 75000) if labor_cost > 0 else 1  # 40% of labor is nursing, avg salary $75k
            total_fte = round(labor_cost / 60000) if labor_cost > 0 else 1  # Average healthcare worker salary
            
            operational_metrics['staffing'] = [
                {'label': 'Total FTEs Required', 'value': str(total_fte)},
                {'label': 'Beds per Nurse', 'value': f'{beds / nursing_fte:.1f}' if nursing_fte > 0 else 'N/A'}
            ]
            
            operational_metrics['revenue'] = {
                'Revenue per Employee': f'${annual_revenue / total_fte:,.0f}' if total_fte > 0 else 'N/A',
                'Revenue per Bed': f'${annual_revenue / beds:,.0f}' if beds > 0 else 'N/A',
                'Labor Cost Ratio': f'{(labor_cost / annual_revenue * 100):.0f}%' if annual_revenue > 0 else 'N/A',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {'label': 'ALOS Target', 'value': '3.8 days', 'color': 'green'},
                {'label': 'Occupancy', 'value': '85%', 'color': 'green'},
                {'label': 'Efficiency', 'value': f'{efficiency_score:.0f}%', 
                 'color': 'green' if (efficiency_score or 0) > 20 else 'yellow' if (efficiency_score or 0) > 15 else 'red'}
            ]
            
        elif building_type == 'multifamily':
            # Use units if provided, otherwise estimate
            if units == 0:
                units = round(square_footage / 1000)  # Average apartment size
            
            units_per_manager = 50  # Industry standard
            maintenance_staff = max(1, round(units / 30))  # 1 per 30 units
            
            operational_metrics['staffing'] = [
                {'label': 'Units per Manager', 'value': str(units_per_manager)},
                {'label': 'Maintenance Staff', 'value': str(maintenance_staff)}
            ]
            
            operational_metrics['revenue'] = {
                'Revenue per Unit': f'${annual_revenue / units:,.0f}/yr' if units > 0 else 'N/A',
                'Average Rent': f'${annual_revenue / units / 12:,.0f}/mo' if units > 0 else 'N/A',
                'Occupancy Target': '93%',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'NOI Margin',
                    'value': f'{operating_margin * 100:.0f}%',
                    'color': 'green' if (operating_margin or 0) > 0.60 else 'yellow' if (operating_margin or 0) > 0.50 else 'red'
                },
                {
                    'label': 'Expense Ratio',
                    'value': f'{expense_ratio * 100:.0f}%',
                    'color': 'green' if (expense_ratio or 0) < 0.40 else 'yellow' if (expense_ratio or 0) < 0.50 else 'red'
                }
            ]
            
        elif building_type == 'office':
            operational_metrics['staffing'] = [
                {'label': 'Property Mgmt', 'value': f'${operational_efficiency.get("management_fee", 0):,.0f}'},
                {'label': 'Maintenance', 'value': f'${operational_efficiency.get("maintenance_cost", 0):,.0f}'}
            ]
            
            operational_metrics['revenue'] = {
                'Rent per SF': f'${annual_revenue / square_footage:.2f}/yr' if square_footage > 0 else 'N/A',
                'Operating Expenses': f'${total_expenses:,.0f}',
                'CAM Charges': f'${total_expenses / square_footage:.2f}/SF' if square_footage > 0 else 'N/A',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Efficiency',
                    'value': f'{efficiency_score:.0f}%',
                    'color': 'green' if (efficiency_score or 0) > 15 else 'yellow' if (efficiency_score or 0) > 10 else 'red'
                },
                {
                    'label': 'Expense/SF',
                    'value': f'${total_expenses / square_footage:.2f}' if square_footage > 0 else 'N/A',
                    'color': 'yellow'
                }
            ]
            
        else:
            # Generic metrics for other building types
            operational_metrics['staffing'] = [
                {'label': 'Labor Cost', 'value': f'${labor_cost:,.0f}'},
                {'label': 'Management', 'value': f'${operational_efficiency.get("management_fee", 0):,.0f}'}
            ]
            
            operational_metrics['revenue'] = {
                'Total Expenses': f'${total_expenses:,.0f}',
                'Operating Margin': f'{operating_margin * 100:.1f}%',
                'Efficiency Score': f'{efficiency_score:.0f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Expense Ratio',
                    'value': f'{expense_ratio * 100:.0f}%',
                    'color': 'green' if (expense_ratio or 0) < 0.80 else 'yellow' if (expense_ratio or 0) < 0.90 else 'red'
                }
            ]
        
        return operational_metrics

    def calculate_operational_efficiency(self, revenue: float, config) -> dict:
        """Calculate operational efficiency metrics from config ratios"""
        result = {
            'total_expenses': 0,
            'operating_margin': 0,
            'efficiency_score': 0,
            'expense_ratio': 0
        }
        
        # Calculate each expense category from config
        expense_mappings = [
            ('labor_cost', 'labor_cost_ratio'),
            ('utility_cost', 'utility_cost_ratio'),
            ('maintenance_cost', 'maintenance_cost_ratio'),
            ('management_fee', 'management_fee_ratio'),
            ('insurance_cost', 'insurance_cost_ratio'),
            ('property_tax', 'property_tax_ratio'),
            ('supply_cost', 'supply_cost_ratio'),
            ('food_cost', 'food_cost_ratio'),
            ('beverage_cost', 'beverage_cost_ratio'),
            ('franchise_fee', 'franchise_fee_ratio'),
            ('equipment_lease', 'equipment_lease_ratio'),
            ('marketing_cost', 'marketing_ratio'),
            ('reserves', 'reserves_ratio'),
            ('security', 'security_ratio'),
            ('supplies', 'supplies_ratio'),
            ('floor_plan_interest', 'floor_plan_interest_ratio'),
            ('materials', 'materials_ratio'),
            ('program_costs', 'program_costs_ratio'),
            ('equipment', 'equipment_ratio'),
            ('chemicals', 'chemicals_ratio'),
            ('event_costs', 'event_costs_ratio'),
            ('software_fees', 'software_fees_ratio'),
            ('other_expenses', 'other_expenses_ratio'),
        ]
        
        # Calculate expenses
        total_expenses = 0
        for name, attr in expense_mappings:
            if hasattr(config, attr):
                ratio = getattr(config, attr)
                if ratio and ratio > 0:
                    cost = revenue * ratio
                    result[name] = round(cost, 2)
                    total_expenses += cost
        
        result['total_expenses'] = round(total_expenses, 2)
        result['operating_margin'] = round(1 - (total_expenses / revenue) if revenue > 0 else 0, 3)
        result['efficiency_score'] = round((1 - (total_expenses / revenue)) * 100 if revenue > 0 else 0, 1)
        result['expense_ratio'] = round(total_expenses / revenue if revenue > 0 else 0, 3)
        
        return result
    
    def get_available_building_types(self) -> Dict[str, List[str]]:
        """
        Get all available building types and their subtypes
        
        Returns:
            Dictionary mapping building types to their subtypes
        """
        available = {}
        for building_type in BuildingType:
            if building_type in self.config:
                available[building_type.value] = list(self.config[building_type].keys())
        return available
    
    def get_building_details(self, building_type: BuildingType, subtype: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed configuration for a specific building type/subtype
        
        Args:
            building_type: Type from BuildingType enum
            subtype: Specific subtype
            
        Returns:
            Building configuration details or None if not found
        """
        config = get_building_config(building_type, subtype)
        if not config:
            return None
            
        # Convert to dictionary for easier consumption
        return {
            'display_name': config.display_name,
            'base_cost_per_sf': config.base_cost_per_sf,
            'cost_range': config.cost_range,
            'equipment_cost_per_sf': config.equipment_cost_per_sf,
            'typical_floors': config.typical_floors,
            'trades': asdict(config.trades),
            'soft_costs': asdict(config.soft_costs),
            'ownership_types': list(config.ownership_types.keys()),
            'special_features': list(config.special_features.keys()) if config.special_features else [],
            'nlp_keywords': config.nlp.keywords,
            'regional_multipliers': config.regional_multipliers
        }
    
    def estimate_from_description(self, 
                                 description: str,
                                 square_footage: float,
                                 location: str = "Nashville") -> Dict[str, Any]:
        """
        Estimate costs from a natural language description
        
        Args:
            description: Natural language project description
            square_footage: Total square footage
            location: City/location for regional multiplier
            
        Returns:
            Cost estimate with detected building type
        """
        from app.v2.config.master_config import detect_building_type
        
        # Detect building type from description
        detection = detect_building_type(description)
        
        if not detection:
            return {
                'error': 'Could not detect building type from description',
                'description': description
            }
        
        building_type, subtype = detection
        
        # Detect project class from keywords
        description_lower = description.lower()
        if 'renovation' in description_lower or 'remodel' in description_lower:
            project_class = ProjectClass.RENOVATION
        elif 'addition' in description_lower or 'expansion' in description_lower:
            project_class = ProjectClass.ADDITION
        elif 'tenant improvement' in description_lower or 'ti' in description_lower:
            project_class = ProjectClass.TENANT_IMPROVEMENT
        else:
            project_class = ProjectClass.GROUND_UP
        
        # Calculate with detected parameters
        result = self.calculate_project(
            building_type=building_type,
            subtype=subtype,
            square_footage=square_footage,
            location=location,
            project_class=project_class
        )
        
        # Add detection info
        result['detection_info'] = {
            'detected_type': building_type.value,
            'detected_subtype': subtype,
            'detected_class': project_class.value,
            'original_description': description
        }
        
        return result

# Create a singleton instance
unified_engine = UnifiedEngine()