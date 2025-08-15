/**
 * Central configuration for all building types, subtypes, and base costs.
 * Mirrors backend configuration for consistency.
 */

export interface BuildingSubtype {
  name: string;
  base_cost: number;
  equipment_cost: number;
  typical_floors: number;
  keywords: string[];
}

export interface BuildingType {
  display_name: string;
  subtypes: Record<string, BuildingSubtype>;
}

export const BUILDING_TYPES_CONFIG: Record<string, BuildingType> = {
  restaurant: {
    display_name: 'Restaurant/Food Service',
    subtypes: {
      qsr: {
        name: 'Quick Service (QSR)',
        base_cost: 275,
        equipment_cost: 75,
        typical_floors: 1,
        keywords: ['qsr', 'quick service', 'fast food', 'drive through', 'drive-through']
      },
      fast_casual: {
        name: 'Fast Casual',
        base_cost: 325,
        equipment_cost: 75,
        typical_floors: 1,
        keywords: ['fast casual', 'counter service', 'chipotle', 'panera']
      },
      casual_dining: {
        name: 'Casual Dining',
        base_cost: 350,
        equipment_cost: 75,
        typical_floors: 1,
        keywords: ['casual dining', 'sit down', 'family restaurant']
      },
      fine_dining: {
        name: 'Fine Dining',
        base_cost: 450,
        equipment_cost: 100,
        typical_floors: 1,
        keywords: ['fine dining', 'upscale', 'high end restaurant', 'steakhouse']
      }
    }
  },
  
  healthcare: {
    display_name: 'Healthcare Facilities',
    subtypes: {
      hospital: {
        name: 'Hospital',
        base_cost: 950,
        equipment_cost: 200,
        typical_floors: 5,
        keywords: ['hospital', 'medical center', 'emergency', 'trauma center']
      },
      medical_office: {
        name: 'Medical Office Building',
        base_cost: 280,
        equipment_cost: 50,
        typical_floors: 3,
        keywords: ['medical office', 'mob', 'clinic', 'outpatient']
      },
      urgent_care: {
        name: 'Urgent Care',
        base_cost: 350,
        equipment_cost: 100,
        typical_floors: 1,
        keywords: ['urgent care', 'walk in clinic', 'immediate care']
      },
      surgery_center: {
        name: 'Ambulatory Surgery Center',
        base_cost: 650,
        equipment_cost: 150,
        typical_floors: 1,
        keywords: ['surgery center', 'asc', 'ambulatory', 'surgical center']
      },
      dental_office: {
        name: 'Dental Office',
        base_cost: 325,
        equipment_cost: 125,
        typical_floors: 1,
        keywords: ['dental', 'dentist', 'orthodontist']
      }
    }
  },
  
  residential: {
    display_name: 'Multifamily Residential',
    subtypes: {
      luxury_apartments: {
        name: 'Class A / Luxury Apartments',
        base_cost: 185,
        equipment_cost: 40,
        typical_floors: 4,
        keywords: ['luxury apartment', 'class a', 'high end apartment']
      },
      market_rate_apartments: {
        name: 'Class B / Market Rate',
        base_cost: 145,
        equipment_cost: 25,
        typical_floors: 3,
        keywords: ['apartment', 'multifamily', 'market rate']
      },
      affordable_housing: {
        name: 'Affordable Housing',
        base_cost: 120,
        equipment_cost: 15,
        typical_floors: 3,
        keywords: ['affordable housing', 'workforce housing', 'section 8', 'lihtc']
      },
      student_housing: {
        name: 'Student Housing',
        base_cost: 165,
        equipment_cost: 20,
        typical_floors: 4,
        keywords: ['student housing', 'dormitory', 'student apartment']
      },
      condominiums: {
        name: 'Condominiums',
        base_cost: 195,
        equipment_cost: 35,
        typical_floors: 6,
        keywords: ['condo', 'condominium', 'owned apartment']
      }
    }
  },
  
  office: {
    display_name: 'Office Buildings',
    subtypes: {
      class_a_office: {
        name: 'Class A Office',
        base_cost: 325,
        equipment_cost: 25,
        typical_floors: 10,
        keywords: ['class a office', 'premium office', 'corporate headquarters']
      },
      class_b_office: {
        name: 'Class B Office',
        base_cost: 225,
        equipment_cost: 15,
        typical_floors: 5,
        keywords: ['class b office', 'standard office', 'professional building', 'office building', 'office']
      },
      class_c_office: {
        name: 'Class C Office',
        base_cost: 165,
        equipment_cost: 10,
        typical_floors: 3,
        keywords: ['class c office', 'basic office']
      },
      tech_office: {
        name: 'Tech/Creative Office',
        base_cost: 425,
        equipment_cost: 50,
        typical_floors: 4,
        keywords: ['tech office', 'creative office', 'startup', 'open office']
      }
    }
  },
  
  industrial: {
    display_name: 'Industrial Buildings',
    subtypes: {
      warehouse: {
        name: 'Warehouse/Distribution',
        base_cost: 75,
        equipment_cost: 10,
        typical_floors: 1,
        keywords: ['warehouse', 'distribution center', 'storage', 'distribution']
      },
      manufacturing: {
        name: 'Manufacturing',
        base_cost: 110,
        equipment_cost: 15,
        typical_floors: 1,
        keywords: ['manufacturing', 'factory', 'production facility']
      },
      flex_space: {
        name: 'Flex/Light Industrial',
        base_cost: 95,
        equipment_cost: 15,
        typical_floors: 1,
        keywords: ['flex space', 'light industrial', 'workshop']
      },
      cold_storage: {
        name: 'Cold Storage',
        base_cost: 175,
        equipment_cost: 25,
        typical_floors: 1,
        keywords: ['cold storage', 'freezer', 'refrigerated warehouse']
      },
      data_center: {
        name: 'Data Center',
        base_cost: 850,
        equipment_cost: 350,
        typical_floors: 1,
        keywords: ['data center', 'server farm', 'colocation']
      }
    }
  },
  
  retail: {
    display_name: 'Retail',
    subtypes: {
      big_box: {
        name: 'Big Box Retail',
        base_cost: 135,
        equipment_cost: 15,
        typical_floors: 1,
        keywords: ['big box', 'walmart', 'target', 'home depot']
      },
      strip_center: {
        name: 'Strip Center',
        base_cost: 185,
        equipment_cost: 15,
        typical_floors: 1,
        keywords: ['strip mall', 'strip center', 'retail center']
      },
      mall_retail: {
        name: 'Mall Retail',
        base_cost: 225,
        equipment_cost: 25,
        typical_floors: 1,
        keywords: ['mall store', 'anchor store', 'department store', 'retail store', 'retail']
      },
      boutique_retail: {
        name: 'Boutique/High-End',
        base_cost: 325,
        equipment_cost: 25,
        typical_floors: 1,
        keywords: ['boutique', 'luxury retail', 'flagship store']
      },
      grocery: {
        name: 'Grocery Store',
        base_cost: 245,
        equipment_cost: 30,
        typical_floors: 1,
        keywords: ['grocery', 'supermarket', 'food store']
      },
      convenience_store: {
        name: 'Convenience Store',
        base_cost: 285,
        equipment_cost: 40,
        typical_floors: 1,
        keywords: ['convenience store', 'gas station', 'c-store', '7-eleven']
      }
    }
  },
  
  education: {
    display_name: 'Educational Facilities',
    subtypes: {
      elementary_school: {
        name: 'Elementary School',
        base_cost: 275,
        equipment_cost: 25,
        typical_floors: 2,
        keywords: ['elementary school', 'primary school', 'grade school']
      },
      middle_school: {
        name: 'Middle School',
        base_cost: 285,
        equipment_cost: 30,
        typical_floors: 2,
        keywords: ['middle school', 'junior high']
      },
      high_school: {
        name: 'High School',
        base_cost: 325,
        equipment_cost: 35,
        typical_floors: 3,
        keywords: ['high school', 'secondary school']
      },
      university: {
        name: 'University/College',
        base_cost: 385,
        equipment_cost: 45,
        typical_floors: 4,
        keywords: ['university', 'college', 'higher education']
      },
      vocational_school: {
        name: 'Vocational/Technical',
        base_cost: 295,
        equipment_cost: 50,
        typical_floors: 2,
        keywords: ['vocational', 'technical school', 'trade school']
      },
      daycare: {
        name: 'Daycare/Preschool',
        base_cost: 225,
        equipment_cost: 20,
        typical_floors: 1,
        keywords: ['daycare', 'preschool', 'childcare', 'kindergarten']
      }
    }
  },
  
  hospitality: {
    display_name: 'Hospitality',
    subtypes: {
      luxury_hotel: {
        name: 'Luxury/5-Star Hotel',
        base_cost: 425,
        equipment_cost: 75,
        typical_floors: 20,
        keywords: ['luxury hotel', '5 star', 'five star', 'resort']
      },
      full_service_hotel: {
        name: 'Full Service Hotel',
        base_cost: 325,
        equipment_cost: 50,
        typical_floors: 10,
        keywords: ['full service hotel', 'marriott', 'hilton', 'convention hotel', 'hotel']
      },
      limited_service_hotel: {
        name: 'Limited Service Hotel',
        base_cost: 225,
        equipment_cost: 35,
        typical_floors: 4,
        keywords: ['limited service', 'hampton inn', 'holiday inn express']
      },
      economy_hotel: {
        name: 'Economy Hotel',
        base_cost: 165,
        equipment_cost: 25,
        typical_floors: 3,
        keywords: ['economy hotel', 'motel', 'budget hotel', 'motel 6']
      },
      boutique_hotel: {
        name: 'Boutique Hotel',
        base_cost: 385,
        equipment_cost: 60,
        typical_floors: 6,
        keywords: ['boutique hotel', 'design hotel', 'lifestyle hotel']
      }
    }
  },
  
  senior_living: {
    display_name: 'Senior Living',
    subtypes: {
      independent_living: {
        name: 'Independent Living',
        base_cost: 185,
        equipment_cost: 30,
        typical_floors: 3,
        keywords: ['independent living', 'senior apartments', '55+']
      },
      assisted_living: {
        name: 'Assisted Living',
        base_cost: 245,
        equipment_cost: 40,
        typical_floors: 3,
        keywords: ['assisted living', 'alf', 'senior care']
      },
      memory_care: {
        name: 'Memory Care',
        base_cost: 285,
        equipment_cost: 45,
        typical_floors: 2,
        keywords: ['memory care', 'dementia care', 'alzheimer']
      },
      skilled_nursing: {
        name: 'Skilled Nursing',
        base_cost: 325,
        equipment_cost: 60,
        typical_floors: 2,
        keywords: ['skilled nursing', 'nursing home', 'snf']
      }
    }
  },
  
  mixed_use: {
    display_name: 'Mixed Use',
    subtypes: {
      retail_residential: {
        name: 'Retail + Residential',
        base_cost: 245,
        equipment_cost: 35,
        typical_floors: 5,
        keywords: ['mixed use', 'retail residential', 'live work']
      },
      office_residential: {
        name: 'Office + Residential',
        base_cost: 265,
        equipment_cost: 30,
        typical_floors: 8,
        keywords: ['office residential', 'mixed use office']
      },
      hotel_retail: {
        name: 'Hotel + Retail',
        base_cost: 285,
        equipment_cost: 45,
        typical_floors: 12,
        keywords: ['hotel retail', 'mixed use hotel']
      },
      full_mixed: {
        name: 'Retail + Office + Residential',
        base_cost: 275,
        equipment_cost: 40,
        typical_floors: 15,
        keywords: ['full mixed use', 'urban mixed', 'tod']
      }
    }
  },
  
  specialty: {
    display_name: 'Specialty Buildings',
    subtypes: {
      laboratory: {
        name: 'Laboratory/Research',
        base_cost: 525,
        equipment_cost: 175,
        typical_floors: 3,
        keywords: ['laboratory', 'lab', 'research facility', 'r&d']
      },
      clean_room: {
        name: 'Clean Room Facility',
        base_cost: 750,
        equipment_cost: 250,
        typical_floors: 2,
        keywords: ['clean room', 'semiconductor', 'pharma manufacturing']
      },
      sports_facility: {
        name: 'Sports/Recreation',
        base_cost: 225,
        equipment_cost: 50,
        typical_floors: 1,
        keywords: ['gym', 'sports facility', 'recreation center', 'ymca']
      },
      theater: {
        name: 'Theater/Performance',
        base_cost: 385,
        equipment_cost: 75,
        typical_floors: 1,
        keywords: ['theater', 'cinema', 'performing arts', 'auditorium']
      },
      parking_garage: {
        name: 'Parking Garage',
        base_cost: 65,
        equipment_cost: 5,
        typical_floors: 5,
        keywords: ['parking garage', 'parking structure', 'deck']
      },
      religious: {
        name: 'Religious/Worship',
        base_cost: 245,
        equipment_cost: 25,
        typical_floors: 1,
        keywords: ['church', 'mosque', 'synagogue', 'temple', 'worship']
      }
    }
  }
};

