"""
Healthcare Facility Classification Service
Detects facility type, equipment needs, and compliance requirements
"""

from typing import Dict, List, Optional
import re

class HealthcareFacilityClassifier:
    """
    Classifies healthcare facilities and identifies special requirements
    """
    
    def classify_healthcare_facility(self, description: str) -> Dict:
        """
        Main classification method - returns facility type and requirements
        """
        description_lower = description.lower()
        
        # Determine primary facility type
        facility_type = self._identify_facility_type(description_lower)
        
        # Identify specialties and departments
        specialties = self._identify_specialties(description_lower)
        
        # Identify special spaces
        special_spaces = self._identify_special_spaces(description_lower)
        
        # Determine compliance requirements
        compliance = self._identify_compliance_requirements(
            facility_type, specialties, special_spaces, description_lower
        )
        
        # Identify medical equipment needs
        equipment = self._identify_equipment_needs(
            facility_type, specialties, special_spaces
        )
        
        # Calculate complexity multiplier
        complexity = self._calculate_complexity(
            facility_type, specialties, special_spaces, compliance
        )
        
        return {
            'facility_type': facility_type,
            'specialties': specialties,
            'special_spaces': special_spaces,
            'compliance_requirements': compliance,
            'equipment_needs': equipment,
            'complexity_multiplier': complexity,
            'base_construction_per_sf': self._get_base_cost(facility_type),
            'equipment_cost_per_sf': self._get_equipment_cost(facility_type, specialties)
        }
    
    def _identify_facility_type(self, description: str) -> str:
        """
        Identify primary healthcare facility type
        """
        # Hospital indicators (most complex first)
        # Note: 'er' alone is too generic, need more context
        if any(term in description for term in [
            'hospital', 'medical center', 'trauma center', 
            'acute care', 'inpatient'
        ]):
            if 'children' in description or 'pediatric' in description:
                return 'pediatric_hospital'
            elif 'psychiatric' in description or 'behavioral' in description:
                return 'psychiatric_hospital'
            elif 'rehabilitation' in description or 'rehab' in description:
                return 'rehabilitation_hospital'
            elif 'critical access' in description:
                return 'critical_access_hospital'
            else:
                return 'general_hospital'
        
        # Surgical/Procedure Centers (check before imaging to catch ASCs)
        elif any(term in description for term in [
            'surgery center', 'surgical center', 'asc', 
            'ambulatory surgery'
        ]):
            return 'ambulatory_surgery_center'
        
        # Imaging Centers
        elif any(term in description for term in [
            'imaging center', 'radiology', 'mri', 'ct scan', 
            'diagnostic imaging', 'x-ray center'
        ]):
            return 'imaging_center'
        
        # Emergency/Urgent Care
        elif any(term in description for term in [
            'urgent care', 'walk-in clinic', 'express care',
            'immediate care', 'emergency clinic'
        ]):
            return 'urgent_care'
        
        # Specialty Clinics
        elif any(term in description for term in [
            'dialysis', 'renal center', 'kidney center'
        ]):
            return 'dialysis_center'
        elif any(term in description for term in [
            'cancer center', 'cancer treatment', 'oncology', 'infusion center',
            'chemotherapy', 'radiation therapy'
        ]):
            return 'cancer_center'
        elif any(term in description for term in [
            'birth center', 'birthing center', 'maternity',
            'obstetric', 'ob/gyn', 'womens health', "women's health"
        ]):
            return 'birthing_center'
        
        # Outpatient Clinics
        elif any(term in description for term in [
            'health center', 'community health', 'fqhc',
            'federally qualified', 'public health'
        ]):
            return 'community_health_center'
        elif any(term in description for term in [
            'dental clinic', 'dental office', 'dentist',
            'oral surgery', 'orthodontic'
        ]):
            return 'dental_clinic'
        elif any(term in description for term in [
            'eye clinic', 'ophthalmology', 'optometry',
            'vision center', 'lasik'
        ]):
            return 'eye_clinic'
        
        # Senior Care
        elif any(term in description for term in [
            'nursing home', 'skilled nursing', 'snf',
            'long-term care', 'ltc'
        ]):
            return 'skilled_nursing_facility'
        elif any(term in description for term in [
            'assisted living', 'senior living', 'memory care',
            'alzheimer', 'dementia care'
        ]):
            return 'assisted_living'
        
        # Default medical office
        elif any(term in description for term in [
            'medical office', 'doctor', 'physician office',
            'clinic', 'medical building', 'mob', 'healthcare',
            'health'
        ]):
            return 'medical_office'
        
        # If no healthcare terms found
        else:
            return 'unknown'
    
    def _identify_specialties(self, description: str) -> List[str]:
        """
        Identify medical specialties mentioned
        """
        specialties = []
        
        specialty_map = {
            'cardiology': ['cardiology', 'cardiac', 'heart center', 'cath lab'],
            'orthopedics': ['orthopedic', 'ortho', 'sports medicine', 'joint replacement'],
            'neurology': ['neurology', 'neuro', 'brain', 'spine center'],
            'pediatrics': ['pediatric', 'children', 'kids'],
            'surgery': ['surgery', 'surgical', 'operating', 'or suite'],
            'emergency': ['emergency', 'trauma', 'er', 'ed'],
            'intensive_care': ['icu', 'intensive care', 'critical care'],
            'radiology': ['radiology', 'imaging', 'x-ray', 'mri', 'ct'],
            'laboratory': ['lab', 'laboratory', 'pathology'],
            'pharmacy': ['pharmacy', 'medication', 'drug'],
            'rehabilitation': ['rehab', 'physical therapy', 'pt', 'occupational therapy'],
            'mental_health': ['psychiatric', 'behavioral', 'mental health', 'psychology']
        }
        
        for specialty, keywords in specialty_map.items():
            if any(keyword in description for keyword in keywords):
                specialties.append(specialty)
        
        return specialties
    
    def _identify_special_spaces(self, description: str) -> List[str]:
        """
        Identify special spaces that affect construction costs
        """
        special_spaces = []
        
        space_map = {
            'operating_room': ['operating room', ' or ', 'surgery suite', 'surgical suite', 'surgical center', '4 ors', '6 ors', '8 ors'],
            'emergency_dept': ['emergency department', 'emergency room'],
            'icu': ['icu', 'intensive care', 'critical care unit'],
            'clean_room': ['clean room', 'sterile processing', 'compounding'],
            'isolation_room': ['isolation', 'negative pressure', 'airborne infection'],
            'mri_suite': ['mri', 'magnetic resonance'],
            'ct_suite': ['ct scan', 'cat scan', 'computed tomography'],
            'xray_suite': ['x-ray', 'radiography', 'fluoroscopy'],
            'cath_lab': ['cath lab', 'catheterization', 'angiography'],
            'linear_accelerator': ['linear accelerator', 'radiation therapy', 'linac'],
            'pharmacy': ['pharmacy', 'medication room', 'drug storage'],
            'laboratory': ['laboratory', 'lab', 'pathology'],
            'morgue': ['morgue', 'autopsy'],
            'kitchen': ['kitchen', 'dietary', 'food service'],
            'data_center': ['data center', 'server room', 'it room'],
            'helicopter_pad': ['helipad', 'helicopter', 'rooftop landing']
        }
        
        for space, keywords in space_map.items():
            if any(keyword in description for keyword in keywords):
                special_spaces.append(space)
        
        return special_spaces
    
    def _identify_compliance_requirements(
        self, facility_type: str, specialties: List[str], 
        special_spaces: List[str], description: str
    ) -> Dict[str, bool]:
        """
        Identify regulatory and compliance requirements
        """
        compliance = {
            'joint_commission': False,
            'medicare_certified': False,
            'state_licensed': True,  # Almost always required
            'oshpd_seismic': False,  # California specific
            'fgc_guidelines': False,  # FGI Guidelines for Healthcare
            'usp_797_800': False,  # Pharmacy compounding
            'life_safety_code': False,
            'infection_control': False,
            'radiation_shielding': False,
            'magnetic_shielding': False
        }
        
        # Hospital-level requirements
        if 'hospital' in facility_type:
            compliance['joint_commission'] = True
            compliance['medicare_certified'] = True
            compliance['fgc_guidelines'] = True
            compliance['life_safety_code'] = True
            compliance['infection_control'] = True
        
        # Surgery center requirements
        if 'surgery' in facility_type or 'operating_room' in special_spaces:
            compliance['medicare_certified'] = True
            compliance['infection_control'] = True
            compliance['life_safety_code'] = True
        
        # Pharmacy requirements
        if 'pharmacy' in specialties or 'pharmacy' in special_spaces:
            compliance['usp_797_800'] = True
        
        # Radiation requirements
        if any(space in ['mri_suite', 'ct_suite', 'xray_suite', 'linear_accelerator'] 
               for space in special_spaces):
            compliance['radiation_shielding'] = True
        
        # MRI specific
        if 'mri_suite' in special_spaces:
            compliance['magnetic_shielding'] = True
        
        # California specific
        if any(loc in description.lower() for loc in ['california', 'ca', 'los angeles', 'san francisco']):
            compliance['oshpd_seismic'] = True
        
        return compliance
    
    def _identify_equipment_needs(
        self, facility_type: str, specialties: List[str], special_spaces: List[str]
    ) -> Dict[str, Dict]:
        """
        Identify medical equipment needs and estimated costs
        """
        equipment = {}
        
        # Imaging equipment
        if 'mri_suite' in special_spaces:
            equipment['mri'] = {
                'type': '1.5T MRI Scanner',
                'cost_range': (1500000, 3000000),
                'typical_cost': 2000000,
                'requires_shielding': True
            }
        
        if 'ct_suite' in special_spaces:
            equipment['ct_scanner'] = {
                'type': '64-Slice CT Scanner',
                'cost_range': (500000, 2000000),
                'typical_cost': 1000000,
                'requires_shielding': True
            }
        
        if 'xray_suite' in special_spaces:
            equipment['xray'] = {
                'type': 'Digital X-Ray System',
                'cost_range': (150000, 500000),
                'typical_cost': 250000,
                'requires_shielding': True
            }
        
        # Surgical equipment
        if 'operating_room' in special_spaces:
            equipment['surgical_suite'] = {
                'type': 'Complete OR Setup',
                'cost_range': (500000, 1500000),
                'typical_cost': 800000,
                'includes': ['surgical lights', 'tables', 'booms', 'integration']
            }
        
        # Emergency equipment
        if 'emergency_dept' in special_spaces:
            equipment['emergency'] = {
                'type': 'ED Equipment Package',
                'cost_range': (300000, 800000),
                'typical_cost': 500000,
                'includes': ['crash carts', 'defibrillators', 'monitors', 'ultrasound']
            }
        
        # Laboratory equipment
        if 'laboratory' in special_spaces:
            equipment['lab'] = {
                'type': 'Clinical Laboratory Equipment',
                'cost_range': (200000, 1000000),
                'typical_cost': 400000,
                'includes': ['analyzers', 'centrifuges', 'microscopes', 'refrigeration']
            }
        
        # Basic medical office equipment
        if facility_type == 'medical_office':
            equipment['exam_rooms'] = {
                'type': 'Exam Room Equipment',
                'cost_range': (5000, 15000),
                'typical_cost': 8000,
                'per_room': True
            }
        
        return equipment
    
    def _calculate_complexity(
        self, facility_type: str, specialties: List[str], 
        special_spaces: List[str], compliance: Dict[str, bool]
    ) -> float:
        """
        Calculate complexity multiplier based on requirements
        """
        base_multiplier = 1.0
        
        # Facility type complexity
        facility_complexity = {
            'general_hospital': 1.3,
            'pediatric_hospital': 1.35,
            'psychiatric_hospital': 1.15,
            'rehabilitation_hospital': 1.2,
            'ambulatory_surgery_center': 1.25,
            'imaging_center': 1.15,
            'cancer_center': 1.3,
            'urgent_care': 1.05,
            'medical_office': 1.0,
            'dental_clinic': 1.05,
            'skilled_nursing_facility': 1.1,
            'assisted_living': 1.0
        }
        
        base_multiplier = facility_complexity.get(facility_type, 1.0)
        
        # Add complexity for special spaces
        space_complexity = {
            'operating_room': 0.15,
            'emergency_dept': 0.1,
            'icu': 0.12,
            'clean_room': 0.15,
            'mri_suite': 0.1,
            'ct_suite': 0.08,
            'cath_lab': 0.12,
            'linear_accelerator': 0.2
        }
        
        for space in special_spaces:
            base_multiplier += space_complexity.get(space, 0.05)
        
        # Add complexity for compliance requirements
        compliance_count = sum(1 for req in compliance.values() if req)
        if compliance_count > 5:
            base_multiplier += 0.1
        elif compliance_count > 3:
            base_multiplier += 0.05
        
        return min(base_multiplier, 2.0)  # Cap at 2x
    
    def _get_base_cost(self, facility_type: str) -> int:
        """
        Get base construction cost per square foot (excluding equipment)
        """
        base_costs = {
            'general_hospital': 450,
            'pediatric_hospital': 475,
            'psychiatric_hospital': 350,
            'rehabilitation_hospital': 375,
            'critical_access_hospital': 400,
            'ambulatory_surgery_center': 425,
            'imaging_center': 375,
            'cancer_center': 450,
            'dialysis_center': 325,
            'birthing_center': 400,
            'urgent_care': 325,
            'community_health_center': 275,
            'medical_office': 275,
            'dental_clinic': 300,
            'eye_clinic': 325,
            'skilled_nursing_facility': 250,
            'assisted_living': 225
        }
        
        return base_costs.get(facility_type, 275)
    
    def _get_equipment_cost(self, facility_type: str, specialties: List[str]) -> int:
        """
        Get typical equipment cost per square foot
        """
        equipment_costs = {
            'general_hospital': 150,
            'pediatric_hospital': 140,
            'psychiatric_hospital': 30,
            'rehabilitation_hospital': 60,
            'ambulatory_surgery_center': 125,
            'imaging_center': 200,  # High due to imaging equipment
            'cancer_center': 175,   # Radiation therapy equipment
            'dialysis_center': 80,
            'urgent_care': 40,
            'medical_office': 25,
            'dental_clinic': 60,
            'eye_clinic': 75,
            'skilled_nursing_facility': 20,
            'assisted_living': 10
        }
        
        base_equipment = equipment_costs.get(facility_type, 25)
        
        # Adjust for specialties
        if 'radiology' in specialties:
            base_equipment += 50
        if 'surgery' in specialties:
            base_equipment += 75
        if 'laboratory' in specialties:
            base_equipment += 30
        
        return base_equipment


