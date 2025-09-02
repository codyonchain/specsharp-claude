"""Service for managing project scenarios and comparisons"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import json
import copy
from datetime import datetime

from app.models.scenario import ProjectScenario, ScenarioModification, SCENARIO_MODIFICATIONS
from app.db.models import Project
from app.services.cost_service import CostService
# V2 imports removed - functionality to be replaced
# from app.v2.services.financial_analyzer import FinancialAnalyzer
# from app.v2.engines.unified_engine import UnifiedEngine
from app.schemas.scenario import ScenarioComparisonResponse, MetricComparison


class ScenarioService:
    """Service for handling scenario operations"""
    
    def __init__(self):
        self.cost_service = CostService()
        # V2 dependencies removed - to be replaced with appropriate services
        # self.financial_analyzer = FinancialAnalyzer()
        # self.unified_engine = UnifiedEngine()
    
    def create_base_scenario(self, db: Session, project: Project, user_id: int) -> ProjectScenario:
        """Create base scenario from existing project"""
        
        # Extract current project metrics
        scope_data = json.loads(project.scope_data) if project.scope_data else {}
        
        base_scenario = ProjectScenario(
            project_id=project.id,
            name="Current Design",
            description="Base scenario from current project configuration",
            is_base=True,
            modifications={},
            total_cost=project.total_cost,
            construction_cost=project.subtotal,
            soft_costs=project.soft_costs or 0,
            cost_per_sqft=project.cost_per_sqft,
            square_footage=project.square_footage,
            unit_count=scope_data.get('units', 1),
            finish_level=scope_data.get('finish_level', 'standard'),
            created_by=user_id,
            calculation_results=scope_data
        )
        
        # Extract financial metrics if available
        if 'analysis' in scope_data:
            analysis = scope_data['analysis']
            if 'calculations' in analysis:
                calcs = analysis['calculations']
                ownership = calcs.get('ownership_analysis', {})
                returns = ownership.get('return_metrics', {})
                
                base_scenario.roi = returns.get('estimated_roi', 0)
                base_scenario.npv = returns.get('ten_year_npv', 0)
                base_scenario.irr = returns.get('irr', 0)
                base_scenario.payback_period = returns.get('payback_period', 0)
                base_scenario.dscr = ownership.get('debt_metrics', {}).get('calculated_dscr', 1.0)
                
                base_scenario.annual_revenue = ownership.get('annual_revenue', 0)
                base_scenario.monthly_revenue = ownership.get('monthly_revenue', 0)
                base_scenario.noi = returns.get('estimated_annual_noi', 0)
        
        db.add(base_scenario)
        db.commit()
        db.refresh(base_scenario)
        
        return base_scenario
    
    def create_scenario(
        self,
        db: Session,
        project: Project,
        name: str,
        description: str,
        modifications: Dict[str, Any],
        user_id: int
    ) -> ProjectScenario:
        """Create a new scenario with modifications"""
        
        # Get or create base scenario
        base_scenario = db.query(ProjectScenario).filter(
            ProjectScenario.project_id == project.id,
            ProjectScenario.is_base == True
        ).first()
        
        if not base_scenario:
            base_scenario = self.create_base_scenario(db, project, user_id)
        
        # Apply modifications to calculate new metrics
        modified_project = self._apply_modifications(project, modifications)
        
        # Create new scenario
        new_scenario = ProjectScenario(
            project_id=project.id,
            name=name,
            description=description,
            is_base=False,
            modifications=modifications,
            total_cost=modified_project['total_cost'],
            construction_cost=modified_project['construction_cost'],
            soft_costs=modified_project['soft_costs'],
            cost_per_sqft=modified_project['cost_per_sqft'],
            square_footage=modified_project['square_footage'],
            unit_count=modified_project.get('unit_count', 1),
            finish_level=modifications.get('finish_level', base_scenario.finish_level),
            roi=modified_project.get('roi', 0),
            npv=modified_project.get('npv', 0),
            irr=modified_project.get('irr', 0),
            payback_period=modified_project.get('payback_period', 0),
            dscr=modified_project.get('dscr', 1.0),
            annual_revenue=modified_project.get('annual_revenue', 0),
            monthly_revenue=modified_project.get('monthly_revenue', 0),
            noi=modified_project.get('noi', 0),
            created_by=user_id,
            calculation_results=modified_project
        )
        
        db.add(new_scenario)
        
        # Track individual modifications
        for param, new_value in modifications.items():
            mod = ScenarioModification(
                scenario_id=new_scenario.id,
                parameter=param,
                original_value=self._get_original_value(base_scenario, param),
                new_value=new_value,
                cost_impact=modified_project['total_cost'] - base_scenario.total_cost,
                roi_impact=modified_project.get('roi', 0) - base_scenario.roi,
                impact_description=self._describe_impact(param, new_value)
            )
            db.add(mod)
        
        db.commit()
        db.refresh(new_scenario)
        
        return new_scenario
    
    def update_scenario(
        self,
        db: Session,
        scenario: ProjectScenario,
        modifications: Dict[str, Any],
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> ProjectScenario:
        """Update scenario and recalculate"""
        
        if name:
            scenario.name = name
        if description:
            scenario.description = description
        
        # Get the base project
        project = scenario.project
        
        # Apply modifications and recalculate
        modified_project = self._apply_modifications(project, modifications)
        
        # Update scenario with new values
        scenario.modifications = modifications
        scenario.total_cost = modified_project['total_cost']
        scenario.construction_cost = modified_project['construction_cost']
        scenario.soft_costs = modified_project['soft_costs']
        scenario.cost_per_sqft = modified_project['cost_per_sqft']
        scenario.roi = modified_project.get('roi', 0)
        scenario.npv = modified_project.get('npv', 0)
        scenario.irr = modified_project.get('irr', 0)
        scenario.payback_period = modified_project.get('payback_period', 0)
        scenario.dscr = modified_project.get('dscr', 1.0)
        scenario.annual_revenue = modified_project.get('annual_revenue', 0)
        scenario.monthly_revenue = modified_project.get('monthly_revenue', 0)
        scenario.noi = modified_project.get('noi', 0)
        scenario.calculation_results = modified_project
        scenario.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(scenario)
        
        return scenario
    
    def calculate_scenario_impact(self, project: Project, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the impact of modifications without saving to database"""
        
        # Apply modifications and calculate results
        modified_results = self._apply_modifications(project, modifications)
        
        # Return the calculated results with additional impact metrics
        base_cost = project.total_cost or 0
        new_cost = modified_results.get('total_cost', base_cost)
        
        return {
            'total_cost': new_cost,
            'construction_cost': modified_results.get('construction_cost', project.subtotal),
            'soft_costs': modified_results.get('soft_costs', project.soft_costs or 0),
            'cost_per_sqft': modified_results.get('cost_per_sqft', project.cost_per_sqft),
            'square_footage': modified_results.get('square_footage', project.square_footage),
            'roi': modified_results.get('roi', 0),
            'npv': modified_results.get('npv', 0),
            'irr': modified_results.get('irr', 0),
            'payback_period': modified_results.get('payback_period', 0),
            'dscr': modified_results.get('dscr', 1.0),
            'annual_revenue': modified_results.get('annual_revenue', 0),
            'monthly_revenue': modified_results.get('monthly_revenue', 0),
            'noi': modified_results.get('noi', 0),
            'cost_delta': new_cost - base_cost,
            'cost_delta_percentage': ((new_cost - base_cost) / base_cost * 100) if base_cost > 0 else 0
        }
    
    def _apply_modifications(self, project: Project, modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Apply modifications to project and recalculate all metrics"""
        
        # Start with base project data
        scope_data = json.loads(project.scope_data) if project.scope_data else {}
        building_type = project.building_type or project.project_type
        
        # Get modification rules for this building type
        mod_rules = SCENARIO_MODIFICATIONS.get(building_type, {})
        
        # Create modified project data
        modified_data = {
            'building_type': building_type,
            'square_footage': project.square_footage,
            'location': project.location,
            'total_project_cost': project.total_cost,
            'subtype': scope_data.get('subtype', '')
        }
        
        # Apply each modification
        for param, new_value in modifications.items():
            if param in mod_rules:
                rule = mod_rules[param]
                modified_data = self._apply_single_modification(
                    modified_data, param, new_value, rule
                )
        
        # Recalculate with modifications
        try:
            # V2 financial analyzer removed - using basic calculation for now
            # TODO: Replace with appropriate financial analysis service
            # result = self.financial_analyzer.analyze_investment(modified_data)
            result = {
                'ownership_analysis': {
                    'return_metrics': {}
                }
            }
            
            # Extract key metrics
            ownership = result.get('ownership_analysis', {})
            returns = ownership.get('return_metrics', {})
            
            modified_data.update({
                'total_cost': modified_data.get('total_project_cost', project.total_cost),
                'construction_cost': modified_data.get('total_project_cost', project.total_cost) * 0.85,
                'soft_costs': modified_data.get('total_project_cost', project.total_cost) * 0.15,
                'cost_per_sqft': modified_data.get('total_project_cost', project.total_cost) / project.square_footage,
                'roi': returns.get('estimated_roi', 0),
                'npv': returns.get('ten_year_npv', 0),
                'irr': returns.get('irr', 0),
                'payback_period': returns.get('payback_period', 0),
                'dscr': ownership.get('debt_metrics', {}).get('calculated_dscr', 1.0),
                'annual_revenue': ownership.get('annual_revenue', 0),
                'monthly_revenue': ownership.get('monthly_revenue', 0),
                'noi': returns.get('estimated_annual_noi', 0),
                'square_footage': modified_data.get('square_footage', project.square_footage),
                'unit_count': modified_data.get('unit_count', 1)
            })
            
        except Exception as e:
            # Fallback to simple calculations
            print(f"Error in financial analysis: {e}")
            modified_data.update({
                'total_cost': modified_data.get('total_project_cost', project.total_cost),
                'construction_cost': project.subtotal,
                'soft_costs': project.soft_costs or 0,
                'cost_per_sqft': project.cost_per_sqft,
                'square_footage': project.square_footage
            })
        
        return modified_data
    
    def _apply_single_modification(
        self,
        data: Dict[str, Any],
        param: str,
        new_value: Any,
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a single modification based on rules"""
        
        if 'options' in rule and 'impact' in rule:
            # Discrete option with predefined impacts
            impact = rule['impact'].get(new_value, {})
            
            if 'cost_multiplier' in impact:
                data['total_project_cost'] *= impact['cost_multiplier']
            
            if 'cost_add' in impact:
                data['total_project_cost'] += impact['cost_add']
            
            if 'revenue_multiplier' in impact:
                data['annual_revenue'] = data.get('annual_revenue', 0) * impact['revenue_multiplier']
            
            if 'rent_premium' in impact:
                data['rent_multiplier'] = 1 + impact['rent_premium']
        
        elif 'min' in rule and 'max' in rule:
            # Numeric range modification
            if param == 'unit_count':
                data['unit_count'] = new_value
                # Adjust square footage if needed
                if 'sf_per_unit' in data:
                    data['square_footage'] = new_value * data['sf_per_unit']
            
            elif param == 'floor_count':
                data['floor_count'] = new_value
                # Could affect costs non-linearly
                if new_value > 10:
                    # Economies of scale for tall buildings
                    data['total_project_cost'] *= (1 - 0.01 * (new_value - 10))
            
            elif param == 'seating_capacity':
                data['seats'] = new_value
                if 'cost_per_seat' in rule:
                    seat_diff = new_value - data.get('original_seats', 120)
                    data['total_project_cost'] += seat_diff * rule['cost_per_seat']
                if 'revenue_per_seat' in rule:
                    data['annual_revenue'] = new_value * rule['revenue_per_seat']
        
        return data
    
    def compare_scenarios(
        self,
        scenarios: List[ProjectScenario],
        comparison_name: Optional[str] = None
    ) -> ScenarioComparisonResponse:
        """Generate comprehensive comparison of scenarios"""
        
        # Prepare comparison data
        metrics_comparison = {
            'total_cost': [],
            'construction_cost': [],
            'soft_costs': [],
            'cost_per_sqft': [],
            'roi': [],
            'npv': [],
            'irr': [],
            'payback_period': [],
            'dscr': [],
            'annual_revenue': [],
            'noi': []
        }
        
        scenario_ids = []
        scenario_names = []
        
        # Collect metrics from each scenario
        for scenario in scenarios:
            scenario_ids.append(scenario.id)
            scenario_names.append(scenario.name)
            
            metrics_comparison['total_cost'].append(scenario.total_cost)
            metrics_comparison['construction_cost'].append(scenario.construction_cost)
            metrics_comparison['soft_costs'].append(scenario.soft_costs)
            metrics_comparison['cost_per_sqft'].append(scenario.cost_per_sqft)
            metrics_comparison['roi'].append(scenario.roi)
            metrics_comparison['npv'].append(scenario.npv)
            metrics_comparison['irr'].append(scenario.irr)
            metrics_comparison['payback_period'].append(scenario.payback_period)
            metrics_comparison['dscr'].append(scenario.dscr)
            metrics_comparison['annual_revenue'].append(scenario.annual_revenue)
            metrics_comparison['noi'].append(scenario.noi)
        
        # Identify winners for each metric
        winner_by_metric = {}
        for metric, values in metrics_comparison.items():
            if metric in ['roi', 'npv', 'irr', 'annual_revenue', 'noi', 'dscr']:
                # Higher is better
                best_idx = values.index(max(values))
            else:
                # Lower is better (costs, payback)
                best_idx = values.index(min(values))
            
            winner_by_metric[metric] = scenario_names[best_idx]
        
        # Calculate deltas from base (first scenario)
        base_scenario = scenarios[0]
        cost_deltas = {}
        roi_deltas = {}
        timeline_deltas = {}
        
        for i, scenario in enumerate(scenarios[1:], 1):
            cost_deltas[scenario.id] = scenario.total_cost - base_scenario.total_cost
            roi_deltas[scenario.id] = scenario.roi - base_scenario.roi
            timeline_deltas[scenario.id] = scenario.payback_period - base_scenario.payback_period
        
        # Determine best overall scenario (weighted scoring)
        scores = []
        for i, scenario in enumerate(scenarios):
            score = 0
            # ROI weight: 40%
            score += (scenario.roi / max(metrics_comparison['roi'])) * 0.4
            # NPV weight: 30%
            if max(metrics_comparison['npv']) > 0:
                score += (scenario.npv / max(metrics_comparison['npv'])) * 0.3
            # Cost efficiency: 20% (inverse)
            score += (min(metrics_comparison['total_cost']) / scenario.total_cost) * 0.2
            # Payback: 10% (inverse)
            score += (min(metrics_comparison['payback_period']) / scenario.payback_period) * 0.1
            scores.append(score)
        
        best_overall_idx = scores.index(max(scores))
        
        # Create detailed metric comparisons
        metric_details = []
        for metric, values in metrics_comparison.items():
            metric_detail = MetricComparison(
                metric_name=metric,
                values=values,
                winner_scenario_id=scenario_ids[winner_by_metric[metric] == scenario_names[winner_by_metric[metric]]],
                winner_scenario_name=winner_by_metric[metric],
                best_value=max(values) if metric in ['roi', 'npv', 'irr'] else min(values),
                worst_value=min(values) if metric in ['roi', 'npv', 'irr'] else max(values),
                delta_from_base=[v - values[0] for v in values]
            )
            metric_details.append(metric_detail)
        
        return ScenarioComparisonResponse(
            comparison_name=comparison_name or f"Comparison of {len(scenarios)} scenarios",
            scenario_ids=scenario_ids,
            scenario_names=scenario_names,
            metrics_comparison=metrics_comparison,
            winner_by_metric=winner_by_metric,
            cost_deltas=cost_deltas,
            roi_deltas=roi_deltas,
            timeline_deltas=timeline_deltas,
            best_overall_scenario=scenario_names[best_overall_idx],
            best_roi_scenario=winner_by_metric['roi'],
            lowest_cost_scenario=winner_by_metric['total_cost'],
            fastest_payback_scenario=winner_by_metric['payback_period'],
            metric_details=metric_details
        )
    
    def _get_original_value(self, base_scenario: ProjectScenario, param: str) -> Any:
        """Get original value for a parameter from base scenario"""
        
        if param == 'finish_level':
            return base_scenario.finish_level
        elif param == 'unit_count':
            return base_scenario.unit_count
        elif param == 'square_footage':
            return base_scenario.square_footage
        else:
            # Check in calculation results
            if base_scenario.calculation_results:
                return base_scenario.calculation_results.get(param)
        
        return None
    
    def _describe_impact(self, param: str, new_value: Any) -> str:
        """Generate human-readable impact description"""
        
        descriptions = {
            'finish_level': {
                'luxury': "Premium finishes add 35% to construction costs but enable 10-15% rent premium",
                'mid_range': "Mid-range finishes add 15% to costs with 5-8% rent premium",
                'standard': "Standard finishes maintain base construction costs"
            },
            'unit_count': f"Adjusting to {new_value} units impacts total square footage and economies of scale",
            'parking_ratio': f"Parking ratio of {new_value} spaces per unit affects construction costs and rental appeal",
            'amenity_package': {
                'premium': "Premium amenities (pool, gym, rooftop) add $1.5M but justify 12% rent premium",
                'standard': "Standard amenities add $500K with 5% rent premium",
                'basic': "Basic amenities minimize additional costs"
            }
        }
        
        if isinstance(descriptions.get(param), dict):
            return descriptions[param].get(new_value, f"Modified {param} to {new_value}")
        else:
            return descriptions.get(param, f"Modified {param} to {new_value}")
    
    def export_comparison_pdf(self, scenarios: List[ProjectScenario], project: Project) -> bytes:
        """Export comparison as PDF (placeholder - would use reportlab or similar)"""
        # This would generate a professional PDF report
        # For now, return placeholder
        return b"PDF export not yet implemented"
    
    def export_comparison_excel(self, scenarios: List[ProjectScenario], project: Project) -> bytes:
        """Export comparison as Excel (placeholder - would use openpyxl)"""
        # This would generate an Excel workbook with multiple sheets
        # For now, return placeholder
        return b"Excel export not yet implemented"
    
    def export_comparison_pptx(self, scenarios: List[ProjectScenario], project: Project) -> bytes:
        """Export comparison as PowerPoint (placeholder - would use python-pptx)"""
        # This would generate a PowerPoint presentation
        # For now, return placeholder
        return b"PowerPoint export not yet implemented"