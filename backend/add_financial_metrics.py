#!/usr/bin/env python3
"""
Script to add financial_metrics to all building subtypes that are missing them.
This adds financial metrics for subtypes 31-57 as specified in SPRINT_3_5_PART_2.
"""

import re

# Define all the financial metrics to add for each subtype
FINANCIAL_METRICS = {
    # CIVIC (31-34)
    'public_safety': {
        'primary_unit': 'response_units',
        'units_per_sf': 0.0001,  # ~1 unit per 10K SF
        'revenue_per_unit_annual': 0,  # Tax-funded
        'target_utilization': 0.90,
        'breakeven_utilization': 0.80,
        'market_rate_type': 'budget_per_unit',
        'market_rate_default': 850000,
        'display_name': 'Per Response Unit Requirements'
    },
    'library': {
        'primary_unit': 'visitor_capacity',
        'units_per_sf': 0.02,  # 20 visitors per 1000 SF
        'revenue_per_unit_annual': 0,  # Public service
        'target_utilization': 0.70,
        'breakeven_utilization': 0.50,
        'market_rate_type': 'budget_per_visitor',
        'market_rate_default': 50,
        'display_name': 'Visitor Capacity Requirements'
    },
    'community_center': {
        'primary_unit': 'program_spaces',
        'units_per_sf': 0.0002,  # ~1 space per 5K SF
        'revenue_per_unit_annual': 45000,  # Program fees
        'target_utilization': 0.75,
        'breakeven_utilization': 0.60,
        'market_rate_type': 'program_revenue',
        'market_rate_default': 45000,
        'display_name': 'Per Program Space Requirements'
    },
    'courthouse': {
        'primary_unit': 'courtrooms',
        'units_per_sf': 0.00005,  # ~1 courtroom per 20K SF
        'revenue_per_unit_annual': 0,  # Government funded
        'target_utilization': 0.80,
        'breakeven_utilization': 0.65,
        'market_rate_type': 'budget_allocation',
        'market_rate_default': 2500000,
        'display_name': 'Per Courtroom Requirements'
    },
    
    # RECREATION (35-39)
    'fitness_center': {
        'primary_unit': 'members',
        'units_per_sf': 0.05,  # 50 members per 1000 SF capacity
        'revenue_per_unit_annual': 600,  # $50/month membership
        'target_utilization': 0.80,
        'breakeven_utilization': 0.65,
        'market_rate_type': 'monthly_membership',
        'market_rate_default': 50,
        'display_name': 'Per Member Requirements'
    },
    'sports_complex': {
        'primary_unit': 'courts_fields',
        'units_per_sf': 0.00003,  # ~1 court per 30K SF
        'revenue_per_unit_annual': 180000,  # Rental and programs
        'target_utilization': 0.70,
        'breakeven_utilization': 0.55,
        'market_rate_type': 'hourly_rental',
        'market_rate_default': 75,
        'display_name': 'Per Court/Field Requirements'
    },
    'aquatic_center': {
        'primary_unit': 'lanes',
        'units_per_sf': 0.0002,  # ~1 lane per 5K SF
        'revenue_per_unit_annual': 85000,  # Programs and memberships
        'target_utilization': 0.75,
        'breakeven_utilization': 0.60,
        'market_rate_type': 'program_revenue',
        'market_rate_default': 85000,
        'display_name': 'Per Lane Requirements'
    },
    'recreation_center': {
        'primary_unit': 'activity_areas',
        'units_per_sf': 0.0001,  # ~1 area per 10K SF
        'revenue_per_unit_annual': 120000,
        'target_utilization': 0.72,
        'breakeven_utilization': 0.58,
        'market_rate_type': 'program_revenue',
        'market_rate_default': 120000,
        'display_name': 'Per Activity Area Requirements'
    },
    'stadium': {
        'primary_unit': 'seats',
        'units_per_sf': 0.10,  # 1 seat per 10 SF
        'revenue_per_unit_annual': 850,  # Ticket and concession revenue
        'target_utilization': 0.65,  # Events per year / 365
        'breakeven_utilization': 0.50,
        'market_rate_type': 'ticket_price',
        'market_rate_default': 45,
        'display_name': 'Per Seat Requirements'
    },
    
    # MIXED_USE (40-44)
    'retail_residential': {
        'primary_unit': 'blended_sf',
        'units_per_sf': 1.0,
        'revenue_per_unit_annual': 38,  # Blended rate
        'target_occupancy': 0.91,
        'breakeven_occupancy': 0.78,
        'market_rate_type': 'blended_psf',
        'market_rate_default': 38,
        'display_name': 'Blended Revenue Requirements'
    },
    'office_residential': {
        'primary_unit': 'blended_sf',
        'units_per_sf': 1.0,
        'revenue_per_unit_annual': 42,
        'target_occupancy': 0.89,
        'breakeven_occupancy': 0.76,
        'market_rate_type': 'blended_psf',
        'market_rate_default': 42,
        'display_name': 'Blended Revenue Requirements'
    },
    'hotel_retail': {
        'primary_unit': 'blended_units',
        'units_per_sf': 0.0015,  # Mix of rooms and retail
        'revenue_per_unit_annual': 65000,
        'target_occupancy': 0.75,
        'breakeven_occupancy': 0.63,
        'market_rate_type': 'blended_revenue',
        'market_rate_default': 65000,
        'display_name': 'Blended Revenue Requirements'
    },
    'urban_mixed': {
        'primary_unit': 'blended_sf',
        'units_per_sf': 1.0,
        'revenue_per_unit_annual': 48,
        'target_occupancy': 0.90,
        'breakeven_occupancy': 0.77,
        'market_rate_type': 'blended_psf',
        'market_rate_default': 48,
        'display_name': 'Blended Revenue Requirements'
    },
    'transit_oriented': {
        'primary_unit': 'blended_sf',
        'units_per_sf': 1.0,
        'revenue_per_unit_annual': 52,
        'target_occupancy': 0.92,
        'breakeven_occupancy': 0.80,
        'market_rate_type': 'blended_psf',
        'market_rate_default': 52,
        'display_name': 'TOD Revenue Requirements'
    },
    
    # PARKING (45-48)
    'surface_parking': {
        'primary_unit': 'spaces',
        'units_per_sf': 0.00286,  # ~350 SF per space
        'revenue_per_unit_annual': 900,  # $75/month x 12
        'target_utilization': 0.70,
        'breakeven_utilization': 0.55,
        'market_rate_type': 'monthly_rate',
        'market_rate_default': 75,
        'display_name': 'Per Space Requirements'
    },
    'parking_garage': {
        'primary_unit': 'spaces',
        'units_per_sf': 0.00333,  # ~300 SF per space
        'revenue_per_unit_annual': 1800,  # $150/month x 12
        'target_utilization': 0.85,
        'breakeven_utilization': 0.65,
        'market_rate_type': 'monthly_rate',
        'market_rate_default': 150,
        'display_name': 'Per Space Requirements'
    },
    'underground_parking': {
        'primary_unit': 'spaces',
        'units_per_sf': 0.00357,  # ~280 SF per space
        'revenue_per_unit_annual': 2400,  # $200/month x 12
        'target_utilization': 0.90,
        'breakeven_utilization': 0.75,
        'market_rate_type': 'monthly_rate',
        'market_rate_default': 200,
        'display_name': 'Per Space Requirements'
    },
    'automated_parking': {
        'primary_unit': 'spaces',
        'units_per_sf': 0.00625,  # ~160 SF per space (very efficient)
        'revenue_per_unit_annual': 3000,  # $250/month x 12
        'target_utilization': 0.92,
        'breakeven_utilization': 0.80,
        'market_rate_type': 'monthly_rate',
        'market_rate_default': 250,
        'display_name': 'Per Space Requirements'
    },
    
    # RESTAURANT (49-52)
    'quick_service': {
        'primary_unit': 'seats',
        'units_per_sf': 0.033,  # ~1 seat per 30 SF
        'revenue_per_unit_annual': 12000,
        'target_utilization': 0.80,
        'breakeven_utilization': 0.65,
        'market_rate_type': 'revenue_per_seat',
        'market_rate_default': 12000,
        'display_name': 'Per Seat Requirements'
    },
    'full_service': {
        'primary_unit': 'seats',
        'units_per_sf': 0.025,  # ~1 seat per 40 SF
        'revenue_per_unit_annual': 18000,
        'target_utilization': 0.75,
        'breakeven_utilization': 0.60,
        'market_rate_type': 'revenue_per_seat',
        'market_rate_default': 18000,
        'display_name': 'Per Seat Requirements'
    },
    'bar_tavern': {
        'primary_unit': 'seats',
        'units_per_sf': 0.028,  # ~1 seat per 35 SF
        'revenue_per_unit_annual': 22000,
        'target_utilization': 0.70,
        'breakeven_utilization': 0.55,
        'market_rate_type': 'revenue_per_seat',
        'market_rate_default': 22000,
        'display_name': 'Per Seat Requirements'
    },
    'cafe': {
        'primary_unit': 'seats',
        'units_per_sf': 0.030,  # ~1 seat per 33 SF
        'revenue_per_unit_annual': 14000,
        'target_utilization': 0.72,
        'breakeven_utilization': 0.58,
        'market_rate_type': 'revenue_per_seat',
        'market_rate_default': 14000,
        'display_name': 'Per Seat Requirements'
    },
    
    # SPECIALTY (53-57)
    'data_center': {
        'primary_unit': 'kw',  # Power capacity
        'units_per_sf': 0.10,  # 100 watts per SF
        'revenue_per_unit_annual': 1200,  # Per kW per year
        'target_utilization': 0.85,
        'breakeven_utilization': 0.70,
        'market_rate_type': 'per_kw',
        'market_rate_default': 100,  # Monthly per kW
        'display_name': 'Per kW Requirements'
    },
    'laboratory': {
        'primary_unit': 'lab_benches',
        'units_per_sf': 0.0005,  # ~1 bench per 2000 SF
        'revenue_per_unit_annual': 180000,
        'target_utilization': 0.82,
        'breakeven_utilization': 0.68,
        'market_rate_type': 'per_bench',
        'market_rate_default': 180000,
        'display_name': 'Per Lab Bench Requirements'
    },
    'self_storage': {
        'primary_unit': 'units',
        'units_per_sf': 0.012,  # ~12 units per 1000 SF
        'revenue_per_unit_annual': 1440,  # $120/month average
        'target_occupancy': 0.88,
        'breakeven_occupancy': 0.72,
        'market_rate_type': 'monthly_unit_rate',
        'market_rate_default': 120,
        'display_name': 'Per Unit Requirements'
    },
    'car_dealership': {
        'primary_unit': 'vehicle_capacity',
        'units_per_sf': 0.0025,  # Display and lot capacity
        'revenue_per_unit_annual': 45000,  # Revenue per vehicle slot
        'target_utilization': 0.65,  # Inventory turnover
        'breakeven_utilization': 0.50,
        'market_rate_type': 'revenue_per_vehicle',
        'market_rate_default': 45000,
        'display_name': 'Per Vehicle Slot Requirements'
    },
    'broadcast_facility': {
        'primary_unit': 'studios',
        'units_per_sf': 0.00005,  # ~1 studio per 20K SF
        'revenue_per_unit_annual': 2500000,
        'target_utilization': 0.78,
        'breakeven_utilization': 0.62,
        'market_rate_type': 'studio_revenue',
        'market_rate_default': 2500000,
        'display_name': 'Per Studio Requirements'
    }
}

