"""
Enhanced Cost Calculation Engine with DNA Tracking
Provides complete transparency on how costs are calculated
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
from app.core.cost_engine import (
    REGIONAL_MULTIPLIERS,
    BUILDING_TYPE_SPECIFICATIONS
)
from app.services.nlp_service import NLPService
from app.services.healthcare_cost_service import healthcare_cost_service


class CostCalculationEngine:
    """Enhanced cost engine that tracks WHY costs are what they are"""
    
    def __init__(self):
        self.nlp_service = NLPService()
        
    def calculate_with_dna(
        self,
        square_footage: int,
        occupancy_type: str,
        location: str,
        project_classification: str,
        description: str = "",
        finish_level: str = "standard",
        building_mix: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate costs and return the complete "DNA" of how we arrived at the number
        """
        
        # Check if this is a healthcare facility - use comprehensive v2 calculation
        if occupancy_type == "healthcare":
            # Use the comprehensive healthcare calculation
            healthcare_result = healthcare_cost_service.calculate_healthcare_costs_v2(
                description=description,
                square_feet=square_footage,
                location=location
            )
            
            # Extract costs from the nested structure
            project_totals = healthcare_result.get("project_total", {})
            total_cost = project_totals.get("all_in_total", 0)
            cost_per_sf = project_totals.get("all_in_cost_per_sf", 0)
            
            # Get base cost from classification
            classification = healthcare_result.get("classification", {})
            base_cost_per_sf = classification.get("base_cost_per_sf", 350)
            facility_type = healthcare_result.get("facility_type", "medical_office")
            
            # Extract and format the healthcare result into DNA format
            cost_dna = {
                "detected_factors": [],
                "applied_multipliers": [],
                "base_components": [],
                "market_adjustments": [],
                "special_conditions": [],
                "confidence_factors": []
            }
            
            # Add base cost component
            cost_dna["base_components"].append({
                "factor": "Healthcare Base Cost",
                "value": f"${base_cost_per_sf}/SF",
                "reason": f"{facility_type.replace('_', ' ').title()} facility with specialized medical systems",
                "impact": "baseline",
                "source": "RSMeans 2024 Healthcare Data"
            })
            
            # Add detected features as factors
            features = healthcare_result.get("features_detected", [])
            for feature in features:
                cost_dna["detected_factors"].append({
                    "factor": feature["name"],
                    "category": "Medical Systems",
                    "impact": f"+${feature['cost_impact']}/SF",
                    "description": feature.get("description", "Specialized medical requirement")
                })
            
            # Add regional multiplier
            regional_mult = healthcare_result.get("regional_multiplier", 1.0)
            if regional_mult != 1.0:
                cost_dna["applied_multipliers"].append({
                    "factor": "Regional Healthcare Index",
                    "value": f"{regional_mult:.2f}x",
                    "reason": f"Healthcare costs in {location}",
                    "impact": f"{((regional_mult - 1) * 100):+.1f}%",
                    "source": "RSMeans City Cost Index Q3 2024"
                })
            
            # Add complexity multiplier from classification
            complexity_mult = classification.get("complexity_multiplier", 1.0)
            if complexity_mult != 1.0:
                cost_dna["applied_multipliers"].append({
                    "factor": "Healthcare Facility Complexity",
                    "value": f"{complexity_mult:.2f}x", 
                    "reason": classification.get("description", "Healthcare facility complexity"),
                    "impact": f"{((complexity_mult - 1) * 100):+.1f}%",
                    "source": "Healthcare construction standards"
                })
            
            # Add project classification multiplier if applicable
            if project_classification != "ground_up":
                if project_classification == "addition":
                    class_mult = 1.25 if "hospital" in facility_type else 1.12
                else:  # renovation
                    class_mult = 0.92
                cost_dna["applied_multipliers"].append({
                    "factor": f"Healthcare {project_classification.title()} Complexity",
                    "value": f"{class_mult:.2f}x",
                    "reason": f"Healthcare {project_classification} requires special protocols",
                    "impact": f"{((class_mult - 1) * 100):+.1f}%",
                    "source": "Healthcare construction standards"
                })
            
            # Add confidence scoring
            confidence_score = 85  # High confidence for healthcare with detailed analysis
            confidence_factors = [
                {"factor": "Facility Type Identified", "impact": "+15%"},
                {"factor": "Healthcare-Specific Costing", "impact": "+20%"},
                {"factor": "Feature Detection", "impact": "+10%"}
            ]
            cost_dna["confidence_factors"] = confidence_factors
            
            # Get comparable projects for healthcare
            comparables = self.find_comparable_projects(
                "healthcare", location, square_footage, project_classification
            )
            
            # Extract trade costs
            construction = healthcare_result.get("construction", {})
            trade_costs = construction.get("trades", {})
            
            return {
                "total_cost": total_cost,
                "cost_per_sf": cost_per_sf,
                "square_footage": square_footage,
                "cost_dna": cost_dna,
                "confidence_score": confidence_score,
                "comparable_projects": comparables,
                "calculation_date": datetime.now().isoformat(),
                "market_data_version": "RSMeans 2024 Q3 Healthcare",
                "facility_type": facility_type,
                "is_healthcare": True,
                "trade_costs": trade_costs,
                "healthcare_details": healthcare_result  # Include full details for debugging
            }
        
        # Initialize DNA tracking for non-healthcare
        cost_dna = {
            "detected_factors": [],
            "applied_multipliers": [],
            "base_components": [],
            "market_adjustments": [],
            "special_conditions": [],
            "confidence_factors": []
        }
        
        # Base cost selection with reasoning
        base_cost, base_reason = self.get_base_cost_with_reason(occupancy_type, description)
        cost_dna["base_components"].append({
            "factor": "Base Cost",
            "value": f"${base_cost}/SF",
            "reason": base_reason,
            "impact": "baseline",
            "source": "RSMeans 2024 Q3"
        })
        
        # Detect special factors from description
        detected = self.detect_special_factors(description, occupancy_type)
        cost_dna["detected_factors"] = detected
        
        # Calculate special factor multiplier
        special_factor_mult = 1.0
        for factor in detected:
            # Parse impact to get multiplier
            impact = factor.get("impact", "+0%")
            if "+" in impact:
                percent = float(impact.replace("+", "").replace("%", "").split("-")[0])
                special_factor_mult *= (1 + percent / 100)
        
        # Location analysis
        location_mult, location_reason = self.get_location_multiplier_with_reason(location)
        cost_dna["applied_multipliers"].append({
            "factor": "Regional Cost Index",
            "value": f"{location_mult:.2f}x",
            "reason": location_reason,
            "impact": f"{((location_mult - 1) * 100):+.1f}%",
            "source": "RSMeans City Cost Index Q3 2024"
        })
        
        # Project classification with special handling
        class_mult, class_reason = self.get_classification_multiplier_with_reason(
            project_classification, 
            occupancy_type,
            detected
        )
        cost_dna["applied_multipliers"].append({
            "factor": f"{project_classification.title()} Complexity",
            "value": f"{class_mult:.2f}x",
            "reason": class_reason,
            "impact": f"{((class_mult - 1) * 100):+.1f}%",
            "source": "Historical project data"
        })
        
        # Special conditions (winter, seismic, etc.)
        special_conditions = self.detect_special_conditions(location, description, occupancy_type)
        for condition in special_conditions:
            cost_dna["special_conditions"].append(condition)
        
        # Market conditions
        market_adjustment = self.get_current_market_conditions()
        cost_dna["market_adjustments"].append(market_adjustment)
        
        # Calculate final cost
        total_multiplier = location_mult * class_mult * special_factor_mult
        for condition in special_conditions:
            total_multiplier *= condition.get("multiplier", 1.0)
        
        # Apply market adjustment
        market_mult = 1 + (market_adjustment.get("adjustment_percent", 0) / 100)
        total_multiplier *= market_mult
        
        cost_per_sf = base_cost * total_multiplier
        
        # Handle mixed-use projects
        if building_mix and len(building_mix) > 1:
            weighted_cost = 0
            for btype, percentage in building_mix.items():
                type_base, _ = self.get_base_cost_with_reason(btype, description)
                type_cost = type_base * total_multiplier
                weighted_cost += type_cost * percentage
            cost_per_sf = weighted_cost
            
            cost_dna["base_components"].append({
                "factor": "Mixed-Use Weighting",
                "value": f"${cost_per_sf:.2f}/SF",
                "reason": f"Weighted average of: {', '.join([f'{k} ({v*100:.0f}%)' for k, v in building_mix.items()])}",
                "impact": "weighted",
                "source": "Component analysis"
            })
        
        total_cost = cost_per_sf * square_footage
        
        # Add confidence scoring
        confidence_score, confidence_factors = self.calculate_confidence_score(
            occupancy_type, location, square_footage, len(detected)
        )
        cost_dna["confidence_factors"] = confidence_factors
        
        # Find comparable projects
        comparables = self.find_comparable_projects(
            occupancy_type, location, square_footage, project_classification
        )
        
        return {
            "total_cost": total_cost,
            "cost_per_sf": cost_per_sf,
            "square_footage": square_footage,
            "cost_dna": cost_dna,
            "confidence_score": confidence_score,
            "comparable_projects": comparables,
            "calculation_date": datetime.now().isoformat(),
            "market_data_version": "RSMeans 2024 Q3"
        }
    
    def get_base_cost_with_reason(self, occupancy_type: str, description: str) -> Tuple[float, str]:
        """Get base cost with explanation"""
        
        # Check for healthcare facilities first
        if occupancy_type == "healthcare":
            healthcare_data = healthcare_cost_service.get_healthcare_cost(description)
            base_cost = healthcare_data.get("base_cost_per_sf", 350)
            facility_type = healthcare_data.get("facility_type", "medical_office")
            
            reasons = {
                "hospital": "Full-service hospital with complex MEP systems, redundancy, medical gas",
                "surgical_center": "Surgical center with OR requirements, precise HVAC, medical gas",
                "imaging_center": "Imaging center with shielding, high power requirements",
                "outpatient_clinic": "Outpatient clinic with exam rooms, enhanced ventilation",
                "urgent_care": "Urgent care with walk-in capabilities, basic imaging",
                "medical_office": "Medical office with standard medical fit-out",
                "dental_office": "Dental office with specialized plumbing and equipment"
            }
            return base_cost, reasons.get(facility_type, "Healthcare facility with medical-grade systems")
        
        # Restaurant detection
        if occupancy_type == "restaurant" or "restaurant" in description.lower():
            # Determine restaurant type
            desc_lower = description.lower()
            if any(term in desc_lower for term in ["fast food", "quick service", "qsr"]):
                return 300, "Quick-service restaurant with basic kitchen, limited seating"
            elif any(term in desc_lower for term in ["casual dining", "family restaurant"]):
                return 375, "Casual dining with full kitchen, dining room, bar area"
            elif any(term in desc_lower for term in ["fine dining", "upscale", "premium"]):
                return 550, "Fine dining with premium finishes, extensive kitchen, wine storage"
            else:
                return 425, "Full-service restaurant with commercial kitchen, dining, and bar"
        
        # Standard occupancy types
        base_costs = {
            "office": (250, "Standard office with open plan layout, conference rooms, standard MEP"),
            "retail": (200, "Retail space with storefront, basic MEP, customer areas"),
            "warehouse": (150, "Warehouse with clear height, loading docks, basic systems"),
            "industrial": (175, "Light industrial with reinforced floors, utility connections"),
            "educational": (300, "Educational facility with classrooms, common areas, technology"),
            "residential": (225, "Multi-family residential with standard unit finishes"),
            "hospitality": (350, "Hotel/hospitality with guest rooms, common areas, amenities")
        }
        
        if occupancy_type in base_costs:
            return base_costs[occupancy_type]
        
        # Default
        return 250, "Commercial building with standard systems and finishes"
    
    def detect_special_factors(self, description: str, occupancy_type: str) -> List[Dict]:
        """Detect special factors that affect cost"""
        detected = []
        desc_lower = description.lower()
        
        # Healthcare specific
        if occupancy_type == "healthcare":
            if any(term in desc_lower for term in ["oshpd", "seismic", "california"]):
                detected.append({
                    "factor": "OSHPD Compliance",
                    "category": "Regulatory",
                    "impact": "+15-20%",
                    "description": "California seismic requirements for healthcare facilities"
                })
            
            if any(term in desc_lower for term in ["operating", "surgery", " or ", "operating room"]):
                detected.append({
                    "factor": "Surgical Suite Requirements",
                    "category": "Specialized Systems",
                    "impact": "+25-30%",
                    "description": "Laminar flow HVAC, medical gas, redundant power"
                })
            
            if any(term in desc_lower for term in ["mri", "ct scan", "imaging", "radiology", "x-ray"]):
                detected.append({
                    "factor": "Imaging Equipment Infrastructure",
                    "category": "Specialized Systems",
                    "impact": "+10-15%",
                    "description": "RF shielding, structural reinforcement, special power"
                })
            
            if any(term in desc_lower for term in ["emergency", "trauma", "er ", "emergency department"]):
                detected.append({
                    "factor": "Emergency Department",
                    "category": "Specialized Systems",
                    "impact": "+20-25%",
                    "description": "Trauma bays, decontamination, redundant systems"
                })
            
            if "infection control" in desc_lower or ("addition" in desc_lower and occupancy_type == "healthcare"):
                detected.append({
                    "factor": "Infection Control Measures",
                    "category": "Construction Complexity",
                    "impact": "+8-12%",
                    "description": "Negative air, barriers, phased construction"
                })
            
            if any(term in desc_lower for term in ["pharmacy", "compounding"]):
                detected.append({
                    "factor": "Pharmacy/Compounding",
                    "category": "Specialized Systems",
                    "impact": "+5-8%",
                    "description": "Clean room, special ventilation, security"
                })
        
        # Restaurant specific
        if occupancy_type == "restaurant" or "restaurant" in desc_lower:
            if any(term in desc_lower for term in ["commercial kitchen", "full kitchen", "kitchen equipment"]):
                detected.append({
                    "factor": "Commercial Kitchen",
                    "category": "Specialized Systems",
                    "impact": "+20-25%",
                    "description": "Hood systems, grease traps, gas lines, floor drains"
                })
            
            if any(term in desc_lower for term in ["drive-through", "drive through", "drive-thru", "drive thru"]):
                detected.append({
                    "factor": "Drive-Through Lane",
                    "category": "Site Work",
                    "impact": "+5-8%",
                    "description": "Additional site work, ordering systems, canopy"
                })
            
            if any(term in desc_lower for term in ["outdoor dining", "patio", "terrace", "outdoor seating"]):
                detected.append({
                    "factor": "Outdoor Dining Area",
                    "category": "Site Work",
                    "impact": "+3-5%",
                    "description": "Patio construction, outdoor furniture, lighting"
                })
            
            if any(term in desc_lower for term in ["bar", "tavern", "pub", "cocktail"]):
                detected.append({
                    "factor": "Full Bar Service",
                    "category": "Specialized Systems",
                    "impact": "+5-7%",
                    "description": "Bar equipment, draft systems, additional plumbing"
                })
            
            if any(term in desc_lower for term in ["wine cellar", "wine storage", "wine room"]):
                detected.append({
                    "factor": "Wine Storage",
                    "category": "Specialized Systems",
                    "impact": "+3-5%",
                    "description": "Climate-controlled storage, racking systems"
                })
        
        # General factors
        if any(term in desc_lower for term in ["leed", "sustainable", "green building", "energy star"]):
            leed_level = "Silver"  # Default
            if "platinum" in desc_lower:
                leed_level = "Platinum"
                impact = "+8-12%"
            elif "gold" in desc_lower:
                leed_level = "Gold"
                impact = "+6-10%"
            else:
                impact = "+5-8%"
            
            detected.append({
                "factor": f"LEED {leed_level} Certification",
                "category": "Certification",
                "impact": impact,
                "description": "Sustainable materials, energy systems, certification costs"
            })
        
        if any(term in desc_lower for term in ["fast track", "accelerated", "urgent", "expedited"]):
            detected.append({
                "factor": "Accelerated Schedule",
                "category": "Schedule",
                "impact": "+10-15%",
                "description": "Overtime, multiple shifts, expedited materials"
            })
        
        if any(term in desc_lower for term in ["high-end", "luxury", "premium finish"]):
            detected.append({
                "factor": "Premium Finishes",
                "category": "Quality Level",
                "impact": "+15-20%",
                "description": "High-end materials, custom millwork, premium fixtures"
            })
        
        if any(term in desc_lower for term in ["historic", "historical", "preservation"]):
            detected.append({
                "factor": "Historic Preservation",
                "category": "Regulatory",
                "impact": "+10-15%",
                "description": "Preservation requirements, specialized contractors"
            })
        
        if any(term in desc_lower for term in ["clean room", "cleanroom", "controlled environment"]):
            detected.append({
                "factor": "Clean Room Requirements",
                "category": "Specialized Systems",
                "impact": "+20-30%",
                "description": "HEPA filtration, pressure control, special finishes"
            })
        
        if any(term in desc_lower for term in ["data center", "server room", "it infrastructure"]):
            detected.append({
                "factor": "Data Center Infrastructure",
                "category": "Specialized Systems",
                "impact": "+15-20%",
                "description": "Redundant power, cooling, raised floors, security"
            })
        
        # Warehouse/Industrial specific
        if occupancy_type in ["warehouse", "industrial"]:
            if "refrigerated" in desc_lower or "cold storage" in desc_lower:
                detected.append({
                    "factor": "Refrigerated Storage",
                    "category": "Specialized Systems",
                    "impact": "+25-35%",
                    "description": "Insulated panels, refrigeration systems, specialized doors"
                })
            
            if any(term in desc_lower for term in ["automated", "automation", "conveyor", "robotics"]):
                detected.append({
                    "factor": "Automation Systems",
                    "category": "Specialized Equipment",
                    "impact": "+10-15%",
                    "description": "Conveyor systems, robotics infrastructure, controls"
                })
            
            # Check for clear height
            import re
            height_match = re.search(r'(\d+)[\s-]*(foot|feet|ft|\')', desc_lower)
            if height_match:
                height = int(height_match.group(1))
                if height >= 30:
                    detected.append({
                        "factor": f"{height}' Clear Height",
                        "category": "Structural",
                        "impact": "+5-10%",
                        "description": "Taller structure, enhanced structural system"
                    })
        
        return detected
    
    def get_location_multiplier_with_reason(self, location: str) -> Tuple[float, str]:
        """Get location multiplier with explanation"""
        
        # Comprehensive location data based on RSMeans
        location_data = {
            # Tennessee
            "Nashville, TN": (1.02, "2% above national average - growing market, moderate labor costs"),
            "Nashville, Tennessee": (1.02, "2% above national average - growing market, moderate labor costs"),
            "Franklin, TN": (1.03, "3% above national average - affluent market, quality expectations"),
            "Franklin, Tennessee": (1.03, "3% above national average - affluent market, quality expectations"),
            "Murfreesboro, TN": (1.01, "1% above national average - competitive market"),
            "Memphis, TN": (0.98, "2% below national average - lower labor costs"),
            "Memphis, Tennessee": (0.98, "2% below national average - lower labor costs"),
            
            # New Hampshire
            "Manchester, NH": (0.99, "1% below national average - competitive labor market"),
            "Manchester, New Hampshire": (0.99, "1% below national average - competitive labor market"),
            "Downtown Manchester, New Hampshire": (1.00, "At national average - downtown premium offsets regional discount"),
            "Nashua, NH": (0.98, "2% below national average - proximity to Massachusetts"),
            "Nashua, New Hampshire": (0.98, "2% below national average - proximity to Massachusetts"),
            "Concord, NH": (0.97, "3% below national average - smaller market"),
            "Concord, New Hampshire": (0.97, "3% below national average - smaller market"),
            
            # Massachusetts
            "Boston, MA": (1.18, "18% above national average - high labor costs, union requirements"),
            "Boston, Massachusetts": (1.18, "18% above national average - high labor costs, union requirements"),
            "Cambridge, MA": (1.20, "20% above national average - premium market, strict regulations"),
            "Worcester, MA": (1.10, "10% above national average - secondary market in high-cost state"),
            
            # California
            "San Francisco, CA": (1.35, "35% above national average - highest labor costs, strict regulations"),
            "San Francisco, California": (1.35, "35% above national average - highest labor costs, strict regulations"),
            "Los Angeles, CA": (1.28, "28% above national average - high costs, seismic requirements"),
            "San Diego, CA": (1.25, "25% above national average - high costs, limited labor"),
            "Sacramento, CA": (1.20, "20% above national average - capital city premium"),
            "Sacramento, California": (1.20, "20% above national average - capital city premium"),
            
            # Texas
            "Dallas, TX": (0.95, "5% below national average - competitive market, lower regulations"),
            "Dallas, Texas": (0.95, "5% below national average - competitive market, lower regulations"),
            "Houston, TX": (0.96, "4% below national average - large market, competitive pricing"),
            "Austin, TX": (1.02, "2% above national average - tech hub, growing rapidly"),
            "San Antonio, TX": (0.93, "7% below national average - lower costs across the board"),
            
            # Other major markets
            "New York, NY": (1.40, "40% above national average - highest costs, union labor, regulations"),
            "Chicago, IL": (1.08, "8% above national average - union market, winter conditions"),
            "Atlanta, GA": (0.94, "6% below national average - competitive Southeast market"),
            "Denver, CO": (1.05, "5% above national average - growing market, altitude considerations"),
            "Seattle, WA": (1.15, "15% above national average - high demand, limited labor"),
            "Phoenix, AZ": (0.98, "2% below national average - competitive market, heat considerations"),
            "Miami, FL": (1.06, "6% above national average - hurricane requirements, international market"),
        }
        
        # Check for exact match
        if location in location_data:
            return location_data[location]
        
        # Check for state only
        state_defaults = {
            "Tennessee": (1.00, "Tennessee average - varies by city"),
            "TN": (1.00, "Tennessee average - varies by city"),
            "New Hampshire": (0.98, "New Hampshire average - generally below national"),
            "NH": (0.98, "New Hampshire average - generally below national"),
            "Massachusetts": (1.15, "Massachusetts average - generally above national"),
            "MA": (1.15, "Massachusetts average - generally above national"),
            "California": (1.25, "California average - high costs statewide"),
            "CA": (1.25, "California average - high costs statewide"),
            "Texas": (0.96, "Texas average - generally below national"),
            "TX": (0.96, "Texas average - generally below national"),
        }
        
        for state, data in state_defaults.items():
            if state in location:
                return data
        
        # Default with explanation
        return (1.0, "National average - no specific local data available")
    
    def get_classification_multiplier_with_reason(
        self, 
        project_classification: str, 
        occupancy_type: str,
        detected_factors: List[Dict]
    ) -> Tuple[float, str]:
        """Get project classification multiplier with explanation"""
        
        if project_classification == "ground_up":
            return (1.0, "New construction - standard complexity, no existing conditions")
        
        elif project_classification == "addition":
            # Healthcare additions are more complex
            if occupancy_type == "healthcare":
                # Check if it's a hospital
                has_surgery = any("Surgical" in f.get("factor", "") for f in detected_factors)
                if has_surgery:
                    return (1.25, "Hospital addition - 24/7 operations, infection control, complex tie-ins")
                else:
                    return (1.20, "Medical addition - infection control, phased work, operational facility")
            else:
                return (1.12, "Building addition - structural tie-ins, weather protection, limited access")
        
        elif project_classification == "renovation":
            # Check complexity based on occupancy type
            if occupancy_type == "healthcare":
                return (1.40, "Healthcare renovation - infection control, phased work, unknown conditions")
            elif occupancy_type == "restaurant":
                return (0.92, "Restaurant renovation - kitchen systems, code upgrades, limited hours")
            else:
                return (0.92, "Full renovation - demolition, unknowns, code compliance, phased work")
        
        else:
            return (1.0, "Standard project classification")
    
    def detect_special_conditions(self, location: str, description: str, occupancy_type: str) -> List[Dict]:
        """Detect special conditions like weather, seismic, etc."""
        conditions = []
        desc_lower = description.lower()
        
        # Winter conditions for cold climates
        cold_states = ["NH", "MA", "ME", "VT", "CT", "RI", "NY", "MI", "WI", "MN", "ND", "MT", "AK"]
        if any(state in location for state in cold_states):
            if "addition" in desc_lower or "renovation" in desc_lower:
                conditions.append({
                    "factor": "Winter Protection",
                    "category": "Climate",
                    "impact": "+3-5%",
                    "description": "Temporary enclosures, heating, weather protection",
                    "multiplier": 1.04
                })
            elif "ground" in desc_lower or "new" in desc_lower:
                conditions.append({
                    "factor": "Winter Conditions",
                    "category": "Climate",
                    "impact": "+2-3%",
                    "description": "Cold weather concrete, frost protection",
                    "multiplier": 1.025
                })
        
        # Seismic for California
        if any(term in location for term in ["CA", "California"]):
            if occupancy_type == "healthcare":
                conditions.append({
                    "factor": "OSHPD Seismic Requirements",
                    "category": "Structural",
                    "impact": "+12-18%",
                    "description": "Enhanced structural, non-structural bracing, special inspections",
                    "multiplier": 1.15
                })
            else:
                conditions.append({
                    "factor": "Seismic Zone 4 Requirements",
                    "category": "Structural",
                    "impact": "+8-12%",
                    "description": "Enhanced structural systems, special inspections",
                    "multiplier": 1.10
                })
        
        # Hurricane zones
        hurricane_locations = ["FL", "LA", "TX", "SC", "NC", "GA", "AL", "MS"]
        if any(state in location for state in hurricane_locations):
            if any(term in location.lower() for term in ["coast", "beach", "island", "key"]):
                conditions.append({
                    "factor": "Hurricane/Wind Resistance",
                    "category": "Structural",
                    "impact": "+5-8%",
                    "description": "Impact windows, reinforced structure, tie-downs",
                    "multiplier": 1.06
                })
        
        # High altitude considerations
        high_altitude_cities = ["Denver", "Boulder", "Aspen", "Salt Lake", "Boise", "Cheyenne"]
        if any(city in location for city in high_altitude_cities):
            conditions.append({
                "factor": "High Altitude Considerations",
                "category": "Environmental",
                "impact": "+2-3%",
                "description": "Modified HVAC, UV protection, specialized equipment",
                "multiplier": 1.025
            })
        
        # Flood zones
        if any(term in desc_lower for term in ["flood zone", "flood plain", "waterfront", "riverfront"]):
            conditions.append({
                "factor": "Flood Zone Requirements",
                "category": "Site",
                "impact": "+5-10%",
                "description": "Elevated foundation, flood vents, waterproofing",
                "multiplier": 1.07
            })
        
        # Urban constraints
        if any(term in location.lower() for term in ["downtown", "midtown", "city center", "urban"]):
            conditions.append({
                "factor": "Urban Site Constraints",
                "category": "Logistics",
                "impact": "+3-5%",
                "description": "Limited staging, street closures, neighbor protection",
                "multiplier": 1.04
            })
        
        # Brownfield/contaminated sites
        if any(term in desc_lower for term in ["brownfield", "contaminated", "remediation"]):
            conditions.append({
                "factor": "Site Remediation",
                "category": "Environmental",
                "impact": "+10-20%",
                "description": "Environmental cleanup, special handling, monitoring",
                "multiplier": 1.15
            })
        
        return conditions
    
    def get_current_market_conditions(self) -> Dict:
        """Get current market conditions and adjustments"""
        
        # In production, this would pull from real-time data sources
        # For now, return realistic market conditions
        
        return {
            "factor": "Current Market Conditions",
            "category": "Market",
            "status": "Elevated",
            "adjustment_percent": 3.5,
            "description": "Material costs up 3.5% YoY, labor shortage in skilled trades",
            "volatile_materials": ["lumber", "steel", "copper"],
            "labor_availability": "tight",
            "supply_chain": "improving",
            "source": "AGC Construction Inflation Alert Q3 2024"
        }
    
    def calculate_confidence_score(
        self, 
        occupancy_type: str, 
        location: str, 
        square_footage: int,
        detected_factors_count: int
    ) -> Tuple[int, List[Dict]]:
        """Calculate confidence score for the estimate"""
        
        score = 100
        factors = []
        
        # Check if we have good data for this type
        well_known_types = ["office", "restaurant", "retail", "healthcare", "educational", "warehouse", "industrial"]
        if occupancy_type in well_known_types:
            factors.append({
                "factor": "Common building type with extensive data",
                "impact": "+0%",
                "status": "positive"
            })
        else:
            score -= 10
            factors.append({
                "factor": "Less common building type",
                "impact": "-10%",
                "status": "warning"
            })
        
        # Check location data
        if self.has_specific_location_data(location):
            factors.append({
                "factor": f"Specific cost data for {location}",
                "impact": "+0%",
                "status": "positive"
            })
        else:
            score -= 5
            factors.append({
                "factor": "Using regional averages for location",
                "impact": "-5%",
                "status": "warning"
            })
        
        # Size considerations
        if 2000 <= square_footage <= 200000:
            factors.append({
                "factor": "Typical project size range",
                "impact": "+0%",
                "status": "positive"
            })
        elif square_footage < 2000:
            score -= 8
            factors.append({
                "factor": "Very small project - higher per-SF costs likely",
                "impact": "-8%",
                "status": "warning"
            })
        else:
            score -= 8
            factors.append({
                "factor": "Very large project - economies of scale may apply",
                "impact": "-8%",
                "status": "info"
            })
        
        # Complexity based on detected factors
        if detected_factors_count == 0:
            factors.append({
                "factor": "Standard project with no special requirements",
                "impact": "+0%",
                "status": "positive"
            })
        elif detected_factors_count <= 2:
            factors.append({
                "factor": f"{detected_factors_count} special factors detected",
                "impact": "+0%",
                "status": "positive"
            })
        elif detected_factors_count <= 4:
            score -= 5
            factors.append({
                "factor": f"{detected_factors_count} complexity factors - moderate uncertainty",
                "impact": "-5%",
                "status": "info"
            })
        else:
            score -= 10
            factors.append({
                "factor": f"{detected_factors_count} complexity factors - higher uncertainty",
                "impact": "-10%",
                "status": "warning"
            })
        
        # Market volatility
        volatile_materials = self.check_market_volatility()
        if volatile_materials:
            score -= 7
            factors.append({
                "factor": f"Market volatility in: {', '.join(volatile_materials)}",
                "impact": "-7%",
                "status": "warning"
            })
        else:
            factors.append({
                "factor": "Stable material markets",
                "impact": "+0%",
                "status": "positive"
            })
        
        # Data freshness
        factors.append({
            "factor": "Using Q3 2024 RSMeans data",
            "impact": "+0%",
            "status": "positive"
        })
        
        return max(score, 60), factors  # Minimum 60% confidence
    
    def has_specific_location_data(self, location: str) -> bool:
        """Check if we have specific data for this location"""
        known_locations = [
            "Nashville", "Franklin", "Murfreesboro", "Memphis",
            "Manchester", "Nashua", "Concord",
            "Boston", "Cambridge", "Worcester",
            "San Francisco", "Los Angeles", "San Diego", "Sacramento",
            "Dallas", "Houston", "Austin", "San Antonio",
            "New York", "Chicago", "Atlanta", "Denver", "Seattle", "Phoenix", "Miami"
        ]
        return any(city in location for city in known_locations)
    
    def check_market_volatility(self) -> List[str]:
        """Check for volatile materials in current market"""
        # In production, this would check real commodity prices
        # For now, return current volatile materials
        
        volatile = []
        
        # Check recent volatility (mock data - replace with real feeds)
        material_volatility = {
            "lumber": 15,  # % change in last 30 days
            "steel": 8,
            "copper": 12,
            "concrete": 3,
            "drywall": 2,
            "insulation": 6
        }
        
        for material, change in material_volatility.items():
            if abs(change) > 10:
                volatile.append(material)
        
        return volatile
    
    def find_comparable_projects(
        self,
        occupancy_type: str,
        location: str,
        square_footage: int,
        project_classification: str
    ) -> List[Dict]:
        """Find comparable projects (mock data - replace with real database)"""
        
        # In production, query your database of historical projects
        # For now, return realistic mock comparables
        
        comparables = []
        
        # Get base cost for this project type
        base_cost, _ = self.get_base_cost_with_reason(occupancy_type, "")
        location_mult, _ = self.get_location_multiplier_with_reason(location)
        class_mult, _ = self.get_classification_multiplier_with_reason(
            project_classification, occupancy_type, []
        )
        
        expected_cost = base_cost * location_mult * class_mult
        
        # Generate realistic comparable project names
        project_names = {
            "healthcare": [
                "Regional Medical Center Expansion",
                "Outpatient Surgery Center",
                "Medical Office Building",
                "Community Health Clinic"
            ],
            "restaurant": [
                "Urban Gastropub",
                "Fast Casual Chain Location",
                "Fine Dining Establishment",
                "Family Restaurant Renovation"
            ],
            "office": [
                "Corporate Headquarters",
                "Professional Office Building",
                "Tech Company Workspace",
                "Mixed-Use Office Complex"
            ],
            "retail": [
                "Flagship Retail Store",
                "Shopping Center Anchor",
                "Boutique Retail Space",
                "Big Box Retail Location"
            ],
            "warehouse": [
                "Distribution Center",
                "E-Commerce Fulfillment Hub",
                "Cold Storage Facility",
                "Light Industrial Warehouse"
            ]
        }
        
        names = project_names.get(occupancy_type, [
            "Commercial Building A",
            "Commercial Building B", 
            "Commercial Building C"
        ])
        
        # Create 3 comparables with realistic variations
        for i in range(min(3, len(names))):
            # Vary size by -20% to +20%
            size_factor = 0.8 + (i * 0.2)
            comp_size = int(square_footage * size_factor)
            
            # Vary cost by -10% to +10%
            cost_factor = 0.9 + (i * 0.1)
            comp_cost_psf = int(expected_cost * cost_factor)
            comp_total = comp_size * comp_cost_psf
            
            # Vary completion date
            quarters = ["Q1 2024", "Q4 2023", "Q3 2023", "Q2 2023"]
            
            # Determine location variation
            if i == 0:
                comp_location = location
            else:
                # Use nearby location
                if "," in location:
                    city, state = location.split(",")
                    comp_location = f"Near {city.strip()},{state}"
                else:
                    comp_location = f"Near {location}"
            
            comparables.append({
                "project_name": names[i],
                "location": comp_location,
                "square_footage": comp_size,
                "total_cost": comp_total,
                "cost_per_sf": comp_cost_psf,
                "completion_date": quarters[i],
                "project_type": project_classification,
                "similarity_score": 95 - (i * 5)
            })
        
        return comparables


# Create singleton instance
cost_calculation_engine = CostCalculationEngine()
