"""
Smart grouping utilities for organizing similar items in exports
Groups pumps together, AHUs together, electrical panels together, etc.
"""
from typing import List, Dict, Any, Optional
from collections import defaultdict
import re


class ItemGrouper:
    """Groups similar construction items for organized exports"""
    
    # Define grouping patterns and their display names
    GROUPING_RULES = {
        # Mechanical Equipment
        "Air Handling Units": [
            r"air handling unit", r"ahu", r"air handler", r"hvac unit",
            r"rooftop unit", r"rtu", r"packaged unit"
        ],
        "Pumps": [
            r"pump", r"circulator", r"booster"
        ],
        "Fans & Ventilation": [
            r"fan", r"exhaust", r"ventilation", r"blower", r"vav", r"vfd"
        ],
        "Chillers & Cooling": [
            r"chiller", r"cooling tower", r"condenser", r"split system",
            r"dx unit", r"refrigeration"
        ],
        "Boilers & Heating": [
            r"boiler", r"furnace", r"heater", r"heat pump", r"radiator"
        ],
        "Ductwork & Distribution": [
            r"duct", r"diffuser", r"grille", r"register", r"damper"
        ],
        
        # Plumbing
        "Fixtures": [
            r"toilet", r"urinal", r"lavatory", r"sink", r"faucet",
            r"water closet", r"drinking fountain", r"shower", r"tub"
        ],
        "Water Heaters": [
            r"water heater", r"hot water", r"dhw", r"tankless"
        ],
        "Piping Systems": [
            r"pipe", r"piping", r"valve", r"fitting", r"insulation"
        ],
        "Drainage": [
            r"drain", r"sewer", r"waste", r"vent", r"trap"
        ],
        
        # Electrical
        "Panels & Distribution": [
            r"panel", r"switchgear", r"switchboard", r"breaker",
            r"distribution", r"mcc", r"transformer"
        ],
        "Lighting": [
            r"light", r"fixture", r"lamp", r"luminaire", r"led",
            r"fluorescent", r"emergency lighting"
        ],
        "Power Systems": [
            r"generator", r"ups", r"battery", r"inverter",
            r"automatic transfer", r"ats"
        ],
        "Low Voltage": [
            r"fire alarm", r"security", r"data", r"telecom",
            r"av system", r"cctv", r"access control"
        ],
        "Wiring & Devices": [
            r"wire", r"cable", r"conduit", r"receptacle", r"outlet",
            r"switch", r"junction box"
        ],
        
        # Structural
        "Foundations": [
            r"foundation", r"footing", r"pile", r"caisson", r"grade beam"
        ],
        "Framing": [
            r"beam", r"column", r"girder", r"joist", r"decking",
            r"steel frame", r"structural steel"
        ],
        "Concrete Work": [
            r"concrete", r"slab", r"rebar", r"forming", r"reinforcing"
        ],
        
        # Finishes
        "Flooring": [
            r"floor", r"carpet", r"tile", r"vinyl", r"hardwood",
            r"polished concrete", r"epoxy"
        ],
        "Walls & Ceilings": [
            r"drywall", r"gypsum", r"paint", r"wallpaper", r"paneling",
            r"ceiling", r"acoustical"
        ],
        "Doors & Windows": [
            r"door", r"frame", r"hardware", r"window", r"storefront",
            r"curtain wall", r"glazing"
        ],
        
        # Specialties
        "Kitchen Equipment": [
            r"kitchen", r"cooking", r"refrigerator", r"freezer",
            r"dishwasher", r"hood", r"grease"
        ],
        "Medical Equipment": [
            r"medical gas", r"oxygen", r"vacuum", r"nurse call",
            r"x-ray", r"mri", r"surgical"
        ],
        "Elevators & Conveyance": [
            r"elevator", r"escalator", r"lift", r"dumbwaiter"
        ]
    }
    
    def __init__(self):
        # Compile regex patterns for efficiency
        self.compiled_rules = {}
        for group_name, patterns in self.GROUPING_RULES.items():
            combined_pattern = "|".join(f"({pattern})" for pattern in patterns)
            self.compiled_rules[group_name] = re.compile(combined_pattern, re.IGNORECASE)
    
    def determine_group(self, item_description: str) -> str:
        """
        Determine which group an item belongs to based on its description
        """
        description_lower = item_description.lower()
        
        # Check each group's patterns
        for group_name, pattern in self.compiled_rules.items():
            if pattern.search(description_lower):
                return group_name
        
        # Default group for unmatched items
        return "Other Systems"
    
    def group_items(self, items: List[Dict[str, Any]], 
                   description_key: str = "description") -> Dict[str, List[Dict[str, Any]]]:
        """
        Group a list of items by their type
        
        Args:
            items: List of item dictionaries
            description_key: Key in the dictionary containing the item description
            
        Returns:
            Dictionary with group names as keys and lists of items as values
        """
        grouped = defaultdict(list)
        
        for item in items:
            description = item.get(description_key, "")
            group = self.determine_group(description)
            grouped[group].append(item)
        
        # Sort groups by a logical order
        group_order = [
            # Site work
            "Foundations",
            # Structural
            "Concrete Work", "Framing",
            # Mechanical
            "Air Handling Units", "Pumps", "Fans & Ventilation", 
            "Chillers & Cooling", "Boilers & Heating", "Ductwork & Distribution",
            # Plumbing
            "Water Heaters", "Fixtures", "Piping Systems", "Drainage",
            # Electrical
            "Panels & Distribution", "Power Systems", "Lighting", 
            "Wiring & Devices", "Low Voltage",
            # Finishes
            "Flooring", "Walls & Ceilings", "Doors & Windows",
            # Specialties
            "Kitchen Equipment", "Medical Equipment", "Elevators & Conveyance",
            # Catch-all
            "Other Systems"
        ]
        
        # Create ordered result
        ordered_groups = {}
        for group in group_order:
            if group in grouped and grouped[group]:
                ordered_groups[group] = sorted(
                    grouped[group], 
                    key=lambda x: x.get(description_key, "").lower()
                )
        
        # Add any groups not in the predefined order
        for group, items_list in grouped.items():
            if group not in ordered_groups and items_list:
                ordered_groups[group] = sorted(
                    items_list,
                    key=lambda x: x.get(description_key, "").lower()
                )
        
        return ordered_groups
    
    def group_by_trade(self, items: List[Dict[str, Any]], 
                      trade_key: str = "trade") -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Group items first by trade, then by type within each trade
        
        Returns:
            Nested dictionary: {trade: {group: [items]}}
        """
        # First group by trade
        by_trade = defaultdict(list)
        for item in items:
            trade = item.get(trade_key, "General")
            by_trade[trade].append(item)
        
        # Then group by type within each trade
        result = {}
        for trade, trade_items in by_trade.items():
            result[trade] = self.group_items(trade_items)
        
        return result
    
    def create_grouped_summary(self, grouped_items: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Create a summary of grouped items with totals
        """
        summary = []
        
        for group_name, items in grouped_items.items():
            if not items:
                continue
                
            # Calculate group totals
            total_cost = sum(item.get("total_cost", 0) for item in items)
            item_count = len(items)
            
            # Find cost range within group
            costs = [item.get("total_cost", 0) for item in items if item.get("total_cost", 0) > 0]
            min_cost = min(costs) if costs else 0
            max_cost = max(costs) if costs else 0
            
            summary.append({
                "group": group_name,
                "item_count": item_count,
                "total_cost": total_cost,
                "min_item_cost": min_cost,
                "max_item_cost": max_cost,
                "items": items
            })
        
        # Sort by total cost descending
        summary.sort(key=lambda x: x["total_cost"], reverse=True)
        
        return summary