/**
 * Detect building type and subtype from description text
 */
export function detectBuildingType(description: string): {
  building_type: string | null;
  building_subtype: string | null;
  confidence: number;
} {
  const lowercaseDesc = description.toLowerCase();
  let bestMatch = { type: null as string | null, subtype: null as string | null, confidence: 0 };
  
  // Check each building type and subtype
  for (const [typeKey, typeConfig] of Object.entries(BUILDING_TYPES_CONFIG)) {
    for (const [subtypeKey, subtypeConfig] of Object.entries(typeConfig.subtypes)) {
      // Check if any keywords match
      for (const keyword of subtypeConfig.keywords) {
        if (lowercaseDesc.includes(keyword)) {
          // Multi-word keywords get higher confidence
          const wordCount = keyword.split(' ').length;
          const confidence = Math.min(0.3 * wordCount, 0.95);
          
          // Exact match bonus
          const exactMatchBonus = lowercaseDesc === keyword ? 0.2 : 0;
          const finalConfidence = Math.min(confidence + exactMatchBonus, 1.0);
          
          if (finalConfidence > bestMatch.confidence) {
            bestMatch = {
              type: typeKey,
              subtype: subtypeKey,
              confidence: finalConfidence
            };
          }
        }
      }
    }
  }
  
  return {
    building_type: bestMatch.type,
    building_subtype: bestMatch.subtype,
    confidence: bestMatch.confidence
  };
}

