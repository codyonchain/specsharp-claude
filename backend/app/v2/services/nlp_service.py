"""
Single NLP service that uses the master config
No more scattered detection logic
"""

from app.v2.config.master_config import (
    MASTER_CONFIG, 
    BuildingType, 
    ProjectClass,
    OwnershipType,
    get_building_config
)
import re
from typing import Tuple, Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class NLPService:
    """One NLP service for all detection"""
    
    def __init__(self):
        self.config = MASTER_CONFIG
        
    def parse_description(self, text: str) -> Dict[str, Any]:
        """
        Parse any description and return structured data
        
        Args:
            text: Natural language description
            
        Returns:
            Dictionary with detected building info and metrics
        """
        text_lower = text.lower()
        
        # Detect building type and subtype
        building_type, subtype = self._detect_building_type(text_lower)
        
        # Detect project class
        project_class = self._detect_project_class(text_lower, building_type, subtype)
        
        # Detect ownership type
        ownership_type = self._detect_ownership_type(text_lower)
        
        # Extract metrics
        square_footage = self._extract_square_footage(text_lower)
        floors = self._extract_floors(text_lower)
        location = self._extract_location(text)
        
        # Extract special features
        special_features = self._extract_special_features(text_lower, building_type, subtype)
        
        # Calculate confidence
        confidence = self._calculate_confidence(building_type, subtype, text_lower)
        
        result = {
            'building_type': building_type.value if building_type else None,
            'subtype': subtype,
            'project_class': project_class.value if project_class else None,
            'ownership_type': ownership_type.value if ownership_type else None,
            'square_footage': square_footage,
            'floors': floors,
            'location': location,
            'special_features': special_features,
            'confidence': confidence,
            'original_text': text
        }
        
        logger.debug(f"NLP parsed: {result}")
        return result
    
    def _detect_building_type(self, text: str) -> Tuple[Optional[BuildingType], Optional[str]]:
        """
        Detect building type using priority from config
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            Tuple of (BuildingType, subtype) or (None, None)
        """
        
        # Sort by priority (highest first)
        detections = []
        
        for building_type in BuildingType:
            if building_type not in self.config:
                continue
                
            for subtype, config in self.config[building_type].items():
                # Count keyword matches
                matches = 0
                matched_keywords = []
                for keyword in config.nlp.keywords:
                    if keyword.lower() in text:
                        matches += 1
                        matched_keywords.append(keyword)
                
                if matches > 0:
                    detections.append({
                        'priority': config.nlp.priority,
                        'matches': matches,
                        'building_type': building_type,
                        'subtype': subtype,
                        'keywords': matched_keywords
                    })
        
        if detections:
            # Sort by priority (lower number = higher priority), then by match count
            detections.sort(key=lambda x: (x['priority'], -x['matches']))
            best = detections[0]
            
            logger.debug(f"Building detection: {best['building_type'].value}/{best['subtype']} "
                        f"(matched: {best['keywords']})")
            
            return best['building_type'], best['subtype']
        
        # Default fallback
        logger.debug("No building type detected, using default office/class_b")
        return BuildingType.OFFICE, 'class_b'
    
    def _detect_project_class(self, text: str, 
                            building_type: Optional[BuildingType], 
                            subtype: Optional[str]) -> ProjectClass:
        """
        Detect project classification
        
        Args:
            text: Lowercase text to analyze
            building_type: Detected building type
            subtype: Detected subtype
            
        Returns:
            ProjectClass enum value
        """
        
        # Check for explicit mentions
        if any(phrase in text for phrase in ['new construction', 'ground up', 'new build', 'build new']):
            return ProjectClass.GROUND_UP
            
        if any(phrase in text for phrase in ['tenant improvement', ' ti ', 'tenant build', 'fit out', 'fitout']):
            # Check if this building type can be TI
            if building_type and subtype:
                config = get_building_config(building_type, subtype)
                if config and ProjectClass.TENANT_IMPROVEMENT not in config.nlp.incompatible_classes:
                    return ProjectClass.TENANT_IMPROVEMENT
            
        if any(phrase in text for phrase in ['renovation', 'renovate', 'remodel', 'rehab', 'retrofit']):
            # Check if compatible
            if building_type and subtype:
                config = get_building_config(building_type, subtype)
                if config and ProjectClass.RENOVATION not in config.nlp.incompatible_classes:
                    return ProjectClass.RENOVATION
                    
        if any(phrase in text for phrase in ['addition', 'expansion', 'add on', 'extend', 'enlargement']):
            # Check if compatible
            if building_type and subtype:
                config = get_building_config(building_type, subtype)
                if config and ProjectClass.ADDITION not in config.nlp.incompatible_classes:
                    return ProjectClass.ADDITION
        
        # Default for "new" projects
        if 'new' in text:
            return ProjectClass.GROUND_UP
            
        return ProjectClass.GROUND_UP  # Safe default
    
    def _detect_ownership_type(self, text: str) -> OwnershipType:
        """
        Detect ownership/financing type
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            OwnershipType enum value
        """
        
        if any(phrase in text for phrase in ['non profit', 'nonprofit', 'not for profit', '501c3']):
            return OwnershipType.NON_PROFIT
            
        if any(phrase in text for phrase in ['government', 'municipal', 'federal', 'state', 'public', 'city']):
            return OwnershipType.GOVERNMENT
            
        if any(phrase in text for phrase in ['ppp', 'public private', 'p3']):
            return OwnershipType.PPP
            
        # Default to for-profit
        return OwnershipType.FOR_PROFIT
    
    def _extract_square_footage(self, text: str) -> Optional[int]:
        """
        Extract square footage from text
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            Square footage as integer or None
        """
        
        # Look for patterns like "50,000 sf", "50000 square feet", "50k sqft"
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:square foot|square feet|sq ft|sq\. ft|sf|sqft)',
            r'(\d+)k\s*(?:square foot|square feet|sq ft|sq\. ft|sf|sqft)',
            r'(\d+)\s*(?:square foot|square feet|sq ft|sq\. ft|sf|sqft)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                # Handle 'k' notation
                if 'k' in match.group(0):
                    return int(value) * 1000
                # Remove commas and convert
                value = value.replace(',', '')
                return int(value)
        
        return None
    
    def _extract_floors(self, text: str) -> Optional[int]:
        """
        Extract number of floors from text
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            Number of floors as integer or None
        """
        
        # Look for patterns like "5 story", "5-story", "five floors"
        patterns = [
            r'(\d+)[\s-]?stor(?:y|ey|ies)',
            r'(\d+)[\s-]?floor',
            r'(\d+)[\s-]?level',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        
        # Check for word numbers
        word_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'single': 1
        }
        
        for word, value in word_numbers.items():
            if f'{word} stor' in text or f'{word} floor' in text:
                return value
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location/city from text
        
        Args:
            text: Original case text
            
        Returns:
            Location string or None
        """
        
        # Common cities in our config
        cities = [
            'Nashville', 'Manchester', 'Memphis', 'Knoxville',
            'New York', 'San Francisco', 'Chicago', 'Miami',
            'Boston', 'Dallas', 'Atlanta', 'Seattle', 'Portland',
            'Los Angeles', 'San Diego', 'Phoenix', 'Denver',
            'Austin', 'Houston', 'Philadelphia', 'Washington'
        ]
        
        for city in cities:
            if city.lower() in text.lower():
                return city
        
        # Look for "in [City]" pattern
        pattern = r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_special_features(self, text: str, 
                                 building_type: Optional[BuildingType],
                                 subtype: Optional[str]) -> List[str]:
        """
        Extract special features mentioned in text
        
        Args:
            text: Lowercase text to analyze
            building_type: Detected building type
            subtype: Detected subtype
            
        Returns:
            List of special feature names
        """
        
        features = []
        
        if not building_type or not subtype:
            return features
        
        config = get_building_config(building_type, subtype)
        if not config or not config.special_features:
            return features
        
        # Check for each special feature
        for feature_name in config.special_features.keys():
            # Convert feature name to searchable terms
            search_terms = feature_name.replace('_', ' ')
            if search_terms in text:
                features.append(feature_name)
        
        return features
    
    def _calculate_confidence(self, building_type: Optional[BuildingType],
                            subtype: Optional[str], 
                            text: str) -> float:
        """
        Calculate confidence score for detection
        
        Args:
            building_type: Detected building type
            subtype: Detected subtype
            text: Lowercase text
            
        Returns:
            Confidence score between 0 and 1
        """
        
        if not building_type or not subtype:
            return 0.0
        
        config = get_building_config(building_type, subtype)
        if not config:
            return 0.0
        
        # Count matching keywords
        matches = sum(1 for keyword in config.nlp.keywords if keyword.lower() in text)
        total_keywords = len(config.nlp.keywords)
        
        if total_keywords == 0:
            return 0.0
        
        # Calculate base confidence
        base_confidence = matches / min(total_keywords, 3)  # Cap at 3 for percentage
        
        # Boost confidence if multiple keywords match
        if matches >= 3:
            base_confidence = min(1.0, base_confidence * 1.2)
        elif matches == 2:
            base_confidence = min(1.0, base_confidence * 1.1)
        
        # Apply threshold
        if base_confidence >= config.nlp.confidence_threshold:
            return base_confidence
        
        return base_confidence * 0.8  # Reduce if below threshold
    
    def extract_all_metrics(self, text: str) -> Dict[str, Any]:
        """
        Extract all possible metrics from text
        
        Args:
            text: Natural language description
            
        Returns:
            Dictionary with all extracted metrics
        """
        
        result = self.parse_description(text)
        
        # Additional extractions
        text_lower = text.lower()
        
        # Extract budget if mentioned
        budget = self._extract_budget(text_lower)
        if budget:
            result['budget'] = budget
        
        # Extract timeline if mentioned
        timeline = self._extract_timeline(text_lower)
        if timeline:
            result['timeline'] = timeline
        
        # Extract any percentages (for things like "20% retail")
        percentages = self._extract_percentages(text_lower)
        if percentages:
            result['percentages'] = percentages
        
        return result
    
    def _extract_budget(self, text: str) -> Optional[float]:
        """Extract budget from text"""
        
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:million|mil|m)\b',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:thousand|k)\b',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b',
            r'budget of (\d{1,3}(?:,\d{3})*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1).replace(',', '')
                value_float = float(value)
                
                if 'million' in match.group(0) or 'mil' in match.group(0):
                    return value_float * 1000000
                elif 'thousand' in match.group(0) or 'k' in match.group(0):
                    return value_float * 1000
                else:
                    return value_float
        
        return None
    
    def _extract_timeline(self, text: str) -> Optional[str]:
        """Extract timeline from text"""
        
        patterns = [
            r'(\d+)\s*(?:month|months)',
            r'(\d+)\s*(?:year|years)',
            r'(q\d)\s*(\d{4})',  # Q1 2024
            r'(spring|summer|fall|winter)\s*(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_percentages(self, text: str) -> Dict[str, float]:
        """Extract percentages with context"""
        
        percentages = {}
        pattern = r'(\d+)%?\s+(\w+)'
        
        matches = re.findall(pattern, text)
        for match in matches:
            if match[0].isdigit():
                value = int(match[0])
                if 0 < value <= 100:
                    context = match[1]
                    percentages[context] = value / 100.0
        
        return percentages

# Create singleton instance
nlp_service = NLPService()