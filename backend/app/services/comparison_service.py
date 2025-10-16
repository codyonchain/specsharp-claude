from typing import Dict, List, Optional, Any, Tuple
import copy
from app.models.scope import ScopeRequest, ScopeResponse
from app.v2.engines.unified_engine import unified_engine
from app.services.floor_plan_service import floor_plan_service
import json


class ComparisonService:
    def __init__(self):
        self.max_scenarios = 3
        
    def create_scenario_comparison(self, base_project: Dict, scenarios: List[Dict]) -> Dict[str, Any]:
        """Create a comparison between multiple scenarios"""
        
        if len(scenarios) > self.max_scenarios:
            raise ValueError(f"Maximum {self.max_scenarios} scenarios allowed")
        
        # First, add the base scenario
        base_scenario_result = self._create_base_scenario(base_project)
        scenario_results = [base_scenario_result]
        
        # Generate scope for each additional scenario
        for i, scenario_params in enumerate(scenarios):
            try:
                scope_result = self._generate_scenario(base_project, scenario_params, i + 1)
                scenario_results.append(scope_result)
            except Exception as e:
                raise ValueError(f"Failed to generate scenario {i + 1}: {str(e)}")
        
        # Calculate deltas and analysis
        comparison_analysis = self._analyze_scenarios(scenario_results)
        
        # Generate comparison visualization data
        visualization_data = self._generate_visualization_data(scenario_results)
        
        return {
            'scenarios': scenario_results,
            'analysis': comparison_analysis,
            'visualization': visualization_data,
            'summary': self._generate_summary(scenario_results, comparison_analysis)
        }
    
    def _create_base_scenario(self, base_project: Dict) -> Dict:
        """Create the base scenario from existing project data"""
        scenario_data = copy.deepcopy(base_project)
        scenario_data['scenario_id'] = 'scenario_0'
        scenario_data['scenario_name'] = 'Current Design'
        scenario_data['modifications'] = {}
        return scenario_data
    
    def _generate_scenario(self, base_project: Dict, scenario_params: Dict, index: int) -> Dict:
        """Generate a new scenario based on modified parameters"""
        
        # Create a copy of the base request data
        base_request = base_project.get('request_data', {})
        
        # Create new scope request with modified parameters
        modified_request = self._apply_scenario_modifications(base_request, scenario_params)
        
        # Ensure project_type is properly formatted
        if 'project_type' in modified_request and isinstance(modified_request['project_type'], str):
            # Keep as string - ScopeRequest will handle the enum conversion
            pass
        
        # Convert to ScopeRequest object
        try:
            scope_request = ScopeRequest(**modified_request)
        except Exception as e:
            raise ValueError(f"Failed to create scope request: {str(e)} - Request data: {modified_request}")
        
        # Generate new scope using clean_engine_v2
        # Convert ScopeRequest to dict for clean_engine_v2
        request_dict = {
            'building_type': scope_request.building_type,
            'building_subtype': scope_request.building_subtype or scope_request.building_type,
            'square_footage': scope_request.square_footage,
            'location': scope_request.location,
            'num_floors': scope_request.num_floors or 1,
            'features': scope_request.building_features or [],
            'finish_level': getattr(scope_request, 'finish_level', 'standard'),
            'project_classification': str(getattr(scope_request, 'project_classification', 'ground_up')),
            'project_name': scope_request.project_name or f"Scenario {index}"
        }
        
        # Calculate scope using unified_engine (V2)
        from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType
        
        # Convert to unified_engine format
        building_type = BuildingType(request_dict.get('building_type', 'office'))
        project_class = ProjectClass(request_dict.get('project_class', 'ground_up'))
        ownership_type = OwnershipType(request_dict.get('ownership_type', 'for_profit'))
        
        calc_result = unified_engine.calculate_project(
            building_type=building_type,
            subtype=request_dict.get('subtype', 'class_b'),
            square_footage=request_dict.get('square_footage', 100000),
            location=request_dict.get('location', 'Nashville'),
            project_class=project_class,
            floors=request_dict.get('floors'),
            ownership_type=ownership_type,
            finish_level=request_dict.get('finish_level'),
            special_features=request_dict.get('special_features', [])
        )
        
        # Fix categories to have subtotal field (for compatibility)
        categories = calc_result.get('categories', [])
        for category in categories:
            # Add subtotal field (clean_engine_v2 uses 'amount' instead)
            if 'amount' in category and 'subtotal' not in category:
                category['subtotal'] = category['amount']
        
        # Convert result to match expected format
        scope_response = {
            'project_id': calc_result.get('project_id'),
            'project_name': calc_result.get('project_name'),
            'categories': categories,
            'total_cost': calc_result.get('total_cost'),
            'cost_per_sqft': calc_result.get('cost_per_sqft'),
            'subtotal': calc_result.get('subtotal'),
            'contingency_percentage': calc_result.get('contingency_percentage', 10),
            'request_data': scope_request.model_dump() if hasattr(scope_request, 'model_dump') else vars(scope_request)
        }
        
        # Generate floor plan for the scenario
        floor_plan_data = floor_plan_service.generate_floor_plan(
            square_footage=scope_request.square_footage,
            project_type=scope_request.building_type,
            building_mix=scope_request.building_mix
        )
        
        # Add scenario metadata
        scenario_data = scope_response if isinstance(scope_response, dict) else scope_response.model_dump()
        scenario_data['floor_plan'] = floor_plan_data
        scenario_data['scenario_id'] = f"scenario_{index + 1}"
        scenario_data['scenario_name'] = scenario_params.get('name', f"Scenario {index + 1}")
        scenario_data['modifications'] = scenario_params
        
        return scenario_data
    
    def _apply_scenario_modifications(self, base_request: Dict, modifications: Dict) -> Dict:
        """Apply modifications to create a new scenario"""
        
        # Deep copy the base request
        modified = copy.deepcopy(base_request)
        
        # Apply square footage change
        if 'square_footage' in modifications:
            modified['square_footage'] = modifications['square_footage']
        
        # Apply building mix changes
        if 'building_mix' in modifications:
            modified['building_mix'] = modifications['building_mix']
            # Ensure it sums to 1.0
            total = sum(modifications['building_mix'].values())
            if abs(total - 1.0) > 0.01:
                # Normalize
                for key in modified['building_mix']:
                    modified['building_mix'][key] /= total
        
        # Apply feature modifications
        if 'features' in modifications:
            features = modifications['features']
            
            # Handle bathroom count
            if 'bathrooms' in features:
                if 'special_requirements' not in modified:
                    modified['special_requirements'] = ""
                
                # Update bathroom count in special requirements
                import re
                bathroom_pattern = r'\d+\s*bathroom'
                if re.search(bathroom_pattern, modified['special_requirements'], re.IGNORECASE):
                    modified['special_requirements'] = re.sub(
                        bathroom_pattern, 
                        f"{features['bathrooms']} bathroom", 
                        modified['special_requirements'],
                        flags=re.IGNORECASE
                    )
                else:
                    modified['special_requirements'] += f" {features['bathrooms']} bathrooms"
            
            # Handle dock doors
            if 'dock_doors' in features:
                if 'special_requirements' not in modified:
                    modified['special_requirements'] = ""
                
                dock_pattern = r'\d+\s*dock\s*door'
                if re.search(dock_pattern, modified['special_requirements'], re.IGNORECASE):
                    modified['special_requirements'] = re.sub(
                        dock_pattern, 
                        f"{features['dock_doors']} dock door", 
                        modified['special_requirements'],
                        flags=re.IGNORECASE
                    )
                else:
                    modified['special_requirements'] += f" {features['dock_doors']} dock doors"
            
            # Handle other features
            for feature, value in features.items():
                if feature not in ['bathrooms', 'dock_doors'] and value:
                    if 'special_requirements' not in modified:
                        modified['special_requirements'] = ""
                    modified['special_requirements'] += f" {feature}"
        
        # Apply other direct modifications
        for key, value in modifications.items():
            if key not in ['building_mix', 'features', 'name']:
                modified[key] = value
        
        return modified
    
    def _analyze_scenarios(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Analyze differences between scenarios"""
        
        if not scenarios:
            return {}
        
        base_scenario = scenarios[0]
        analysis = {
            'cost_deltas': [],
            'feature_differences': [],
            'category_comparisons': {},
            'key_metrics': []
        }
        
        # Calculate cost deltas
        for i, scenario in enumerate(scenarios[1:], 1):
            delta = scenario['total_cost'] - base_scenario['total_cost']
            delta_percentage = (delta / base_scenario['total_cost']) * 100 if base_scenario['total_cost'] > 0 else 0
            
            analysis['cost_deltas'].append({
                'scenario_id': scenario['scenario_id'],
                'scenario_name': scenario['scenario_name'],
                'delta_amount': delta,
                'delta_percentage': delta_percentage,
                'comparison_text': f"{'+'if delta >= 0 else ''}{delta:,.0f} ({delta_percentage:+.1f}%)"
            })
        
        # Compare features
        for scenario in scenarios:
            features = []
            
            # Extract key features from modifications
            mods = scenario.get('modifications', {})
            
            # Square footage
            if 'square_footage' in mods:
                features.append(f"{mods['square_footage']:,} sq ft")
            
            # Building mix
            if 'building_mix' in mods:
                mix_text = ", ".join([f"{int(v*100)}% {k}" for k, v in mods['building_mix'].items()])
                features.append(mix_text)
            
            # Special features
            if 'features' in mods:
                for feature, value in mods['features'].items():
                    if isinstance(value, bool) and value:
                        features.append(feature.replace('_', ' ').title())
                    elif isinstance(value, int):
                        features.append(f"{value} {feature.replace('_', ' ')}")
            
            analysis['feature_differences'].append({
                'scenario_id': scenario['scenario_id'],
                'scenario_name': scenario['scenario_name'],
                'features': features
            })
        
        # Compare categories across scenarios
        all_categories = set()
        for scenario in scenarios:
            for cat in scenario['categories']:
                all_categories.add(cat['name'])
        
        for category in all_categories:
            category_comparison = []
            for scenario in scenarios:
                cat_data = next((c for c in scenario['categories'] if c['name'] == category), None)
                category_comparison.append({
                    'scenario_id': scenario['scenario_id'],
                    'scenario_name': scenario['scenario_name'],
                    'cost': cat_data['subtotal'] if cat_data else 0
                })
            analysis['category_comparisons'][category] = category_comparison
        
        # Key metrics comparison
        for scenario in scenarios:
            analysis['key_metrics'].append({
                'scenario_id': scenario['scenario_id'],
                'scenario_name': scenario['scenario_name'],
                'total_cost': scenario['total_cost'],
                'cost_per_sqft': scenario['cost_per_sqft'],
                'square_footage': scenario['request_data']['square_footage']
            })
        
        return analysis
    
    def _generate_visualization_data(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Generate data for visualization charts"""
        
        # Cost comparison chart data
        cost_comparison = {
            'labels': [s['scenario_name'] for s in scenarios],
            'datasets': [{
                'label': 'Total Cost',
                'data': [s['total_cost'] for s in scenarios],
                'backgroundColor': ['#0088FE', '#00C49F', '#FFBB28']
            }]
        }
        
        # Category breakdown chart data
        all_categories = set()
        for scenario in scenarios:
            for cat in scenario['categories']:
                all_categories.add(cat['name'])
        
        category_breakdown = {
            'labels': [s['scenario_name'] for s in scenarios],
            'datasets': []
        }
        
        colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']
        for i, category in enumerate(all_categories):
            dataset = {
                'label': category,
                'data': [],
                'backgroundColor': colors[i % len(colors)]
            }
            
            for scenario in scenarios:
                cat_data = next((c for c in scenario['categories'] if c['name'] == category), None)
                dataset['data'].append(cat_data['subtotal'] if cat_data else 0)
            
            category_breakdown['datasets'].append(dataset)
        
        # Cost per sqft comparison
        cost_per_sqft = {
            'labels': [s['scenario_name'] for s in scenarios],
            'data': [s['cost_per_sqft'] for s in scenarios]
        }
        
        return {
            'cost_comparison': cost_comparison,
            'category_breakdown': category_breakdown,
            'cost_per_sqft': cost_per_sqft
        }
    
    def _generate_summary(self, scenarios: List[Dict], analysis: Dict) -> Dict[str, Any]:
        """Generate a summary of the comparison"""
        
        if not scenarios:
            return {}
        
        # Find best value scenario
        best_value = min(scenarios, key=lambda s: s['cost_per_sqft'])
        lowest_cost = min(scenarios, key=lambda s: s['total_cost'])
        
        # Calculate ranges
        cost_range = max(s['total_cost'] for s in scenarios) - min(s['total_cost'] for s in scenarios)
        cost_per_sqft_range = max(s['cost_per_sqft'] for s in scenarios) - min(s['cost_per_sqft'] for s in scenarios)
        
        return {
            'scenario_count': len(scenarios),
            'best_value': {
                'scenario_name': best_value['scenario_name'],
                'cost_per_sqft': best_value['cost_per_sqft']
            },
            'lowest_cost': {
                'scenario_name': lowest_cost['scenario_name'],
                'total_cost': lowest_cost['total_cost']
            },
            'cost_range': cost_range,
            'cost_per_sqft_range': cost_per_sqft_range,
            'recommendations': self._generate_recommendations(scenarios, analysis)
        }
    
    def _generate_recommendations(self, scenarios: List[Dict], analysis: Dict) -> List[str]:
        """Generate recommendations based on scenario comparison"""
        
        recommendations = []
        
        if not scenarios:
            return recommendations
        
        # Cost efficiency recommendation
        cost_per_sqft_values = [s['cost_per_sqft'] for s in scenarios]
        if len(set(cost_per_sqft_values)) > 1:
            best_efficiency = min(scenarios, key=lambda s: s['cost_per_sqft'])
            recommendations.append(
                f"{best_efficiency['scenario_name']} offers the best cost efficiency at "
                f"${best_efficiency['cost_per_sqft']:.2f} per sq ft"
            )
        
        # Building mix recommendation
        for scenario in scenarios:
            if 'building_mix' in scenario.get('modifications', {}):
                mix = scenario['modifications']['building_mix']
                if 'warehouse' in mix and mix['warehouse'] > 0.6:
                    recommendations.append(
                        f"{scenario['scenario_name']} with {int(mix['warehouse']*100)}% warehouse "
                        f"maximizes cost savings for storage needs"
                    )
        
        # Feature impact analysis
        for delta in analysis['cost_deltas']:
            if abs(delta['delta_percentage']) > 10:
                direction = "increases" if delta['delta_amount'] > 0 else "decreases"
                recommendations.append(
                    f"{delta['scenario_name']} {direction} cost by {abs(delta['delta_percentage']):.1f}% "
                    f"compared to base scenario"
                )
        
        return recommendations[:3]  # Limit to top 3 recommendations


comparison_service = ComparisonService()
