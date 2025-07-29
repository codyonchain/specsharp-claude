from typing import Dict, List, Optional, Tuple
from app.models.scope import ClimateZone
import re


class ClimateService:
    def __init__(self):
        self.climate_data = self._initialize_climate_data()
        self.hvac_requirements = self._initialize_hvac_requirements()
        self.insulation_requirements = self._initialize_insulation_requirements()
        self.code_requirements = self._initialize_code_requirements()
    
    def _initialize_climate_data(self) -> Dict:
        return {
            "states": {
                "FL": {"zone": ClimateZone.HOT_HUMID, "region": "Southeast"},
                "TX": {"zone": ClimateZone.HOT_DRY, "region": "South"},
                "AZ": {"zone": ClimateZone.HOT_DRY, "region": "Southwest"},
                "CA": {"zone": ClimateZone.TEMPERATE, "region": "West"},
                "NY": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "MA": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "IL": {"zone": ClimateZone.COLD, "region": "Midwest"},
                "MN": {"zone": ClimateZone.VERY_COLD, "region": "North"},
                "WA": {"zone": ClimateZone.TEMPERATE, "region": "Northwest"},
                "CO": {"zone": ClimateZone.COLD, "region": "Mountain"},
                "GA": {"zone": ClimateZone.HOT_HUMID, "region": "Southeast"},
                "NC": {"zone": ClimateZone.TEMPERATE, "region": "Southeast"},
                "OH": {"zone": ClimateZone.COLD, "region": "Midwest"},
                "PA": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "MI": {"zone": ClimateZone.COLD, "region": "Midwest"},
                "OR": {"zone": ClimateZone.TEMPERATE, "region": "Northwest"},
                "NV": {"zone": ClimateZone.HOT_DRY, "region": "Southwest"},
                "UT": {"zone": ClimateZone.COLD, "region": "Mountain"},
                "ME": {"zone": ClimateZone.VERY_COLD, "region": "Northeast"},
                "AK": {"zone": ClimateZone.VERY_COLD, "region": "Arctic"},
                "NH": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "VT": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "CT": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "RI": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "NJ": {"zone": ClimateZone.COLD, "region": "Northeast"},
                "DE": {"zone": ClimateZone.TEMPERATE, "region": "Mid-Atlantic"},
                "MD": {"zone": ClimateZone.TEMPERATE, "region": "Mid-Atlantic"},
                "VA": {"zone": ClimateZone.TEMPERATE, "region": "Mid-Atlantic"},
                "WV": {"zone": ClimateZone.COLD, "region": "Mid-Atlantic"},
                "KY": {"zone": ClimateZone.TEMPERATE, "region": "South"},
                "TN": {"zone": ClimateZone.TEMPERATE, "region": "South"},
                "SC": {"zone": ClimateZone.HOT_HUMID, "region": "Southeast"},
                "AL": {"zone": ClimateZone.HOT_HUMID, "region": "Southeast"},
                "MS": {"zone": ClimateZone.HOT_HUMID, "region": "Southeast"},
                "LA": {"zone": ClimateZone.HOT_HUMID, "region": "South"},
                "AR": {"zone": ClimateZone.HOT_HUMID, "region": "South"},
                "OK": {"zone": ClimateZone.HOT_DRY, "region": "South Central"},
                "KS": {"zone": ClimateZone.COLD, "region": "Midwest"},
                "NE": {"zone": ClimateZone.COLD, "region": "Midwest"},
                "SD": {"zone": ClimateZone.VERY_COLD, "region": "North Central"},
                "ND": {"zone": ClimateZone.VERY_COLD, "region": "North Central"},
                "WY": {"zone": ClimateZone.COLD, "region": "Mountain"},
                "MT": {"zone": ClimateZone.COLD, "region": "Mountain"},
                "ID": {"zone": ClimateZone.COLD, "region": "Mountain"},
                "NM": {"zone": ClimateZone.HOT_DRY, "region": "Southwest"},
                "HI": {"zone": ClimateZone.HOT_HUMID, "region": "Pacific"},
                "IA": {"zone": ClimateZone.COLD, "region": "Midwest"},
                "MO": {"zone": ClimateZone.TEMPERATE, "region": "Midwest"},
                "IN": {"zone": ClimateZone.COLD, "region": "Midwest"},
                "WI": {"zone": ClimateZone.COLD, "region": "North Central"},
            },
            "cities": {
                "Miami": ClimateZone.HOT_HUMID,
                "Houston": ClimateZone.HOT_HUMID,
                "Phoenix": ClimateZone.HOT_DRY,
                "Las Vegas": ClimateZone.HOT_DRY,
                "Los Angeles": ClimateZone.TEMPERATE,
                "San Francisco": ClimateZone.TEMPERATE,
                "Seattle": ClimateZone.TEMPERATE,
                "Portland": ClimateZone.TEMPERATE,
                "Denver": ClimateZone.COLD,
                "Chicago": ClimateZone.COLD,
                "Boston": ClimateZone.COLD,
                "New York": ClimateZone.COLD,
                "Minneapolis": ClimateZone.VERY_COLD,
                "Anchorage": ClimateZone.VERY_COLD,
            }
        }
    
    def _initialize_hvac_requirements(self) -> Dict:
        return {
            ClimateZone.HOT_HUMID: {
                "cooling_load_factor": 1.25,
                "heating_load_factor": 0.7,
                "dehumidification": True,
                "recommended_seer": 16,
                "recommended_systems": ["VRF", "Chilled Water", "Split System with Dehumidification"],
                "ventilation_rate_multiplier": 1.2
            },
            ClimateZone.HOT_DRY: {
                "cooling_load_factor": 1.2,
                "heating_load_factor": 0.6,
                "dehumidification": False,
                "recommended_seer": 14,
                "recommended_systems": ["Evaporative Cooling", "VRF", "High-Efficiency Split"],
                "ventilation_rate_multiplier": 1.0
            },
            ClimateZone.TEMPERATE: {
                "cooling_load_factor": 1.0,
                "heating_load_factor": 1.0,
                "dehumidification": False,
                "recommended_seer": 14,
                "recommended_systems": ["Heat Pump", "VRF", "Split System"],
                "ventilation_rate_multiplier": 1.0
            },
            ClimateZone.COLD: {
                "cooling_load_factor": 0.8,
                "heating_load_factor": 1.3,
                "dehumidification": False,
                "recommended_seer": 13,
                "recommended_systems": ["Boiler with Chiller", "VRF with Heat Recovery", "Geothermal"],
                "ventilation_rate_multiplier": 0.9
            },
            ClimateZone.VERY_COLD: {
                "cooling_load_factor": 0.6,
                "heating_load_factor": 1.5,
                "dehumidification": False,
                "recommended_seer": 13,
                "recommended_systems": ["High-Efficiency Boiler", "Radiant Heat", "Geothermal"],
                "ventilation_rate_multiplier": 0.8
            }
        }
    
    def _initialize_insulation_requirements(self) -> Dict:
        return {
            ClimateZone.HOT_HUMID: {
                "wall_r_value": 13,
                "roof_r_value": 30,
                "floor_r_value": 13,
                "window_u_value": 0.4,
                "vapor_barrier": "exterior",
                "air_sealing_priority": "high"
            },
            ClimateZone.HOT_DRY: {
                "wall_r_value": 13,
                "roof_r_value": 30,
                "floor_r_value": 13,
                "window_u_value": 0.4,
                "vapor_barrier": "not_required",
                "air_sealing_priority": "medium"
            },
            ClimateZone.TEMPERATE: {
                "wall_r_value": 19,
                "roof_r_value": 38,
                "floor_r_value": 19,
                "window_u_value": 0.32,
                "vapor_barrier": "interior",
                "air_sealing_priority": "medium"
            },
            ClimateZone.COLD: {
                "wall_r_value": 21,
                "roof_r_value": 49,
                "floor_r_value": 30,
                "window_u_value": 0.27,
                "vapor_barrier": "interior",
                "air_sealing_priority": "high"
            },
            ClimateZone.VERY_COLD: {
                "wall_r_value": 25,
                "roof_r_value": 60,
                "floor_r_value": 38,
                "window_u_value": 0.22,
                "vapor_barrier": "interior",
                "air_sealing_priority": "critical"
            }
        }
    
    def _initialize_code_requirements(self) -> Dict:
        return {
            "energy_codes": {
                ClimateZone.HOT_HUMID: "IECC Zone 1-2",
                ClimateZone.HOT_DRY: "IECC Zone 2-3",
                ClimateZone.TEMPERATE: "IECC Zone 3-4",
                ClimateZone.COLD: "IECC Zone 5-6",
                ClimateZone.VERY_COLD: "IECC Zone 7-8"
            },
            "special_requirements": {
                ClimateZone.HOT_HUMID: ["Hurricane strapping", "Flood elevation", "Corrosion protection"],
                ClimateZone.HOT_DRY: ["Seismic bracing", "Low water landscaping"],
                ClimateZone.TEMPERATE: ["Seismic design (West Coast)", "Rain screen"],
                ClimateZone.COLD: ["Snow load design", "Freeze protection"],
                ClimateZone.VERY_COLD: ["Extreme snow load", "Permafrost considerations", "Freeze protection"]
            }
        }
    
    def determine_climate_zone(self, location: str) -> ClimateZone:
        for city, zone in self.climate_data["cities"].items():
            if city.lower() in location.lower():
                return zone
        
        # Check for state abbreviation
        state_match = re.search(r',\s*([A-Z]{2})', location)
        if state_match:
            state_code = state_match.group(1)
            state_data = self.climate_data["states"].get(state_code)
            if state_data:
                return state_data["zone"]
        
        # Check for full state names
        state_names = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
        
        location_lower = location.lower()
        for state_name, state_code in state_names.items():
            if state_name in location_lower:
                state_data = self.climate_data["states"].get(state_code)
                if state_data:
                    return state_data["zone"]
        
        return ClimateZone.TEMPERATE
    
    def get_hvac_recommendations(self, climate_zone: ClimateZone, square_footage: float) -> Dict:
        hvac_data = self.hvac_requirements[climate_zone]
        
        base_cooling_tons = square_footage / 500
        base_heating_btus = square_footage * 30
        
        cooling_tons = base_cooling_tons * hvac_data["cooling_load_factor"]
        heating_btus = base_heating_btus * hvac_data["heating_load_factor"]
        
        return {
            "climate_zone": climate_zone.value,
            "cooling_capacity_tons": round(cooling_tons, 1),
            "heating_capacity_btus": round(heating_btus, 0),
            "recommended_seer": hvac_data["recommended_seer"],
            "dehumidification_required": hvac_data["dehumidification"],
            "recommended_systems": hvac_data["recommended_systems"],
            "ventilation_cfm": round(square_footage * 0.15 * hvac_data["ventilation_rate_multiplier"], 0)
        }
    
    def get_insulation_requirements(self, climate_zone: ClimateZone) -> Dict:
        return {
            "climate_zone": climate_zone.value,
            **self.insulation_requirements[climate_zone]
        }
    
    def get_compliance_requirements(self, climate_zone: ClimateZone, location: str) -> Dict:
        energy_code = self.code_requirements["energy_codes"][climate_zone]
        special_reqs = self.code_requirements["special_requirements"][climate_zone]
        
        state_match = re.search(r',\s*([A-Z]{2})', location)
        state_specific = []
        
        if state_match:
            state_code = state_match.group(1)
            if state_code == "CA":
                state_specific.append("Title 24 Energy Standards")
                state_specific.append("CALGreen Building Standards")
            elif state_code == "FL":
                state_specific.append("Florida Building Code - Energy")
                state_specific.append("High-Velocity Hurricane Zone (HVHZ) requirements")
            elif state_code == "NY":
                state_specific.append("NYStretch Energy Code")
                state_specific.append("NYC Energy Conservation Code")
        
        return {
            "climate_zone": climate_zone.value,
            "energy_code": energy_code,
            "special_requirements": special_reqs,
            "state_specific_codes": state_specific,
            "recommended_certifications": self._get_recommended_certifications(climate_zone)
        }
    
    def _get_recommended_certifications(self, climate_zone: ClimateZone) -> List[str]:
        base_certs = ["ENERGY STAR", "LEED"]
        
        if climate_zone in [ClimateZone.HOT_HUMID, ClimateZone.HOT_DRY]:
            base_certs.append("Cool Roof Rating Council")
        
        if climate_zone == ClimateZone.HOT_HUMID:
            base_certs.append("FORTIFIED Commercial")
        
        if climate_zone in [ClimateZone.COLD, ClimateZone.VERY_COLD]:
            base_certs.append("Passive House")
        
        return base_certs
    
    def calculate_climate_cost_adjustments(
        self, 
        climate_zone: ClimateZone,
        base_mechanical_cost: float,
        base_envelope_cost: float
    ) -> Dict[str, float]:
        mechanical_multipliers = {
            ClimateZone.HOT_HUMID: 1.2,
            ClimateZone.HOT_DRY: 1.1,
            ClimateZone.TEMPERATE: 1.0,
            ClimateZone.COLD: 1.15,
            ClimateZone.VERY_COLD: 1.25
        }
        
        envelope_multipliers = {
            ClimateZone.HOT_HUMID: 1.1,
            ClimateZone.HOT_DRY: 1.0,
            ClimateZone.TEMPERATE: 1.05,
            ClimateZone.COLD: 1.2,
            ClimateZone.VERY_COLD: 1.3
        }
        
        mechanical_adjustment = base_mechanical_cost * (mechanical_multipliers[climate_zone] - 1)
        envelope_adjustment = base_envelope_cost * (envelope_multipliers[climate_zone] - 1)
        
        return {
            "mechanical_adjustment": round(mechanical_adjustment, 2),
            "envelope_adjustment": round(envelope_adjustment, 2),
            "total_climate_adjustment": round(mechanical_adjustment + envelope_adjustment, 2),
            "mechanical_multiplier": mechanical_multipliers[climate_zone],
            "envelope_multiplier": envelope_multipliers[climate_zone]
        }


climate_service = ClimateService()