def format_financial_metrics(metrics):
    """Format the financial metrics dictionary as Python code."""
    lines = ["            financial_metrics={"]
    for key, value in metrics.items():
        if isinstance(value, str):
            lines.append(f"                '{key}': '{value}',")
        else:
            lines.append(f"                '{key}': {value},")
    # Remove trailing comma from last line
    lines[-1] = lines[-1].rstrip(',')
    lines.append("            },")
    return '\n'.join(lines)

def main():
    # Read the master config file
    with open('/Users/codymarchant/specsharp/backend/app/v2/config/master_config.py', 'r') as f:
        content = f.read()
    
    # Track changes made
    changes_made = []
    
    for subtype, metrics in FINANCIAL_METRICS.items():
        # Find the subtype configuration
        pattern = f"        '{subtype}': BuildingConfig("
        if pattern not in content:
            print(f"Warning: Subtype '{subtype}' not found in config")
            continue
        
        # Check if financial_metrics already exists for this subtype
        # Look for it after the subtype definition
        subtype_start = content.find(pattern)
        if subtype_start == -1:
            continue
            
        # Find the end of this BuildingConfig (look for the closing ")," at the correct indentation)
        # This is complex, so let's look for the pattern of "# Revenue metrics" which typically comes after special_features
        
        # Find the special_features section for this subtype
        search_start = subtype_start
        special_features_match = content.find('special_features={', search_start)
        
        if special_features_match == -1:
            print(f"Warning: special_features not found for {subtype}")
            continue
        
        # Find the closing of special_features
        bracket_count = 0
        pos = special_features_match + len('special_features={')
        while pos < len(content):
            if content[pos] == '{':
                bracket_count += 1
            elif content[pos] == '}':
                if bracket_count == 0:
                    # Found the closing bracket
                    special_features_end = pos + 1
                    break
                bracket_count -= 1
            pos += 1
        
        # Check if financial_metrics already exists
        check_area = content[special_features_end:special_features_end + 500]
        if 'financial_metrics=' in check_area:
            print(f"Info: financial_metrics already exists for {subtype}")
            continue
        
        # Find where to insert (after special_features closing)
        # Look for the pattern "},\n" after special_features
        insert_point = content.find('},', special_features_end)
        if insert_point == -1:
            print(f"Warning: Could not find insertion point for {subtype}")
            continue
        
        insert_point += 2  # Move past "},"
        
        # Format the financial metrics
        metrics_code = format_financial_metrics(metrics)
        
        # Insert the financial metrics
        # Add proper spacing
        insertion = f"\n            \n            # Financial metrics\n{metrics_code}"
        
        # Check what comes after to ensure proper formatting
        next_content = content[insert_point:insert_point+50]
        if next_content.strip().startswith('# Revenue metrics'):
            insertion += "\n"
        else:
            insertion += "\n            "
        
        # Update content
        content = content[:insert_point] + insertion + content[insert_point:]
        changes_made.append(subtype)
        print(f"Added financial_metrics for {subtype}")
    
    # Write the updated content back
    if changes_made:
        with open('/Users/codymarchant/specsharp/backend/app/v2/config/master_config.py', 'w') as f:
            f.write(content)
        print(f"\nSuccessfully updated {len(changes_made)} subtypes with financial_metrics")
        print("Updated subtypes:", ', '.join(changes_made))
    else:
        print("No changes were made")

if __name__ == '__main__':
    main()