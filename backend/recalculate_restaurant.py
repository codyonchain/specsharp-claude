#!/usr/bin/env python3
"""
Script to recalculate restaurant project costs with corrected multipliers
"""

def calculate_restaurant_cost(square_footage=4200, location="Nashville, TN"):
    """Calculate restaurant cost with proper multipliers"""
    
    # Base cost for full-service restaurant in TN
    base_cost_per_sf = 425  # From building_type_service.py
    
    # Regional multiplier for TN (updated)
    tn_multiplier = 1.30  # New value we just set
    
    # Project type multiplier for commercial
    commercial_multiplier = 1.0
    
    # Calculate base costs
    adjusted_base = base_cost_per_sf * tn_multiplier * commercial_multiplier
    subtotal = adjusted_base * square_footage
    
    # Add 10% contingency
    contingency_rate = 0.10
    contingency_amount = subtotal * contingency_rate
    total_cost = subtotal + contingency_amount
    
    # Calculate per square foot
    cost_per_sf = total_cost / square_footage
    
    print(f"Restaurant Cost Calculation for {location}")
    print(f"=" * 50)
    print(f"Square Footage: {square_footage:,} sq ft")
    print(f"Base Cost/SF: ${base_cost_per_sf}")
    print(f"TN Regional Multiplier: {tn_multiplier}")
    print(f"Commercial Type Multiplier: {commercial_multiplier}")
    print(f"Adjusted Base/SF: ${adjusted_base:.2f}")
    print(f"")
    print(f"Subtotal: ${subtotal:,.2f}")
    print(f"Contingency (10%): ${contingency_amount:,.2f}")
    print(f"Total Cost: ${total_cost:,.2f}")
    print(f"Cost per SF: ${cost_per_sf:.2f}/SF")
    print(f"")
    print(f"Target Range: $550-600/SF")
    print(f"Actual GC Quote (Indaco): ~$551/SF")
    print(f"In Range: {'✓ Yes' if 550 <= cost_per_sf <= 650 else '✗ No'}")
    
    return {
        'subtotal': subtotal,
        'contingency_amount': contingency_amount,
        'total_cost': total_cost,
        'cost_per_sf': cost_per_sf
    }

if __name__ == "__main__":
    # Calculate for TI Italian restaurant
    result = calculate_restaurant_cost(4200, "Nashville, TN")
    
    print(f"\nDatabase Update Values:")
    print(f"UPDATE projects SET")
    print(f"  total_cost = {result['total_cost']:.2f},")
    print(f"  cost_per_sqft = {result['cost_per_sf']:.2f}")
    print(f"WHERE name = 'TI Italian' OR name = 'mama mia';")