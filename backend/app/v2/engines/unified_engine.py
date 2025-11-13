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
    get_effective_modifiers,
    get_margin_pct,
    get_target_roi,
    detect_building_type_with_method,
    resolve_quality_factor,
    validate_project_class,
    infer_finish_level
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
                         finish_level: Optional[str] = None,
                         special_features: List[str] = None,
                         finish_level_source: Optional[str] = None) -> Dict[str, Any]:
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
            finish_level: Optional finish quality override
            special_features: List of special features to add
            finish_level_source: Trace provenance for finish level selection
            
        Returns:
            Comprehensive cost breakdown dictionary
        """
        
        # Clear trace for new calculation
        self.calculation_trace = []
        self._log_trace("calculation_start", {
            'building_type': building_type.value,
            'subtype': subtype,
            'square_footage': square_footage,
            'location': location
        })

        normalized_finish_level = finish_level.lower().strip() if isinstance(finish_level, str) and finish_level.strip() else None
        inferred_source = finish_level_source if finish_level_source in {'explicit', 'description', 'default'} else None

        if inferred_source == 'explicit':
            finish_source = 'explicit'
        elif inferred_source == 'description':
            finish_source = 'description'
        elif inferred_source == 'default':
            finish_source = 'default'
        elif normalized_finish_level:
            finish_source = 'explicit'
        else:
            finish_source = 'default'

        if not normalized_finish_level:
            normalized_finish_level = 'standard'

        self._log_trace("finish_level_source", {
            'source': finish_source,
            'finish_level': normalized_finish_level or 'standard'
        })
        quality_factor = resolve_quality_factor(normalized_finish_level, building_type, subtype)
        self._log_trace("quality_factor_resolved", {
            'finish_level': normalized_finish_level or 'standard',
            'quality_factor': round(quality_factor, 4)
        })

        city_only_warning_logged = False

        def _city_only_warning():
            nonlocal city_only_warning_logged
            if not city_only_warning_logged:
                self._log_trace("warning", {
                    'message': 'City-only location used default regional multiplier'
                })
                city_only_warning_logged = True
        
        # Get configuration
        building_config = get_building_config(building_type, subtype)
        if not building_config:
            raise ValueError(f"No configuration found for {building_type.value}/{subtype}")
        
        # Validate and adjust project class if incompatible
        original_class = project_class
        project_class = validate_project_class(building_type, subtype, project_class)
        if project_class != original_class:
            self._log_trace("project_class_adjusted", {
                'original': original_class.value,
                'adjusted': project_class.value,
                'reason': 'Incompatible with building type'
            })
        
        # Base construction cost calculation with finish level adjustment
        original_base_cost_per_sf = building_config.base_cost_per_sf

        # Height premium for office towers: add modest multipliers for taller structures
        height_factor = 1.0
        if building_type == BuildingType.OFFICE:
            try:
                floor_count = int(floors or building_config.typical_floors or 1)
            except (TypeError, ValueError):
                floor_count = 1

            extra_premium = 0.0
            if floor_count > 4:
                extra_premium += max(0, min(floor_count, 8) - 4) * 0.02  # 2% per floor from 5-8
            if floor_count > 8:
                extra_premium += max(0, min(floor_count, 12) - 8) * 0.01  # 1% per floor from 9-12

            height_factor = 1.0 + min(extra_premium, 0.20)  # Cap at +20%

        base_cost_per_sf = original_base_cost_per_sf * height_factor
        self._log_trace("base_cost_retrieved", {
            'base_cost_per_sf': original_base_cost_per_sf,
            'quality_factor': round(quality_factor, 4),
            'height_factor': round(height_factor, 4),
            'adjusted_base_cost_per_sf': round(base_cost_per_sf, 4)
        })
        
        # Apply project class multiplier (treated as complexity factor)
        class_multiplier = PROJECT_CLASS_MULTIPLIERS[project_class]
        complexity_factor = class_multiplier
        cost_after_complexity = base_cost_per_sf * complexity_factor
        self._log_trace("project_class_multiplier_applied", {
            'multiplier': complexity_factor,
            'adjusted_cost_per_sf': round(cost_after_complexity, 4)
        })

        modifiers = get_effective_modifiers(
            building_type,
            subtype,
            normalized_finish_level,
            location,
            warning_callback=_city_only_warning
        )

        self._log_trace("finish_cost_applied", {
            'finish_level': normalized_finish_level or 'standard',
            'factor': round(modifiers.get('finish_cost_factor', 1.0), 4)
        })

        finish_cost_factor = modifiers.get('finish_cost_factor', 1.0)
        if not finish_cost_factor:
            finish_cost_factor = 1.0
        cost_factor = modifiers['cost_factor']
        if finish_cost_factor:
            regional_multiplier_effective = cost_factor / finish_cost_factor
        else:
            regional_multiplier_effective = cost_factor

        cost_after_regional = cost_after_complexity * regional_multiplier_effective
        final_cost_per_sf = cost_after_regional * finish_cost_factor
        self._log_trace("modifiers_applied", {
            'finish_level': normalized_finish_level or 'standard',
            'cost_factor': round(cost_factor, 4),
            'regional_multiplier': round(regional_multiplier_effective, 4),
            'revenue_factor': round(modifiers['revenue_factor'], 4),
            'margin_pct': round(modifiers['margin_pct'], 4)
        })
        
        # Calculate base construction cost
        construction_cost = final_cost_per_sf * square_footage
        
        # Calculate equipment cost with finish/regional adjustments
        equipment_multiplier = modifiers.get('finish_cost_factor', 1.0)
        equipment_cost = building_config.equipment_cost_per_sf * equipment_multiplier * square_footage
        
        # Add special features if any
        special_features_cost = 0
        if special_features and building_config.special_features:
            for feature in special_features:
                if feature in building_config.special_features:
                    feature_cost = building_config.special_features[feature] * square_footage
                    special_features_cost += feature_cost
                    self._log_trace("special_feature_applied", {
                        'feature': feature,
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
                self._log_trace("restaurant_cost_clamp", {
                    'mode': 'minimum',
                    'original_cost_per_sf': cost_per_sf,
                    'target_cost_per_sf': min_cost
                })
                # Adjust costs proportionally
                adjustment_factor = (min_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = min_cost * square_footage
            elif cost_per_sf > max_cost and subtype != 'fine_dining':
                self._log_trace("restaurant_cost_clamp", {
                    'mode': 'maximum',
                    'original_cost_per_sf': cost_per_sf,
                    'target_cost_per_sf': max_cost
                })
                # Cap costs proportionally
                adjustment_factor = (max_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = max_cost * square_footage
        
        # Calculate ownership/financing analysis with enhanced financial metrics
        ownership_analysis = None
        if ownership_type in building_config.ownership_types:
            # Calculate comprehensive revenue analysis using master_config
            revenue_data = self.calculate_ownership_analysis({
                'building_type': building_type.value,
                'subtype': subtype,
                'square_footage': square_footage,
                'total_cost': total_project_cost,
                'subtotal': construction_cost,  # Construction cost before contingency
                'modifiers': modifiers,
                'quality_factor': quality_factor,
                'finish_level': normalized_finish_level
            })

            # Get basic ownership metrics (prefer revenue-derived NOI when available)
            revenue_analysis_for_financing = revenue_data.get('revenue_analysis') if revenue_data else None
            ownership_analysis = self._calculate_ownership(
                total_project_cost,
                building_config.ownership_types[ownership_type],
                revenue_analysis=revenue_analysis_for_financing
            )
            
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
                if 'yield_on_cost' in revenue_data:
                    ownership_analysis['yield_on_cost'] = revenue_data.get('yield_on_cost')
                if 'market_cap_rate' in revenue_data:
                    ownership_analysis['market_cap_rate'] = revenue_data.get('market_cap_rate')
                if 'cap_rate_spread_bps' in revenue_data:
                    ownership_analysis['cap_rate_spread_bps'] = revenue_data.get('cap_rate_spread_bps')
                
                actual_noi = (
                    revenue_data.get('return_metrics', {}).get('estimated_annual_noi')
                    or revenue_data['revenue_analysis'].get('net_income')
                )
                debt_metrics = ownership_analysis.get('debt_metrics') or {}
                annual_debt_service = debt_metrics.get('annual_debt_service', 0)
                if actual_noi is not None:
                    recalculated_dscr = actual_noi / annual_debt_service if annual_debt_service else 0
                    debt_metrics['calculated_dscr'] = recalculated_dscr
                    debt_metrics['dscr_meets_target'] = recalculated_dscr >= debt_metrics.get('target_dscr', 0)
                    ownership_analysis['debt_metrics'] = debt_metrics
                    ownership_analysis['return_metrics']['estimated_annual_noi'] = actual_noi
                    self._log_trace("dscr_recalculated_from_revenue", {
                        'actual_noi': actual_noi,
                        'annual_debt_service': annual_debt_service,
                        'calculated_dscr': recalculated_dscr
                    })
        
        # Financial requirements removed - was only partially implemented for hospital
        
        # Generate cost DNA for transparency
        cost_dna = {
            'base_cost': base_cost_per_sf,
            'finish_adjustment': finish_cost_factor,
            'regional_adjustment': regional_multiplier_effective,
            'complexity_factor': complexity_factor,
            'final_cost': final_cost_per_sf,
            'location': location,
            'market_name': location.split(',')[0] if location else 'Nashville',  # Extract city name
            'building_type': building_type.value if hasattr(building_type, 'value') else str(building_type),
            'subtype': subtype,
            'detected_factors': [],  # Will be populated with special features
            'applied_adjustments': {
                'base': base_cost_per_sf,
                'after_finish': cost_after_complexity,
                'after_class': cost_after_complexity,
                'after_complexity': cost_after_complexity,
                'after_finish_factor': final_cost_per_sf,
                'after_regional': cost_after_regional,
                'final': final_cost_per_sf
            },
            'market_context': {
                'market': location.split(',')[0] if location else 'Nashville',
                'index': modifiers.get('market_factor', 1.0),
                'comparison': 'above national average' if modifiers.get('market_factor', 1.0) > 1.0 else 'below national average' if modifiers.get('market_factor', 1.0) < 1.0 else 'at national average',
                'percentage_difference': round((modifiers.get('market_factor', 1.0) - 1.0) * 100, 1)
            }
        }
        
        # Add special features if present
        if special_features:
            cost_dna['detected_factors'] = list(special_features) if isinstance(special_features, (list, dict)) else [special_features]

        cost_build_up = [
            {
                'label': 'Base Cost',
                'value_per_sf': base_cost_per_sf
            },
            {
                'label': 'Regional',
                'multiplier': regional_multiplier_effective
            },
            {
                'label': 'Complexity',
                'multiplier': complexity_factor
            }
        ]

        display_finish_level = (normalized_finish_level or 'standard').lower()
        if display_finish_level != 'standard':
            cost_build_up.append({
                'label': 'Finish Level',
                'multiplier': finish_cost_factor
            })
        
        # Ensure the build-up array always has something meaningful so frontend visuals don't break
        fallback_cost_build_up = cost_build_up if cost_build_up else [
            {'label': 'Base Cost', 'value_per_sf': original_base_cost_per_sf},
            {'label': 'Regional', 'multiplier': regional_multiplier_effective},
            {'label': 'Complexity', 'multiplier': complexity_factor},
        ]
        if not cost_build_up and display_finish_level != 'standard':
            fallback_cost_build_up.append({'label': 'Finish Level', 'multiplier': finish_cost_factor})

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
            'typical_floors': building_config.typical_floors,
            'finish_level': normalized_finish_level or 'standard',
            'finish_level_source': finish_source,
            'available_special_features': list(building_config.special_features.keys()) if building_config.special_features else []
        },
            'modifiers': modifiers,
            # Flatten calculations to top level to match frontend CalculationResult interface
            'construction_costs': {
                'base_cost_per_sf': base_cost_per_sf,
                'original_base_cost_per_sf': original_base_cost_per_sf,
                'class_multiplier': class_multiplier,
                'regional_multiplier': regional_multiplier_effective,
                'finish_cost_factor': finish_cost_factor,
                'cost_factor': cost_factor,
                'quality_factor': quality_factor,
                'final_cost_per_sf': final_cost_per_sf,
                'construction_total': construction_cost,
                'equipment_total': equipment_cost,
                'special_features_total': special_features_cost,
                'cost_build_up': fallback_cost_build_up
            },
            'cost_dna': cost_dna,  # Add cost DNA for transparency
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
            # Add return metrics at top level for investment visibility
            'return_metrics': ownership_analysis.get('return_metrics', {}) if ownership_analysis else {},
            # Add roi metrics at top level for investment analysis
            'roi_metrics': ownership_analysis.get('roi_metrics', {}) if ownership_analysis else {},
            # Add department and operational metrics at top level for easy frontend access
            'department_allocation': ownership_analysis.get('department_allocation', []) if ownership_analysis else [],
            'operational_metrics': ownership_analysis.get('operational_metrics', {}) if ownership_analysis else {},
            'calculation_trace': self.calculation_trace,
            'timestamp': datetime.now().isoformat()
        }
        
        # Financial requirements removed - was only partially implemented
        
        self._log_trace("calculation_end", {
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
            
        self._log_trace("trade_breakdown_calculated", {
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
            
        self._log_trace("soft_costs_calculated", {
            'base': construction_cost,
            'total_soft': sum(soft_costs.values())
        })
        
        return soft_costs
    
    def _calculate_ownership(
        self,
        total_cost: float,
        financing_terms: Any,
        revenue_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate ownership/financing metrics with DSCR tied to revenue NOI when available."""
        
        # Calculate debt and equity
        debt_amount = total_cost * financing_terms.debt_ratio
        equity_amount = total_cost * financing_terms.equity_ratio
        philanthropy_amount = total_cost * financing_terms.philanthropy_ratio
        grants_amount = total_cost * financing_terms.grants_ratio
        
        # Calculate debt service
        annual_debt_service = debt_amount * financing_terms.debt_rate
        monthly_debt_service = annual_debt_service / 12
        
        # Prefer NOI from revenue analysis when available so DSCR matches frontend revenue panel
        noi_from_revenue = None
        if revenue_analysis and isinstance(revenue_analysis.get('net_income'), (int, float)):
            noi_from_revenue = float(revenue_analysis['net_income'])
        
        fallback_noi = total_cost * getattr(financing_terms, 'noi_percentage', 0.08)
        estimated_annual_noi = noi_from_revenue if noi_from_revenue is not None else fallback_noi
        dscr = estimated_annual_noi / annual_debt_service if annual_debt_service > 0 else 0
        
        self._log_trace("noi_derived", {
            'total_project_cost': total_cost,
            'estimated_noi': estimated_annual_noi,
            'method': 'revenue_analysis' if noi_from_revenue is not None else 'fixed_percentage'
        })

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
        
        self._log_trace("ownership_analysis_calculated", {
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
                    finish_level=scenario.get('finish_level') or scenario.get('finishLevel'),
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
        
        provided_quality_factor = calculations.get('quality_factor')
        finish_level = calculations.get('finish_level')
        normalized_finish_level = finish_level.lower() if isinstance(finish_level, str) else None

        modifiers = calculations.get('modifiers') or {}
        revenue_factor = float(modifiers.get('revenue_factor', 1.0) or 1.0)
        margin_pct = float(modifiers.get('margin_pct', get_margin_pct(building_enum, subtype)))
        office_operating_expense_override = None
        office_cam_charges = None
        staffing_pct_pm = None
        staffing_pct_maintenance = None
        if building_enum == BuildingType.OFFICE:
            if getattr(subtype_config, 'operating_expense_per_sf', None) and square_footage > 0:
                office_operating_expense_override = square_footage * float(subtype_config.operating_expense_per_sf)
            if getattr(subtype_config, 'cam_charges_per_sf', None) and square_footage > 0:
                office_cam_charges = square_footage * float(subtype_config.cam_charges_per_sf)
            staffing_pct_pm = getattr(subtype_config, 'staffing_pct_property_mgmt', None)
            staffing_pct_maintenance = getattr(subtype_config, 'staffing_pct_maintenance', None)

        base_cost_psf = subtype_config.base_cost_per_sf
        if provided_quality_factor is not None:
            quality_factor = provided_quality_factor
        else:
            actual_cost_psf = construction_cost / square_footage if square_footage > 0 else base_cost_psf
            quality_factor = pow(actual_cost_psf / base_cost_psf, 0.5) if base_cost_psf > 0 else 1.0
            if quality_factor is None:
                quality_factor = 1.0

        if normalized_finish_level in ("premium", "luxury"):
            is_premium = True
        else:
            is_premium = quality_factor > 1.2

        occupancy_rate = subtype_config.occupancy_rate_premium if is_premium else subtype_config.occupancy_rate_base
        if occupancy_rate is None:
            occupancy_rate = 0.85

        annual_revenue = self._calculate_revenue_by_type(
            building_enum, subtype_config, square_footage, quality_factor, occupancy_rate
        )
        
        # Apply revenue modifiers
        annual_revenue *= revenue_factor
        
        margin_pct = margin_pct if margin_pct else get_margin_pct(building_enum, subtype)
        self._log_trace("margin_normalized", {
            'building_type': building_enum.value,
            'subtype': subtype,
            'margin_pct': round(margin_pct, 4)
        })
        if office_operating_expense_override is not None:
            total_expenses = round(office_operating_expense_override, 2)
            if annual_revenue > 0:
                margin_pct = max(0.05, min(0.65, 1 - (total_expenses / annual_revenue)))
        else:
            total_expenses = round(annual_revenue * (1 - margin_pct), 2)

        net_income = round(annual_revenue - total_expenses, 2)
        cam_charges_value = round(office_cam_charges, 2) if office_cam_charges is not None else round(float(calculations.get('cam_charges', 0) or 0), 2)
        market_cap_rate_config = getattr(subtype_config, 'market_cap_rate', None)
        yield_on_cost = net_income / total_cost if total_cost > 0 else 0
        cap_rate_spread_bps = None
        if isinstance(market_cap_rate_config, (int, float)):
            cap_rate_spread_bps = int(round((yield_on_cost - market_cap_rate_config) * 10000))

        property_mgmt_staff_cost = None
        maintenance_staff_cost = None
        if building_enum == BuildingType.OFFICE and total_expenses > 0:
            prop_pct = float(staffing_pct_pm or 0.06)
            maint_pct = float(staffing_pct_maintenance or 0.12)
            property_mgmt_staff_cost = round(total_expenses * prop_pct, 2)
            maintenance_staff_cost = round(total_expenses * maint_pct, 2)

        operational_efficiency = self.calculate_operational_efficiency(
            revenue=annual_revenue,
            config=subtype_config,
            subtype=subtype,
            margin_pct=margin_pct,
            total_expenses_override=total_expenses
        )
        total_expenses = operational_efficiency.get('total_expenses', total_expenses)
        operating_margin = round(margin_pct, 3) if annual_revenue > 0 else 0
        expense_ratio = round(1 - margin_pct, 3) if annual_revenue > 0 else 0
        operational_efficiency['operating_margin'] = operating_margin
        operational_efficiency['expense_ratio'] = expense_ratio
        operational_efficiency['efficiency_score'] = round(margin_pct * 100, 1) if annual_revenue > 0 else 0
        if property_mgmt_staff_cost is not None:
            operational_efficiency['property_mgmt_staffing'] = property_mgmt_staff_cost
        if maintenance_staff_cost is not None:
            operational_efficiency['maintenance_staffing'] = maintenance_staff_cost
        operational_efficiency['cam_charges'] = cam_charges_value
        
        # Standard projection period for IRR calculation
        years = 10

        property_value = None
        market_cap_rate = None

        if net_income <= 0:
            npv = -total_cost
            irr = 0.0
            property_value = 0
        else:
            logger.info(f"🏢 Building enum check: {building_enum} == {BuildingType.MULTIFAMILY}? {building_enum == BuildingType.MULTIFAMILY}")
            if building_enum == BuildingType.MULTIFAMILY:
                market_cap_rate = getattr(subtype_config, 'market_cap_rate', 0.06)
                property_value = net_income / market_cap_rate if market_cap_rate > 0 else 0
                npv = property_value - total_cost
                logger.info(f"🏢 Multifamily Cap Rate Valuation:")
                logger.info(f"   NOI: ${net_income:,.0f}")
                logger.info(f"   Cap Rate: {market_cap_rate:.1%}")
                logger.info(f"   Property Value: ${property_value:,.0f}")
                logger.info(f"   NPV: ${npv:,.0f}")
                try:
                    irr = self.calculate_irr_with_terminal_value(
                        initial_investment=total_cost,
                        annual_cash_flow=net_income,
                        terminal_value=property_value,
                        years=years
                    ) if property_value else 0.0
                except OverflowError:
                    irr = 0.0
            else:
                discount_rate = getattr(subtype_config, 'discount_rate', None) or 0.08
                npv = self.calculate_npv(
                    initial_investment=total_cost,
                    annual_cash_flow=net_income,
                    years=years,
                    discount_rate=discount_rate
                )
                try:
                    irr = self.calculate_irr(
                        initial_investment=total_cost,
                        annual_cash_flow=net_income,
                        years=years
                    )
                except OverflowError:
                    irr = 0.0
        
        revenue_requirements = self.calculate_revenue_requirements(
            total_cost=total_cost,
            config=subtype_config,
            square_footage=square_footage,
            actual_annual_revenue=annual_revenue,
            actual_net_income=net_income,
            margin_pct=margin_pct
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
        
        cash_on_cash_return_pct = round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0
        cap_rate_pct = round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0

        target_roi = get_target_roi(building_enum)
        feasible = (npv >= 0) and ((cash_on_cash_return_pct / 100) >= target_roi)

        self._log_trace("feasibility_evaluated", {
            'roi': cash_on_cash_return_pct,
            'target_roi': target_roi,
            'npv': npv,
            'feasible': feasible
        })

        default_vacancy_rate = 0.0
        if isinstance(occupancy_rate, (int, float)):
            default_vacancy_rate = max(0.0, min(1.0, 1.0 - occupancy_rate))

        underwriting = calculations.get('underwriting')
        if not underwriting:
            underwriting = {
                'effective_gross_income': round(annual_revenue, 2),
                'underwritten_operating_expenses': round(total_expenses, 2),
                'underwritten_noi': round(net_income, 2),
                'vacancy_rate': default_vacancy_rate,
                'collection_loss': 0.0,
                'management_fee': 0.0,
                'capex_reserve': 0.0,
            }

        return {
            'revenue_analysis': {
                'annual_revenue': round(annual_revenue, 2),
                'revenue_per_sf': round(annual_revenue / square_footage, 2) if square_footage > 0 else 0,
                'operating_margin': operating_margin,
                'net_income': round(net_income, 2),
                'underwritten_noi': round(underwriting.get('underwritten_noi', net_income), 2),
                'operating_expenses': round(total_expenses, 2),
                'cam_charges': cam_charges_value,
                'occupancy_rate': occupancy_rate,
                'quality_factor': round(quality_factor, 2),
                'is_premium': is_premium,
                'revenue_factor': round(revenue_factor, 4),
                'finish_revenue_factor': round(modifiers.get('finish_revenue_factor', 1.0), 4),
                'regional_multiplier': round(modifiers.get('market_factor', 1.0), 4)
            },
            'return_metrics': {
                'estimated_annual_noi': round(net_income, 2),
                'cash_on_cash_return': cash_on_cash_return_pct,
                'cap_rate': cap_rate_pct,
                'npv': npv,
                'irr': round(irr * 100, 2),  # Convert to percentage
                'payback_period': payback_period,
                'property_value': property_value,  # Always include the value
                'market_cap_rate': market_cap_rate,  # Always include the rate
                'is_multifamily': building_enum == BuildingType.MULTIFAMILY,  # Debug flag
                'feasible': feasible
            },
            'yield_on_cost': round(yield_on_cost, 4),
            'market_cap_rate': round(market_cap_rate_config, 4) if isinstance(market_cap_rate_config, (int, float)) else None,
            'cap_rate_spread_bps': cap_rate_spread_bps,
            'revenue_requirements': revenue_requirements,
            'operational_efficiency': operational_efficiency,  # Keep raw data
            'operational_metrics': operational_metrics,  # ADD formatted display data
            'underwriting': underwriting
        }

    def _calculate_revenue_by_type(self, building_enum, config, square_footage, quality_factor, occupancy_rate):
        """Calculate revenue based on the specific building type's metrics"""
        
        # Initialize base_revenue to avoid uninitialized variable
        base_revenue = 0
        
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
        # Ensure no None values
        base_revenue = base_revenue or 0
        quality_factor = quality_factor or 1.0
        occupancy_rate = occupancy_rate or 0.85
        
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
    
    def calculate_irr_with_terminal_value(self, initial_investment: float, annual_cash_flow: float,
                                         terminal_value: float, years: int = 10) -> float:
        """
        Calculate IRR including terminal value (property sale) at end of investment period.
        Used for real estate investments where property value is realized at exit.
        """
        if initial_investment <= 0:
            return 0.0
        
        # Newton-Raphson method for IRR with terminal value
        rate = 0.1  # Initial guess
        for _ in range(50):  # More iterations for complex calculation
            npv = -initial_investment
            dnpv = 0
            
            # Annual cash flows
            for year in range(1, years + 1):
                npv += annual_cash_flow / ((1 + rate) ** year)
                dnpv -= year * annual_cash_flow / ((1 + rate) ** (year + 1))
            
            # Terminal value at end of last year
            npv += terminal_value / ((1 + rate) ** years)
            dnpv -= years * terminal_value / ((1 + rate) ** (years + 1))
            
            if abs(npv) < 0.01:  # Converged
                break
            
            # Update rate estimate
            if dnpv != 0:
                new_rate = rate - npv / dnpv
                # Bound the rate to prevent divergence
                if new_rate < -0.99:
                    new_rate = -0.99
                elif new_rate > 10:
                    new_rate = 10
                rate = new_rate
            else:
                break
        
        return round(rate, 4)

    def calculate_revenue_requirements(
        self,
        total_cost: float,
        config,
        square_footage: float,
        actual_annual_revenue: float = 0,
        actual_net_income: float = 0,
        margin_pct: Optional[float] = None
    ) -> dict:
        """
        Calculate revenue requirements comparing actual projected returns to required returns.
        This determines true feasibility based on whether the project meets ROI targets.
        """
        
        # Target ROI (use config if available, otherwise default)
        target_roi = getattr(config, 'target_roi', 0.08)
        
        # Calculate required annual return (what investor needs)
        required_annual_return = total_cost * target_roi
        
        # Use ACTUAL projected revenue and profit from the project
        # This is what the project will actually generate
        
        # For feasibility, compare actual profit to required return
        # NOT theoretical market capacity
        if actual_net_income > 0:
            gap = actual_net_income - required_annual_return
            gap_percentage = (gap / required_annual_return) * 100 if required_annual_return > 0 else 0
            
            # Feasibility based on whether actual returns meet requirements
            if gap >= 0:
                feasibility = 'Feasible'
            elif gap >= -required_annual_return * 0.2:  # Within 20% of target
                feasibility = 'Marginal'
            else:
                feasibility = 'Not Feasible'
        else:
            gap = -required_annual_return
            gap_percentage = -100
            feasibility = 'Not Feasible'
        
        # Normalize operating margin using provided margin or config hints
        normalized_margin = margin_pct
        if normalized_margin is None and getattr(config, 'operating_margin_base', None) is not None:
            normalized_margin = getattr(config, 'operating_margin_base')
        if normalized_margin is None and getattr(config, 'financial_metrics', None):
            normalized_margin = config.financial_metrics.get('operating_margin')
        if normalized_margin is None and getattr(config, 'operating_margin_premium', None) is not None:
            normalized_margin = getattr(config, 'operating_margin_premium')
        if normalized_margin is None:
            normalized_margin = 0.20
        normalized_margin = max(0.05, min(0.40, normalized_margin))
        operating_margin = normalized_margin
        
        # Simple payback calculation using actual net income
        simple_payback_years = round(total_cost / actual_net_income, 1) if actual_net_income > 0 else 999
        
        # ALWAYS return this exact structure
        # The Revenue Requirements card expects these exact fields
        return {
            # Core fields for Revenue Requirements card
            'required_value': round(required_annual_return, 2),
            'market_value': round(actual_annual_revenue, 2),  # Now shows actual projected revenue
            'feasibility': feasibility,
            'gap': round(gap, 2),
            'gap_percentage': round(gap_percentage, 1),
            
            # Additional fields for debugging/clarity
            'actual_net_income': round(actual_net_income, 2),
            
            # Additional display fields
            'metric_name': 'Annual Return Required',
            'required_revenue_per_sf': round(required_annual_return / square_footage, 2) if square_footage > 0 else 0,
            'actual_revenue_per_sf': round(actual_annual_revenue / square_footage, 2) if square_footage > 0 else 0,
            'target_roi': target_roi,
            'operating_margin': round(operating_margin, 3),
            'break_even_revenue': round(total_cost * 0.1, 2),  # Simple 10% of cost
            'required_monthly': round(required_annual_return / 12, 2),
            
            # Simple payback for the card
            'simple_payback_years': simple_payback_years,
            
            # Detailed feasibility for additional context
            'feasibility_detail': {
                'status': feasibility,
                'gap': round(gap, 2),
                'recommendation': self._get_revenue_feasibility_recommendation(gap, square_footage)
            }
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
        
        # SAFETY CHECK - Handle None/empty operational_efficiency
        if not operational_efficiency:
            return operational_metrics
        
        # SAFETY CHECK - Ensure numeric values aren't None
        annual_revenue = float(annual_revenue or 0)
        square_footage = float(square_footage or 1)  # Avoid division by zero
        units = int(units or 0)
        
        # Get data from operational_efficiency with safe defaults
        labor_cost = float(operational_efficiency.get('labor_cost', 0) or 0)
        total_expenses = float(operational_efficiency.get('total_expenses', 0) or 0)
        operating_margin = float(operational_efficiency.get('operating_margin', 0) or 0)
        efficiency_score = float(operational_efficiency.get('efficiency_score', 0) or 0)
        expense_ratio = float(operational_efficiency.get('expense_ratio', 0) or 0)
        
        # Building-type specific metrics
        if building_type == 'restaurant':
            food_cost = float(operational_efficiency.get('food_cost', 0) or 0)
            beverage_cost = float(operational_efficiency.get('beverage_cost', 0) or 0)
            
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
            property_mgmt_staffing = float(
                operational_efficiency.get('property_mgmt_staffing', operational_efficiency.get('management_fee', 0)) or 0
            )
            maintenance_staffing = float(
                operational_efficiency.get('maintenance_staffing', operational_efficiency.get('maintenance_cost', 0)) or 0
            )
            cam_charges = float(operational_efficiency.get('cam_charges', 0) or 0)
            rent_per_sf = (annual_revenue / square_footage) if square_footage > 0 else 0
            operating_expenses_per_sf = (total_expenses / square_footage) if square_footage > 0 else 0
            cam_per_sf = (cam_charges / square_footage) if square_footage > 0 else 0

            operational_metrics['staffing'] = [
                {'label': 'Property Mgmt', 'value': f'${property_mgmt_staffing:,.0f}'},
                {'label': 'Maintenance', 'value': f'${maintenance_staffing:,.0f}'}
            ]
            
            operational_metrics['revenue'] = {
                'Rent per SF': f'${rent_per_sf:.2f}/yr' if square_footage > 0 else 'N/A',
                'Operating Expenses': f'${total_expenses:,.0f} (${operating_expenses_per_sf:.2f}/SF)',
                'CAM Charges': (
                    f'${cam_charges:,.0f} (${cam_per_sf:.2f}/SF)' if cam_charges > 0 and square_footage > 0 else 'Included in lease'
                ),
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
                    'value': f'${operating_expenses_per_sf:.2f}' if square_footage > 0 else 'N/A',
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

    def calculate_operational_efficiency(
        self,
        revenue: float,
        config,
        subtype: str = None,
        margin_pct: Optional[float] = None,
        total_expenses_override: Optional[float] = None
    ) -> dict:
        """Calculate operational efficiency metrics from config ratios and normalized margin."""
        result = {
            'total_expenses': 0,
            'operating_margin': 0,
            'efficiency_score': 0,
            'expense_ratio': 0
        }
        
        # For manufacturing, separate facility expenses from business operations
        exclude_from_facility_opex = []
        if subtype == 'manufacturing':
            # These are business operations, not real estate facility expenses
            exclude_from_facility_opex = ['labor_cost_ratio', 'raw_materials_ratio']
        
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
            ('janitorial', 'janitorial_ratio'),
            ('rooms_operations', 'rooms_operations_ratio'),
            ('food_beverage', 'food_beverage_ratio'),
            ('sales_marketing', 'sales_marketing_ratio'),
            ('floor_plan_interest', 'floor_plan_interest_ratio'),
            ('materials', 'materials_ratio'),
            ('raw_materials', 'raw_materials_ratio'),  # Added this mapping
            ('program_costs', 'program_costs_ratio'),
            ('equipment', 'equipment_ratio'),
            ('chemicals', 'chemicals_ratio'),
            ('event_costs', 'event_costs_ratio'),
            ('software_fees', 'software_fees_ratio'),
            ('other_expenses', 'other_expenses_ratio'),
            ('monitoring_cost', 'monitoring_cost_ratio'),  # Added for cold storage
            ('connectivity', 'connectivity_ratio'),  # Added for data center
        ]
        
        # Calculate expenses
        expense_details = {}
        raw_total_expenses = 0
        for name, attr in expense_mappings:
            # Skip business operation expenses for manufacturing
            if attr in exclude_from_facility_opex:
                continue
                
            if hasattr(config, attr):
                ratio = getattr(config, attr)
                if ratio and ratio > 0:
                    cost = revenue * ratio
                    expense_details[name] = cost
                    raw_total_expenses += cost

        # Determine target expenses based on provided overrides or margin
        if total_expenses_override is not None:
            target_total_expenses = round(total_expenses_override, 2)
        elif margin_pct is not None and revenue > 0:
            target_total_expenses = round(revenue * (1 - margin_pct), 2)
        else:
            target_total_expenses = round(raw_total_expenses, 2)

        # Scale detailed expenses to match the normalized total
        if raw_total_expenses > 0 and target_total_expenses > 0:
            scale_factor = target_total_expenses / raw_total_expenses
            scaled_sum = 0
            for key, value in expense_details.items():
                scaled_value = round(value * scale_factor, 2)
                expense_details[key] = scaled_value
                scaled_sum += scaled_value

            # Adjust for rounding drift by applying difference to the first key
            adjustment = round(target_total_expenses - scaled_sum, 2)
            if adjustment and expense_details:
                first_key = next(iter(expense_details))
                expense_details[first_key] = round(expense_details[first_key] + adjustment, 2)
        elif not expense_details and target_total_expenses > 0:
            # If no detailed breakdown but expenses exist, record as generic operating expense
            expense_details['operating_expenses'] = target_total_expenses

        result.update({key: value for key, value in expense_details.items()})
        result['total_expenses'] = target_total_expenses

        if revenue > 0:
            normalized_margin = margin_pct if margin_pct is not None else (1 - (target_total_expenses / revenue))
            normalized_margin = max(0.0, normalized_margin)
            result['operating_margin'] = round(normalized_margin, 3)
            result['efficiency_score'] = round(normalized_margin * 100, 1)
            result['expense_ratio'] = round(1 - normalized_margin, 3)
        else:
            result['operating_margin'] = round(margin_pct or 0, 3) if margin_pct is not None else 0
            result['efficiency_score'] = 0
            result['expense_ratio'] = 0
        
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
                                 location: str = "Nashville",
                                 finish_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Estimate costs from a natural language description
        
        Args:
            description: Natural language project description
            square_footage: Total square footage
            location: City/location for regional multiplier
            finish_level: Optional explicit finish level override
            
        Returns:
            Cost estimate with detected building type
        """
        # Detect building type from description
        detection = detect_building_type_with_method(description)

        if not detection:
            return {
                'error': 'Could not detect building type from description',
                'description': description
            }
        
        building_type, subtype, detection_method = detection
        
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
        
        inferred_finish_level, explicit_factor = infer_finish_level(description)
        finish_source = 'default'
        finish_for_calculation: Optional[str] = None

        if finish_level:
            finish_for_calculation = finish_level
            finish_source = 'explicit'
        elif inferred_finish_level:
            finish_for_calculation = inferred_finish_level
            finish_source = 'description'

        # Calculate with detected parameters
        result = self.calculate_project(
            building_type=building_type,
            subtype=subtype,
            square_footage=square_footage,
            location=location,
            project_class=project_class,
            finish_level=finish_for_calculation,
            finish_level_source=finish_source
        )

        self._log_trace("nlp_detected", {
            'building_type': building_type.value,
            'subtype': subtype,
            'method': detection_method
        })

        if inferred_finish_level or explicit_factor is not None:
            self._log_trace("finish_level_inferred", {
                'from': 'description',
                'finish_level': inferred_finish_level,
                'explicit_factor': explicit_factor
            })
        if explicit_factor is not None:
            self._log_trace("finish_factor_inferred", {
                'factor': explicit_factor
            })
        
        # Add detection info
        result['detection_info'] = {
            'detected_type': building_type.value,
            'detected_subtype': subtype,
            'detected_class': project_class.value,
            'original_description': description,
            'method': detection_method
        }
        
        return result
    
    # REMOVED DUPLICATE calculate_revenue_requirements - using the one at line 710
    # REMOVED DUPLICATE calculate_operational_efficiency - using the one at line 977
    
    def get_market_rate(self, building_type: str, subtype: str, location: str, 
                        rate_type: str, default_rate: float) -> float:
        """
        Get market-specific rates based on location.
        Eventually this should pull from a real market data API.
        """
        # Location multipliers (simplified - should use real data)
        location_multipliers = {
            'Nashville, TN': 1.0,
            'New York, NY': 1.8,
            'San Francisco, CA': 1.7,
            'Los Angeles, CA': 1.5,
            'Chicago, IL': 1.2,
            'Austin, TX': 1.15,
            'Miami, FL': 1.3,
            'Denver, CO': 1.1,
            'Seattle, WA': 1.4,
            'Boston, MA': 1.5,
            'Dallas, TX': 1.05,
            'Atlanta, GA': 1.0,
            'Phoenix, AZ': 0.95,
            'Las Vegas, NV': 0.9,
            'Detroit, MI': 0.7
        }
        
        multiplier = location_multipliers.get(location, 1.0)
        
        # Apply multiplier to default rate
        adjusted_rate = default_rate * multiplier
        
        # Add some variance based on building quality/class
        if 'luxury' in subtype.lower() or 'class_a' in subtype.lower():
            adjusted_rate *= 1.15
        elif 'affordable' in subtype.lower() or 'class_c' in subtype.lower():
            adjusted_rate *= 0.75
        
        return adjusted_rate
    
    def format_financial_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the financial requirements for display.
        Add visual indicators and recommendations.
        """
        if not requirements:
            return {}
        
        # Add visual status indicators
        feasibility = requirements.get('feasibility', {}).get('status', 'Unknown')
        
        if feasibility == 'Feasible':
            requirements['overall_status'] = {
                'status': 'success',
                'message': 'Market rates support project requirements',
                'icon': '✅'
            }
        elif 'Optimization' in feasibility:
            requirements['overall_status'] = {
                'status': 'warning',
                'message': 'Consider value engineering or phasing',
                'icon': '⚠️'
            }
        else:
            requirements['overall_status'] = {
                'status': 'error',
                'message': 'Significant gap between cost and market',
                'icon': '❌'
            }
        
        return requirements
    
    def _get_revenue_feasibility_recommendation(self, gap: float, square_footage: float) -> str:
        """Generate feasibility recommendations for revenue requirements."""
        if gap >= 0:
            return "Project meets market revenue expectations"
        elif abs(gap) < 1000000:
            return "Minor revenue optimization needed through operational efficiency"
        elif abs(gap) < 5000000:
            return "Consider phased development or value engineering to reduce costs"
        else:
            return "Significant restructuring required to achieve feasibility"
    
    def _get_feasibility_recommendation(self, gap: float, unit_type: str) -> str:
        """Generate feasibility recommendations based on gap analysis."""
        if gap <= 0:
            return f"Project is financially feasible at current market rates"
        elif gap < 1000000:
            return f"Minor optimization needed: Consider value engineering or phasing"
        elif gap < 5000000:
            return f"Moderate gap: Explore alternative financing or reduce scope"
        else:
            return f"Significant feasibility gap: Major restructuring required"
    
    def _get_efficiency_rating(self, score: float) -> str:
        """Convert efficiency score to rating."""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Average'
        elif score >= 45:
            return 'Below Average'
        else:
            return 'Poor'
    
    def _get_efficiency_recommendations(self, score: float) -> List[str]:
        """Generate efficiency recommendations based on score."""
        recommendations = []
        
        if score < 60:
            recommendations.append("Consider operational improvements to increase efficiency")
            recommendations.append("Review staffing levels and automation opportunities")
        elif score < 75:
            recommendations.append("Explore revenue optimization strategies")
            recommendations.append("Benchmark against industry best practices")
        elif score < 90:
            recommendations.append("Minor optimizations could improve margins")
            recommendations.append("Consider premium service offerings")
        else:
            recommendations.append("Maintain current operational excellence")
            recommendations.append("Share best practices across portfolio")
        
        return recommendations

    # REMOVED calculate_financial_requirements - was only partially implemented for hospital
    # This feature should be rebuilt properly after launch based on user needs
    
    # REMOVED DUPLICATE get_market_rate - using the one at line 1134
    
    # REMOVED assess_feasibility - was part of financial requirements feature
    # This was only partially implemented and should be rebuilt properly after launch

# Create a singleton instance
unified_engine = UnifiedEngine()
