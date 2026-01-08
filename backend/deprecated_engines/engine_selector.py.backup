"""
Engine Selector - Allows gradual migration from old engine to clean engine
Can be configured via environment variable or feature flag
"""

import os
import logging
from typing import Optional

from app.models.scope import ScopeRequest, ScopeResponse
from app.core.clean_scope_engine import CleanScopeEngine, ScopeRequest as CleanRequest
from app.models.scope import ScopeCategory, BuildingSystem
from datetime import datetime

logger = logging.getLogger(__name__)


class EngineSelector:
    """
    Manages the selection between old and new calculation engines
    Allows for A/B testing and gradual rollout
    """
    
    def __init__(self):
        # Check environment variable for engine selection
        # Options: 'old', 'clean', 'both' (for comparison)
        self.engine_mode = os.getenv('SCOPE_ENGINE_MODE', 'old').lower()
        self.clean_engine = CleanScopeEngine() if self.engine_mode in ['clean', 'both'] else None
        
        # Import old engine only if needed
        if self.engine_mode in ['old', 'both']:
            from app.core.engine import engine as old_engine
            self.old_engine = old_engine
        else:
            self.old_engine = None
        
        logger.info(f"Engine Selector initialized with mode: {self.engine_mode}")
    
    def should_use_clean_engine(self, request: ScopeRequest) -> bool:
        """
        Determine if clean engine should be used for this request
        Can implement gradual rollout logic here
        """
        if self.engine_mode == 'clean':
            return True
        elif self.engine_mode == 'old':
            return False
        elif self.engine_mode == 'both':
            # For 'both' mode, we could implement percentage-based rollout
            # For now, let's use clean engine for specific building types
            priority_types = ['education', 'healthcare', 'restaurant']
            return request.building_type in priority_types
        
        return False
    
    def generate_scope(self, request: ScopeRequest) -> ScopeResponse:
        """
        Generate scope using the appropriate engine
        """
        use_clean = self.should_use_clean_engine(request)
        
        if use_clean and self.clean_engine:
            logger.info("Using CLEAN engine for scope generation")
            return self._generate_with_clean_engine(request)
        elif self.old_engine:
            logger.info("Using OLD engine for scope generation")
            return self.old_engine.generate_scope(request)
        else:
            raise RuntimeError("No engine available for scope generation")
    
    def _generate_with_clean_engine(self, request: ScopeRequest) -> ScopeResponse:
        """
        Generate scope using the clean engine and convert to ScopeResponse
        """
        # Convert to clean engine request
        # Use the actual building_subtype from request, don't default to office for non-office types
        subtype = request.building_subtype
        if not subtype or subtype == 'office':
            # Only use office default if building type is actually office/commercial
            if request.building_type in ['office', 'commercial', None]:
                subtype = 'class_b_office'
            else:
                # For other types, we need to determine appropriate subtype
                subtype_defaults = {
                    'education': 'elementary_school',
                    'healthcare': 'medical_office',
                    'restaurant': 'casual_dining',
                    'industrial': 'warehouse',
                    'retail': 'strip_center',
                    'hospitality': 'limited_service_hotel',
                    'residential': 'market_rate_apartments'
                }
                subtype = subtype_defaults.get(request.building_type, 'class_b_office')
        
        clean_request = CleanRequest(
            building_type=request.building_type or 'commercial',
            building_subtype=subtype,
            square_footage=request.square_footage,
            location=request.location,
            num_floors=request.num_floors or 1,
            features=getattr(request, 'building_features', []) or [],
            finish_level=getattr(request, 'finish_level', 'standard'),
            project_classification=str(getattr(request, 'project_classification', 'ground_up')),
            project_name=request.project_name or 'New Project'
        )
        
        # Calculate using clean engine
        result = self.clean_engine.calculate(clean_request)
        
        # Log the calculation for transparency
        logger.info(f"Clean Engine Calculation:")
        logger.info(f"  Input: {clean_request.building_type}/{clean_request.building_subtype}")
        logger.info(f"  Location: {clean_request.location}")
        logger.info(f"  Features: {clean_request.features}")
        logger.info(f"  Result: ${result['cost_per_sqft']}/SF")
        logger.info(f"  Formula: {result['calculation_breakdown']['formula']}")
        
        # Debug log the breakdown
        logger.info(f"  Base cost: ${result['calculation_breakdown']['base_cost']}")
        logger.info(f"  Equipment: ${result['calculation_breakdown']['equipment_cost']}")
        logger.info(f"  Features: ${result['calculation_breakdown']['feature_cost']}")
        logger.info(f"  Regional: {result['calculation_breakdown']['multipliers']['regional']}")
        
        # Convert to ScopeResponse format
        categories = []
        for category_data in result['categories']:
            systems = []
            for system_data in category_data['systems']:
                system = BuildingSystem(
                    name=system_data['name'],
                    quantity=system_data['quantity'],
                    unit=system_data['unit'],
                    unit_cost=system_data['unit_cost'],
                    total_cost=system_data['total_cost'],
                    confidence_score=95,
                    confidence_label="High"
                )
                systems.append(system)
            
            category = ScopeCategory(
                name=category_data['name'],
                systems=systems
            )
            categories.append(category)
        
        # Create the response
        response = ScopeResponse(
            project_id=result['project_id'],
            project_name=result['project_name'],
            created_at=datetime.utcnow(),
            request_data=request,
            categories=categories,
            contingency_percentage=result['contingency_percentage']
        )
        
        # Log comparison if in 'both' mode
        if self.engine_mode == 'both' and self.old_engine:
            try:
                old_response = self.old_engine.generate_scope(request)
                logger.info(f"ENGINE COMPARISON:")
                logger.info(f"  Clean Engine: ${response.cost_per_sqft}/SF (${response.total_cost:,.0f})")
                logger.info(f"  Old Engine: ${old_response.cost_per_sqft}/SF (${old_response.total_cost:,.0f})")
                diff_percent = ((response.cost_per_sqft - old_response.cost_per_sqft) / old_response.cost_per_sqft) * 100
                logger.info(f"  Difference: {diff_percent:+.1f}%")
            except Exception as e:
                logger.error(f"Failed to generate comparison with old engine: {e}")
        
        return response
    
    def compare_engines(self, request: ScopeRequest) -> dict:
        """
        Compare results from both engines (useful for testing)
        """
        if not (self.clean_engine and self.old_engine):
            return {"error": "Both engines must be available for comparison"}
        
        # Generate with both engines
        clean_response = self._generate_with_clean_engine(request)
        old_response = self.old_engine.generate_scope(request)
        
        return {
            "clean_engine": {
                "cost_per_sqft": clean_response.cost_per_sqft,
                "total_cost": clean_response.total_cost,
                "subtotal": clean_response.subtotal
            },
            "old_engine": {
                "cost_per_sqft": old_response.cost_per_sqft,
                "total_cost": old_response.total_cost,
                "subtotal": old_response.subtotal
            },
            "difference": {
                "cost_per_sqft": clean_response.cost_per_sqft - old_response.cost_per_sqft,
                "total_cost": clean_response.total_cost - old_response.total_cost,
                "percent_diff": ((clean_response.cost_per_sqft - old_response.cost_per_sqft) / old_response.cost_per_sqft * 100)
                    if old_response.cost_per_sqft > 0 else 0
            }
        }


# Create singleton instance
engine_selector = EngineSelector()