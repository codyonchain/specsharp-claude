from typing import Dict, List, Optional, Any
import os
import re
from enum import Enum
from app.core.config import settings
from app.core.floor_parser import extract_floors
from app.core.building_type_detector import determine_building_type, get_building_subtype
from app.services.healthcare_cost_service import healthcare_cost_service

# Optional imports
try:
    import openai
except ImportError:
    openai = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    FALLBACK = "fallback"


class NLPService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.openai_api_key and openai:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
        
        if settings.anthropic_api_key and Anthropic:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        
        self.patterns = self._initialize_patterns()
        self.keywords = self._initialize_keywords()
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        return {
            "square_footage": re.compile(r'(\d+(?:,\d+)?)\s*(?:sq\.?\s*ft\.?|square\s*feet|sf)', re.IGNORECASE),
            "dimensions": re.compile(r'(\d+)\s*x\s*(\d+)', re.IGNORECASE),  # For "150x300" format
            "floors": re.compile(r'(\d+)\s*(?:floor|story|storey|level)s?', re.IGNORECASE),
            "budget": re.compile(r'\$\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            "ceiling_height": re.compile(r'(\d+(?:\.\d+)?)\s*(?:ft\.?|feet|foot)\s*(?:ceiling|height)', re.IGNORECASE),
            "room_count": re.compile(r'(\d+)\s*(?:room|office|space)s?', re.IGNORECASE),
            # Unit mix patterns for multi-family residential
            "unit_count": re.compile(r'(\d+)\s*(?:unit|apartment|condo|townhome|townhouse)s?', re.IGNORECASE),
            "studio_units": re.compile(r'(\d+)\s*(?:studio|efficiency)', re.IGNORECASE),
            "one_bedroom": re.compile(r'(\d+)\s*(?:1\s*br|1\s*bed|one\s*bed|1-bed)', re.IGNORECASE),
            "two_bedroom": re.compile(r'(\d+)\s*(?:2\s*br|2\s*bed|two\s*bed|2-bed)', re.IGNORECASE),
            "three_bedroom": re.compile(r'(\d+)\s*(?:3\s*br|3\s*bed|three\s*bed|3-bed)', re.IGNORECASE),
        }
    
    def detect_healthcare_type(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Detect if the project is a healthcare facility and return details
        
        Returns:
            Dictionary with healthcare details or None if not healthcare
        """
        text_lower = text.lower()
        
        # Check if this is a healthcare project
        is_healthcare = False
        healthcare_type = None
        
        for category, keywords in self.keywords.get("healthcare", {}).items():
            for keyword in keywords:
                if keyword in text_lower:
                    is_healthcare = True
                    healthcare_type = category
                    break
            if is_healthcare:
                break
        
        if not is_healthcare:
            # Also check general healthcare terms
            general_healthcare = ["healthcare", "medical", "health facility", "health care"]
            for term in general_healthcare:
                if term in text_lower:
                    is_healthcare = True
                    healthcare_type = "medical_office"  # Default
                    break
        
        if is_healthcare:
            # Get detailed healthcare analysis
            healthcare_details = healthcare_cost_service.get_healthcare_cost(
                description=text,
                occupancy_type="healthcare"
            )
            
            return {
                "is_healthcare": True,
                "healthcare_type": healthcare_type,
                "facility_type": healthcare_details.get("facility_type"),
                "base_cost_per_sf": healthcare_details.get("adjusted_cost_per_sf"),
                "features": healthcare_details.get("features"),
                "complexity": healthcare_details.get("complexity"),
                "trade_breakdown": healthcare_details.get("trade_breakdown")
            }
        
        return None
    
    def detect_project_classification(self, text: str) -> str:
        """
        Detect project classification from natural language description.
        Returns: 'ground_up', 'addition', or 'renovation'
        """
        text_lower = text.lower()
        
        # Check renovation keywords first (most specific)
        renovation_keywords = [
            'renovate', 'renovation', 'remodel', 'retrofit', 'modernize',
            'update existing', 'gut renovation', 'tenant improvement',
            'ti ', ' ti,', ' ti.', 'refresh', 'refurbish', 'rehabilitate', 
            'restore', 'convert', 'conversion', 'transform existing', 
            'upgrade existing', 'existing space', 'existing building',
            'build-out', 'buildout', 'makeover', 'redesign', 'rehab'
        ]
        
        # Check addition keywords
        addition_keywords = [
            'addition', 'expansion', 'extend', 'extension', 'add on',
            'add-on', 'add to existing', 'enlarge', 'expand existing',
            'expand', 'new wing', 'wing', 'building extension',
            'square footage addition', 'add sf', 'connect to existing', 
            'attached to existing', 'annex', 'expanding'
        ]
        
        # Check ground-up keywords
        ground_up_keywords = [
            'ground up', 'ground-up', 'new construction', 'new build',
            'empty lot', 'vacant lot', 'greenfield', 'from scratch',
            'new development', 'new building', 'construct new',
            'brand new', 'undeveloped'
        ]
        
        # Check for explicit keyword matches
        for keyword in renovation_keywords:
            if keyword in text_lower:
                return 'renovation'
        
        for keyword in addition_keywords:
            if keyword in text_lower:
                return 'addition'
        
        for keyword in ground_up_keywords:
            if keyword in text_lower:
                return 'ground_up'
        
        # Context-based inference if no explicit keywords found
        if 'existing' in text_lower and 'add' not in text_lower and 'expand' not in text_lower:
            # "existing" without "add" or "expand" suggests renovation
            return 'renovation'
        elif 'new' in text_lower and 'existing' not in text_lower:
            # "new" without "existing" suggests ground-up
            return 'ground_up'
        
        # Default to ground_up if uncertain
        return 'ground_up'
    
    def _initialize_keywords(self) -> Dict[str, List[str]]:
        return {
            "sustainable": ["leed", "green", "sustainable", "eco-friendly", "energy efficient", "solar"],
            "luxury": ["high-end", "luxury", "premium", "executive", "upscale"],
            "modern": ["modern", "contemporary", "open concept", "minimalist"],
            "traditional": ["traditional", "classic", "conventional"],
            "special_systems": ["data center", "clean room", "laboratory", "kitchen", "auditorium"],
            "restaurant_features": ["restaurant", "dining", "commercial kitchen", "bar", "tavern", "pub", 
                                  "cafe", "bistro", "grill", "diner", "food service", "hospitality",
                                  "full-service", "quick-service", "fast food", "fine dining"],
            "restaurant_equipment": ["hood", "exhaust", "grease trap", "walk-in", "cooler", "freezer",
                                   "fryer", "grill", "range", "oven", "dishwasher", "prep area"],
            "service_levels": {
                "quick_service": ["quick service", "fast food", "fast-food", "qsr", "drive-thru", "drive thru"],
                "casual_dining": ["casual dining", "family restaurant", "casual restaurant"],
                "full_service": ["full service", "full-service", "sit-down", "table service"],
                "fine_dining": ["fine dining", "upscale", "high-end dining", "white tablecloth", "gourmet"]
            },
            "project_classification": {
                "ground_up": ["new construction", "new build", "ground up", "ground-up", "empty lot", 
                             "greenfield", "vacant lot", "undeveloped", "from scratch", "brand new"],
                "addition": ["addition", "expansion", "extension", "add on", "add-on", "enlargement",
                           "expanding", "annex", "wing", "building addition"],
                "renovation": ["renovation", "remodel", "retrofit", "modernize", "update", "refurbish",
                             "rehab", "redesign", "makeover", "restoration", "conversion", "tenant improvement",
                             "TI", "build-out", "buildout", "existing space", "existing building"]
            },
            "healthcare": {
                "hospital": ["hospital", "medical center", "health center", "trauma center", 
                           "emergency department", "emergency room", "acute care", "inpatient"],
                "surgical": ["surgical center", "surgery center", "operating room", "OR suite",
                           "ambulatory surgery", "outpatient surgery", "procedure room"],
                "imaging": ["imaging center", "radiology", "MRI", "CT scan", "x-ray", 
                          "diagnostic imaging", "pet scan", "mammography"],
                "outpatient": ["outpatient", "clinic", "urgent care", "walk-in clinic",
                             "ambulatory care", "immediate care"],
                "medical_office": ["medical office", "doctor office", "physician office",
                                 "primary care", "family medicine", "specialist"],
                "specialty": ["cancer center", "cardiac center", "pediatric", "maternity",
                            "oncology", "cardiology", "neurology", "orthopedic"],
                "senior_care": ["nursing home", "assisted living", "senior living", 
                              "memory care", "long term care", "skilled nursing"]
            },
        }
    
    def extract_project_details(self, text: str) -> Dict[str, Any]:
        extracted = {}
        
        for field, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                if field == "dimensions":
                    # Calculate square footage from dimensions
                    width = int(match.group(1))
                    length = int(match.group(2))
                    extracted["square_footage"] = width * length
                else:
                    value = match.group(1).replace(',', '')
                    if field in ["square_footage", "room_count"]:
                        extracted[field] = int(value)
                    elif field == "floors":
                        # Skip pattern matching for floors - use dedicated parser below
                        continue
                    elif field == "budget":
                        extracted[field] = float(value)
                    elif field == "ceiling_height":
                        extracted[field] = float(value)
        
        # Use dedicated floor parser for better accuracy
        floors = extract_floors(text)
        if floors > 0:
            extracted["floors"] = floors
        
        for category, keywords in self.keywords.items():
            if category == "service_levels":
                # Handle service levels differently as it's a nested dictionary
                for service_level, level_keywords in keywords.items():
                    if any(kw in text.lower() for kw in level_keywords):
                        extracted["service_level"] = service_level
                        break
            elif category == "project_classification":
                # Handle project classification with improved detection
                classification = self.detect_project_classification(text)
                if classification:
                    extracted["project_classification"] = classification
            elif any(keyword in text.lower() for keyword in keywords):
                if category == "special_systems":
                    extracted["special_requirements"] = extracted.get("special_requirements", [])
                    for keyword in keywords:
                        if keyword in text.lower():
                            extracted["special_requirements"].append(keyword)
                elif category == "restaurant_features":
                    extracted["is_restaurant"] = True
                    extracted["restaurant_features"] = [k for k in keywords if k in text.lower()]
                elif category == "restaurant_equipment":
                    extracted["restaurant_equipment"] = extracted.get("restaurant_equipment", [])
                    for keyword in keywords:
                        if keyword in text.lower():
                            extracted["restaurant_equipment"].append(keyword)
                else:
                    extracted[f"style_{category}"] = True
        
        climate_indicators = {
            "hot": ["hot", "warm", "tropical", "desert"],
            "cold": ["cold", "snow", "winter", "freezing"],
            "humid": ["humid", "wet", "rainy"],
            "dry": ["dry", "arid"],
        }
        
        climate_features = []
        for climate_type, indicators in climate_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                climate_features.append(climate_type)
        
        if climate_features:
            extracted["climate_features"] = climate_features
        
        # Extract location
        location = self._extract_location(text)
        if location:
            extracted["location"] = location
            print(f"[NLP] Extracted location: '{location}' from text: '{text}'")
        
        # Check for healthcare facilities first (highest priority)
        healthcare_details = self.detect_healthcare_type(text)
        if healthcare_details:
            extracted["is_healthcare"] = True
            extracted["building_type"] = "healthcare"
            extracted["occupancy_type"] = "healthcare"
            extracted["healthcare_details"] = healthcare_details
            extracted["base_cost_per_sf"] = healthcare_details.get("base_cost_per_sf")
            # Healthcare facilities detected, skip generic building type detection
        else:
            # Extract building type using the centralized detector
            building_type = determine_building_type(text)
            if building_type and building_type != 'commercial':  # Don't return generic 'commercial'
                extracted["building_type"] = building_type
        
        # Extract building mix for mixed-use projects
        building_mix = self._extract_building_mix(text)
        if building_mix:
            extracted["building_mix"] = building_mix
        
        # Determine occupancy type if not already set
        if not extracted.get("occupancy_type"):
            if extracted.get("is_healthcare"):
                extracted["occupancy_type"] = "healthcare"
            elif extracted.get("building_type"):
                extracted["occupancy_type"] = extracted["building_type"]
        
        # Generate smart project name
        suggested_name = self.generate_project_name(text, extracted)
        extracted["suggested_project_name"] = suggested_name
        
        # Add detail suggestions based on occupancy type
        occupancy = extracted.get("occupancy_type", "")
        extracted["detail_suggestions"] = self.get_detail_suggestions(occupancy)
        
        return extracted
    
    async def enhance_scope_with_llm(
        self,
        project_description: str,
        provider: LLMProvider = LLMProvider.OPENAI
    ) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following construction project description and extract key requirements:
        
        "{project_description}"
        
        Please identify and structure:
        1. Project type (residential, commercial, industrial, mixed-use)
        2. Building subtype if applicable (e.g., restaurant, retail, office, warehouse)
        3. Size and scope details
        4. Special requirements or features (especially for restaurants: commercial kitchen, bar, dining areas)
        5. Quality level expectations
        6. Any sustainability or compliance requirements
        7. For restaurants: identify kitchen equipment needs, ventilation requirements, seating capacity
        
        Format the response as a structured analysis.
        """
        
        try:
            if provider == LLMProvider.OPENAI and self.openai_client:
                response = await self._call_openai(prompt)
            elif provider == LLMProvider.ANTHROPIC and self.anthropic_client:
                response = await self._call_anthropic(prompt)
            else:
                response = self._fallback_analysis(project_description)
            
            return self._parse_llm_response(response)
            
        except Exception as e:
            print(f"LLM call failed: {str(e)}, using fallback")
            return self._fallback_analysis(project_description)
    
    async def _call_openai(self, prompt: str) -> str:
        response = self.openai_client.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a construction project analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content
    
    async def _call_anthropic(self, prompt: str) -> str:
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        extracted = self.extract_project_details(text)
        
        # Use centralized building type detection
        occupancy_type = determine_building_type(text)
        building_subtype = get_building_subtype(occupancy_type, text) if occupancy_type != 'commercial' else None
        
        print(f"[NLP] Detected {occupancy_type} building type for: {text}")
        if building_subtype:
            print(f"[NLP] Building subtype: {building_subtype}")
        
        # Parse unit mix for multi-family residential
        if occupancy_type == 'multi_family_residential':
            unit_mix = self.parse_unit_mix(text)
            extracted["unit_mix"] = unit_mix
            print(f"[NLP] Parsed unit mix: {unit_mix}")
        
        # Determine project type based on occupancy type
        if occupancy_type == 'warehouse':
            project_type = "industrial"
        elif occupancy_type == 'multi_family_residential':
            project_type = "commercial"  # Multi-family is considered commercial construction
        elif occupancy_type in ['healthcare', 'educational', 'restaurant', 'retail', 'office']:
            project_type = "commercial"
        elif any(word in text.lower() for word in ["home", "house", "single family"]):
            project_type = "residential"
        elif any(word in text.lower() for word in ["mixed", "multi-use"]):
            project_type = "mixed_use"
        else:
            project_type = "commercial"
        
        # Restaurant was already detected by determine_building_type if applicable
        
        quality_level = "standard"
        if any(word in text.lower() for word in ["luxury", "premium", "high-end", "fine dining"]):
            quality_level = "premium"
        elif any(word in text.lower() for word in ["budget", "economical", "basic", "fast food"]):
            quality_level = "economy"
        
        result = {
            "project_type": project_type,
            "quality_level": quality_level,
            "extracted_details": extracted,
            "analysis_method": "pattern_matching"
        }
        
        result["occupancy_type"] = occupancy_type
        if building_subtype:
            result["building_subtype"] = building_subtype
        
        # Add service level if detected
        if extracted.get("service_level"):
            result["service_level"] = extracted["service_level"]
        elif building_subtype == "restaurant" and not extracted.get("service_level"):
            # Default to full_service if not specified
            result["service_level"] = "full_service"
        
        # Detect building features
        building_features = []
        if building_subtype == "restaurant":
            # Check for specific restaurant features
            if any(word in text.lower() for word in ["commercial kitchen", "kitchen"]):
                building_features.append("commercial_kitchen")
            if any(word in text.lower() for word in ["bar", "tavern", "pub"]):
                building_features.append("full_bar")
            if any(word in text.lower() for word in ["outdoor", "patio", "terrace"]):
                building_features.append("outdoor_dining")
            if any(word in text.lower() for word in ["drive-thru", "drive thru", "drive through"]):
                building_features.append("drive_thru")
            if any(word in text.lower() for word in ["wine cellar", "wine storage"]):
                building_features.append("wine_cellar")
            if any(word in text.lower() for word in ["premium", "upscale", "luxury", "high-end"]):
                building_features.append("premium_finishes")
        
        if building_features:
            result["building_features"] = building_features
        
        # Add unit mix data if available
        if extracted.get("unit_mix"):
            result["unit_mix"] = extracted["unit_mix"]
            
        return result
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        try:
            lines = response.strip().split('\n')
            parsed = {
                "analysis_method": "llm",
                "raw_response": response
            }
            
            for line in lines:
                line_lower = line.lower()
                if "project type:" in line_lower:
                    if "residential" in line_lower:
                        parsed["project_type"] = "residential"
                    elif "commercial" in line_lower:
                        parsed["project_type"] = "commercial"
                    elif "industrial" in line_lower:
                        parsed["project_type"] = "industrial"
                    elif "mixed" in line_lower:
                        parsed["project_type"] = "mixed_use"
                
                elif "quality" in line_lower or "level" in line_lower:
                    if "premium" in line_lower or "luxury" in line_lower:
                        parsed["quality_level"] = "premium"
                    elif "standard" in line_lower:
                        parsed["quality_level"] = "standard"
                    elif "economy" in line_lower or "budget" in line_lower:
                        parsed["quality_level"] = "economy"
            
            return parsed
            
        except Exception as e:
            return {
                "analysis_method": "llm",
                "error": str(e),
                "raw_response": response
            }
    
    def generate_specification_text(
        self,
        system_name: str,
        project_type: str,
        quality_level: str = "standard"
    ) -> str:
        specifications = {
            "hvac": {
                "premium": "High-efficiency VRF system with zone control and smart thermostats",
                "standard": "Standard split system with programmable thermostats",
                "economy": "Basic packaged unit with manual controls"
            },
            "electrical": {
                "premium": "Redundant power feeds, generator backup, smart lighting controls",
                "standard": "Code-compliant distribution with LED lighting",
                "economy": "Basic electrical service meeting minimum code requirements"
            },
            "plumbing": {
                "premium": "Low-flow fixtures, hot water recirculation, water filtration",
                "standard": "Standard commercial-grade fixtures",
                "economy": "Basic fixtures meeting code requirements"
            }
        }
        
        system_key = system_name.lower().replace(" ", "_")
        if system_key in specifications:
            return specifications[system_key].get(quality_level, specifications[system_key]["standard"])
        
        return f"Standard {system_name} installation per local codes"
    
    def parse_unit_mix(self, text: str) -> Dict[str, Any]:
        """
        Parse unit mix information from natural language descriptions.
        Examples:
        - "120 units: 60 1BR, 40 2BR, 20 3BR"
        - "100 apartments with 50 studios, 30 one-bedroom, 20 two-bedroom"
        - "50 unit complex"
        """
        unit_mix = {
            "total_units": 0,
            "unit_breakdown": {},
            "amenity_spaces": [],
            "parking_spaces": 0,
            "average_unit_size": None
        }
        
        # Extract total unit count
        unit_match = self.patterns["unit_count"].search(text)
        if unit_match:
            unit_mix["total_units"] = int(unit_match.group(1))
        
        # Extract specific unit types
        unit_types = {
            "studio": self.patterns["studio_units"],
            "1BR": self.patterns["one_bedroom"],
            "2BR": self.patterns["two_bedroom"],
            "3BR": self.patterns["three_bedroom"]
        }
        
        for unit_type, pattern in unit_types.items():
            match = pattern.search(text)
            if match:
                count = int(match.group(1))
                unit_mix["unit_breakdown"][unit_type] = count
        
        # Parse unit mix in format "X units: Y 1BR, Z 2BR"
        mix_pattern = re.compile(r'(\d+)\s*units?[:\s]+(.+)', re.IGNORECASE)
        mix_match = mix_pattern.search(text)
        if mix_match:
            total = int(mix_match.group(1))
            unit_mix["total_units"] = total
            breakdown_text = mix_match.group(2)
            
            # Parse breakdown like "60 1BR, 40 2BR, 20 3BR"
            breakdown_pattern = re.compile(r'(\d+)\s*(?:x\s*)?(\w+)', re.IGNORECASE)
            for match in breakdown_pattern.finditer(breakdown_text):
                count = int(match.group(1))
                unit_type = match.group(2).upper()
                # Normalize unit type
                if 'STUDIO' in unit_type or 'EFF' in unit_type:
                    unit_type = 'studio'
                elif '1' in unit_type or 'ONE' in unit_type:
                    unit_type = '1BR'
                elif '2' in unit_type or 'TWO' in unit_type:
                    unit_type = '2BR'
                elif '3' in unit_type or 'THREE' in unit_type:
                    unit_type = '3BR'
                elif '4' in unit_type or 'FOUR' in unit_type:
                    unit_type = '4BR'
                
                if unit_type in ['studio', '1BR', '2BR', '3BR', '4BR']:
                    unit_mix["unit_breakdown"][unit_type] = count
        
        # Extract parking information
        parking_pattern = re.compile(r'(\d+)\s*(?:parking|space|stall)s?', re.IGNORECASE)
        parking_match = parking_pattern.search(text)
        if parking_match:
            unit_mix["parking_spaces"] = int(parking_match.group(1))
        
        # Extract amenity spaces
        amenities = []
        amenity_keywords = {
            "clubhouse": ["clubhouse", "club house", "community center"],
            "fitness_center": ["gym", "fitness", "exercise", "workout"],
            "pool": ["pool", "swimming"],
            "business_center": ["business center", "office center", "co-working"],
            "leasing_office": ["leasing office", "management office", "rental office"],
            "laundry": ["laundry", "washer", "dryer"],
            "storage": ["storage", "locker"],
            "playground": ["playground", "play area"],
            "dog_park": ["dog park", "pet area", "bark park"],
            "lounge": ["lounge", "social room", "party room"],
            "rooftop_deck": ["rooftop", "roof deck", "sky deck"]
        }
        
        for amenity, keywords in amenity_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                amenities.append(amenity)
        
        unit_mix["amenity_spaces"] = amenities
        
        # Calculate average unit size if not provided
        if unit_mix["unit_breakdown"]:
            # Default unit sizes (can be overridden by user input)
            default_sizes = {
                "studio": 500,
                "1BR": 750,
                "2BR": 1000,
                "3BR": 1400,
                "4BR": 1800
            }
            
            total_sf = 0
            total_units = 0
            for unit_type, count in unit_mix["unit_breakdown"].items():
                if unit_type in default_sizes:
                    total_sf += default_sizes[unit_type] * count
                    total_units += count
            
            if total_units > 0:
                unit_mix["average_unit_size"] = total_sf // total_units
        
        # If we didn't get a unit breakdown but have total units, 
        # assume a typical mix
        if unit_mix["total_units"] > 0 and not unit_mix["unit_breakdown"]:
            total = unit_mix["total_units"]
            # Typical apartment mix: 20% studio, 40% 1BR, 30% 2BR, 10% 3BR
            unit_mix["unit_breakdown"] = {
                "studio": int(total * 0.2),
                "1BR": int(total * 0.4),
                "2BR": int(total * 0.3),
                "3BR": int(total * 0.1)
            }
            # Adjust for rounding
            calculated_total = sum(unit_mix["unit_breakdown"].values())
            if calculated_total < total:
                unit_mix["unit_breakdown"]["1BR"] += total - calculated_total
        
        return unit_mix
    
    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location from text.
        Looks for patterns like:
        - "in [City], [State]"
        - "in [City] [State]"
        - "in [State]"
        - "[City], [State] at the end"
        """
        # US states mapping
        states = {
            'alabama': 'Alabama', 'al': 'Alabama',
            'alaska': 'Alaska', 'ak': 'Alaska',
            'arizona': 'Arizona', 'az': 'Arizona',
            'arkansas': 'Arkansas', 'ar': 'Arkansas',
            'california': 'California', 'ca': 'California',
            'colorado': 'Colorado', 'co': 'Colorado',
            'connecticut': 'Connecticut', 'ct': 'Connecticut',
            'delaware': 'Delaware', 'de': 'Delaware',
            'florida': 'Florida', 'fl': 'Florida',
            'georgia': 'Georgia', 'ga': 'Georgia',
            'hawaii': 'Hawaii', 'hi': 'Hawaii',
            'idaho': 'Idaho', 'id': 'Idaho',
            'illinois': 'Illinois', 'il': 'Illinois',
            'indiana': 'Indiana', 'in': 'Indiana',
            'iowa': 'Iowa', 'ia': 'Iowa',
            'kansas': 'Kansas', 'ks': 'Kansas',
            'kentucky': 'Kentucky', 'ky': 'Kentucky',
            'louisiana': 'Louisiana', 'la': 'Louisiana',
            'maine': 'Maine', 'me': 'Maine',
            'maryland': 'Maryland', 'md': 'Maryland',
            'massachusetts': 'Massachusetts', 'ma': 'Massachusetts',
            'michigan': 'Michigan', 'mi': 'Michigan',
            'minnesota': 'Minnesota', 'mn': 'Minnesota',
            'mississippi': 'Mississippi', 'ms': 'Mississippi',
            'missouri': 'Missouri', 'mo': 'Missouri',
            'montana': 'Montana', 'mt': 'Montana',
            'nebraska': 'Nebraska', 'ne': 'Nebraska',
            'nevada': 'Nevada', 'nv': 'Nevada',
            'new hampshire': 'New Hampshire', 'nh': 'New Hampshire',
            'new jersey': 'New Jersey', 'nj': 'New Jersey',
            'new mexico': 'New Mexico', 'nm': 'New Mexico',
            'new york': 'New York', 'ny': 'New York',
            'north carolina': 'North Carolina', 'nc': 'North Carolina',
            'north dakota': 'North Dakota', 'nd': 'North Dakota',
            'ohio': 'Ohio', 'oh': 'Ohio',
            'oklahoma': 'Oklahoma', 'ok': 'Oklahoma',
            'oregon': 'Oregon', 'or': 'Oregon',
            'pennsylvania': 'Pennsylvania', 'pa': 'Pennsylvania',
            'rhode island': 'Rhode Island', 'ri': 'Rhode Island',
            'south carolina': 'South Carolina', 'sc': 'South Carolina',
            'south dakota': 'South Dakota', 'sd': 'South Dakota',
            'tennessee': 'Tennessee', 'tn': 'Tennessee',
            'texas': 'Texas', 'tx': 'Texas',
            'utah': 'Utah', 'ut': 'Utah',
            'vermont': 'Vermont', 'vt': 'Vermont',
            'virginia': 'Virginia', 'va': 'Virginia',
            'washington': 'Washington', 'wa': 'Washington',
            'west virginia': 'West Virginia', 'wv': 'West Virginia',
            'wisconsin': 'Wisconsin', 'wi': 'Wisconsin',
            'wyoming': 'Wyoming', 'wy': 'Wyoming'
        }
        
        # City to default state mappings for ambiguous cities
        city_state_defaults = {
            'portland': 'Oregon',  # Portland, OR is much larger than Portland, ME
            'springfield': None,   # Too many Springfields - no default
            'washington': 'Washington',  # Washington state vs DC - context dependent
            'columbus': 'Ohio',    # Columbus, OH is largest
            'birmingham': 'Alabama',
            'richmond': 'Virginia',
            'jackson': 'Mississippi',
            'albany': 'New York',
            'concord': 'New Hampshire',
            'bristol': 'Tennessee',
            'manchester': 'New Hampshire',  # Manchester, NH is the primary Manchester in examples
            'franklin': 'Tennessee',  # Franklin, TN is common in Nashville area
            'murfreesboro': 'Tennessee',
            'nashua': 'New Hampshire'
        }
        
        # Common cities
        major_cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
            'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
            'Fort Worth', 'Columbus', 'San Francisco', 'Charlotte', 'Indianapolis',
            'Seattle', 'Denver', 'Washington', 'Boston', 'Nashville', 'Baltimore',
            'Oklahoma City', 'Las Vegas', 'Portland', 'Detroit', 'Memphis', 'Louisville',
            'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno', 'Mesa', 'Sacramento',
            'Atlanta', 'Kansas City', 'Colorado Springs', 'Miami', 'Raleigh', 'Omaha',
            'Long Beach', 'Virginia Beach', 'Oakland', 'Minneapolis', 'Tulsa', 'Arlington',
            'Tampa', 'New Orleans', 'Wichita', 'Cleveland', 'Bakersfield', 'Aurora',
            'Anchorage', 'Honolulu', 'Anaheim', 'Santa Ana', 'Corpus Christi', 'Riverside',
            'Lexington', 'St. Louis', 'Stockton', 'Pittsburgh', 'Cincinnati', 'Saint Paul',
            'Greensboro', 'Lincoln', 'Orlando', 'Irvine', 'Newark', 'Durham', 'Chula Vista',
            'Fort Wayne', 'Jersey City', 'St. Petersburg', 'Laredo', 'Buffalo', 'Madison',
            # Add cities from our examples
            'Manchester', 'Franklin', 'Murfreesboro', 'Nashua', 'Concord'
        ]
        
        text_lower = text.lower()
        
        # Try to find "in [location]" pattern, including "downtown"
        in_pattern = re.compile(r'\bin\s+((?:downtown\s+)?[A-Za-z\s,]+?)(?:\.|$|\s+(?:with|including|featuring)|\Z)', re.IGNORECASE)
        match = in_pattern.search(text)
        if match:
            location_str = match.group(1).strip().rstrip(',')
            
            # Check if it's an exact state match first
            for state_key, state_name in states.items():
                if state_key == location_str.lower() or state_name.lower() == location_str.lower():
                    return state_name
            
            # Check for city, state format (explicit comma separation)
            parts = location_str.split(',')
            if len(parts) == 2:
                city_part = parts[0].strip()
                state_part = parts[1].strip()
                
                # Find the state
                matched_state = None
                for state_key, state_name in states.items():
                    if state_key == state_part.lower() or state_name.lower() == state_part.lower():
                        matched_state = state_name
                        break
                
                if matched_state:
                    return f"{city_part.title()}, {matched_state}"
            
            # Handle "downtown" prefix
            clean_location = location_str
            is_downtown = False
            if location_str.lower().startswith('downtown '):
                is_downtown = True
                clean_location = location_str[9:].strip()  # Remove "downtown " prefix
            
            # Check if it's a known major city (before doing substring state matching)
            for city in major_cities:
                if city.lower() == clean_location.lower():
                    # Check if this city has a default state
                    default_state = city_state_defaults.get(city.lower())
                    if default_state:
                        prefix = "Downtown " if is_downtown else ""
                        return f"{prefix}{city}, {default_state}"
                    else:
                        prefix = "Downtown " if is_downtown else ""
                        return f"{prefix}{city}"
            
            # Check for multi-word state names first (e.g., "New Hampshire", "New York")
            location_lower = location_str.lower()
            for state_key, state_name in states.items():
                state_lower = state_name.lower()
                if state_lower in location_lower:
                    # Found a state name, extract the city part
                    city_part = location_lower.replace(state_lower, '').strip()
                    if city_part:
                        # Capitalize properly
                        city = ' '.join(word.capitalize() for word in city_part.split())
                        return f"{city}, {state_name}"
                    else:
                        return state_name
            
            # If no multi-word state match, check individual words
            location_words = location_str.lower().split()
            for word in location_words:
                for state_key, state_name in states.items():
                    if state_key == word:
                        # Found a state abbreviation, try to extract city
                        remaining_words = [w for w in location_words if w != word]
                        if remaining_words:
                            city = ' '.join(remaining_words).title()
                            return f"{city}, {state_name}"
                        else:
                            return state_name
        
        # Try to find state at the end of text
        for state_key, state_name in states.items():
            if text_lower.endswith(' ' + state_key) or text_lower.endswith(' ' + state_name.lower()):
                # Check if there's a city before it
                city_state_pattern = re.compile(rf'([A-Za-z\s]+)[,\s]+{re.escape(state_name)}$', re.IGNORECASE)
                match = city_state_pattern.search(text)
                if match:
                    city = match.group(1).strip().rstrip(',').title()
                    if city and len(city) > 2:  # Avoid matching single letters
                        return f"{city}, {state_name}"
                return state_name
        
        # Check for major cities
        for city in major_cities:
            if city.lower() in text_lower:
                # Try to find associated state
                city_pattern = re.compile(rf'{re.escape(city)}[,\s]+([A-Za-z\s]+)', re.IGNORECASE)
                match = city_pattern.search(text)
                if match:
                    potential_state = match.group(1).strip()
                    for state_key, state_name in states.items():
                        if state_key == potential_state.lower() or state_name.lower() == potential_state.lower():
                            return f"{city}, {state_name}"
                
                # No state found, use default if available
                default_state = city_state_defaults.get(city.lower())
                if default_state:
                    return f"{city}, {default_state}"
                else:
                    return city
        
        return None
    
    def generate_project_name(self, description: str, parsed_data: dict) -> str:
        """
        Generate a smart, descriptive project name from the natural language description.
        Examples:
        - "Expand hospital with new 50000 sf wing" -> "Hospital Wing Addition - Manchester"
        - "New restaurant with outdoor patio" -> "New Restaurant - Nashville"
        - "Renovate office to open plan" -> "Office Renovation - Downtown"
        """
        
        description_lower = description.lower()
        
        # Extract key components
        project_type = parsed_data.get('project_classification', 'Project')
        location = parsed_data.get('location', '')
        occupancy = parsed_data.get('occupancy_type', '')
        square_footage = parsed_data.get('square_footage', 0)
        
        # Determine the primary subject (what's being built)
        building_types = {
            'restaurant': 'Restaurant',
            'hospital': 'Hospital',
            'medical': 'Medical Facility',
            'office': 'Office',
            'school': 'School',
            'warehouse': 'Warehouse',
            'retail': 'Retail Space',
            'dealership': 'Auto Dealership',
            'clinic': 'Clinic',
            'surgical': 'Surgical Center',
            'urgent care': 'Urgent Care',
            'bank': 'Bank Branch',
            'manufacturing': 'Manufacturing',
            'distribution': 'Distribution Center',
            'gym': 'Fitness Center',
            'fitness': 'Fitness Center',
            'hotel': 'Hotel',
            'apartment': 'Apartments',
            'condo': 'Condominiums',
            'fast-casual': 'Fast-Casual Restaurant',
            'fast food': 'Fast Food Restaurant',
            'fine dining': 'Fine Dining Restaurant',
            'quick service': 'QSR',
            'cafe': 'Cafe',
            'bistro': 'Bistro',
            'bar': 'Bar & Grill',
            'tavern': 'Tavern',
            'pub': 'Pub',
            'imaging': 'Imaging Center',
            'outpatient': 'Outpatient Clinic',
            'surgery': 'Surgery Center',
            'dental': 'Dental Office',
            'pharmacy': 'Pharmacy',
            'lab': 'Laboratory',
            'classroom': 'Classroom Building',
            'gymnasium': 'Gymnasium',
            'cafeteria': 'Cafeteria',
            'showroom': 'Showroom',
            'service center': 'Service Center',
            'fulfillment': 'Fulfillment Center'
        }
        
        # Find the building type - prioritize longer matches first
        building_name = None
        # Sort by length (descending) to match longer phrases first
        sorted_types = sorted(building_types.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, name in sorted_types:
            if keyword in description_lower:
                building_name = name
                break
        
        # Check for healthcare facilities
        if parsed_data.get('is_healthcare'):
            healthcare_details = parsed_data.get('healthcare_details', {})
            facility_type = healthcare_details.get('facility_type', '')
            if facility_type == 'hospital':
                building_name = 'Hospital'
            elif facility_type == 'surgical_center':
                building_name = 'Surgical Center'
            elif facility_type == 'imaging_center':
                building_name = 'Imaging Center'
            elif facility_type == 'urgent_care':
                building_name = 'Urgent Care'
            elif facility_type == 'outpatient_clinic':
                building_name = 'Outpatient Clinic'
            elif facility_type == 'medical_office':
                building_name = 'Medical Office'
            elif facility_type == 'dental_office':
                building_name = 'Dental Office'
        
        if not building_name:
            building_name = occupancy.title() if occupancy else 'Commercial Building'
        
        # Check for special features to add to name
        special_features = []
        if 'wing' in description_lower:
            special_features.append('Wing')
        if 'expansion' in description_lower and 'addition' not in description_lower:
            special_features.append('Expansion')
        if 'surgical' in description_lower and 'Hospital' in building_name:
            special_features.append('Surgical Wing')
        if 'imaging' in description_lower and 'Medical' in building_name:
            special_features.append('w/ Imaging')
        if 'kitchen' in description_lower and 'Restaurant' in building_name:
            special_features.append('Kitchen')
        if 'patio' in description_lower or 'outdoor' in description_lower:
            if 'Restaurant' in building_name or 'Cafe' in building_name:
                special_features.append('w/ Patio')
        if 'drive-thru' in description_lower or 'drive thru' in description_lower:
            special_features.append('w/ Drive-Thru')
        if 'operating room' in description_lower or 'operating rooms' in description_lower:
            or_match = re.search(r'(\d+)\s*operating\s*rooms?', description_lower)
            if or_match:
                num_ors = or_match.group(1)
                special_features.append(f'{num_ors} ORs')
        if 'exam room' in description_lower or 'exam rooms' in description_lower:
            exam_match = re.search(r'(\d+)\s*exam\s*rooms?', description_lower)
            if exam_match:
                num_exams = exam_match.group(1)
                special_features.append(f'{num_exams} Exam Rooms')
        if 'loading dock' in description_lower or 'loading docks' in description_lower:
            dock_match = re.search(r'(\d+)\s*loading\s*docks?', description_lower)
            if dock_match:
                num_docks = dock_match.group(1)
                special_features.append(f'{num_docks} Docks')
        
        # Build the name based on project classification
        prefix = ""
        if project_type == 'renovation':
            if 'convert' in description_lower or 'conversion' in description_lower:
                # Find what it's being converted to
                if 'to' in description_lower:
                    parts = description_lower.split('to')
                    if len(parts) > 1:
                        new_use = parts[1].strip().split()[0:3]  # Get first few words after "to"
                        for keyword, name in building_types.items():
                            if keyword in ' '.join(new_use):
                                building_name = f"{name} Conversion"
                                break
                else:
                    building_name = f"{building_name} Conversion"
                prefix = building_name
            else:
                prefix = f"{building_name} Renovation"
        elif project_type == 'addition':
            if special_features:
                prefix = f"{building_name} {' '.join(special_features[:2])}"  # Limit to 2 features
            else:
                prefix = f"{building_name} Addition"
        else:  # ground_up
            prefix = f"New {building_name}"
            if special_features:
                prefix += f" {' '.join(special_features[:2])}"  # Limit to 2 features
        
        # Add location if available
        if location:
            # Simplify location (remove state if it's long)
            location_parts = location.split(',')
            city = location_parts[0].strip()
            
            # Special handling for downtown/specific areas
            if 'downtown' in description_lower:
                city = f"Downtown {city}"
            
            name = f"{prefix} - {city}"
        else:
            name = prefix
        
        # Add size for large projects
        if square_footage >= 50000:
            size_k = int(square_footage / 1000)
            name = f"{name} ({size_k}K SF)"
        elif square_footage >= 10000:
            size_k = int(square_footage / 1000)
            name = f"{name} ({size_k}K SF)"
        
        # Ensure name isn't too long
        if len(name) > 60:
            # Truncate intelligently
            if ' - ' in name:
                parts = name.split(' - ')
                if '(' in parts[0]:  # Has size in first part
                    size_part = parts[0][parts[0].rfind('('):]
                    main_part = parts[0][:parts[0].rfind('(')].strip()
                    if len(main_part) > 35:
                        main_part = main_part[:35] + "..."
                    parts[0] = f"{main_part} {size_part}"
                else:
                    parts[0] = parts[0][:40] + "..."
                name = f"{parts[0]} - {parts[1]}"
            else:
                name = name[:57] + "..."
        
        return name
    
    def get_detail_suggestions(self, occupancy_type: str) -> list:
        """
        Suggest what details users should include for better estimates
        """
        suggestions = {
            'restaurant': [
                'Type of restaurant (fast-food, casual, fine dining)',
                'Kitchen size and equipment needs',
                'Seating capacity',
                'Special features (bar, patio, drive-through)'
            ],
            'healthcare': [
                'Type of facility (hospital, clinic, surgical center)',
                'Number of exam/operating rooms',
                'Special equipment (MRI, CT, X-ray)',
                'Lab or pharmacy needs'
            ],
            'office': [
                'Class of office (A, B, C)',
                'Open plan vs traditional layout',
                'Number of conference rooms',
                'Special requirements (data center, trading floor)'
            ],
            'retail': [
                'Type of retail (boutique, big box, grocery)',
                'Storage/warehouse needs',
                'Customer amenities',
                'Loading dock requirements'
            ],
            'educational': [
                'Grade levels served',
                'Special facilities (gym, cafeteria, labs)',
                'Technology requirements',
                'Outdoor facilities (playground, sports fields)'
            ],
            'warehouse': [
                'Clear height requirements',
                'Number of loading docks',
                'Climate control needs',
                'Racking or automation systems'
            ],
            'industrial': [
                'Type of manufacturing or processing',
                'Equipment and machinery needs',
                'Environmental controls',
                'Power and utility requirements'
            ],
            'residential': [
                'Number and mix of units',
                'Amenity spaces (gym, pool, clubhouse)',
                'Parking requirements',
                'Quality level (affordable, market-rate, luxury)'
            ]
        }
        
        return suggestions.get(occupancy_type, [
            'Specific use case',
            'Special equipment or features',
            'Quality level (economy, standard, premium)',
            'Any unique requirements'
        ])
    
    def _extract_building_mix(self, text: str) -> Optional[Dict[str, float]]:
        """
        Extract building mix percentages from text.
        Looks for patterns like:
        - "warehouse (70%) + office (30%)"
        - "60% office, 40% retail"
        - "warehouse 70% office 30%"
        - "150x300 warehouse (70%) + office(30%)"
        """
        # Skip building mix extraction for pure restaurant descriptions
        # Restaurant components (kitchen, dining, bar) are not separate building types
        restaurant_keywords = ['restaurant', 'dining', 'kitchen', 'bar', 'cafe', 'bistro']
        if any(keyword in text.lower() for keyword in restaurant_keywords):
            # Check if this is just a restaurant (not mixed with office, retail, etc.)
            mixed_indicators = ['office', 'retail', 'residential', 'warehouse', 'industrial']
            has_percentage = re.search(r'\d+\s*%', text)
            has_mixed_types = any(indicator in text.lower() for indicator in mixed_indicators)
            
            # If no percentages and no mixed-use indicators, it's just a restaurant
            if not has_percentage and not has_mixed_types:
                return None
        
        # Common building types to look for
        building_types = [
            'warehouse', 'office', 'retail', 'restaurant', 'residential',
            'industrial', 'manufacturing', 'storage', 'distribution'
        ]
        
        # Pattern 1: "type (XX%)" or "type XX%"
        pattern1 = re.compile(r'(\w+)\s*[\(\[]?\s*(\d+)\s*%\s*[\)\]]?', re.IGNORECASE)
        
        # Pattern 2: "XX% type"
        pattern2 = re.compile(r'(\d+)\s*%\s*(\w+)', re.IGNORECASE)
        
        # Find all matches
        building_mix = {}
        
        # Try pattern 1
        for match in pattern1.finditer(text):
            building_type = match.group(1).lower()
            percentage = int(match.group(2))
            
            # Normalize building type
            if building_type in building_types:
                building_mix[building_type] = percentage / 100.0
        
        # Try pattern 2 if no matches found
        if not building_mix:
            for match in pattern2.finditer(text):
                percentage = int(match.group(1))
                building_type = match.group(2).lower()
                
                # Normalize building type
                if building_type in building_types:
                    building_mix[building_type] = percentage / 100.0
        
        # Special case: "mixed use" or "mixed-use" without specific percentages
        if not building_mix and ('mixed use' in text.lower() or 'mixed-use' in text.lower()):
            # Look for building types mentioned
            mentioned_types = []
            for btype in building_types:
                if btype in text.lower():
                    mentioned_types.append(btype)
            
            # If we found exactly 2 types, assume 50/50
            if len(mentioned_types) == 2:
                building_mix[mentioned_types[0]] = 0.5
                building_mix[mentioned_types[1]] = 0.5
            # If we found more, distribute evenly
            elif len(mentioned_types) > 2:
                share = 1.0 / len(mentioned_types)
                for btype in mentioned_types:
                    building_mix[btype] = share
        
        # Validate percentages sum to approximately 100%
        if building_mix:
            total = sum(building_mix.values())
            if 0.95 <= total <= 1.05:  # Allow small rounding errors
                # Normalize to exactly 100%
                for key in building_mix:
                    building_mix[key] = building_mix[key] / total
                return building_mix
            elif total < 0.95:
                # If total is less than 95%, it might be incomplete
                print(f"[NLP] Warning: Building mix percentages sum to {total*100}%, which is less than 95%")
                return building_mix
            else:
                print(f"[NLP] Warning: Building mix percentages sum to {total*100}%, which exceeds 105%")
                # Normalize anyway
                for key in building_mix:
                    building_mix[key] = building_mix[key] / total
                return building_mix
        
        return None


nlp_service = NLPService()