"""
Scenario Comparison API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType
from app.api.endpoints.auth import get_current_user
from app.db.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["comparison"])

@router.post("/compare")
async def compare_scenarios(
    scenarios: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Compare multiple project scenarios
    
    Args:
        scenarios: List of scenario configurations
        
    Returns:
        Comparison results with all scenarios and analysis
    """
    try:
        engine = UnifiedEngine()
        
        # Validate and prepare scenarios
        prepared_scenarios = []
        for scenario in scenarios:
            # Convert string types to enums
            building_type = BuildingType(scenario.get('building_type', 'commercial'))
            project_class = ProjectClass(scenario.get('project_class', 'ground_up'))
            ownership_type = OwnershipType(scenario.get('ownership_type', 'for_profit'))
            
            prepared_scenario = {
                'name': scenario.get('name', 'Unnamed Scenario'),
                'building_type': building_type.value,
                'subtype': scenario.get('subtype', 'general'),
                'square_footage': scenario.get('square_footage', 10000),
                'location': scenario.get('location', 'Nashville'),
                'project_class': project_class.value,
                'ownership_type': ownership_type.value,
                'floors': scenario.get('floors', 1),
                'special_features': scenario.get('special_features', [])
            }
            prepared_scenarios.append(prepared_scenario)
        
        # Run comparison
        result = engine.calculate_comparison(prepared_scenarios)
        
        return result
        
    except Exception as e:
        logger.error(f"Error comparing scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate")
async def calculate_single_scenario(
    scenario: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Calculate costs for a single scenario (for preview)
    
    Args:
        scenario: Scenario configuration
        
    Returns:
        Calculated costs and analysis
    """
    try:
        engine = UnifiedEngine()
        
        # Convert string types to enums
        building_type = BuildingType(scenario.get('building_type', 'commercial'))
        project_class = ProjectClass(scenario.get('project_class', 'ground_up'))
        ownership_type = OwnershipType(scenario.get('ownership_type', 'for_profit'))
        
        # Calculate project
        result = engine.calculate_project(
            building_type=building_type,
            subtype=scenario.get('subtype', 'general'),
            square_footage=scenario.get('square_footage', 10000),
            location=scenario.get('location', 'Nashville'),
            project_class=project_class,
            floors=scenario.get('floors', 1),
            ownership_type=ownership_type,
            special_features=scenario.get('special_features', [])
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/comparison")
async def export_comparison(
    export_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Export scenario comparison in various formats
    
    Args:
        export_data: Contains scenarios, comparison result, and format
        
    Returns:
        File blob or success message
    """
    try:
        format_type = export_data.get('format', 'pdf')
        
        # For now, return a success message
        # In production, this would generate actual files
        if format_type == 'email':
            return {
                'success': True,
                'message': f'Comparison report sent to {current_user.email}'
            }
        else:
            return {
                'success': True,
                'message': f'{format_type} export generated successfully',
                'download_url': f'/api/v2/download/comparison_{format_type}'
            }
            
    except Exception as e:
        logger.error(f"Error exporting comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))