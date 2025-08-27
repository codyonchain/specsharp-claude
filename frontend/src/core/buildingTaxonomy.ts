/**
 * Single source of truth for building types - TypeScript version
 */
import taxonomyData from '../../../shared/building_types.json';

export type CanonicalBuildingType = 
  | 'residential'
  | 'healthcare'
  | 'educational'
  | 'commercial'
  | 'industrial'
  | 'retail'
  | 'hospitality'
  | 'restaurant'
  | 'civic'
  | 'recreation'
  | 'parking';

export interface SubtypeInfo {
  display_name: string;
  keywords: string[];
  base_cost_per_sf: number;
}

export interface BuildingTypeConfig {
  display_name: string;
  aliases?: string[];
  subtypes: Record<string, SubtypeInfo>;
}

export class BuildingTaxonomy {
  private static taxonomy = taxonomyData;
  
  /**
   * Convert any building type string to canonical form
   */
  static normalizeType(typeString: string): CanonicalBuildingType {
    if (!typeString) {
      return 'commercial'; // Default
    }
    
    const typeLower = typeString.toLowerCase().replace(/_/g, ' ').trim();
    
    // Check if already canonical
    if (typeLower in this.taxonomy.building_types) {
      return typeLower as CanonicalBuildingType;
    }
    
    // Check aliases
    for (const [canonical, config] of Object.entries(this.taxonomy.building_types)) {
      const typeConfig = config as BuildingTypeConfig;
      if (typeConfig.aliases) {
        // Check exact match in aliases
        const normalizedAliases = typeConfig.aliases.map(a => a.toLowerCase().replace(/_/g, ' '));
        if (normalizedAliases.includes(typeLower)) {
          return canonical as CanonicalBuildingType;
        }
        
        // Check partial match
        for (const alias of typeConfig.aliases) {
          const aliasLower = alias.toLowerCase();
          if (aliasLower.includes(typeLower) || typeLower.includes(aliasLower)) {
            return canonical as CanonicalBuildingType;
          }
        }
      }
    }
    
    // Special mappings
    const specialMappings: Record<string, CanonicalBuildingType> = {
      'multi family': 'residential',
      'multifamily': 'residential',
      'multi family residential': 'residential',
      'apartments': 'residential',
      'medical': 'healthcare',
      'education': 'educational',
      'office': 'commercial',
      'warehouse': 'industrial',
      'manufacturing': 'industrial',
      'shopping': 'retail',
      'store': 'retail',
      'hotel': 'hospitality',
      'lodging': 'hospitality',
      'dining': 'restaurant',
      'food service': 'restaurant'
    };
    
    for (const [pattern, canonical] of Object.entries(specialMappings)) {
      if (typeLower.includes(pattern)) {
        return canonical;
      }
    }
    
    // Default
    console.warn(`Unknown building type '${typeString}', defaulting to 'commercial'`);
    return 'commercial';
  }
  
  /**
   * Get canonical building types list
   */
  static getCanonicalTypes(): CanonicalBuildingType[] {
    return Object.keys(this.taxonomy.building_types) as CanonicalBuildingType[];
  }
  
  /**
   * Get display name for a building type
   */
  static getDisplayName(buildingType: string): string {
    const canonical = this.normalizeType(buildingType);
    const config = this.taxonomy.building_types[canonical] as BuildingTypeConfig;
    return config?.display_name || canonical.charAt(0).toUpperCase() + canonical.slice(1);
  }
  
  /**
   * Get valid subtypes for a building type
   */
  static getSubtypes(buildingType: string): string[] {
    const canonical = this.normalizeType(buildingType);
    const config = this.taxonomy.building_types[canonical] as BuildingTypeConfig;
    return Object.keys(config?.subtypes || {});
  }
  
  /**
   * Get subtype information
   */
  static getSubtypeInfo(buildingType: string, subtype: string): SubtypeInfo | null {
    const canonical = this.normalizeType(buildingType);
    const config = this.taxonomy.building_types[canonical] as BuildingTypeConfig;
    return config?.subtypes?.[subtype] || null;
  }
  
