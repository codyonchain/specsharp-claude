// NLP Service for parsing natural language project descriptions
// Extracts structured data from user input for auto-population

export interface ParsedInput {
  square_footage: number | null;
  occupancy_type: string | null;  // Primary category
  subtype: string | null;          // Specific type within category
  features: string[];              // Additional features/amenities
  stories: number | null;
  location: string | null;
  confidence: number;              // 0-100 confidence score
}

interface OccupancyMapping {
  keywords: string[];
  subtypes: {
    [key: string]: {
      keywords: string[];
      default_cost: number;
    };
  };
}

// Comprehensive mapping of building types and their variations
const OCCUPANCY_MAPPINGS: { [key: string]: OccupancyMapping } = {
  healthcare: {
    keywords: ['hospital', 'medical', 'clinic', 'healthcare', 'surgical', 'health'],
    subtypes: {
      hospital: {
        keywords: ['hospital', 'emergency', 'emergency department', 'er', 'trauma center', 'acute care'],
        default_cost: 1150
      },
      surgical_center: {
        keywords: ['surgical center', 'surgery center', 'ambulatory surgical', 'asc'],
        default_cost: 475
      },
      imaging_center: {
        keywords: ['imaging center', 'radiology', 'mri', 'ct scan', 'x-ray', 'diagnostic imaging'],
        default_cost: 450
      },
      outpatient_clinic: {
        keywords: ['outpatient', 'clinic', 'health clinic', 'community clinic'],
        default_cost: 375
      },
      urgent_care: {
        keywords: ['urgent care', 'walk-in clinic', 'immediate care'],
        default_cost: 350
      },
      medical_office: {
        keywords: ['medical office', 'doctor office', 'physician office', 'practice'],
        default_cost: 325
      },
      dental_office: {
        keywords: ['dental', 'dentist', 'orthodontic', 'oral surgery'],
        default_cost: 300
      },
      senior_care: {
        keywords: ['senior care', 'nursing home', 'assisted living', 'memory care', 'skilled nursing'],
        default_cost: 275
      }
    }
  },
  restaurant: {
    keywords: ['restaurant', 'dining', 'qsr', 'food', 'kitchen', 'eatery', 'cafe'],
    subtypes: {
      qsr: {
        keywords: ['qsr', 'quick service', 'fast food', 'drive through', 'drive-through', 'fast casual'],
        default_cost: 300
      },
      casual_dining: {
        keywords: ['casual dining', 'family restaurant', 'sit-down', 'table service'],
        default_cost: 375
      },
      full_service: {
        keywords: ['full service', 'full-service restaurant', 'traditional restaurant'],
        default_cost: 425
      },
      fine_dining: {
        keywords: ['fine dining', 'upscale', 'high-end restaurant', 'luxury dining', 'white tablecloth'],
        default_cost: 550
      }
    }
  },
  residential: {
    keywords: ['apartment', 'condo', 'residential', 'housing', 'multifamily', 'living', 'dwelling'],
    subtypes: {
      luxury_apartments: {
        keywords: ['luxury apartment', 'high-end', 'class a', 'premium apartment', 'upscale residential'],
        default_cost: 225
      },
      standard_apartments: {
        keywords: ['apartment', 'multifamily', 'residential', 'mid-market', 'class b'],
        default_cost: 165
      },
      affordable_housing: {
        keywords: ['affordable housing', 'workforce housing', 'section 8', 'low income', 'subsidized'],
        default_cost: 135
      },
      senior_living: {
        keywords: ['senior living', 'retirement community', '55+', 'active adult'],
        default_cost: 185
      },
      student_housing: {
        keywords: ['student housing', 'dormitory', 'dorm', 'student apartment'],
        default_cost: 175
      }
    }
  },
  commercial: {
    keywords: ['office', 'commercial', 'business', 'corporate', 'workspace'],
    subtypes: {
      office: {
        keywords: ['office', 'office building', 'corporate', 'headquarters', 'business center'],
        default_cost: 250
      },
      retail: {
        keywords: ['retail', 'store', 'shop', 'shopping', 'boutique', 'storefront'],
        default_cost: 200
      },
      mixed_use: {
        keywords: ['mixed use', 'mixed-use', 'live work', 'retail residential'],
        default_cost: 275
      }
    }
  },
  industrial: {
    keywords: ['warehouse', 'industrial', 'manufacturing', 'distribution', 'logistics'],
    subtypes: {
      warehouse: {
        keywords: ['warehouse', 'storage', 'distribution center', 'fulfillment'],
        default_cost: 150
      },
      light_industrial: {
        keywords: ['light industrial', 'flex space', 'workshop', 'light manufacturing'],
        default_cost: 175
      },
      manufacturing: {
        keywords: ['manufacturing', 'factory', 'production', 'assembly'],
        default_cost: 200
      }
    }
  },
  education: {
    keywords: ['school', 'education', 'academic', 'university', 'college', 'campus'],
    subtypes: {
      elementary_school: {
        keywords: ['elementary school', 'primary school', 'grade school', 'elementary'],
        default_cost: 275
      },
      middle_school: {
        keywords: ['middle school', 'junior high', 'intermediate school', 'middle'],
        default_cost: 285
      },
      high_school: {
        keywords: ['high school', 'secondary school', 'senior high'],
        default_cost: 325
      },
      university: {
        keywords: ['university', 'college', 'higher education', 'campus building'],
        default_cost: 385
      },
      vocational: {
        keywords: ['vocational', 'technical school', 'trade school', 'career center'],
        default_cost: 295
      },
      daycare: {
        keywords: ['daycare', 'preschool', 'childcare', 'early learning'],
        default_cost: 225
      }
    }
  }
};

