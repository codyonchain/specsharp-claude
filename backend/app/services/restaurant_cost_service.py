"""
Enhanced restaurant cost calculation service with accurate market-specific pricing
Focuses on Nashville TN and Southern NH markets
"""
from typing import Dict, List, Optional, Any
import logging
from app.data.restaurant_costs import (
    get_restaurant_cost,
    KITCHEN_EQUIPMENT,
    DRIVE_THROUGH_COSTS,
    SEATING_RATIOS,
    TRADE_PERCENTAGES
)

logger = logging.getLogger(__name__)


class RestaurantCostService:
    """Calculate accurate restaurant construction costs with regional variations"""
    
    def calculate_restaurant_costs(self, 
                                 building_type_data: dict,
                                 square_feet: int,
                                 location: str,
                                 restaurant_info: dict) -> dict:
        """
        Calculate restaurant-specific costs with proper breakdowns
        
        Args:
            building_type_data: Building type information
            square_feet: Total square footage
            location: Project location (e.g., "Nashville, TN")
            restaurant_info: Restaurant details from NLP service
        
        Returns:
            Dictionary with cost breakdown and details
        """
        
        # Parse location to get city
        city_key = self._parse_location_to_city_key(location)
        
        # Get restaurant type (check both 'restaurant_type' and 'type' for compatibility)
        restaurant_type = restaurant_info.get('restaurant_type') or restaurant_info.get('type', 'full_service')
        
        # Map restaurant types to cost categories
        type_mapping = {
            'quick_service': 'quick_service',
            'casual_dining': 'full_service',  # Casual dining uses full service costs
            'full_service': 'full_service',
            'fine_dining': 'fine_dining',
            'bar_focused': 'full_service',  # Use full service as base
            'ghost_kitchen': 'specialty',
            'coffee_shop': 'specialty',  # Coffee shops are specialty
            'pizza': 'specialty'  # Pizza is specialty
        }
        
        cost_type = type_mapping.get(restaurant_type, 'full_service')
        
        # Build features list
        features = []
        if restaurant_info.get('has_drive_through'):
            features.append('drive_through')
        if restaurant_info.get('has_brewery_equipment'):
            features.append('brewery')
        if restaurant_info.get('has_outdoor_seating'):
            features.append('outdoor_seating')
        
        # Get base costs from market data
        # For specialty types, pass the specific type (coffee_shop, pizza, etc)
        if cost_type == 'specialty':
            # Use the original restaurant_type for specialty lookups
            if restaurant_type in ['coffee_shop', 'pizza', 'brewery', 'ghost_kitchen']:
                cost_lookup_type = restaurant_type
            else:
                cost_lookup_type = cost_type
        else:
            cost_lookup_type = cost_type
            
        cost_data = get_restaurant_cost(city_key, cost_lookup_type, features)
        base_cost_per_sf = cost_data['adjusted_cost_per_sf']
        
        logger.info(f"[RESTAURANT COST] Location: {location} -> {city_key}")
        logger.info(f"[RESTAURANT COST] Type: {restaurant_type} -> {cost_type}")
        logger.info(f"[RESTAURANT COST] Base Cost/SF: ${base_cost_per_sf}")
        logger.info(f"[RESTAURANT COST] Features: {features}")
        
        # Calculate seating
        seating_info = SEATING_RATIOS.get(restaurant_type, SEATING_RATIOS['full_service'])
        if seating_info['max_seats']:
            seat_count = min(square_feet / seating_info['sf_per_seat'], 
                           seating_info['max_seats'])
        else:
            seat_count = square_feet / seating_info['sf_per_seat']
        seat_count = int(seat_count)
        
        logger.info(f"[RESTAURANT COST] Seating: {seat_count} seats ({seating_info['sf_per_seat']} SF/seat)")
        
        # Get trade percentages
        trade_percentages = cost_data['trade_percentages']
        
        # Calculate base trade costs
        base_total = base_cost_per_sf * square_feet
        
        trade_costs = {
            'structural': base_total * trade_percentages['structural'],
            'mechanical': base_total * trade_percentages['mechanical'],
            'electrical': base_total * trade_percentages['electrical'],
            'plumbing': base_total * trade_percentages['plumbing'],
            'finishes': base_total * trade_percentages['finishes'],
            'general_conditions': base_total * trade_percentages['general_conditions']
        }
        
        # Calculate kitchen equipment separately
        kitchen_equipment_cost = self._calculate_kitchen_equipment(
            restaurant_type, square_feet, restaurant_info
        )
        
        # Calculate bar equipment if applicable
        bar_equipment_cost = 0
        if restaurant_info.get('has_bar'):
            if restaurant_type == 'bar_focused':
                bar_equipment_cost = KITCHEN_EQUIPMENT['bar']['full']
            elif restaurant_type == 'fine_dining':
                bar_equipment_cost = KITCHEN_EQUIPMENT['bar']['premium']
            elif restaurant_type == 'full_service':
                bar_equipment_cost = KITCHEN_EQUIPMENT['bar']['basic']
        
        # Drive-through costs
        # Note: Drive-through is already included in base_cost_per_sf if has_drive_through is true
        # The adjusted_cost_per_sf from get_restaurant_cost already factors in drive-through
        drive_through_cost = 0
        dt_costs = {}
        if restaurant_info.get('has_drive_through'):
            # Drive-through costs are already in the base, just track them for reporting
            dt_costs = DRIVE_THROUGH_COSTS['basic']
            drive_through_cost = sum(dt_costs.values())
            # Don't add to trades - already included in base_cost_per_sf!
        
        # Equipment and FF&E are SEPARATE from construction trades
        # Equipment detail (not part of base construction)
        equipment_detail = {
            'Kitchen Equipment': kitchen_equipment_cost,
            'Dining Furniture': seat_count * 350,  # $350 per seat
            'POS System': 20000 if restaurant_type != 'quick_service' else 15000,
        }
        
        if bar_equipment_cost > 0:
            equipment_detail['Bar Equipment'] = bar_equipment_cost
        
        if drive_through_cost > 0:
            equipment_detail['Drive-Through Equipment'] = dt_costs['menu_boards'] + dt_costs['ordering_system']
        
        if restaurant_info.get('has_outdoor_seating'):
            # Add 20% more seating for outdoor
            outdoor_seats = int(seat_count * 0.2)
            equipment_detail['Outdoor Furniture'] = outdoor_seats * 250
        
        # Construction finishes detail (part of base construction, already in trade_costs['finishes'])
        finishes_detail = {
            'Flooring': square_feet * 8,
            'Wall Finishes': square_feet * 6,
            'Ceiling': square_feet * 5,
            'Millwork/Casework': square_feet * 4,
            'Other Finishes': trade_costs['finishes'] - (square_feet * 23)  # Remainder of finishes budget
        }
        
        # Calculate totals
        # Construction subtotal is just the trade costs (base construction)
        construction_subtotal = sum(trade_costs.values())
        
        # Equipment and FF&E are added separately
        equipment_total = sum(equipment_detail.values())
        
        # Total project cost
        subtotal = construction_subtotal + equipment_total
        contingency = subtotal * 0.10
        total = subtotal + contingency
        
        # Validate against expected range
        cost_per_sf = total / square_feet
        self._validate_cost_per_sf(cost_per_sf, restaurant_type, location)
        
        return {
            'total': total,
            'total_cost': total,  # Add for compatibility
            'subtotal': subtotal,
            'cost_per_sf': cost_per_sf,
            'breakdown': {
                'base_construction': {
                    'total': construction_subtotal,
                    'per_sf': construction_subtotal / square_feet
                },
                'trades': trade_costs,
                'equipment': equipment_detail,
                'equipment_total': equipment_total,
                'equipment_per_sf': equipment_total / square_feet
            },
            'finishes_detail': finishes_detail,
            'equipment_detail': equipment_detail,
            'seat_count': seat_count,
            'kitchen_equipment_total': kitchen_equipment_cost,
            'bar_equipment_total': bar_equipment_cost,
            'drive_through_total': drive_through_cost,
            'contingency': contingency,
            'city_key': city_key,
            'restaurant_type': restaurant_type,
            'applied_features': cost_data.get('applied_features', [])
        }
    
    def _calculate_kitchen_equipment(self, restaurant_type: str, 
                                    square_feet: int, 
                                    restaurant_info: dict) -> float:
        """Calculate kitchen equipment costs based on restaurant type"""
        
        # Base kitchen equipment by type
        if restaurant_type == 'quick_service':
            equipment = KITCHEN_EQUIPMENT.get('qsr_basic', {})
            base_cost = sum(equipment.values())
        elif restaurant_type == 'fine_dining':
            equipment = KITCHEN_EQUIPMENT.get('fine_dining', {})
            base_cost = sum(equipment.values())
        elif restaurant_type == 'coffee_shop':
            equipment = KITCHEN_EQUIPMENT.get('coffee', {})
            base_cost = sum(equipment.values())
        elif restaurant_type == 'pizza':
            equipment = KITCHEN_EQUIPMENT.get('pizza', {})
            base_cost = sum(equipment.values())
        elif restaurant_type == 'brewery':
            equipment = KITCHEN_EQUIPMENT.get('brewery', {})
            base_cost = sum(equipment.values())
        elif restaurant_type == 'ghost_kitchen':
            # Ghost kitchens have dense equipment
            base_cost = square_feet * 65  # $65/SF for equipment
        elif restaurant_type == 'casual_dining':
            # Casual dining uses full service equipment
            equipment = KITCHEN_EQUIPMENT.get('full_service', {})
            base_cost = sum(equipment.values())
        else:  # Default to full_service
            equipment = KITCHEN_EQUIPMENT.get('full_service', {})
            base_cost = sum(equipment.values())
        
        # Add specialty equipment
        if restaurant_info.get('has_pizza_oven'):
            pizza_equipment = KITCHEN_EQUIPMENT.get('pizza', {})
            base_cost += sum(pizza_equipment.values())
        
        if restaurant_info.get('has_brewery_equipment'):
            brewery_equipment = KITCHEN_EQUIPMENT.get('brewery', {})
            base_cost += brewery_equipment.get('brewing_system_7bbl', 150000)
            base_cost += brewery_equipment.get('fermenters', 45000)
        
        # Scale equipment cost for larger restaurants
        if square_feet > 5000:
            scale_factor = 1 + ((square_feet - 5000) / 10000) * 0.2
            base_cost *= scale_factor
        
        return base_cost
    
    def _parse_location_to_city_key(self, location: str) -> str:
        """Convert location string to city key for cost lookup"""
        
        if not location:
            return 'default'
        
        location_lower = location.lower()
        
        # Nashville area cities
        if 'nashville' in location_lower:
            return 'nashville_tn'
        elif 'franklin' in location_lower and 'tn' in location_lower:
            return 'franklin_tn'
        elif 'murfreesboro' in location_lower:
            return 'murfreesboro_tn'
        elif 'brentwood' in location_lower:
            return 'brentwood_tn'
        
        # Southern NH cities
        elif 'manchester' in location_lower and ('nh' in location_lower or 'hampshire' in location_lower):
            return 'manchester_nh'
        elif 'nashua' in location_lower:
            return 'nashua_nh'
        elif 'concord' in location_lower and ('nh' in location_lower or 'hampshire' in location_lower):
            return 'concord_nh'
        elif 'salem' in location_lower and ('nh' in location_lower or 'hampshire' in location_lower):
            return 'salem_nh'
        elif 'derry' in location_lower:
            return 'derry_nh'
        
        # Check state only
        elif 'tennessee' in location_lower or ', tn' in location_lower:
            return 'nashville_tn'  # Use Nashville as TN default
        elif 'new hampshire' in location_lower or ', nh' in location_lower:
            return 'manchester_nh'  # Use Manchester as NH default
        
        return 'default'
    
    def _validate_cost_per_sf(self, cost_per_sf: float, 
                             restaurant_type: str, 
                             location: str) -> None:
        """Validate that cost per SF is within expected range"""
        
        expected_ranges = {
            'quick_service': (280, 450),
            'full_service': (325, 500),
            'fine_dining': (450, 650),
            'bar_focused': (300, 450),
            'ghost_kitchen': (250, 350)
        }
        
        min_cost, max_cost = expected_ranges.get(restaurant_type, (300, 600))
        
        if cost_per_sf < min_cost:
            logger.warning(f"[RESTAURANT COST] Cost ${cost_per_sf:.2f}/SF is below expected range "
                         f"${min_cost}-${max_cost} for {restaurant_type} in {location}")
        elif cost_per_sf > max_cost:
            logger.warning(f"[RESTAURANT COST] Cost ${cost_per_sf:.2f}/SF is above expected range "
                         f"${min_cost}-${max_cost} for {restaurant_type} in {location}")
        else:
            logger.info(f"[RESTAURANT COST] Cost ${cost_per_sf:.2f}/SF is within expected range "
                       f"${min_cost}-${max_cost} for {restaurant_type}")


# Singleton instance
restaurant_cost_service = RestaurantCostService()