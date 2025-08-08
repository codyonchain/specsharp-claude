"""
Cost DNA API endpoints - SEPARATE from existing scope endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.simple_cost_dna_service import SimpleCostDNAService
from app.api.endpoints.auth import get_current_user_optional

router = APIRouter()

class CostDNARequest(BaseModel):
    square_footage: int
    occupancy_type: str
    location: str
    project_classification: str
    description: Optional[str] = ""
    total_cost: Optional[float] = None

@router.post("/generate")
async def generate_cost_dna(
    request: CostDNARequest,
    current_user = Depends(get_current_user_optional)
):
    """
    Generate Cost DNA for a project
    This is a NEW endpoint - doesn't affect existing /generate endpoint
    """
    try:
        service = SimpleCostDNAService()
        cost_dna = service.generate_cost_dna(
            square_footage=request.square_footage,
            occupancy_type=request.occupancy_type,
            location=request.location,
            project_classification=request.project_classification,
            description=request.description,
            total_cost=request.total_cost
        )
        
        return {
            "success": True,
            "cost_dna": cost_dna
        }
    
    except Exception as e:
        # Log error but don't crash
        print(f"Error generating Cost DNA: {e}")
        return {
            "success": False,
            "cost_dna": None,
            "error": str(e)
        }