  /**
   * Normalize a subtype string
   */
  static normalizeSubtype(buildingType: string, subtype: string): string | null {
    if (!subtype) {
      return null;
    }
    
    const canonicalType = this.normalizeType(buildingType);
    const validSubtypes = this.getSubtypes(canonicalType);
    
    const subtypeLower = subtype.toLowerCase().replace(/-/g, '_').replace(/ /g, '_');
    
    // Direct match
    if (validSubtypes.includes(subtypeLower)) {
      return subtypeLower;
    }
    
    // Check keywords
    const config = this.taxonomy.building_types[canonicalType] as BuildingTypeConfig;
    for (const [validSub, subtypeConfig] of Object.entries(config.subtypes || {})) {
      const keywords = subtypeConfig.keywords || [];
      for (const keyword of keywords) {
        if (keyword.toLowerCase().includes(subtypeLower) || subtypeLower.includes(keyword.toLowerCase())) {
          return validSub;
        }
      }
    }
    
    // Partial match
    for (const validSub of validSubtypes) {
      if (validSub.includes(subtypeLower) || subtypeLower.includes(validSub)) {
        return validSub;
      }
    }
    
    return null;
  }
  
  /**
   * Validate and normalize a type/subtype pair
   */
  static validate(buildingType: string, subtype?: string): [CanonicalBuildingType, string | null] {
    const canonicalType = this.normalizeType(buildingType);
    
    if (!subtype) {
      return [canonicalType, null];
    }
    
    const canonicalSubtype = this.normalizeSubtype(canonicalType, subtype);
    
    if (canonicalSubtype) {
      return [canonicalType, canonicalSubtype];
    }
    
    console.warn(`Invalid subtype '${subtype}' for type '${canonicalType}'`);
    return [canonicalType, null];
  }
  
  /**
   * Get base cost per square foot
   */
  static getBaseCostPerSF(buildingType: string, subtype?: string): number {
    const [canonicalType, canonicalSubtype] = this.validate(buildingType, subtype);
    
    if (canonicalSubtype) {
      const subtypeInfo = this.getSubtypeInfo(canonicalType, canonicalSubtype);
      if (subtypeInfo?.base_cost_per_sf) {
        return subtypeInfo.base_cost_per_sf;
      }
    }
    
    // Default costs by type
    const defaultCosts: Record<CanonicalBuildingType, number> = {
      'residential': 375,
      'healthcare': 550,
      'educational': 295,
      'commercial': 350,
      'industrial': 185,
      'retail': 250,
      'hospitality': 425,
      'restaurant': 375,
      'civic': 425,
      'recreation': 325,
      'parking': 65
    };
    
    return defaultCosts[canonicalType] || 350;
  }
}

// Migration helper
export const MIGRATION_MAP: Record<string, CanonicalBuildingType> = {
  'multifamily': 'residential',
  'multi_family': 'residential',
  'multi_family_residential': 'residential',
  'medical': 'healthcare',
  'education': 'educational',
  'office': 'commercial',
  'warehouse': 'industrial',
  'manufacturing': 'industrial',
  'shopping': 'retail',
  'hotel': 'hospitality'
};

export function migrateBuildingType(oldType: string): CanonicalBuildingType {
  return MIGRATION_MAP[oldType.toLowerCase()] || BuildingTaxonomy.normalizeType(oldType);
}

// Export convenience functions
export const normalizeType = BuildingTaxonomy.normalizeType.bind(BuildingTaxonomy);
export const getDisplayName = BuildingTaxonomy.getDisplayName.bind(BuildingTaxonomy);
export const getSubtypes = BuildingTaxonomy.getSubtypes.bind(BuildingTaxonomy);
export const validate = BuildingTaxonomy.validate.bind(BuildingTaxonomy);
export const getBaseCost = BuildingTaxonomy.getBaseCostPerSF.bind(BuildingTaxonomy);