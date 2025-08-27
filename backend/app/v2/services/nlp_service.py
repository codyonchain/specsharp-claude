"""
Compatibility shim - redirects to phrase parser
This file exists only for backward compatibility.
All new code should import phrase_parser directly.

DEPRECATED: Use phrase_parser instead of nlp_service
"""
from app.v2.services.phrase_parser import phrase_parser
import logging

logger = logging.getLogger(__name__)

class NLPService:
    """
    Compatibility wrapper for old NLP service interface.
    Now uses phrase parser internally.
    """
    
    def __init__(self):
        logger.warning("NLPService is deprecated. Use phrase_parser directly.")
    
    def parse_description(self, text: str):
        """Redirect to phrase parser"""
        return phrase_parser.parse(text)
    
    def extract_all_metrics(self, text: str):
        """Redirect to phrase parser"""
        return phrase_parser.parse(text)
    
    def extract_project_details(self, text: str):
        """Redirect to phrase parser"""
        return phrase_parser.parse(text)
    
    def _detect_building_type(self, text: str):
        """Compatibility method"""
        result = phrase_parser.parse(text)
        return result.get('building_type'), result.get('subtype')
    
    def _detect_project_class(self, text: str, building_type=None, subtype=None):
        """Compatibility method"""
        result = phrase_parser.parse(text)
        return result.get('project_class', 'ground_up')
    
    def _extract_square_footage(self, text: str):
        """Compatibility method"""
        result = phrase_parser.parse(text)
        return result.get('square_footage')
    
    def _extract_location(self, text: str):
        """Compatibility method"""
        result = phrase_parser.parse(text)
        return result.get('location', 'Nashville')

# Singleton for compatibility with old code
nlp_service = NLPService()

# Log deprecation warning when module is imported
logger.warning(
    "nlp_service module is deprecated and will be removed in a future version. "
    "Please update your code to use 'from app.v2.services.phrase_parser import phrase_parser' instead."
)