// Feature detection patterns - context-aware
const FEATURE_PATTERNS: { [key: string]: string[] } = {
  // Healthcare features - only detected in healthcare context
  emergency_department: ['emergency department', 'emergency room', 'trauma center', 'emergency care'],
  operating_room: ['operating room', 'surgery suite', 'surgical suite', 'operating theater'],
  imaging: ['mri suite', 'ct scan', 'x-ray room', 'imaging center', 'radiology department'],
  pharmacy: ['pharmacy', 'dispensary', 'medication room'],
  
  // Restaurant features
  drive_through: ['drive through', 'drive-through', 'drive thru', 'drive-thru'],
  commercial_kitchen: ['commercial kitchen', 'full kitchen', 'restaurant kitchen'],
  
  // Education features
  gymnasium: ['gymnasium', 'gym', 'athletic facility', 'sports facility'],
  auditorium: ['auditorium', 'theater', 'performing arts', 'assembly hall'],
  cafeteria: ['cafeteria', 'lunch room', 'dining hall', 'food service'],
  library: ['library', 'media center', 'learning commons'],
  laboratory: ['science lab', 'laboratory', 'lab space', 'stem lab'],
  
  // General features
  pool: ['swimming pool', 'aquatic center', 'natatorium'],
  fitness_center: ['fitness center', 'workout facility', 'exercise room'],
  parking_garage: ['parking garage', 'parking structure', 'structured parking', 'parking deck']
};

// Parse square footage from various formats
function parseSquareFootage(text: string): number | null {
  const normalized = text.toLowerCase().replace(/,/g, '');
  
  // Patterns to match:
  // "200000 sf", "200000 square feet", "200k sf", "200,000 sq ft"
  const patterns = [
    /(\d+)\s*k\s*(?:sf|sq|square)/i,  // "200k sf"
    /(\d+(?:\.\d+)?)\s*(?:sf|sq\.?\s*ft\.?|square\s*feet|square\s*foot|sqft)/i,  // "200000 sf"
    /(\d+(?:,\d{3})*)\s*(?:sf|sq\.?\s*ft\.?|square\s*feet|square\s*foot|sqft)/i,  // "200,000 sf"
  ];
  
  for (let i = 0; i < patterns.length; i++) {
    const pattern = patterns[i];
    const match = normalized.match(pattern);
    if (match) {
      let value = match[1].replace(/,/g, '');
      // Handle 'k' notation - ONLY for the first pattern (index 0)
      if (i === 0 && match[0].includes('k')) {
        value = String(parseFloat(value) * 1000);
      }
      const parsed = parseInt(value);
      if (!isNaN(parsed) && parsed > 0) {
        return parsed;
      }
    }
  }
  
  return null;
}