# Singleton instance
healthcare_classifier = HealthcareFacilityClassifier()


# Test the classifier
if __name__ == "__main__":
    classifier = HealthcareFacilityClassifier()
    
    # Test cases
    test_descriptions = [
        "50,000 sf hospital addition with surgical suite in Manchester NH",
        "15,000 sf medical office building in Nashville TN",
        "8,000 sf urgent care center with x-ray in Franklin TN",
        "25,000 sf ambulatory surgery center with 4 ORs in Nashua NH",
        "12,000 sf imaging center with MRI and CT in Murfreesboro TN",
        "5,000 sf dental clinic in Concord NH",
        "100,000 sf skilled nursing facility in Nashville",
        "3,000 sf dialysis center with 20 stations in Manchester NH"
    ]
    
    print("="*70)
    print("HEALTHCARE FACILITY CLASSIFIER TEST RESULTS")
    print("="*70)
    
    for desc in test_descriptions:
        result = classifier.classify_healthcare_facility(desc)
        print(f"\nDescription: {desc}")
        print(f"Type: {result['facility_type']}")
        print(f"Base Cost: ${result['base_construction_per_sf']}/SF")
        print(f"Equipment: ${result['equipment_cost_per_sf']}/SF")
        print(f"Total Cost: ${result['base_construction_per_sf'] + result['equipment_cost_per_sf']}/SF")
        print(f"Complexity: {result['complexity_multiplier']}x")
        print(f"Specialties: {', '.join(result['specialties']) if result['specialties'] else 'None'}")
        print(f"Special Spaces: {', '.join(result['special_spaces']) if result['special_spaces'] else 'None'}")
        print(f"Equipment Needs: {', '.join(result['equipment_needs'].keys()) if result['equipment_needs'] else 'None'}")
        
        # Show compliance requirements if any special ones
        special_compliance = [k for k, v in result['compliance_requirements'].items() 
                            if v and k not in ['state_licensed']]
        if special_compliance:
            print(f"Compliance: {', '.join(special_compliance)}")
        print("-"*70)