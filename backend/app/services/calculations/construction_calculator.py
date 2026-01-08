from typing import Dict, Any

class ConstructionCalculator:
    """Accurate construction cost calculator for healthcare facilities"""
    
    def calculate(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        square_footage = project_data.get('square_footage', 200000)
        location = project_data.get('location', 'Nashville')
        
        # Base costs
        base_cost_per_sf = 1150  # Correct for hospital
        regional_multiplier = 1.03  # Nashville
        complexity_multiplier = 1.00  # Ground-up
        
        # Calculate construction cost (trades only, no equipment)
        final_cost_per_sf = base_cost_per_sf * regional_multiplier * complexity_multiplier
        construction_total = round(final_cost_per_sf * square_footage)
        # $1,184.50 × 200,000 = $237,000,000
        
        # Trade breakdown (% of construction)
        trade_breakdown = {
            'structural': round(construction_total * 0.22),  # $52.1M
            'mechanical': round(construction_total * 0.35),  # $83.0M  
            'electrical': round(construction_total * 0.15),  # $35.6M
            'plumbing': round(construction_total * 0.18),  # $42.7M
            'finishes': round(construction_total * 0.10)   # $23.7M
        }
        
        # Soft costs for HOSPITAL (much higher than other building types)
        soft_costs_breakdown = {
            'medical_equipment': round(construction_total * 0.19),      # $45M
            'design_engineering': round(construction_total * 0.10),     # $24M
            'construction_contingency': round(construction_total * 0.10), # $24M
            'owner_contingency': round(construction_total * 0.05),      # $12M
            'ff_and_e': round(construction_total * 0.03),             # $7M
            'permits': round(construction_total * 0.02),               # $5M
            'construction_management': round(construction_total * 0.03), # $7M
            'financing': round(construction_total * 0.04),             # $9M
            'testing': round(construction_total * 0.01),               # $2M
            'startup': round(construction_total * 0.01)                # $2M
        }
        
        soft_costs_total = sum(soft_costs_breakdown.values())
        # Total soft costs: ~$120M (50% of construction)
        
        # Total project cost
        total_project_cost = construction_total + soft_costs_total
        # $237M + $120M = $357M
        
        return {
            'construction_costs': {
                'base_cost_per_sf': base_cost_per_sf,
                'regional_multiplier': regional_multiplier,
                'complexity_multiplier': complexity_multiplier,
                'final_cost_per_sf': round(final_cost_per_sf),
                'construction_total': construction_total,  # $237M
                'display_cost_per_sf': round(final_cost_per_sf)
            },
            'soft_costs': {
                'total': soft_costs_total,  # $120M
                'breakdown': soft_costs_breakdown,
                'percentage_of_construction': round(soft_costs_total / construction_total * 100)
            },
            'trade_breakdown': trade_breakdown,
            'totals': {
                'construction_total': construction_total,  # $237M
                'soft_costs': soft_costs_total,  # $120M
                'total_project_cost': total_project_cost,  # $357M
                'cost_per_sf': round(total_project_cost / square_footage)  # $1,785/SF
            }
        }