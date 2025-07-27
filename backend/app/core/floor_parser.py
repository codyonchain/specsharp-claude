"""
Floor count extraction and parsing utilities
"""
import re
from typing import Optional


def extract_floors(description: str) -> int:
    """
    Extract number of floors from description with comprehensive pattern matching
    
    Args:
        description: Natural language description of the building
        
    Returns:
        Number of floors detected (minimum 1)
    """
    if not description:
        return 1
        
    description_lower = description.lower()
    
    # Word to number mapping
    word_to_number = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
    }
    
    # Pattern 1: "X stories" or "X story" or "X-story"
    stories_patterns = [
        r'(\d+)\s*stor(?:ies|ey|y)',  # 3 stories, 3 story
        r'(\d+)[-\s]stor(?:ies|ey|y)', # 3-story, 3 story
        r'(\d+)\s*floor\s*stor(?:ies|ey|y)', # 3 floor story
    ]
    
    for pattern in stories_patterns:
        match = re.search(pattern, description_lower)
        if match:
            floors = int(match.group(1))
            print(f"[FLOOR PARSER] Detected {floors} floors from pattern: {pattern}")
            return floors
    
    # Pattern 2: "X floors" or "X floor" or "X-floor"
    floor_patterns = [
        r'(\d+)\s*floors?',  # 5 floors, 5 floor
        r'(\d+)[-\s]floors?', # 5-floor
        r'(\d+)\s*floor\s*building', # 5 floor building
    ]
    
    for pattern in floor_patterns:
        match = re.search(pattern, description_lower)
        if match:
            floors = int(match.group(1))
            print(f"[FLOOR PARSER] Detected {floors} floors from pattern: {pattern}")
            return floors
    
    # Pattern 3: "X levels" or "X-level"
    level_patterns = [
        r'(\d+)\s*levels?',  # 3 levels, 3 level
        r'(\d+)[-\s]levels?', # 3-level
        r'(one|two|three|four|five|six|seven|eight|nine|ten)[-\s]levels?', # three-level
    ]
    
    for pattern in level_patterns:
        match = re.search(pattern, description_lower)
        if match:
            captured = match.group(1)
            if captured.isdigit():
                floors = int(captured)
            else:
                # Handle word numbers
                floors = word_to_number.get(captured, 1)
            print(f"[FLOOR PARSER] Detected {floors} floors from level pattern: {pattern}")
            return floors
    
    # Pattern 4: Word numbers (one through twenty)
    
    for word, num in word_to_number.items():
        patterns = [
            f'{word}\\s*stor(?:ies|ey|y)',
            f'{word}[-\\s]stor(?:ies|ey|y)',
            f'{word}\\s*floors?',
            f'{word}[-\\s]floors?'
        ]
        for pattern in patterns:
            if re.search(pattern, description_lower):
                print(f"[FLOOR PARSER] Detected {num} floors from word pattern: {word}")
                return num
    
    # Pattern 5: "multi-story" or "multistory" or "multi-floor"
    multi_patterns = ['multi-story', 'multistory', 'multi-floor', 'multilevel', 'multi-level']
    if any(term in description_lower for term in multi_patterns):
        print("[FLOOR PARSER] Detected multi-story building, defaulting to 2 floors")
        return 2
    
    # Pattern 6: "tall", "high-rise", "tower" suggests multiple floors
    tall_patterns = ['high-rise', 'highrise', 'tower', 'tall building', 'skyscraper']
    if any(term in description_lower for term in tall_patterns):
        # Conservative estimate for tall buildings
        if 'office' in description_lower:
            print("[FLOOR PARSER] Detected high-rise office building, defaulting to 10 floors")
            return 10
        else:
            print("[FLOOR PARSER] Detected tall building, defaulting to 5 floors")
            return 5
    
    # Pattern 7: Look for basement mentions
    has_basement = any(term in description_lower for term in ['basement', 'below grade', 'underground'])
    has_ground = 'ground floor' in description_lower or 'first floor' in description_lower
    
    # Pattern 8: Check for floor-specific mentions
    floor_mentions = []
    specific_floor_patterns = [
        r'(?:first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|sixth|6th|seventh|7th|eighth|8th|ninth|9th|tenth|10th)\s*floor',
        r'floor\s*(?:one|two|three|four|five|six|seven|eight|nine|ten)',
        r'floors?\s*\d+\s*(?:through|to|-)\s*\d+',  # "floors 1 through 5"
    ]
    
    max_floor = 1
    for pattern in specific_floor_patterns:
        matches = re.findall(pattern, description_lower)
        for match in matches:
            # Extract the floor number
            if 'second' in match or '2nd' in match or 'two' in match:
                max_floor = max(max_floor, 2)
            elif 'third' in match or '3rd' in match or 'three' in match:
                max_floor = max(max_floor, 3)
            elif 'fourth' in match or '4th' in match or 'four' in match:
                max_floor = max(max_floor, 4)
            elif 'fifth' in match or '5th' in match or 'five' in match:
                max_floor = max(max_floor, 5)
            # Continue for other floors...
    
    if max_floor > 1:
        print(f"[FLOOR PARSER] Detected {max_floor} floors from specific floor mentions")
        return max_floor
    
    # Pattern 9: Building type defaults
    if 'warehouse' in description_lower or 'distribution' in description_lower:
        # Warehouses are typically single story
        print("[FLOOR PARSER] Warehouse detected, defaulting to 1 floor")
        return 1
    elif 'hospital' in description_lower or 'medical center' in description_lower:
        # Hospitals are typically multi-story
        print("[FLOOR PARSER] Hospital detected, defaulting to 4 floors")
        return 4
    
    # Default: 1 floor plus basement if mentioned
    base_floors = 1
    if has_basement:
        print("[FLOOR PARSER] Basement mentioned, but no above-grade floors specified")
    
    print(f"[FLOOR PARSER] No specific floor count found, defaulting to {base_floors} floor(s)")
    return base_floors


