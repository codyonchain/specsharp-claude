"""
Executive Summary Generator for Construction Projects
Provides high-level overview with key metrics and insights
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.utils.formatting import (
    format_currency, format_currency_compact, format_percentage,
    format_square_feet, format_cost_per_sf
)


class ExecutiveSummaryService:
    """Service for generating professional executive summaries"""
    
    def generate_executive_summary(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive executive summary with key insights
        """
        # Extract basic project info
        project_name = project_data.get("project_name", "New Construction Project")
        square_footage = project_data.get("square_footage", 0)
        location = project_data.get("location", "Not specified")
        building_type = project_data.get("building_type", "Commercial")
        floors = project_data.get("floors", 1)
        
        # Calculate totals
        total_cost = self._calculate_total_cost(project_data)
        trade_totals = self._calculate_trade_totals(project_data)
        cost_per_sf = total_cost / square_footage if square_footage > 0 else 0
        
        # Get confidence metrics
        confidence_data = self._calculate_confidence_metrics(project_data)
        
        # Generate summary
        summary = {
            "project_overview": {
                "name": project_name,
                "type": self._format_building_type(building_type),
                "size": format_square_feet(square_footage),
                "floors": f"{floors} {'Floor' if floors == 1 else 'Floors'}",
                "location": location
            },
            
            "cost_summary": {
                "total_project_cost": format_currency(total_cost),
                "cost_per_sf": format_cost_per_sf(total_cost, square_footage),
                "cost_range": self._calculate_cost_range(total_cost, confidence_data['avg_confidence']),
                "contingency": format_currency(total_cost * 0.1),  # 10% contingency
                "total_with_contingency": format_currency(total_cost * 1.1)
            },
            
            "major_systems": self._format_major_systems(trade_totals, total_cost),
            
            "key_metrics": {
                "mechanical_cost_per_sf": format_cost_per_sf(trade_totals.get('mechanical', 0), square_footage),
                "electrical_cost_per_sf": format_cost_per_sf(trade_totals.get('electrical', 0), square_footage),
                "structural_cost_per_sf": format_cost_per_sf(trade_totals.get('structural', 0), square_footage),
                "finishes_cost_per_sf": format_cost_per_sf(trade_totals.get('finishes', 0), square_footage)
            },
            
            "confidence_assessment": {
                "overall_confidence": format_percentage(confidence_data['avg_confidence']),
                "confidence_level": confidence_data['confidence_level'],
                "low_confidence_areas": confidence_data['low_confidence_areas'],
                "data_quality": confidence_data['data_quality']
            },
            
            "key_assumptions": self._generate_key_assumptions(project_data),
            
            "validity": {
                "generated_date": datetime.now().strftime("%B %d, %Y"),
                "valid_until": (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y"),
                "pricing_basis": "Current market conditions"
            },
            
            "next_steps": self._generate_next_steps(project_data, confidence_data),
            
            "risk_factors": self._identify_risk_factors(project_data)
        }
        
        return summary
    
    def generate_compact_summary(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a compact executive summary for quick review
        """
        total_cost = self._calculate_total_cost(project_data)
        square_footage = project_data.get("square_footage", 0)
        cost_per_sf = total_cost / square_footage if square_footage > 0 else 0
        
        return {
            "project": project_data.get("project_name", "New Project"),
            "total_cost": format_currency(total_cost),
            "cost_per_sf": format_cost_per_sf(total_cost, square_footage),
            "size": format_square_feet(square_footage),
            "location": project_data.get("location", "Not specified"),
            "confidence": format_percentage(self._get_average_confidence(project_data)),
            "valid_for": "30 days"
        }
    
    def _calculate_total_cost(self, project_data: Dict[str, Any]) -> float:
        """Calculate total project cost including all trades"""
        total = 0
        categories = project_data.get("categories", [])
        
        for category in categories:
            for system in category.get("systems", []):
                total += system.get("total_cost", 0)
        
        return total
    
    def _calculate_trade_totals(self, project_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate totals by trade"""
        trade_totals = {}
        categories = project_data.get("categories", [])
        
        for category in categories:
            trade_name = category.get("name", "").lower()
            total = sum(system.get("total_cost", 0) for system in category.get("systems", []))
            
            # Group similar trades
            if "electrical" in trade_name:
                trade_totals["electrical"] = trade_totals.get("electrical", 0) + total
            elif "mechanical" in trade_name or "hvac" in trade_name:
                trade_totals["mechanical"] = trade_totals.get("mechanical", 0) + total
            elif "plumbing" in trade_name:
                trade_totals["plumbing"] = trade_totals.get("plumbing", 0) + total
            elif "structural" in trade_name:
                trade_totals["structural"] = trade_totals.get("structural", 0) + total
            elif "finishes" in trade_name:
                trade_totals["finishes"] = trade_totals.get("finishes", 0) + total
            elif "general" in trade_name:
                trade_totals["general_conditions"] = trade_totals.get("general_conditions", 0) + total
            else:
                trade_totals["other"] = trade_totals.get("other", 0) + total
        
        return trade_totals
    
    def _format_major_systems(self, trade_totals: Dict[str, float], total_cost: float) -> List[Dict[str, str]]:
        """Format major systems with costs and percentages"""
        systems = []
        
        for trade, amount in sorted(trade_totals.items(), key=lambda x: x[1], reverse=True):
            if amount > 0:
                percentage = (amount / total_cost * 100) if total_cost > 0 else 0
                systems.append({
                    "system": self._format_trade_name(trade),
                    "cost": format_currency(amount),
                    "percentage": format_percentage(percentage)
                })
        
        return systems
    
    def _format_trade_name(self, trade: str) -> str:
        """Format trade names for display"""
        trade_names = {
            "mechanical": "Mechanical (HVAC)",
            "electrical": "Electrical",
            "plumbing": "Plumbing",
            "structural": "Structural",
            "finishes": "Interior Finishes",
            "general_conditions": "General Conditions",
            "other": "Other Systems"
        }
        return trade_names.get(trade, trade.title())
    
    def _format_building_type(self, building_type: str) -> str:
        """Format building type for display"""
        type_names = {
            "office": "Office Building",
            "retail": "Retail Space",
            "warehouse": "Warehouse/Distribution",
            "industrial": "Industrial Facility",
            "healthcare": "Healthcare Facility",
            "educational": "Educational Building",
            "hospitality": "Hospitality/Hotel",
            "restaurant": "Restaurant",
            "multi_family_residential": "Multi-Family Residential",
            "commercial": "Commercial Building"
        }
        return type_names.get(building_type.lower(), building_type.title())
    
    def _calculate_confidence_metrics(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence metrics from scope items"""
        confidence_scores = []
        low_confidence_items = []
        
        categories = project_data.get("categories", [])
        
        for category in categories:
            for system in category.get("systems", []):
                score = system.get("confidence_score", 95)
                confidence_scores.append(score)
                
                if score < 80:
                    low_confidence_items.append({
                        "item": system.get("name", "Unknown"),
                        "score": score,
                        "category": category.get("name", "Unknown")
                    })
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 95
        
        # Determine confidence level
        if avg_confidence >= 90:
            confidence_level = "High"
            data_quality = "Excellent - Based on current market data"
        elif avg_confidence >= 80:
            confidence_level = "Medium"
            data_quality = "Good - Minor assumptions made"
        else:
            confidence_level = "Low"
            data_quality = "Fair - Significant assumptions required"
        
        return {
            "avg_confidence": avg_confidence,
            "confidence_level": confidence_level,
            "data_quality": data_quality,
            "low_confidence_areas": low_confidence_items[:5]  # Top 5 low confidence items
        }
    
    def _generate_key_assumptions(self, project_data: Dict[str, Any]) -> List[str]:
        """Generate list of key assumptions"""
        assumptions = []
        
        # Location-based assumption
        location = project_data.get("location", "")
        if location:
            assumptions.append(f"Pricing based on {location} regional costs and labor rates")
        else:
            assumptions.append("National average pricing used (location not specified)")
        
        # Markup assumption
        markup = project_data.get("markup_settings", {})
        if markup:
            total_markup = markup.get("combined_markup", 20)
            assumptions.append(f"Includes {format_percentage(total_markup, 0)} contractor overhead and profit")
        else:
            assumptions.append("Standard 20% contractor markup included")
        
        # Standard assumptions
        assumptions.extend([
            "Prevailing wage rates not included unless specified",
            "Normal site conditions assumed",
            "Pricing valid for 30 days from date of estimate",
            "Does not include land costs, permits, or design fees",
            "Based on new construction (not renovation)"
        ])
        
        # Building-specific assumptions
        building_type = project_data.get("building_type", "").lower()
        if building_type == "healthcare":
            assumptions.append("Includes medical gas and specialized healthcare systems")
        elif building_type == "restaurant":
            assumptions.append("Includes commercial kitchen equipment allowance")
        elif building_type == "industrial":
            assumptions.append("Includes basic process utilities (compressed air, process piping)")
        
        return assumptions
    
    def _calculate_cost_range(self, base_cost: float, confidence: float) -> str:
        """Calculate cost range based on confidence level"""
        # Higher confidence = tighter range
        if confidence >= 90:
            variance = 0.05  # +/- 5%
        elif confidence >= 80:
            variance = 0.10  # +/- 10%
        else:
            variance = 0.15  # +/- 15%
        
        low = base_cost * (1 - variance)
        high = base_cost * (1 + variance)
        
        return f"{format_currency_compact(low)} - {format_currency_compact(high)}"
    
    def _generate_next_steps(self, project_data: Dict[str, Any], confidence_data: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps"""
        next_steps = []
        
        # Based on confidence level
        if confidence_data['avg_confidence'] < 80:
            next_steps.append("Refine scope definition for low-confidence items")
            next_steps.append("Obtain subcontractor quotes for specialized systems")
        
        # Standard next steps
        next_steps.extend([
            "Review estimate with project stakeholders",
            "Validate site conditions and access requirements",
            "Confirm local code requirements and permits needed",
            "Develop detailed project schedule",
            "Engage design team for construction documents"
        ])
        
        # Building-specific steps
        building_type = project_data.get("building_type", "").lower()
        if building_type == "healthcare":
            next_steps.append("Coordinate with healthcare planning consultants")
        elif building_type == "educational":
            next_steps.append("Review with educational facility requirements")
        
        return next_steps[:5]  # Top 5 most relevant
    
    def _identify_risk_factors(self, project_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify potential risk factors"""
        risks = []
        
        # Market risks
        risks.append({
            "category": "Market Conditions",
            "risk": "Material price volatility",
            "mitigation": "Consider early material procurement or price escalation clauses"
        })
        
        # Size-based risks
        square_footage = project_data.get("square_footage", 0)
        if square_footage > 100000:
            risks.append({
                "category": "Project Scale",
                "risk": "Large project coordination complexity",
                "mitigation": "Implement robust project management systems"
            })
        
        # Type-based risks
        building_type = project_data.get("building_type", "").lower()
        if building_type == "healthcare":
            risks.append({
                "category": "Regulatory",
                "risk": "Healthcare code compliance requirements",
                "mitigation": "Engage healthcare facility consultants early"
            })
        elif building_type == "restaurant":
            risks.append({
                "category": "Coordination",
                "risk": "Kitchen equipment coordination",
                "mitigation": "Early vendor selection and coordination meetings"
            })
        
        # Location risks
        location = project_data.get("location", "").upper()
        if "CA" in location or "CALIFORNIA" in location:
            risks.append({
                "category": "Regulatory",
                "risk": "Seismic requirements in California",
                "mitigation": "Include structural engineer in early planning"
            })
        
        return risks[:4]  # Top 4 risks
    
    def _get_average_confidence(self, project_data: Dict[str, Any]) -> float:
        """Get average confidence score"""
        confidence_data = self._calculate_confidence_metrics(project_data)
        return confidence_data['avg_confidence']


# Singleton instance
executive_summary_service = ExecutiveSummaryService()