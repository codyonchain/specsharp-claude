"""
Simple Cost DNA Service - Lightweight visualization without modifying core calculations
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re


class SimpleCostDNAService:
    """Lightweight service for generating cost DNA visualization"""
    
    def generate_cost_dna(
        self,
        square_footage: int,
        occupancy_type: str,
        location: str,
        project_classification: str,
        description: str = "",
        total_cost: float = None
    ) -> Dict:
        """
        Generate Cost DNA visualization data
        """
        
        # Initialize DNA structure
        cost_dna = {
            "detected_factors": [],
            "applied_adjustments": [],
            "confidence_score": 85,
            "confidence_factors": [],
            "visual_dna": [],
            "market_context": {}
        }
        
        # Detect factors from description
        detected = self._detect_special_factors(description, occupancy_type, project_classification)
        cost_dna["detected_factors"] = detected
        
        # Explain adjustments
        adjustments = self._explain_adjustments(location, project_classification, occupancy_type)
        cost_dna["applied_adjustments"] = adjustments
        
        # Calculate confidence
        confidence, factors = self._calculate_confidence(occupancy_type, location, square_footage)
        cost_dna["confidence_score"] = confidence
        cost_dna["confidence_factors"] = factors
        
        # Generate visual pattern
        cost_dna["visual_dna"] = self._generate_visual_pattern(detected, adjustments)
        
        # Add market context
        cost_dna["market_context"] = {
            "data_version": "RSMeans 2024 Q2",
            "last_updated": datetime.now().isoformat(),
            "regional_index": self._get_regional_index(location)
        }
        
        return cost_dna
    
    def _detect_special_factors(self, description: str, occupancy_type: str, project_classification: str) -> List[Dict]:
        """Detect special factors from description"""
        detected = []
        desc_lower = description.lower()
        
        # Healthcare detection
        if occupancy_type.lower() in ["healthcare", "medical", "hospital"]:
            if any(term in desc_lower for term in ["surgery", "surgical", "operating room"]):
                detected.append({
                    "factor": "Surgical Facilities",
                    "category": "Specialized Systems",
                    "impact": "High",
                    "impact_percentage": "+20%",
                    "description": "Specialized HVAC, medical gas, backup power"
                })
            
            if any(term in desc_lower for term in ["mri", "imaging", "ct scan"]):
                detected.append({
                    "factor": "Medical Imaging",
                    "category": "Specialized Systems",
                    "impact": "Medium",
                    "impact_percentage": "+12%",
                    "description": "RF shielding, reinforcement, special electrical"
                })
        
        # Restaurant detection
        if occupancy_type.lower() == "restaurant":
            if any(term in desc_lower for term in ["kitchen", "commercial kitchen"]):
                detected.append({
                    "factor": "Commercial Kitchen",
                    "category": "Equipment",
                    "impact": "High",
                    "impact_percentage": "+22%",
                    "description": "Hood systems, grease traps, gas lines"
                })
        
        # Project classification factors
        if project_classification == "addition":
            detected.append({
                "factor": "Addition Complexity",
                "category": "Construction",
                "impact": "Medium",
                "impact_percentage": "+15%",
                "description": "Tie-ins, protection, limited access"
            })
        elif project_classification == "renovation":
            detected.append({
                "factor": "Renovation Premium",
                "category": "Construction",
                "impact": "High",
                "impact_percentage": "+35%",
                "description": "Demolition, unknowns, phased work"
            })
        
        return detected
    
    def _explain_adjustments(self, location: str, project_classification: str, occupancy_type: str) -> List[Dict]:
        """Explain cost adjustments"""
        adjustments = []
        
        # Location adjustment
        location_data = {
            "Nashville, TN": (1.02, "2% above national average"),
            "Manchester, NH": (0.99, "1% below national average"),
            "Boston, MA": (1.18, "18% above national average"),
            "San Francisco, CA": (1.35, "35% above national average")
        }
        
        mult = 1.0
        reason = "National average"
        for city, (multiplier, desc) in location_data.items():
            if city.lower() in location.lower():
                mult = multiplier
                reason = desc
                break
        
        adjustments.append({
            "type": "Regional Index",
            "location": location,
            "multiplier": mult,
            "impact_percentage": f"{(mult - 1) * 100:+.1f}%",
            "reason": reason,
            "source": "RSMeans 2024"
        })
        
        return adjustments
    
    def _calculate_confidence(self, occupancy_type: str, location: str, square_footage: int) -> Tuple[int, List[Dict]]:
        """Calculate confidence score"""
        score = 90
        factors = []
        
        # Building type check
        common_types = ["office", "restaurant", "retail", "healthcare"]
        if occupancy_type.lower() in common_types:
            factors.append({
                "factor": f"Common type: {occupancy_type}",
                "impact": 0,
                "status": "positive"
            })
        else:
            score -= 10
            factors.append({
                "factor": "Less common type",
                "impact": -10,
                "status": "caution"
            })
        
        # Size check
        if 5000 <= square_footage <= 100000:
            factors.append({
                "factor": "Typical size range",
                "impact": 0,
                "status": "positive"
            })
        else:
            score -= 5
            factors.append({
                "factor": "Unusual size",
                "impact": -5,
                "status": "info"
            })
        
        return max(score, 70), factors
    
    def _generate_visual_pattern(self, detected: List[Dict], adjustments: List[Dict]) -> List[Dict]:
        """Generate visual DNA pattern"""
        pattern = []
        
        # Add detected factors
        for factor in detected:
            match = re.search(r'\+(\d+)', factor.get("impact_percentage", ""))
            value = int(match.group(1)) if match else 10
            
            pattern.append({
                "label": factor["factor"],
                "value": value,
                "category": factor["category"],
                "color": self._get_category_color(factor["category"])
            })
        
        # Add adjustments
        for adj in adjustments:
            if adj["multiplier"] != 1.0:
                pattern.append({
                    "label": adj["type"],
                    "value": abs((adj["multiplier"] - 1) * 100),
                    "category": "Adjustment",
                    "color": "#6B7280"
                })
        
        return pattern
    
    def _get_category_color(self, category: str) -> str:
        """Get color for category"""
        colors = {
            "Specialized Systems": "#3B82F6",
            "Construction": "#EF4444",
            "Equipment": "#8B5CF6",
            "Adjustment": "#6B7280"
        }
        return colors.get(category, "#6B7280")
    
    def _get_regional_index(self, location: str) -> float:
        """Get regional cost index"""
        indices = {
            "Nashville": 102,
            "Manchester": 99,
            "Boston": 118,
            "San Francisco": 135
        }
        
        for city, index in indices.items():
            if city.lower() in location.lower():
                return index
        return 100