def needs_elevator(floors: int, building_type: str, square_footage: float) -> bool:
    """
    Determine if a building needs elevators based on floors, type, and size
    
    Args:
        floors: Number of floors
        building_type: Type of building (office, healthcare, etc.)
        square_footage: Total building square footage
        
    Returns:
        True if elevators are needed
    """
    # Single story buildings don't need elevators
    if floors <= 1:
        return False
    
    # All healthcare buildings with 2+ floors need elevators (ADA)
    if building_type in ['healthcare', 'medical', 'hospital']:
        return True
    
    # Buildings 3+ stories always need elevators
    if floors >= 3:
        return True
    
    # 2-story buildings need elevators if large or specific types
    if floors == 2:
        # Large 2-story buildings need elevators
        if square_footage > 20000:
            return True
        # Certain building types need elevators at 2 stories
        if building_type in ['educational', 'hotel', 'residential']:
            return True
        # Office buildings only need elevators if large
        if building_type == 'office' and square_footage > 15000:
            return True
    
    return False


def calculate_elevator_count(floors: int, building_type: str, square_footage: float) -> dict:
    """
    Calculate number and type of elevators needed
    
    Returns:
        Dictionary with elevator types and quantities
    """
    if not needs_elevator(floors, building_type, square_footage):
        return {}
    
    total_sf_served = square_footage * 0.9  # Exclude mechanical spaces
    
    elevators = {}
    
    if building_type in ['healthcare', 'medical', 'hospital']:
        # Healthcare needs patient and service elevators
        patient_elevators = max(2, int(total_sf_served / 40000))
        service_elevators = max(1, int(total_sf_served / 60000))
        
        elevators['patient_elevators'] = patient_elevators
        elevators['service_elevators'] = service_elevators
        
    elif building_type in ['residential', 'hotel']:
        # Residential/hotel buildings
        passenger_elevators = max(1, int(total_sf_served / 40000))
        if floors > 10:
            passenger_elevators = max(2, passenger_elevators)
        
        elevators['passenger_elevators'] = passenger_elevators
        
    else:
        # Commercial, educational, office buildings
        # Rule of thumb: 1 elevator per 50,000 SF
        passenger_elevators = max(1, int(total_sf_served / 50000))
        
        # Add service elevator for large buildings
        if square_footage > 100000:
            elevators['service_elevators'] = 1
        
        elevators['passenger_elevators'] = passenger_elevators
    
    return elevators