def group_similar_items(items: List[Dict[str, Any]], 
                       group_by: str = "type",
                       description_key: str = "description") -> Dict[str, Any]:
    """
    Main function to group similar items for export
    
    Args:
        items: List of items to group
        group_by: "type" or "trade" grouping
        description_key: Key containing item description
        
    Returns:
        Grouped and organized items
    """
    grouper = ItemGrouper()
    
    if group_by == "trade":
        grouped = grouper.group_by_trade(items)
        
        # Create summary for each trade
        result = {}
        for trade, trade_groups in grouped.items():
            result[trade] = {
                "groups": trade_groups,
                "summary": grouper.create_grouped_summary(trade_groups)
            }
        
        return result
    else:
        # Group by type only
        grouped = grouper.group_items(items, description_key)
        
        return {
            "groups": grouped,
            "summary": grouper.create_grouped_summary(grouped)
        }


def format_grouped_export(grouped_data: Dict[str, Any], 
                        format_type: str = "summary") -> List[Dict[str, Any]]:
    """
    Format grouped data for different export types
    
    Args:
        grouped_data: Output from group_similar_items
        format_type: "summary", "detailed", or "compact"
    """
    if "groups" in grouped_data:
        # Single-level grouping
        groups = grouped_data["groups"]
        summary = grouped_data.get("summary", [])
        
        if format_type == "summary":
            return summary
        elif format_type == "detailed":
            # Flatten with group headers
            result = []
            for group_summary in summary:
                result.append({
                    "type": "header",
                    "group": group_summary["group"],
                    "total_cost": group_summary["total_cost"],
                    "item_count": group_summary["item_count"]
                })
                for item in group_summary["items"]:
                    item_copy = item.copy()
                    item_copy["type"] = "item"
                    item_copy["group"] = group_summary["group"]
                    result.append(item_copy)
            return result
        else:  # compact
            # Just the items with group tags
            result = []
            for group_name, items in groups.items():
                for item in items:
                    item_copy = item.copy()
                    item_copy["group"] = group_name
                    result.append(item_copy)
            return result
    else:
        # Trade-based grouping
        result = []
        for trade, trade_data in grouped_data.items():
            if format_type == "summary":
                trade_total = sum(g["total_cost"] for g in trade_data["summary"])
                result.append({
                    "type": "trade",
                    "trade": trade,
                    "total_cost": trade_total,
                    "groups": trade_data["summary"]
                })
            else:
                # Add trade header
                result.append({
                    "type": "trade_header",
                    "trade": trade
                })
                # Add grouped items
                formatted_trade = format_grouped_export(trade_data, format_type)
                result.extend(formatted_trade)
        
        return result


# Example usage for different scenarios
def group_scope_items(scope_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Group scope items from a project estimate
    """
    all_items = []
    
    # Extract all items from categories
    for category in scope_data.get("categories", []):
        trade = category.get("name", "General")
        for system in category.get("systems", []):
            item = {
                "description": system.get("name", ""),
                "quantity": system.get("quantity", 0),
                "unit": system.get("unit", ""),
                "unit_cost": system.get("unit_cost", 0),
                "total_cost": system.get("total_cost", 0),
                "trade": trade,
                "confidence": system.get("confidence_score", 95)
            }
            all_items.append(item)
    
    # Group by type
    return group_similar_items(all_items, group_by="type")