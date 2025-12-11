"""
Config-Driven NLP Service
Automatically generates detection patterns from master_config
"""
import re
from typing import Dict, Tuple, Optional, List, Any
from app.v2.config.master_config import MASTER_CONFIG, BuildingType


class NLPService:
    """NLP service that automatically syncs with master_config"""

    def __init__(self):
        # Build detection patterns from config
        self.building_patterns = self._build_patterns_from_config()
        # Add manual keyword mappings for common variations
        self.keyword_mappings = self._get_keyword_mappings()
        # Merge patterns
        self._merge_patterns()

    def _build_patterns_from_config(self) -> Dict:
        """Generate detection patterns from master_config automatically"""
        patterns = {}

        for building_type_enum, subtypes in MASTER_CONFIG.items():
            building_type = building_type_enum.value  # Get string value from enum
            patterns[building_type] = {
                'keywords': [],
                'subtypes': {}
            }

            # Generate keywords from building type name
            type_keywords = [
                building_type.replace('_', ' '),
                building_type.replace('_', '-'),
                building_type
            ]
            patterns[building_type]['keywords'] = type_keywords

            # For each subtype
            if isinstance(subtypes, dict):
                for subtype_key in subtypes.keys():
                    # Generate keywords from subtype name
                    subtype_keywords = [
                        subtype_key.replace('_', ' '),
                        subtype_key.replace('_', '-'),
                    ]

                    # Add singular forms
                    if 'apartments' in subtype_key:
                        subtype_keywords.append(subtype_key.replace('apartments', 'apartment'))
                    if 'facilities' in subtype_key:
                        subtype_keywords.append(subtype_key.replace('facilities', 'facility'))

                    patterns[building_type]['subtypes'][subtype_key] = subtype_keywords

        return patterns

    def _get_keyword_mappings(self) -> Dict:
        """Additional mappings for common variations"""
        return {
            'healthcare': {
                # High-level words that mean "this is some kind of healthcare asset"
                'keywords': [
                    'hospital',
                    'medical',
                    'clinic',
                    'health',
                    'surgery',
                    'emergency',
                    'dental',
                    'rehabilitation',
                    'urgent care',
                    'imaging'
                ],
                'subtypes': {
                    # Inpatient, acute-care hospital
                    'hospital': [
                        'hospital',
                        'acute care hospital',
                        'inpatient hospital',
                        'emergency department',
                        'emergency room',
                        'er dept',
                        'icu',
                        'trauma center',
                        'medical campus'
                    ],

                    # Ambulatory surgical center / ASC
                    'surgical_center': [
                        'surgery center',
                        'surgical center',
                        'outpatient surgery',
                        'ambulatory surgery center',
                        'asc',
                        'day surgery center',
                        'same day surgery'
                    ],

                    # TRUE medical office building / landlord asset
                    'medical_office': [
                        'medical office',
                        'medical office building',
                        'mob',
                        'm.o.b.',
                        'multi-tenant medical office',
                        'multi tenant medical office',
                        'medical office tower',
                        'physician office building',
                        'physician office suites',
                        'medical office suites',
                        'physician office',
                        'doctor office building',
                        'doctors office building',
                        "doctor's office building",
                        'clinic office building',
                        'ambulatory office building'
                    ],

                    # Outpatient primary care / multispecialty clinic
                    'outpatient_clinic': [
                        'outpatient clinic',
                        'outpatient primary care clinic',
                        'primary care clinic',
                        'primary care',
                        'family medicine clinic',
                        'family practice clinic',
                        'internal medicine clinic',
                        'community health clinic',
                        'community health center',
                        'health clinic',
                        'ambulatory clinic',
                        'ambulatory care clinic',
                        'multispecialty clinic',
                        'multi-specialty clinic',
                        'group practice clinic'
                    ],

                    # Urgent care / walk-in
                    'urgent_care': [
                        'urgent care',
                        'urgent care center',
                        'walk-in clinic',
                        'walk in clinic',
                        'immediate care',
                        'immediate care center',
                        'express care',
                        'after hours clinic'
                    ],

                    # Dental office / practice
                    'dental_office': [
                        'dental office',
                        'dental clinic',
                        'dentist office',
                        "dentist's office",
                        'dentistry office',
                        'general dentistry',
                        'family dentistry',
                        'orthodontic office',
                        'orthodontist office',
                        'pediatric dental office',
                        'oral surgery office',
                        'endodontic office',
                        'prosthodontic office'
                    ],

                    # Diagnostic imaging
                    'imaging_center': [
                        # Core generic labels
                        'imaging center',
                        'diagnostic imaging center',
                        'diagnostic imaging facility',
                        'medical imaging center',
                        'medical imaging facility',
                        'outpatient imaging center',
                        'outpatient imaging facility',
                        'radiology center',
                        'radiology clinic',
                        'radiology imaging center',

                        # Modality-driven phrases (MRI / CT / PET, etc.)
                        'mri center',
                        'mri imaging center',
                        'ct center',
                        'ct imaging center',
                        'mri and ct center',
                        'mri ct imaging center',
                        'pet center',
                        'pet ct center',
                        'pet-ct imaging center',

                        # Department-style phrases that typically mean a dedicated imaging suite
                        'imaging suite',
                        'diagnostic imaging suite',
                        'radiology department',
                    ],

                    # Larger integrated medical center / campus
                    'medical_center': [
                        'medical center',
                        'health center',
                        'healthcare center',
                        'regional medical center',
                        'medical complex'
                    ],

                    # Seniors / long-term care
                    'nursing_home': [
                        'nursing home',
                        'senior care facility',
                        'assisted living',
                        'assisted living facility',
                        'elder care',
                        'senior living',
                        'long term care',
                        'long-term care',
                        'skilled nursing facility',
                        'snf'
                    ],

                    # Rehab / therapy
                    'rehabilitation': [
                        'rehab center',
                        'rehabilitation center',
                        'physical therapy center',
                        'pt clinic',
                        'therapy clinic',
                        'therapy center',
                        'occupational therapy center',
                        'speech therapy center'
                    ]
                }
            },
            'educational': {
                'keywords': ['school', 'university', 'college', 'education', 'campus', 'academic'],
                'subtypes': {
                    'elementary_school': ['elementary school', 'primary school', 'grade school', 'elementary'],
                    'middle_school': ['middle school', 'junior high', 'intermediate school'],
                    'high_school': ['high school', 'secondary school', 'senior high'],
                    'university': ['university', 'college', 'campus', 'higher education']
                }
            },
            'civic': {
                'keywords': ['government', 'public', 'civic', 'municipal', 'city hall', 'fire station', 'police'],
                'subtypes': {
                    'public_safety': ['fire station', 'police station', 'ems station', 'emergency services'],
                    'government_building': ['city hall', 'government building', 'municipal building', 'federal building'],
                    'courthouse': ['courthouse', 'court building', 'justice center'],
                    'library': ['library', 'public library', 'community library']
                }
            },
            'recreation': {
                'keywords': ['fitness', 'gym', 'sports', 'recreation', 'athletic', 'pool', 'basketball'],
                'subtypes': {
                    'fitness_center': ['fitness center', 'gym', 'health club', 'fitness facility', 'workout'],
                    'sports_complex': ['sports complex', 'athletic center', 'sports facility', 'arena'],
                    'aquatic_center': ['aquatic center', 'pool', 'natatorium', 'swimming pool', 'water park']
                }
            },
            'parking': {
                'keywords': ['parking', 'garage', 'parking lot', 'parking structure'],
                'subtypes': {
                    'parking_garage': ['parking garage', 'parking structure', 'parking deck', 'parking ramp'],
                    'surface_parking': ['parking lot', 'surface parking', 'surface lot']
                }
            },
            'specialty': {
                'keywords': ['data center', 'laboratory', 'self storage', 'storage facility', 'car dealership', 'broadcast'],
                'subtypes': {
                    'self_storage': ['self storage', 'storage facility', 'storage units', 'mini storage'],
                    'data_center': ['data center', 'server farm', 'colocation facility'],
                    'laboratory': ['laboratory', 'lab', 'research facility', 'research lab']
                }
            },
            'mixed_use': {
                'keywords': ['mixed use', 'mixed-use', 'multi-use', 'mixed development'],
                'subtypes': {
                    'retail_residential': ['retail and residential', 'shops and apartments', 'retail residential'],
                    'urban_mixed': ['urban mixed', 'downtown mixed', 'mixed development', 'mixed use development']
                }
            },
            'multifamily': {
                'keywords': ['apartment', 'apartments', 'multifamily', 'multi-family', 'residential complex', 'units'],
                'subtypes': {
                    'luxury_apartments': ['luxury apartment', 'luxury apartments', 'high-end apartment', 'premium apartment'],
                    'market_rate_apartments': ['market rate', 'standard apartment', 'apartment building', 'apartment complex'],
                    'affordable_housing': ['affordable housing', 'low income housing', 'subsidized housing']
                }
            },
            'restaurant': {
                'keywords': ['restaurant', 'dining', 'food', 'bar', 'cafe', 'eatery'],
                'subtypes': {
                    'quick_service': ['fast food', 'quick service', 'qsr', 'drive-thru', 'drive thru'],
                    'full_service': ['casual dining', 'full service restaurant', 'sit-down restaurant'],
                    'fine_dining': ['fine dining', 'upscale restaurant', 'high-end restaurant'],
                    'bar_tavern': ['bar', 'tavern', 'pub', 'brewery', 'sports bar']
                }
            },
            'retail': {
                'keywords': ['retail', 'shopping', 'store', 'shop', 'mall'],
                'subtypes': {
                    'shopping_center': ['shopping center', 'retail center', 'strip mall', 'retail shopping'],
                    'big_box': ['big box', 'department store', 'anchor store', 'large format retail']
                }
            },
            'industrial': {
                'keywords': ['warehouse', 'industrial', 'distribution', 'manufacturing', 'logistics'],
                'subtypes': {
                    'warehouse': ['warehouse', 'storage warehouse', 'bulk storage'],
                    'distribution_center': ['distribution center', 'distribution', 'fulfillment center', 'logistics center'],
                    'manufacturing': ['manufacturing', 'factory', 'production facility', 'plant']
                }
            },
            'office': {
                'keywords': ['office', 'corporate', 'professional', 'business center', 'tower'],
                'subtypes': {
                    'class_a': ['class a office', 'class a', 'premium office', 'grade a', 'class a office tower'],
                    'class_b': ['class b office', 'class b', 'standard office', 'grade b']
                }
            },
            'hospitality': {
                'keywords': ['hotel', 'motel', 'inn', 'hospitality', 'lodging', 'rooms'],
                'subtypes': {
                    'full_service_hotel': ['full service hotel', 'luxury hotel', 'resort', 'conference hotel'],
                    'limited_service_hotel': ['limited service hotel', 'hotel', 'business hotel', 'economy hotel']
                }
            }
        }

    def _merge_patterns(self):
        """Merge manual mappings with auto-generated patterns"""
        for building_type, mappings in self.keyword_mappings.items():
            if building_type in self.building_patterns:
                # Add keywords
                self.building_patterns[building_type]['keywords'].extend(mappings['keywords'])
                # Remove duplicates
                self.building_patterns[building_type]['keywords'] = list(set(self.building_patterns[building_type]['keywords']))

                # Add subtype keywords
                for subtype, keywords in mappings['subtypes'].items():
                    if subtype in self.building_patterns[building_type]['subtypes']:
                        self.building_patterns[building_type]['subtypes'][subtype].extend(keywords)
                        # Remove duplicates
                        self.building_patterns[building_type]['subtypes'][subtype] = list(set(
                            self.building_patterns[building_type]['subtypes'][subtype]
                        ))

    def detect_building_type_with_subtype(self, text: str) -> Tuple[str, Optional[str], str]:
        """Detect building type and subtype using config-driven patterns"""
        text_lower = text.lower()

        # Detect classification first
        classification = self.detect_project_classification(text)

        dental_phrases = [
            'dental office',
            'dental clinic',
            'dentist office',
            "dentist's office",
            'orthodontic office'
        ]
        if any(phrase in text_lower for phrase in dental_phrases):
            return 'healthcare', 'dental_office', classification

        mob_keywords = [
            'medical office',
            'medical office building',
            'mob ',
            ' mob',
            'm.o.b.'
        ]
        if any(keyword in text_lower for keyword in mob_keywords):
            return 'healthcare', 'medical_office', classification

        # Priority order (check specific before general)
        PRIORITY_ORDER = [
            'mixed_use',       # Check first - often contains other keywords
            'healthcare',      # Very specific
            'educational',
            'civic',
            'recreation',
            'specialty',
            'parking',
            'multifamily',
            'hospitality',
            'restaurant',
            'retail',
            'industrial',
            'office'          # Most general (default)
        ]

        # Check each building type in priority order
        for building_type in PRIORITY_ORDER:
            if building_type not in self.building_patterns:
                continue

            patterns = self.building_patterns[building_type]

            # Check subtype keywords first (more specific)
            for subtype_key, keywords in patterns['subtypes'].items():
                for keyword in sorted(keywords, key=len, reverse=True):  # Check longer phrases first
                    if keyword in text_lower:
                        return building_type, subtype_key, classification

            # Then check general type keywords
            for keyword in patterns['keywords']:
                if keyword in text_lower:
                    # Found building type, get default subtype
                    subtype = self._get_default_subtype(building_type)
                    return building_type, subtype, classification

        # Default fallback
        return 'office', 'class_b', classification

    def _get_default_subtype(self, building_type: str) -> str:
        """Get default subtype for a building type"""
        defaults = {
            'multifamily': 'market_rate_apartments',
            'office': 'class_b',
            'retail': 'shopping_center',
            'industrial': 'warehouse',
            'hospitality': 'limited_service_hotel',
            'restaurant': 'full_service',
            'healthcare': 'medical_office',
            'educational': 'elementary_school',
            'civic': 'government_building',
            'recreation': 'recreation_center',
            'mixed_use': 'urban_mixed',
            'parking': 'parking_garage',
            'specialty': 'data_center'
        }
        return defaults.get(building_type, list(self.building_patterns[building_type]['subtypes'].keys())[0])

    def detect_project_classification(self, text: str) -> str:
        """Detect project classification from natural language description"""
        text_lower = text.lower()

        # Check renovation keywords first (most specific)
        renovation_keywords = [
            'renovate', 'renovation', 'remodel', 'retrofit', 'modernize',
            'update existing', 'gut renovation', 'tenant improvement',
            'ti ', ' ti,', ' ti.', 'refresh', 'refurbish', 'rehabilitate',
            'restore', 'convert', 'conversion', 'transform existing'
        ]

        # Check addition keywords
        addition_keywords = [
            'addition', 'expansion', 'extend', 'extension', 'add on',
            'add-on', 'add to existing', 'enlarge', 'expand existing'
        ]

        # Check ground-up keywords
        ground_up_keywords = [
            'ground up', 'ground-up', 'new construction', 'new build',
            'empty lot', 'vacant lot', 'greenfield', 'from scratch'
        ]

        for keyword in renovation_keywords:
            if keyword in text_lower:
                return 'renovation'

        for keyword in addition_keywords:
            if keyword in text_lower:
                return 'addition'

        for keyword in ground_up_keywords:
            if keyword in text_lower:
                return 'ground_up'

        # Default to ground_up if uncertain
        return 'ground_up'

    def extract_project_details(self, text: str) -> Dict[str, Any]:
        """Main parsing function that returns all extracted information"""
        # Detect building type and subtype
        building_type, building_subtype, classification = self.detect_building_type_with_subtype(text)

        # Extract other details
        square_footage = self._extract_square_footage(text)
        floors = self._extract_floors(text, building_type)
        location = self._extract_location(text)

        # Parse additional features
        extracted = {
            'building_type': building_type,
            'subtype': building_subtype,  # Primary field expected by API
            'building_subtype': building_subtype,  # Keep for backwards compatibility
            'project_classification': classification,
            'square_footage': square_footage,
            'floors': floors,
            'location': location,
            'description': text,
            'has_kitchen': self._has_kitchen(text),
            'has_bar': self._has_bar(text),
            'has_drive_thru': self._has_drive_thru(text)
        }

        # Log for debugging
        print(f"[NLP] Parsed: type='{building_type}', subtype='{building_subtype}', SF={square_footage}, floors={floors}, location='{location}'")

        return extracted

    def _extract_square_footage(self, text: str) -> Optional[int]:
        """Extract square footage from text"""
        # Patterns to match various SF formats
        # Order matters - try most specific first
        patterns = [
            # Match numbers with commas: "65,000 SF" or "1,234,567 sq ft"
            r'(\d{1,3}(?:,\d{3})+)\s*(?:SF|sf|sq\.?\s*ft\.?|square\s*feet)',
            # Match numbers without commas: "65000 SF" or "1234567 sq ft"
            r'(\d+)\s*(?:SF|sf|sq\.?\s*ft\.?|square\s*feet)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Remove commas and convert to int
                sf_str = match.group(1).replace(',', '')
                try:
                    return int(sf_str)
                except ValueError:
                    continue
        return None

    def _extract_floors(self, text: str, building_type: str = None) -> int:
        """Extract floor count or use smart defaults"""
        from app.core.floor_parser import extract_floors

        # Try to extract floors from text first
        floors = extract_floors(text)
        if floors and floors > 0:
            return floors

        # Use smart defaults if not found
        text_lower = text.lower()

        if building_type == 'multifamily':
            if 'tower' in text_lower or 'high-rise' in text_lower:
                return 20
            elif 'mid-rise' in text_lower:
                return 6
            else:
                return 4
        elif building_type == 'office' and 'tower' in text_lower:
            return 20
        elif building_type == 'healthcare' and 'hospital' in text_lower:
            return 5
        elif building_type == 'parking' and 'garage' in text_lower:
            return 5
        elif building_type == 'hospitality':
            return 4
        elif building_type == 'educational':
            return 2

        return 1

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text"""
        # Common Tennessee cities and areas
        locations = [
            'Nashville', 'Franklin', 'Brentwood', 'Murfreesboro',
            'Antioch', 'La Vergne', 'Smyrna', 'Downtown',
            'Hendersonville', 'Gallatin', 'Lebanon', 'Mount Juliet'
        ]

        text_lower = text.lower()

        print(f"[NLP] Extracted location: '{text}' from text: '{text}'")

        # Check for state abbreviations
        if ' tn' in text_lower or ' tennessee' in text_lower:
            match = re.search(r'in\s+([A-Za-z\s]+?)(?:\s+tn|\s+tennessee)', text, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()

        # Check for known locations
        for location in locations:
            if location.lower() in text_lower:
                return location

        # Look for "in [Location]" pattern
        match = re.search(r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
        if match:
            return match.group(1)

        return "Nashville"  # Default

    def _has_kitchen(self, text: str) -> bool:
        """Check if project includes a kitchen"""
        kitchen_keywords = ['kitchen', 'culinary', 'cooking', 'food prep', 'restaurant']
        return any(keyword in text.lower() for keyword in kitchen_keywords)

    def _has_bar(self, text: str) -> bool:
        """Check if project includes a bar"""
        bar_keywords = ['bar', 'tavern', 'pub', 'brewery', 'cocktail', 'lounge']
        return any(keyword in text.lower() for keyword in bar_keywords)

    def _has_drive_thru(self, text: str) -> bool:
        """Check if project includes a drive-thru"""
        drive_thru_keywords = ['drive-thru', 'drive thru', 'drive through', 'drive-through']
        return any(keyword in text.lower() for keyword in drive_thru_keywords)

    # Compatibility methods for existing code
    def parse_unit_mix(self, text: str) -> Dict[str, Any]:
        """Parse unit mix information from text"""
        # Basic implementation for compatibility
        return {}

    def generate_project_name(self, description: str, parsed_data: dict) -> str:
        """Generate a project name from description"""
        building_type = parsed_data.get('building_type', 'Project')
        location = parsed_data.get('location', 'Nashville')
        subtype = parsed_data.get('building_subtype', '')

        if subtype:
            name_parts = [subtype.replace('_', ' ').title(), 'in', location]
        else:
            name_parts = [building_type.replace('_', ' ').title(), 'in', location]

        return ' '.join(name_parts)


# Create singleton instance
nlp_service = NLPService()