// Parse number of stories/floors
function parseStories(text: string): number | null {
  const normalized = text.toLowerCase();
  
  const patterns = [
    /(\d+)\s*(?:story|stories|floor|floors)/i,
    /(\d+)\s*(?:-story|-stories)/i,
  ];
  
  for (const pattern of patterns) {
    const match = normalized.match(pattern);
    if (match) {
      const value = parseInt(match[1]);
      if (!isNaN(value) && value > 0 && value < 200) {  // Reasonable limit
        return value;
      }
    }
  }
  
  return null;
}

// Parse location from text
function parseLocation(text: string): string | null {
  const normalized = text.toLowerCase();
  
  // Common location patterns
  const patterns = [
    /\bin\s+([a-z\s]+(?:,\s*[a-z]{2})?)/i,  // "in Nashville" or "in Nashville, TN"
    /(?:located\s+in|location:\s*)([a-z\s]+(?:,\s*[a-z]{2})?)/i,
    /([a-z\s]+,\s*[a-z]{2})(?:\s|$)/i,  // "Nashville, TN"
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);  // Use original text for proper capitalization
    if (match) {
      return match[1].trim();
    }
  }
  
  // Check for city names at the end of the string
  const cityPattern = /\b(Nashville|Memphis|Knoxville|Chattanooga|Franklin|Murfreesboro|Boston|New York|Los Angeles|Chicago|Dallas|Houston|Atlanta|Miami|Seattle|Portland|Denver|Phoenix|San Francisco|Austin|Orlando)\b/i;
  const cityMatch = text.match(cityPattern);
  if (cityMatch) {
    return cityMatch[1];
  }
  
  return null;
}

// Detect occupancy type and subtype
function detectOccupancyType(text: string): { occupancy_type: string | null; subtype: string | null; confidence: number } {
  const normalized = text.toLowerCase();
  let bestMatch: { occupancy_type: string; subtype: string; confidence: number } | null = null;
  
  // First, try to find exact subtype matches (more specific)
  for (const [occupancyType, mapping] of Object.entries(OCCUPANCY_MAPPINGS)) {
    for (const [subtypeName, subtypeData] of Object.entries(mapping.subtypes)) {
      for (const keyword of subtypeData.keywords) {
        if (normalized.includes(keyword)) {
          const confidence = keyword.split(' ').length > 1 ? 95 : 85;  // Multi-word matches are more confident
          if (!bestMatch || confidence > bestMatch.confidence) {
            bestMatch = { occupancy_type: occupancyType, subtype: subtypeName, confidence };
          }
        }
      }
    }
  }
  
  // If no subtype match, try occupancy type keywords
  if (!bestMatch) {
    for (const [occupancyType, mapping] of Object.entries(OCCUPANCY_MAPPINGS)) {
      for (const keyword of mapping.keywords) {
        if (normalized.includes(keyword)) {
          // Default to first subtype if only occupancy type is detected
          const defaultSubtype = Object.keys(mapping.subtypes)[0];
          bestMatch = { occupancy_type: occupancyType, subtype: defaultSubtype, confidence: 70 };
          break;
        }
      }
      if (bestMatch) break;
    }
  }
  
  if (bestMatch) {
    return bestMatch;
  }
  
  return { occupancy_type: null, subtype: null, confidence: 0 };
}