/**
 * Get display name for a building type/subtype combination
 */
export function getBuildingDisplayName(building_type: string, building_subtype: string): string {
  const typeConfig = BUILDING_TYPES_CONFIG[building_type];
  if (!typeConfig) return 'Unknown Building Type';
  
  const subtypeConfig = typeConfig.subtypes[building_subtype];
  if (!subtypeConfig) return typeConfig.display_name;
  
  return `${typeConfig.display_name} - ${subtypeConfig.name}`;
}

/**
 * Get all building types for dropdown/selection
 */
export function getAllBuildingTypes(): Array<{
  value: string;
  label: string;
  subtypes: Array<{ value: string; label: string }>;
}> {
  return Object.entries(BUILDING_TYPES_CONFIG).map(([key, config]) => ({
    value: key,
    label: config.display_name,
    subtypes: Object.entries(config.subtypes).map(([subKey, subConfig]) => ({
      value: subKey,
      label: subConfig.name
    }))
  }));
}

// Compatibility exports for ScopeGenerator
export const BUILDING_TYPES = getAllBuildingTypes();

export function getBuildingType(value: string) {
  const config = BUILDING_TYPES_CONFIG[value];
  if (!config) return undefined;
  
  return {
    value,
    label: config.display_name,
    subtypes: Object.entries(config.subtypes).map(([key, sub]) => ({
      value: key,
      label: sub.name,
      costHint: `$${sub.base_cost}-${sub.base_cost + sub.equipment_cost}/SF`,
      typicalFloorPlate: 10000, // Default
      maxFloors: sub.typical_floors
    }))
  };
}

