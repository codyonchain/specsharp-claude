from typing import Dict, List, Optional, Any
import os
import re
from enum import Enum
from app.core.config import settings

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
            "floors": re.compile(r'(\d+)\s*(?:floor|story|storey|level)s?', re.IGNORECASE),
            "budget": re.compile(r'\$\s*(\d+(?:,\d+)*(?:\.\d{2})?)', re.IGNORECASE),
            "ceiling_height": re.compile(r'(\d+(?:\.\d+)?)\s*(?:ft\.?|feet|foot)\s*(?:ceiling|height)', re.IGNORECASE),
            "room_count": re.compile(r'(\d+)\s*(?:room|office|space)s?', re.IGNORECASE),
        }
    
    def _initialize_keywords(self) -> Dict[str, List[str]]:
        return {
            "sustainable": ["leed", "green", "sustainable", "eco-friendly", "energy efficient", "solar"],
            "luxury": ["high-end", "luxury", "premium", "executive", "upscale"],
            "modern": ["modern", "contemporary", "open concept", "minimalist"],
            "traditional": ["traditional", "classic", "conventional"],
            "special_systems": ["data center", "clean room", "laboratory", "kitchen", "auditorium"],
        }
    
    def extract_project_details(self, text: str) -> Dict[str, Any]:
        extracted = {}
        
        for field, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                value = match.group(1).replace(',', '')
                if field in ["square_footage", "floors", "room_count"]:
                    extracted[field] = int(value)
                elif field == "budget":
                    extracted[field] = float(value)
                elif field == "ceiling_height":
                    extracted[field] = float(value)
        
        for category, keywords in self.keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                if category == "special_systems":
                    extracted["special_requirements"] = extracted.get("special_requirements", [])
                    for keyword in keywords:
                        if keyword in text.lower():
                            extracted["special_requirements"].append(keyword)
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
        2. Size and scope details
        3. Special requirements or features
        4. Quality level expectations
        5. Any sustainability or compliance requirements
        
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
        
        project_type = "commercial"
        if any(word in text.lower() for word in ["home", "house", "residential", "apartment"]):
            project_type = "residential"
        elif any(word in text.lower() for word in ["factory", "warehouse", "industrial"]):
            project_type = "industrial"
        elif any(word in text.lower() for word in ["mixed", "multi-use"]):
            project_type = "mixed_use"
        
        quality_level = "standard"
        if any(word in text.lower() for word in ["luxury", "premium", "high-end"]):
            quality_level = "premium"
        elif any(word in text.lower() for word in ["budget", "economical", "basic"]):
            quality_level = "economy"
        
        return {
            "project_type": project_type,
            "quality_level": quality_level,
            "extracted_details": extracted,
            "analysis_method": "pattern_matching"
        }
    
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


nlp_service = NLPService()