// Extract features from text - context-aware based on building type
function extractFeatures(text: string, occupancyType?: string | null): string[] {
  const normalized = text.toLowerCase();
  const features: string[] = [];
  
  // Context-aware feature detection
  const healthcareFeatures = ['emergency_department', 'operating_room', 'imaging', 'pharmacy'];
  const educationFeatures = ['gymnasium', 'auditorium', 'cafeteria', 'library', 'laboratory'];
  const restaurantFeatures = ['drive_through', 'commercial_kitchen'];
  
  for (const [featureName, keywords] of Object.entries(FEATURE_PATTERNS)) {
    // Skip healthcare features unless it's a healthcare building
    if (healthcareFeatures.includes(featureName) && occupancyType !== 'healthcare') {
      continue;
    }
    
    // Skip education features unless it's an education building
    if (educationFeatures.includes(featureName) && occupancyType !== 'education') {
      continue;
    }
    
    // Skip restaurant features unless it's a restaurant
    if (restaurantFeatures.includes(featureName) && occupancyType !== 'restaurant') {
      continue;
    }
    
    for (const keyword of keywords) {
      if (normalized.includes(keyword)) {
        features.push(featureName);
        break;
      }
    }
  }
  
  // Also check for "with" or "including" patterns (with context awareness)
  const withPattern = /(?:with|including|has|features?)\s+([a-z\s,]+?)(?:\.|$|and)/gi;
  const matches = normalized.matchAll(withPattern);
  for (const match of matches) {
    const items = match[1].split(/,|and/).map(s => s.trim());
    for (const item of items) {
      // Check if this item matches any feature pattern
      for (const [featureName, keywords] of Object.entries(FEATURE_PATTERNS)) {
        // Apply same context-aware filtering
        if (healthcareFeatures.includes(featureName) && occupancyType !== 'healthcare') continue;
        if (educationFeatures.includes(featureName) && occupancyType !== 'education') continue;
        if (restaurantFeatures.includes(featureName) && occupancyType !== 'restaurant') continue;
        
        if (keywords.some(keyword => item.includes(keyword))) {
          if (!features.includes(featureName)) {
            features.push(featureName);
          }
        }
      }
    }
  }
  
  return features;
}

// Main parsing function
export function parseDescription(description: string): ParsedInput {
  if (!description) {
    return {
      square_footage: null,
      occupancy_type: null,
      subtype: null,
      features: [],
      stories: null,
      location: null,
      confidence: 0
    };
  }
  
  const squareFootage = parseSquareFootage(description);
  const { occupancy_type, subtype, confidence } = detectOccupancyType(description);
  const features = extractFeatures(description, occupancy_type);  // Pass occupancy type for context
  const stories = parseStories(description);
  const location = parseLocation(description);
  
  // Debug logging
  console.log('🔍 NLP Parse Results:', {
    input: description,
    detected: {
      square_footage: squareFootage,
      occupancy_type,
      subtype,
      features,
      stories,
      location,
      confidence: Math.round(confidence) + '%'
    }
  });
  
  return {
    square_footage: squareFootage,
    occupancy_type,
    subtype,
    features,
    stories,
    location,
    confidence
  };
}

// Export test function for verification
export function testNLPParser() {
  const testCases = [
    "200000 sf hospital with emergency department in Nashville",
    "5,000 square foot QSR with drive-through",
    "luxury apartments 150k sf with rooftop pool and gym",
    "45000 sf medical office building 3 stories",
    "fine dining restaurant 8000 sqft downtown Austin",
    "100k sf warehouse distribution center",
    "senior care facility 75000 square feet with memory care unit"
  ];
  
  console.log("=== NLP Parser Test Results ===");
  testCases.forEach(input => {
    const result = parseDescription(input);
    console.log(`\nInput: "${input}"`);
    console.log("Parsed:", result);
  });
}

// Export occupancy mappings for use in form components
export function getOccupancyTypes() {
  return Object.keys(OCCUPANCY_MAPPINGS);
}

export function getSubtypes(occupancyType: string) {
  return OCCUPANCY_MAPPINGS[occupancyType]?.subtypes 
    ? Object.keys(OCCUPANCY_MAPPINGS[occupancyType].subtypes)
    : [];
}

export function getDefaultCost(occupancyType: string, subtype: string): number | null {
  return OCCUPANCY_MAPPINGS[occupancyType]?.subtypes[subtype]?.default_cost || null;
}