export function getSubtype(buildingType: string, subtypeValue: string) {
  const config = BUILDING_TYPES_CONFIG[buildingType];
  if (!config) return undefined;
  
  const subtype = config.subtypes[subtypeValue];
  if (!subtype) return undefined;
  
  return {
    value: subtypeValue,
    label: subtype.name,
    costHint: `$${subtype.base_cost}-${subtype.base_cost + subtype.equipment_cost}/SF`,
    typicalFloorPlate: 10000, // Default
    maxFloors: subtype.typical_floors
  };
}

export function estimateFloors(
  squareFootage: number, 
  buildingType: string, 
  buildingSubtype: string
): number {
  const config = BUILDING_TYPES_CONFIG[buildingType];
  if (!config) return 1;
  
  const subtype = config.subtypes[buildingSubtype];
  if (!subtype) return 1;
  
  const typicalFloorPlate = 10000; // Default floor plate
  const maxFloors = subtype.typical_floors || 20;
  
  // Calculate estimated floors
  const estimatedFloors = Math.ceil(squareFootage / typicalFloorPlate);
  
  // Apply constraints
  return Math.max(1, Math.min(estimatedFloors, maxFloors));
}

export function getDefaultCeilingHeight(buildingType: string, subtype: string): number {
  // Special cases
  if (buildingType === 'industrial') return 24;
  if (buildingType === 'retail' && subtype === 'big_box') return 20;
  if (buildingType === 'healthcare' && subtype === 'hospital') return 12;
  if (buildingType === 'restaurant') return 14;
  
  // Defaults
  return 10;
}