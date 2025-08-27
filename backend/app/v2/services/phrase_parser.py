"""
Simplified phrase-first parser using standardized taxonomy.
Replaces complex NLP with simple, predictable pattern matching.
"""
import re
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from app.core.building_taxonomy import (
    normalize_building_type,
    validate_building_type
)
import logging

logger = logging.getLogger(__name__)

# Load taxonomy
TAXONOMY_PATH = Path(__file__).parent.parent.parent.parent.parent / "shared" / "building_types.json"
if not TAXONOMY_PATH.exists():
    # Try alternative path
    TAXONOMY_PATH = Path("/Users/codymarchant/specsharp/shared/building_types.json")

with open(TAXONOMY_PATH) as f:
    TAXONOMY = json.load(f)

class PhraseParser:
    """
    Simple, predictable parser that:
    1. Matches complete phrases first
    2. Falls back to keywords only if needed
    3. Uses standardized taxonomy
    """
    
    def __init__(self):
        # Build phrase mappings from taxonomy
        self.phrase_mappings = self._build_phrase_mappings()
        
    def _build_phrase_mappings(self) -> Dict[str, Tuple[str, str]]:
        """Build phrase -> (type, subtype) mappings from taxonomy"""
        mappings = {}
        
        # Add complete phrases for each subtype
        for building_type, config in TAXONOMY['building_types'].items():
            for subtype, subtype_config in config.get('subtypes', {}).items():
                # Add the display name as a phrase
                display = subtype_config.get('display_name', '')
                if display:
                    mappings[display.lower()] = (building_type, subtype)
                
                # Add keywords as phrases
                for keyword in subtype_config.get('keywords', []):
                    mappings[keyword.lower()] = (building_type, subtype)
        
        # Add specific multi-word phrases that should match first
        priority_phrases = {
            # Educational phrases
            'elementary school': ('educational', 'elementary_school'),
            'middle school': ('educational', 'middle_school'),
            'high school': ('educational', 'high_school'),
            'university campus': ('educational', 'university'),
            'college campus': ('educational', 'university'),
            
            # Healthcare phrases
            'medical office building': ('healthcare', 'medical_office'),
            'medical office': ('healthcare', 'medical_office'),
            'medical center': ('healthcare', 'hospital'),
            'urgent care center': ('healthcare', 'urgent_care'),
            'urgent care': ('healthcare', 'urgent_care'),
            'surgical center': ('healthcare', 'surgical_center'),
            'surgery center': ('healthcare', 'surgical_center'),
            
            # Multifamily phrases - MUST come before single-family residential
            'luxury apartment complex': ('multifamily', 'luxury_apartments'),
            'luxury apartment': ('multifamily', 'luxury_apartments'),
            'luxury apartments': ('multifamily', 'luxury_apartments'),
            'apartment complex': ('multifamily', 'market_rate_apartments'),
            'apartment building': ('multifamily', 'market_rate_apartments'),
            'apartments': ('multifamily', 'market_rate_apartments'),
            'apartment': ('multifamily', 'market_rate_apartments'),
            'affordable housing': ('multifamily', 'affordable_housing'),
            'student housing': ('multifamily', 'student_housing'),
            'student dormitory': ('multifamily', 'student_housing'),
            'senior living': ('multifamily', 'senior_living'),
            'assisted living': ('multifamily', 'senior_living'),
            'multifamily': ('multifamily', 'market_rate_apartments'),
            'multi-family': ('multifamily', 'market_rate_apartments'),
            'condo complex': ('multifamily', 'market_rate_apartments'),
            'condominium': ('multifamily', 'market_rate_apartments'),
            'townhomes': ('multifamily', 'market_rate_apartments'),
            'townhouses': ('multifamily', 'market_rate_apartments'),
            
            # Office phrases
            'class a office building': ('office', 'class_a'),
            'class a office': ('office', 'class_a'),
            'class b office building': ('office', 'class_b'),
            'class b office': ('office', 'class_b'),
            'class c office building': ('office', 'class_c'),
            'class c office': ('office', 'class_c'),
            'office building': ('office', 'class_b'),
            'corporate campus': ('office', 'corporate_campus'),
            'corporate headquarters': ('office', 'corporate_campus'),
            'coworking space': ('office', 'coworking'),
            
            # Industrial phrases
            'distribution center': ('industrial', 'warehouse'),
            'fulfillment center': ('industrial', 'warehouse'),
            'manufacturing facility': ('industrial', 'manufacturing'),
            'manufacturing plant': ('industrial', 'manufacturing'),
            'flex space': ('industrial', 'flex_space'),
            'data center': ('industrial', 'data_center'),
            
            # Retail phrases
            'shopping center': ('retail', 'shopping_center'),
            'strip mall': ('retail', 'strip_mall'),
            'strip center': ('retail', 'strip_mall'),
            'big box retail': ('retail', 'big_box'),
            'grocery store': ('retail', 'grocery'),
            'supermarket': ('retail', 'grocery'),
            
            # Hospitality phrases
            'luxury hotel': ('hospitality', 'luxury_hotel'),
            'business hotel': ('hospitality', 'business_hotel'),
            'limited service hotel': ('hospitality', 'limited_service'),
            'extended stay': ('hospitality', 'extended_stay'),
            
            # Restaurant phrases
            'full-service restaurant': ('restaurant', 'full_service'),
            'full service restaurant': ('restaurant', 'full_service'),
            'quick service restaurant': ('restaurant', 'quick_service'),
            'fast food': ('restaurant', 'quick_service'),
            'casual dining': ('restaurant', 'casual_dining'),
            'fine dining': ('restaurant', 'fine_dining'),
            'sports bar': ('restaurant', 'bar_tavern'),
            'bar and grill': ('restaurant', 'bar_tavern'),
            'tavern': ('restaurant', 'bar_tavern'),
            'pub': ('restaurant', 'bar_tavern'),
            'cocktail bar': ('restaurant', 'bar_tavern'),
            'lounge': ('restaurant', 'bar_tavern'),
            'nightclub': ('restaurant', 'bar_tavern'),
            'brewpub': ('restaurant', 'bar_tavern'),
            'coffee shop': ('restaurant', 'cafe'),
            'cafe': ('restaurant', 'cafe'),
            'bakery cafe': ('restaurant', 'cafe'),
        }
        
        mappings.update(priority_phrases)
        return mappings
    
    def parse(self, description: str) -> Dict[str, any]:
        """
        Parse description using phrase-first approach.
        
        Process:
        1. Extract square footage, floors, location
        2. Look for complete phrases FIRST
        3. Fall back to single keywords only if no phrase matches
        4. Normalize through taxonomy
        """
        description_lower = description.lower()
        logger.debug(f"Parsing: {description_lower}")
        
        # Extract square footage
        sf_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*(?:sf|square feet|sq ft)', description_lower)
        square_footage = int(sf_match.group(1).replace(',', '')) if sf_match else 100000
        
        # Extract floors
        floor_match = re.search(r'(\d+)\s*(?:floor|story|stories)', description_lower)
        floors = int(floor_match.group(1)) if floor_match else None
        
        # Extract location (simple list for now)
        location = self._extract_location(description)
        
        # Extract project class
        project_class = self._extract_project_class(description_lower)
        
        # PHRASE-FIRST MATCHING
        building_type = None
        building_subtype = None
        
        # Step 1: Try to match complete phrases (longest first)
        sorted_phrases = sorted(self.phrase_mappings.keys(), key=len, reverse=True)
        for phrase in sorted_phrases:
            if phrase in description_lower:
                building_type, building_subtype = self.phrase_mappings[phrase]
                logger.debug(f"Matched phrase '{phrase}' -> {building_type}/{building_subtype}")
                break
        
        # Step 2: If no phrase matched, try single keywords
        if not building_type:
            # Simple keyword fallbacks
            keyword_fallbacks = {
                'school': ('educational', 'high_school'),
                'hospital': ('healthcare', 'hospital'),
                'apartment': ('multifamily', 'market_rate_apartments'),
                'office': ('office', 'class_b'),  # Changed from commercial to office
                'warehouse': ('industrial', 'warehouse'),
                'retail': ('retail', 'standalone'),
                'hotel': ('hospitality', 'business_hotel'),
                'restaurant': ('restaurant', 'casual_dining'),
                'bar': ('restaurant', 'bar_tavern'),
                'clinic': ('healthcare', 'medical_office'),
                'condo': ('multifamily', 'market_rate_apartments'),
                'multifamily': ('multifamily', 'market_rate_apartments'),
                'industrial': ('industrial', 'flex_space'),
            }
            
            for keyword, (type_val, subtype_val) in keyword_fallbacks.items():
                if keyword in description_lower:
                    building_type = type_val
                    building_subtype = subtype_val
                    logger.debug(f"Matched keyword '{keyword}' -> {building_type}/{building_subtype}")
                    break
        
        # Step 3: Default if nothing matched
        if not building_type:
            building_type = 'office'
            building_subtype = 'class_b'
            logger.debug(f"No match found, using default: {building_type}/{building_subtype}")
        
        # Step 4: Validate through taxonomy
        building_type, building_subtype = validate_building_type(building_type, building_subtype)
        
        # Estimate floors if not provided
        if not floors:
            floors = self._estimate_floors(square_footage, building_type)
        
        result = {
            'building_type': building_type,
            'subtype': building_subtype,
            'building_subtype': building_subtype,  # For compatibility
            'square_footage': square_footage,
            'floors': floors,
            'location': location,
            'project_class': project_class,
            'description': description,
            'confidence': 0.95  # High confidence for phrase matching
        }
        
        logger.debug(f"Parse result: {result}")
        return result
    
    def _extract_location(self, description: str) -> str:
        """Extract location from description"""
        description_lower = description.lower()
        
        # Common cities to check
        cities = [
            'Nashville', 'Memphis', 'Knoxville', 'Chattanooga',
            'Franklin', 'Murfreesboro', 'Clarksville',
            'New York', 'Los Angeles', 'Chicago', 'Houston',
            'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego',
            'Dallas', 'San Jose', 'Austin', 'Jacksonville',
            'Boston', 'Seattle', 'Denver', 'Washington',
            'Miami', 'Atlanta', 'Las Vegas', 'Portland'
        ]
        
        for city in cities:
            if city.lower() in description_lower:
                return city
        
        # Check for "in [City]" pattern
        in_pattern = re.search(r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', description)
        if in_pattern:
            return in_pattern.group(1)
        
        return 'Nashville'  # Default
    
    def _extract_project_class(self, description_lower: str) -> str:
        """Extract project classification"""
        if any(term in description_lower for term in ['renovation', 'renovate', 'remodel', 'retrofit']):
            return 'renovation'
        elif any(term in description_lower for term in ['addition', 'expansion', 'extend']):
            return 'addition'
        elif any(term in description_lower for term in ['tenant improvement', 'ti ', 'build-out']):
            return 'tenant_improvement'
        else:
            return 'ground_up'
    
    def _estimate_floors(self, sf: int, building_type: str) -> int:
        """Simple floor estimation based on building type"""
        estimates = {
            'multifamily': max(3, sf // 25000),
            'healthcare': max(1, min(10, sf // 50000)),
            'educational': min(3, max(1, sf // 30000)),
            'office': max(1, min(50, sf // 15000)),
            'industrial': 1,  # Usually single story
            'retail': 1,
            'hospitality': max(3, min(20, sf // 20000)),
            'restaurant': 1,
            'civic': max(1, min(5, sf // 20000)),
            'recreation': 1,
            'parking': max(1, min(8, sf // 10000))
        }
        return estimates.get(building_type, max(1, sf // 20000))

# Singleton instance
phrase_parser = PhraseParser()