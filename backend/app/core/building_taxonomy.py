"""
Single source of truth for building types.
ALL building type references should use this module.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Load the canonical taxonomy - Updated for hotel subtypes
_HERE = Path(__file__).resolve()

def _find_taxonomy_path() -> Path:
    # Walk upward from this file and find the first shared/building_types.json
    for parent in [_HERE.parent] + list(_HERE.parents):
        candidate = parent / "shared" / "building_types.json"
        if candidate.exists():
            return candidate
    # Final fallback: backend-shipped copy (Railway root dir = backend)
    fallback = Path.cwd() / "shared" / "building_types.json"
    return fallback

TAXONOMY_PATH = _find_taxonomy_path()
with open(TAXONOMY_PATH) as f:
    TAXONOMY = json.load(f)

CUSTOM_SUBTYPE_KEYWORDS = {
    'healthcare': {
        'medical_office': [
            'medical office',
            'medical office building',
            'mob',
            'm.o.b.'
        ],
        'dental_office': [
            'dental office',
            'dental clinic',
            'dentist office',
            "dentist's office",
            'orthodontic office',
            'pediatric dental office'
        ]
    }
}

# Create enum from the canonical source - using UPPERCASE for consistency
CanonicalBuildingType = Enum('CanonicalBuildingType', {
    k.upper(): k for k in TAXONOMY['building_types'].keys()
})

class BuildingTaxonomy:
    """Central authority for building type classification"""
    
    @staticmethod
    def normalize_type(type_string: str) -> str:
        """
        Convert any building type string to canonical form.
        
        Examples:
            'multifamily' -> 'residential'
            'multi_family_residential' -> 'residential'
            'office' -> 'commercial'
            'HEALTHCARE' -> 'healthcare'
        """
        if not type_string:
            return 'office'  # Default

        # Preserve underscore canonical IDs (e.g. mixed_use) before loose matching.
        canonical_candidate = type_string.lower().strip().replace('-', '_').replace(' ', '_')
        if canonical_candidate in TAXONOMY['building_types']:
            return canonical_candidate

        type_lower = type_string.lower().replace('_', ' ').replace('-', ' ').strip()
        
        # Check aliases
        for canonical, config in TAXONOMY['building_types'].items():
            if 'aliases' in config:
                # Check exact match in aliases
                if type_lower in [a.lower().replace('_', ' ') for a in config['aliases']]:
                    logger.debug(f"Normalized '{type_string}' to '{canonical}' via alias")
                    return canonical
                
                # Check if any alias is contained in the type string
                for alias in config['aliases']:
                    if alias.lower() in type_lower or type_lower in alias.lower():
                        logger.debug(f"Normalized '{type_string}' to '{canonical}' via partial alias match")
                        return canonical
        
        # Special cases for common variations - Updated to match master_config.py
        special_mappings = {
            'multi family': 'multifamily',
            'multifamily': 'multifamily',
            'multi family residential': 'multifamily',
            'apartments': 'multifamily',
            'apartment': 'multifamily',
            'residential': 'multifamily',  # Map old residential to multifamily
            'medical': 'healthcare',
            'education': 'educational',
            'commercial': 'office',  # Map old commercial to office
            'office': 'office',
            'warehouse': 'industrial',
            'manufacturing': 'industrial',
            'shopping': 'retail',
            'store': 'retail',
            'hotel': 'hospitality',
            'lodging': 'hospitality',
            'dining': 'restaurant',
            'food service': 'restaurant',
            'mixed use': 'mixed_use',
        }
        
        for pattern, canonical in special_mappings.items():
            if pattern in type_lower:
                logger.debug(f"Normalized '{type_string}' to '{canonical}' via special mapping")
                return canonical
        
        # Default to office if unknown
        logger.warning(f"Unknown building type '{type_string}', defaulting to 'office'")
        return 'office'
    
    @staticmethod
    def get_canonical_types() -> List[str]:
        """Get list of canonical building types"""
        return list(TAXONOMY['building_types'].keys())
    
    @staticmethod
    def get_display_name(building_type: str) -> str:
        """Get display name for a building type"""
        canonical = BuildingTaxonomy.normalize_type(building_type)
        return TAXONOMY['building_types'][canonical].get('display_name', canonical.title())
    
    @staticmethod
    def get_subtypes(building_type: str) -> List[str]:
        """Get valid subtypes for a building type"""
        canonical = BuildingTaxonomy.normalize_type(building_type)
        subtypes_dict = TAXONOMY['building_types'][canonical].get('subtypes', {})
        return list(subtypes_dict.keys())
    
    @staticmethod
    def get_subtype_info(building_type: str, subtype: str) -> Optional[Dict]:
        """Get detailed information about a subtype"""
        canonical = BuildingTaxonomy.normalize_type(building_type)
        subtypes = TAXONOMY['building_types'][canonical].get('subtypes', {})
        return subtypes.get(subtype)
    
    @staticmethod
    def normalize_subtype(building_type: str, subtype: str) -> Optional[str]:
        """
        Normalize a subtype string to canonical form.
        
        Examples:
            ('healthcare', 'MOB') -> 'medical_office'
            ('residential', 'luxury') -> 'luxury_apartments'
        """
        if not subtype:
            return None
            
        canonical_type = BuildingTaxonomy.normalize_type(building_type)
        valid_subtypes = BuildingTaxonomy.get_subtypes(canonical_type)
        
        subtype_lower = subtype.lower().replace('-', '_').replace(' ', '_')
        
        # Direct match
        if subtype_lower in valid_subtypes:
            return subtype_lower
        
        # Check keywords (pick best match by keyword specificity)
        subtypes_dict = TAXONOMY['building_types'][canonical_type].get('subtypes', {})
        best_match = None
        best_score = (-1, -1)  # (length, word_count)
        for valid_sub, config in subtypes_dict.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in subtype_lower or subtype_lower in keyword_lower:
                    score = (len(keyword_lower), keyword_lower.count(' '))
                    if score > best_score:
                        best_score = score
                        best_match = valid_sub
        if best_match:
            logger.debug(f"Normalized subtype '{subtype}' to '{best_match}' via keyword")
            return best_match
        
        # Partial match
        for valid_sub in valid_subtypes:
            if valid_sub in subtype_lower or subtype_lower in valid_sub:
                return valid_sub

        custom_keywords = CUSTOM_SUBTYPE_KEYWORDS.get(canonical_type, {})
        for valid_sub, keywords in custom_keywords.items():
            for keyword in keywords:
                keyword_normalized = keyword.lower().replace('-', '_').replace(' ', '_')
                if keyword_normalized in subtype_lower or subtype_lower in keyword_normalized:
                    logger.debug(f"Normalized subtype '{subtype}' to '{valid_sub}' via custom keyword")
                    return valid_sub
        
        return None
    
    @staticmethod
    def validate(building_type: str, subtype: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Validate and normalize a building type/subtype pair.
        Returns canonical (type, subtype) tuple.
        
        If subtype is invalid or None, returns (canonical_type, None)
        """
        canonical_type = BuildingTaxonomy.normalize_type(building_type)
        
        if not subtype:
            return (canonical_type, None)
        
        canonical_subtype = BuildingTaxonomy.normalize_subtype(canonical_type, subtype)
        
        if canonical_subtype:
            return (canonical_type, canonical_subtype)
        
        # Log warning about invalid subtype
        logger.warning(f"Invalid subtype '{subtype}' for type '{canonical_type}'")
        return (canonical_type, None)
    
    @staticmethod
    def get_base_cost_per_sf(building_type: str, subtype: Optional[str] = None) -> float:
        """Get base cost per square foot for a building type/subtype"""
        canonical_type, canonical_subtype = BuildingTaxonomy.validate(building_type, subtype)
        
        if canonical_subtype:
            subtype_info = BuildingTaxonomy.get_subtype_info(canonical_type, canonical_subtype)
            if subtype_info and 'base_cost_per_sf' in subtype_info:
                return subtype_info['base_cost_per_sf']
        
        # Default costs by type
        default_costs = {
            'multifamily': 375,
            'healthcare': 550,
            'educational': 295,
            'office': 350,
            'industrial': 185,
            'retail': 250,
            'hospitality': 425,
            'restaurant': 375,
            'civic': 425,
            'recreation': 325,
            'parking': 65
        }
        
        return default_costs.get(canonical_type, 350)

# Export for easy import
normalize_building_type = BuildingTaxonomy.normalize_type
validate_building_type = BuildingTaxonomy.validate
get_canonical_types = BuildingTaxonomy.get_canonical_types
get_subtypes = BuildingTaxonomy.get_subtypes
get_display_name = BuildingTaxonomy.get_display_name
get_base_cost = BuildingTaxonomy.get_base_cost_per_sf

# Create a mapping from old names to new for migration
MIGRATION_MAP = {
    'multifamily': 'residential',
    'multi_family': 'residential',
    'multi_family_residential': 'residential',
    'medical': 'healthcare',
    'education': 'educational',
    'office': 'commercial',
    'warehouse': 'industrial',
    'manufacturing': 'industrial',
    'shopping': 'retail',
    'hotel': 'hospitality'
}

def migrate_building_type(old_type: str) -> str:
    """Helper to migrate old building type names to new canonical ones"""
    return MIGRATION_MAP.get(old_type.lower(), old_type.lower())
