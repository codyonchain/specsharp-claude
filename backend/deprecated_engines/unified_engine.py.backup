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
from app.v2.services.financial_analyzer import FinancialAnalyzer
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
        self.financial_analyzer = FinancialAnalyzer()  # Add financial analyzer
        
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
            
            # Enhance with comprehensive financial analysis
            financial_data = {
                'building_type': building_type.value,
                'subtype': subtype,
                'square_footage': square_footage,
                'total_project_cost': total_project_cost
            }
            financial_metrics = self.financial_analyzer.analyze_investment(financial_data)
            
            # Merge financial analysis into ownership analysis
            if financial_metrics:
                ownership_analysis.update(financial_metrics['ownership_analysis'])
                # Add additional calculated sections
                ownership_analysis['project_info'] = financial_metrics.get('project_info', {})
                ownership_analysis['department_allocation'] = financial_metrics.get('department_allocation', [])
                ownership_analysis['operational_metrics'] = financial_metrics.get('operational_metrics', {})
                # Add revenue_analysis section
                ownership_analysis['revenue_analysis'] = financial_metrics.get('revenue_analysis', {})
                # Add revenue_requirements section
                ownership_analysis['revenue_requirements'] = financial_metrics.get('revenue_requirements', {})
        
        # Build comprehensive response
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
            'calculations': {
                'construction_costs': {
                    'base_cost_per_sf': base_cost_per_sf,
                    'class_multiplier': class_multiplier,
                    'regional_multiplier': regional_multiplier,
                    'final_cost_per_sf': final_cost_per_sf,
                    'construction_total': construction_cost,
                    'equipment_total': equipment_cost,
                    'special_features_total': special_features_cost
                },
                'trade_breakdown': trades,  # Moved under calculations
                'soft_costs': soft_costs,
                'totals': {
                    'hard_costs': total_hard_costs,
                    'soft_costs': total_soft_costs,
                    'total_project_cost': total_project_cost,
                    'cost_per_sf': total_project_cost / square_footage if square_footage > 0 else 0
                }
            },
            'ownership_analysis': ownership_analysis,
            # Add revenue_analysis at top level for easy access
            'revenue_analysis': ownership_analysis.get('revenue_analysis', {}) if ownership_analysis else {},
            # Add revenue_requirements at top level for easy access
            'revenue_requirements': ownership_analysis.get('revenue_requirements', {}) if ownership_analysis else {},
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