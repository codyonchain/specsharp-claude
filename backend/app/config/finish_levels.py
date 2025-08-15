"""
Finish level multipliers for different quality levels.
Applied to base construction cost.
"""

FINISH_LEVELS = {
    'basic': {
        'multiplier': 0.85,
        'description': 'Basic finishes, minimal amenities',
        'characteristics': [
            'Vinyl tile flooring',
            'Basic paint',
            'Standard fixtures',
            'Minimal millwork'
        ]
    },
    'standard': {
        'multiplier': 1.00,
        'description': 'Standard commercial grade finishes',
        'characteristics': [
            'Commercial carpet/VCT',
            'Standard paint and wallcovering',
            'Commercial grade fixtures',
            'Standard millwork'
        ]
    },
    'premium': {
        'multiplier': 1.25,
        'description': 'High-end finishes and materials',
        'characteristics': [
            'Wood/stone flooring',
            'Designer finishes',
            'Premium fixtures',
            'Custom millwork'
        ]
    },
    'luxury': {
        'multiplier': 1.50,
        'description': 'Luxury finishes, top-tier materials',
        'characteristics': [
            'Imported stone/hardwood',
            'Custom architectural features',
            'Designer fixtures',
            'Extensive custom millwork'
        ]
    }
}

PROJECT_CLASSIFICATIONS = {
    'ground_up': {
        'multiplier': 1.00,
        'description': 'New construction from ground up',
        'cost_impacts': [
            'Full site work included',
            'New utilities',
            'Standard construction access',
            'No demolition required'
        ]
    },
    'addition': {
        'multiplier': 1.15,
        'description': 'Addition to existing building',
        'cost_impacts': [
            'Structural tie-ins (2.5%)',
            'Weather protection (1%)',
            'Existing building protection (1.5%)',
            'Limited access premium (1%)',
            'Phased construction (1%)',
            'Matching existing finishes (2%)',
            'Connection to existing MEP (3%)',
            'Temporary walls/dust control (1%)',
            'Protection of operations (2%)'
        ]
    },
    'renovation': {
        'multiplier': 1.35,
        'description': 'Major renovation of existing space',
        'cost_impacts': [
            'Selective demolition (4%)',
            'Hazardous material allowance (2.5%)',
            'Dust protection & barriers (2%)',
            'Phased construction premium (1.5%)',
            'Unknown conditions (3%)',
            'Temporary systems (2%)',
            'Off-hours work (3%)',
            'Material handling (2%)',
            'Protection of occupants (2.5%)',
            'Code upgrades (3%)',
            'Structural modifications (2.5%)',
            'MEP system integration (3%)',
            'Limited staging area (1.5%)',
            'Additional coordination (2%)'
        ]
    },
    'tenant_improvement': {
        'multiplier': 1.20,
        'description': 'Interior tenant improvements',
        'cost_impacts': [
            'Limited demolition (2%)',
            'Building rules compliance (1%)',
            'After-hours work (2%)',
            'Freight elevator coordination (1%)',
            'Base building tie-ins (3%)',
            'Dust/noise control (2%)',
            'Protection of common areas (1.5%)',
            'Limited access/staging (1.5%)',
            'Existing tenant coordination (2%)',
            'Building management fees (1%)',
            'Security requirements (1%)',
            'Material delivery restrictions (2%)'
        ]
    },
    'adaptive_reuse': {
        'multiplier': 1.45,
        'description': 'Converting building to new use',
        'cost_impacts': [
            'Major demolition (5%)',
            'Structural modifications (4%)',
            'Complete MEP replacement (5%)',
            'Code compliance upgrades (4%)',
            'Historic preservation (3%)',
            'Hazmat remediation (3%)',
            'Unknown conditions (4%)',
            'Special engineering (2%)',
            'Phased construction (2%)',
            'Temporary systems (2.5%)',
            'Site constraints (2%)',
            'Documentation requirements (1.5%)',
            'Agency approvals (2%)',
            'Extended timeline costs (3%)'
        ]
    }
}

# Healthcare-specific classification adjustments
HEALTHCARE_CLASSIFICATION_MULTIPLIERS = {
    'hospital': {
        'addition': 1.25,  # Higher than standard 1.15 due to 24/7 operations
        'renovation': 1.45  # Higher than standard 1.35 due to critical systems
    },
    'surgical_center': {
        'addition': 1.20,
        'renovation': 1.40
    },
    'medical_office': {
        'addition': 1.15,  # Standard multiplier
        'renovation': 1.35  # Standard multiplier
    }
}

def get_finish_multiplier(level: str) -> float:
    """Get multiplier for finish level"""
    if level and level in FINISH_LEVELS:
        return FINISH_LEVELS[level]['multiplier']
    return FINISH_LEVELS['standard']['multiplier']

def get_classification_multiplier(classification: str, building_type: str = None, subtype: str = None) -> float:
    """Get multiplier for project classification, with special handling for healthcare"""
    
    # Check for healthcare-specific multipliers
    if building_type == 'healthcare' and subtype and classification != 'ground_up':
        if subtype in HEALTHCARE_CLASSIFICATION_MULTIPLIERS:
            if classification in HEALTHCARE_CLASSIFICATION_MULTIPLIERS[subtype]:
                return HEALTHCARE_CLASSIFICATION_MULTIPLIERS[subtype][classification]
    
    # Return standard classification multiplier
    if classification and classification in PROJECT_CLASSIFICATIONS:
        return PROJECT_CLASSIFICATIONS[classification]['multiplier']
    
    return PROJECT_CLASSIFICATIONS['ground_up']['multiplier']

def get_finish_level_description(level: str) -> dict:
    """Get full description of finish level"""
    if level in FINISH_LEVELS:
        return FINISH_LEVELS[level]
    return FINISH_LEVELS['standard']

def get_classification_description(classification: str) -> dict:
    """Get full description of project classification"""
    if classification in PROJECT_CLASSIFICATIONS:
        return PROJECT_CLASSIFICATIONS[classification]
    return PROJECT_CLASSIFICATIONS['ground_up']

def detect_classification_from_text(description: str) -> str:
    """Detect project classification from natural language description"""
    description_lower = description.lower()
    
    # Keywords for each classification
    addition_keywords = ['addition', 'expansion', 'extend', 'add to', 'adding', 'new wing', 'annex']
    renovation_keywords = ['renovation', 'remodel', 'retrofit', 'modernize', 'update', 'renovate', 'rehab', 'refurbish']
    tenant_keywords = ['tenant improvement', 'ti', 'fit-out', 'fitout', 'build-out', 'buildout', 'interior']
    adaptive_keywords = ['adaptive reuse', 'conversion', 'convert', 'repurpose', 'transform']
    
    # Check for keywords
    for keyword in adaptive_keywords:
        if keyword in description_lower:
            return 'adaptive_reuse'
    
    for keyword in renovation_keywords:
        if keyword in description_lower:
            return 'renovation'
    
    for keyword in tenant_keywords:
        if keyword in description_lower:
            return 'tenant_improvement'
    
    for keyword in addition_keywords:
        if keyword in description_lower:
            return 'addition'
    
    # Default to ground up
    return 'ground_up'