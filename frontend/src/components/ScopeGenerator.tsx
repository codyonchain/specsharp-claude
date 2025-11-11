import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProject } from '@/v2/api/client';
import './ScopeGenerator.css';
import { determineOccupancyType, getProjectTypeFromOccupancy } from '../utils/buildingTypeDetection';
import ProjectTypeSelector from './ProjectTypeSelector';
import { parseDescription, ParsedInput, getOccupancyTypes, getSubtypes } from '../services/nlpService';
import { BUILDING_TYPES, getBuildingType, getSubtype, estimateFloors, getDefaultCeilingHeight } from '../config/buildingTypes';

// Enhanced type definition with clear hierarchy
interface ScopeRequest {
  project_name: string;
  project_type: 'residential' | 'commercial' | 'industrial' | 'mixed_use';  // Legacy field for compatibility
  project_classification?: 'ground_up' | 'addition' | 'renovation';
  square_footage: number;
  location: string;
  climate_zone?: string;
  num_floors?: number;
  ceiling_height?: number;
  building_type?: string;     // Primary category (healthcare, restaurant, etc.)
  building_subtype?: string;  // Specific type (hospital, qsr, etc.)
  occupancy_type?: string;    // Legacy field, maps to building_type
  subtype?: string;           // Legacy field, maps to building_subtype
  special_requirements?: string;
  budget_constraint?: number;
  building_mix?: { [key: string]: number };
  service_level?: string;
  building_features?: string[];
  finish_level?: 'basic' | 'standard' | 'premium' | 'luxury';
  finishLevel?: 'standard' | 'premium' | 'luxury';
}

function ScopeGenerator() {
  console.log('ScopeGenerator component mounted');
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inputMode, setInputMode] = useState<'natural' | 'form'>('natural');
  const [naturalLanguageInput, setNaturalLanguageInput] = useState('');
  const [classificationAutoSelected, setClassificationAutoSelected] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedInput | null>(null);
  const [inputHighlight, setInputHighlight] = useState(false);
  const [formData, setFormData] = useState<ScopeRequest>({
    project_name: '',
    project_type: 'commercial',  // Legacy field
    project_classification: 'ground_up',
    square_footage: 10000,
    location: '',
    num_floors: 1,
    ceiling_height: 10,
    building_type: '',  // New primary field
    building_subtype: '',  // New specific type field
    occupancy_type: '',  // Legacy, will map to building_type
    subtype: '',  // Legacy, will map to building_subtype
    special_requirements: '',
    finish_level: 'standard',
  });

  // Natural language parser
  const parseNaturalLanguage = (input: string): Partial<ScopeRequest> => {
    const result: Partial<ScopeRequest> = {};
    
    // Parse project classification (ground_up, addition, renovation)
    const detectProjectClassification = (text: string): 'ground_up' | 'addition' | 'renovation' => {
      const textLower = text.toLowerCase();
      
      // Check renovation keywords first (most specific)
      const renovationKeywords = [
        'renovate', 'renovation', 'remodel', 'retrofit', 'modernize',
        'update existing', 'gut renovation', 'tenant improvement',
        'ti ', ' ti,', ' ti.', 'refresh', 'refurbish', 'rehabilitate',
        'restore', 'convert', 'conversion', 'transform existing',
        'upgrade existing', 'existing space', 'existing building',
        'build-out', 'buildout', 'makeover', 'redesign', 'rehab'
      ];
      
      // Check addition keywords
      const additionKeywords = [
        'addition', 'expansion', 'extend', 'extension', 'add on',
        'add-on', 'add to existing', 'enlarge', 'expand existing',
        'expand', 'new wing', 'wing', 'building extension', 
        'square footage addition', 'add sf', 'connect to existing', 
        'attached to existing', 'annex', 'expanding'
      ];
      
      // Check ground-up keywords
      const groundUpKeywords = [
        'ground up', 'ground-up', 'new construction', 'new build',
        'empty lot', 'vacant lot', 'greenfield', 'from scratch',
        'new development', 'new building', 'construct new',
        'brand new', 'undeveloped'
      ];
      
      // Check for explicit keyword matches
      for (const keyword of renovationKeywords) {
        if (textLower.includes(keyword)) {
          return 'renovation';
        }
      }
      
      for (const keyword of additionKeywords) {
        if (textLower.includes(keyword)) {
          return 'addition';
        }
      }
      
      for (const keyword of groundUpKeywords) {
        if (textLower.includes(keyword)) {
          return 'ground_up';
        }
      }
      
      // Context-based inference if no explicit keywords found
      if (textLower.includes('existing') && !textLower.includes('add') && !textLower.includes('expand')) {
        // "existing" without "add" or "expand" suggests renovation
        return 'renovation';
      } else if (textLower.includes('new') && !textLower.includes('existing')) {
        // "new" without "existing" suggests ground-up
        return 'ground_up';
      }
      
      // Default to ground_up if uncertain
      return 'ground_up';
    };
    
    // Detect and set project classification
    result.project_classification = detectProjectClassification(input);
    
    // Parse dimensions (e.g., "150x300" or "10000 SF" or "10,000 square feet")
    const dimensionMatch = input.match(/(\d+)\s*x\s*(\d+)/i);
    const sqftMatch = input.match(/(\d+,?\d*)\s*(sf|sq\.?\s*ft\.?|square\s*feet)/i);
    
    if (dimensionMatch) {
      const width = parseInt(dimensionMatch[1]);
      const length = parseInt(dimensionMatch[2]);
      result.square_footage = width * length;
    } else if (sqftMatch) {
      result.square_footage = parseInt(sqftMatch[1].replace(/,/g, ''));
    }
    
    // Parse building types with percentages
    const buildingTypes: { [key: string]: number } = {};
    
    // First, try to match patterns like "industrial (80%)" or "60% retail"
    const percentagePatterns = [
      /(warehouse|office|retail|residential|industrial|commercial|manufacturing|facility|restaurant|kitchen|dining|school|educational|university|college)\s*\((\d+)%\)/gi,
      /(\d+)%\s+(warehouse|office|retail|residential|industrial|commercial|manufacturing|restaurant|kitchen|dining|school|educational|university|college)/gi,
      /(warehouse|office|retail|residential|industrial|commercial|manufacturing|restaurant|kitchen|dining|school|educational|university|college)\s+(\d+)%/gi
    ];
    
    let hasPercentages = false;
    let totalPercentage = 0;
    
    // Try each pattern to find percentages
    for (const pattern of percentagePatterns) {
      let match;
      while ((match = pattern.exec(input)) !== null) {
        let type, percentage;
        if (match[1] && isNaN(parseInt(match[1]))) {
          // Pattern like "industrial (80%)"
          type = match[1].toLowerCase();
          percentage = parseInt(match[2]);
        } else {
          // Pattern like "60% retail"
          percentage = parseInt(match[1]);
          type = match[2].toLowerCase();
        }
        
        // Normalize type names
        if (type === 'manufacturing' || type === 'facility') {
          type = 'industrial';
        }
        // Handle restaurant-related terms
        if (type === 'kitchen' || type === 'dining') {
          type = 'restaurant';
        }
        // Handle educational-related terms
        if (type === 'school' || type === 'educational' || type === 'university' || 
            type === 'college' || type === 'classroom' || type === 'academy') {
          type = 'educational';
        }
        
        buildingTypes[type] = percentage;
        totalPercentage += percentage;
        hasPercentages = true;
      }
    }
    
    // Look for patterns like "manufacturing facility with 25% office space"
    if (hasPercentages && totalPercentage < 100) {
      // Find building types mentioned without percentages
      const simpleTypePattern = /(warehouse|office|retail|residential|industrial|commercial|manufacturing|facility|restaurant|kitchen|dining)(?:\s+(?:space|building|area|facility|room))?/gi;
      let typeMatch;
      
      while ((typeMatch = simpleTypePattern.exec(input)) !== null) {
        let type = typeMatch[1].toLowerCase();
        if (type === 'manufacturing' || type === 'facility') {
          type = 'industrial';
        }
        // Handle restaurant-related terms
        if (type === 'kitchen' || type === 'dining') {
          type = 'restaurant';
        }
        // Handle educational-related terms
        if (type === 'school' || type === 'educational' || type === 'university' || 
            type === 'college' || type === 'classroom' || type === 'academy') {
          type = 'educational';
        }
        // If this type doesn't have a percentage assigned yet
        if (!buildingTypes[type]) {
          buildingTypes[type] = 100 - totalPercentage;
          totalPercentage = 100;
          break;
        }
      }
    }
    
    // If no percentages found, look for building types without percentages
    if (!hasPercentages) {
      const simpleTypePattern = /(warehouse|office|retail|residential|industrial|commercial|manufacturing|facility|restaurant|kitchen|dining|school|educational|university|college|classroom|academy)(?:\s+(?:space|building|area|room|facility))?/gi;
      let typeMatch;
      const foundTypes: string[] = [];
      
      while ((typeMatch = simpleTypePattern.exec(input)) !== null) {
        let type = typeMatch[1].toLowerCase();
        if (type === 'manufacturing' || type === 'facility') {
          type = 'industrial';
        }
        // Handle restaurant-related terms
        if (type === 'kitchen' || type === 'dining') {
          type = 'restaurant';
        }
        // Handle educational-related terms
        if (type === 'school' || type === 'educational' || type === 'university' || 
            type === 'college' || type === 'classroom' || type === 'academy') {
          type = 'educational';
        }
        if (!foundTypes.includes(type)) {
          foundTypes.push(type);
        }
      }
      
      // If multiple types found without percentages, assume equal distribution
      if (foundTypes.length > 1) {
        const equalPercentage = Math.floor(100 / foundTypes.length);
        foundTypes.forEach((type, index) => {
          // Give any remainder to the first type
          buildingTypes[type] = index === 0 ? equalPercentage + (100 % foundTypes.length) : equalPercentage;
        });
        totalPercentage = 100;
      } else if (foundTypes.length === 1) {
        buildingTypes[foundTypes[0]] = 100;
        totalPercentage = 100;
      }
    }
    
    // Determine primary project type
    if (Object.keys(buildingTypes).length > 0) {
      if (Object.keys(buildingTypes).length > 1) {
        result.project_type = 'mixed_use';
        // Add building mix to special requirements
        const mixDescription = Object.entries(buildingTypes)
          .map(([type, pct]) => `${type} (${pct}%)`)
          .join(', ');
        result.special_requirements = `Building mix: ${mixDescription}`;
        // Normalize percentages to fractions and add to building_mix
        const normalizedMix: { [key: string]: number } = {};
        Object.entries(buildingTypes).forEach(([type, pct]) => {
          normalizedMix[type] = pct / 100;
        });
        result.building_mix = normalizedMix;
        
        // Set occupancy type to the dominant type
        const dominantType = Object.entries(buildingTypes).reduce((a, b) => 
          b[1] > a[1] ? b : a
        )[0];
        result.occupancy_type = dominantType;
      } else {
        const primaryType = Object.keys(buildingTypes)[0];
        result.project_type = primaryType === 'warehouse' ? 'industrial' : 
                            primaryType === 'office' ? 'commercial' : 
                            primaryType === 'industrial' ? 'industrial' :
                            primaryType === 'retail' ? 'commercial' :
                            primaryType === 'restaurant' ? 'commercial' :
                            primaryType === 'educational' ? 'commercial' :
                            primaryType === 'residential' ? 'residential' :
                            'commercial';
        result.occupancy_type = primaryType;
      }
    }
    
    // Parse location (state names or city, state format)
    const stateMap: { [key: string]: string } = {
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
      'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC', 'dc': 'DC'
    };
    
    // Common city names to look for
    const knownCities = [
      'Nashville', 'Memphis', 'Knoxville', 'Chattanooga', 'Franklin', 'Murfreesboro', // TN
      'Boston', 'Cambridge', 'Worcester', 'Springfield', // MA
      'Manchester', 'Nashua', 'Concord', // NH
      'New York', 'Brooklyn', 'Buffalo', 'Rochester', // NY
      'Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'San Jose', // CA
      'Chicago', 'Aurora', 'Rockford', // IL
      'Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth', // TX
      'Phoenix', 'Tucson', 'Mesa', // AZ
      'Philadelphia', 'Pittsburgh', // PA
      'Detroit', 'Grand Rapids', // MI
      'Seattle', 'Spokane', 'Tacoma', // WA
      'Denver', 'Colorado Springs', // CO
      'Atlanta', 'Augusta', 'Columbus', // GA
      'Miami', 'Orlando', 'Tampa', 'Jacksonville', // FL
      'Portland', 'Eugene', // OR
      'Las Vegas', 'Henderson', 'Reno', // NV
      'Milwaukee', 'Madison', // WI
      'Minneapolis', 'St. Paul', // MN
    ];
    
    // First, try to find known cities
    for (const city of knownCities) {
      const cityRegex = new RegExp(`\b${city}\b`, 'i');
      if (cityRegex.test(input)) {
        // Try to find the state context
        const cityLower = city.toLowerCase();
        
        // Map cities to their states
        const cityStateMap: { [key: string]: string } = {
          'nashville': 'TN', 'memphis': 'TN', 'knoxville': 'TN', 'chattanooga': 'TN', 'franklin': 'TN', 'murfreesboro': 'TN',
          'boston': 'MA', 'cambridge': 'MA', 'worcester': 'MA', 'springfield': 'MA',
          'manchester': 'NH', 'nashua': 'NH', 'concord': 'NH',
          'new york': 'NY', 'brooklyn': 'NY', 'buffalo': 'NY', 'rochester': 'NY',
          'los angeles': 'CA', 'san francisco': 'CA', 'san diego': 'CA', 'sacramento': 'CA', 'san jose': 'CA',
          'chicago': 'IL', 'aurora': 'IL', 'rockford': 'IL',
          'houston': 'TX', 'dallas': 'TX', 'austin': 'TX', 'san antonio': 'TX', 'fort worth': 'TX',
          'phoenix': 'AZ', 'tucson': 'AZ', 'mesa': 'AZ',
          'philadelphia': 'PA', 'pittsburgh': 'PA',
          'detroit': 'MI', 'grand rapids': 'MI',
          'seattle': 'WA', 'spokane': 'WA', 'tacoma': 'WA',
          'denver': 'CO', 'colorado springs': 'CO',
          'atlanta': 'GA', 'augusta': 'GA', 'columbus': 'GA',
          'miami': 'FL', 'orlando': 'FL', 'tampa': 'FL', 'jacksonville': 'FL',
          'portland': 'OR', 'eugene': 'OR',
          'las vegas': 'NV', 'henderson': 'NV', 'reno': 'NV',
          'milwaukee': 'WI', 'madison': 'WI',
          'minneapolis': 'MN', 'st. paul': 'MN',
        };
        
        const stateCode = cityStateMap[cityLower];
        if (stateCode) {
          result.location = `${city}, ${stateCode}`;
          break;
        }
      }
    };
    
    // If no known city found, look for state names with potential city
    if (!result.location) {
      for (const [stateName, stateCode] of Object.entries(stateMap)) {
        if (input.toLowerCase().includes(stateName)) {
          // Try multiple patterns to extract city name
          const patterns = [
            // Pattern 1: "in [city], [state]" (with comma)
            new RegExp(`\\bin\\s+([A-Za-z\\s]+?),\\s*${stateName.replace(/\s+/g, '\\s+')}`, 'i'),
            // Pattern 2: "in [city] [state]" (without comma)
            new RegExp(`\\bin\\s+([A-Za-z\\s]+?)\\s+${stateName.replace(/\s+/g, '\\s+')}`, 'i'),
          ];
          
          let cityMatch = null;
          for (const pattern of patterns) {
            const match = pattern.exec(input);
            if (match && match[1].trim()) {
              const cityPart = match[1].trim();
              // More strict validation - exclude common building-related words
              const excludeWords = /\b(sf|sqft|square|feet|floor|story|building|restaurant|office|warehouse|retail|commercial|industrial|residential|kitchen|dining|room|space|with|and|or|surgical|surgery|center|hospital|clinic|medical)\b/i;
              // Split by spaces and filter out building-related words
              const words = cityPart.split(/\s+/).filter(word => !excludeWords.test(word));
              if (words.length > 0 && !/\d/.test(words.join(' '))) {
                cityMatch = words.join(' ');
                break;
              }
            }
          }
          
          if (cityMatch) {
            // Capitalize the city properly
            const formattedCity = cityMatch.split(' ').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            ).join(' ');
            result.location = `${formattedCity}, ${stateCode}`;
          } else {
            // No city found, just use state with proper capitalization
            const formattedState = stateName.split(' ').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            ).join(' ');
            result.location = `${formattedState}, ${stateCode}`;
          }
          break;
        }
      }
    }
    
    // Look for city, state code pattern (e.g., "in Boston, MA")
    if (!result.location) {
      const cityStateCodeMatch = input.match(/\bin\s+([A-Za-z][A-Za-z\s]*?),\s*([A-Z]{2})\b/);
      if (cityStateCodeMatch) {
        const city = cityStateCodeMatch[1].trim();
        const stateCode = cityStateCodeMatch[2];
        // Verify it's a valid state code
        const validStateCodes = Object.values(stateMap);
        if (validStateCodes.includes(stateCode)) {
          result.location = `${city}, ${stateCode}`;
        }
      }
    }
    
    // Look for state codes with optional city (e.g., "Portland OR", "in TX")
    if (!result.location) {
      // First try: "[city] [state code]" pattern
      const cityStateCodePattern = /\b([A-Za-z][A-Za-z\s]*?)\s+([A-Z]{2})\b/;
      const cityStateMatch = cityStateCodePattern.exec(input);
      if (cityStateMatch) {
        const potentialCity = cityStateMatch[1].trim();
        const stateCode = cityStateMatch[2];
        const validStateCodes = Object.values(stateMap);
        if (validStateCodes.includes(stateCode)) {
          // Check if potential city is not a building-related term
          const excludeWords = /^(sf|sqft|square|feet|floor|story|building|restaurant|office|warehouse|retail|commercial|industrial|residential|kitchen|dining|room|space|with|and|or|in)$/i;
          const cityWords = potentialCity.split(/\s+/).filter(word => !excludeWords.test(word));
          if (cityWords.length > 0 && !/\d/.test(cityWords.join(' '))) {
            const city = cityWords.join(' ');
            result.location = `${city.split(' ').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            ).join(' ')}, ${stateCode}`;
          } else {
            // Just state code, no valid city
            const stateName = Object.entries(stateMap).find(([name, code]) => code === stateCode)?.[0];
            if (stateName) {
              result.location = `${stateName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}, ${stateCode}`;
            }
          }
        }
      }
      
      // Fallback: just state code with "in" prefix
      if (!result.location) {
        const stateCodeMatch = input.match(/\bin\s+([A-Z]{2})\b/);
        if (stateCodeMatch) {
          const stateCode = stateCodeMatch[1];
          const validStateCodes = Object.values(stateMap);
          if (validStateCodes.includes(stateCode)) {
            const stateName = Object.entries(stateMap).find(([name, code]) => code === stateCode)?.[0];
            if (stateName) {
              result.location = `${stateName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}, ${stateCode}`;
            }
          }
        }
      }
    }
    
    // Parse special requirements
    const requirements: string[] = [];
    if (input.toLowerCase().includes('hvac')) requirements.push('HVAC system');
    if (input.toLowerCase().includes('bathroom')) requirements.push('Bathrooms');
    if (input.toLowerCase().includes('commercial kitchen')) {
      requirements.push('Commercial kitchen');
    } else if (input.toLowerCase().includes('kitchen')) {
      requirements.push('Kitchen facilities');
    }
    if (input.toLowerCase().includes('dining')) requirements.push('Dining area');
    if (input.toLowerCase().includes('bar')) requirements.push('Bar area');
    if (input.toLowerCase().includes('parking')) requirements.push('Parking');
    if (input.toLowerCase().includes('elevator')) requirements.push('Elevators');
    if (input.toLowerCase().includes('dock door')) requirements.push('Multiple dock doors');
    if (input.toLowerCase().includes('loading dock')) requirements.push('Loading docks');
    if (input.toLowerCase().includes('crane')) requirements.push('Overhead crane');
    if (input.toLowerCase().includes('high ceiling') || input.toLowerCase().includes('clear height')) {
      requirements.push('High ceilings');
    }
    
    if (requirements.length > 0) {
      const existingReqs = result.special_requirements || '';
      // If we already have building mix in special requirements, append other requirements
      if (existingReqs.includes('Building mix:')) {
        result.special_requirements = `${existingReqs}, ${requirements.join(', ')}`;
      } else {
        result.special_requirements = existingReqs 
          ? `${existingReqs}. ${requirements.join(', ')}`
          : requirements.join(', ');
      }
    }
    
    // Ensure location is properly set and not the full input
    if (!result.location || result.location.toLowerCase() === input.toLowerCase()) {
      // If no location was found or it's the full input, try to extract just city and state
      const cityStatePattern = /(?:in\s+)?([A-Za-z\s]+?),?\s*(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)/i;
      const locationMatch = cityStatePattern.exec(input);
      if (locationMatch) {
        const city = locationMatch[1].trim();
        const state = locationMatch[2];
        // Get state code if full state name provided
        const stateCode = stateMap[state.toLowerCase()] || state;
        result.location = `${city.split(' ').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ')}, ${stateCode}`;
      } else {
        // Clear location if it was set to the full input
        result.location = '';
      }
    }
    
    // Parse floors with comprehensive patterns
    const floorPatterns = [
      // Pattern 1: "X stories" or "X story" or "X-story"
      /(\d+)\s*stor(?:ies|ey|y)/i,
      /(\d+)[-\s]stor(?:ies|ey|y)/i,
      /(\d+)\s*floor\s*stor(?:ies|ey|y)/i,
      // Pattern 2: "X floors" or "X floor" or "X-floor"
      /(\d+)\s*floors?/i,
      /(\d+)[-\s]floors?/i,
      /(\d+)\s*floor\s*building/i,
      // Pattern 3: "X levels" or "X-level"
      /(\d+)\s*levels?/i,
      /(\d+)[-\s]levels?/i,
    ];
    
    let floorsFound = false;
    for (const pattern of floorPatterns) {
      const match = input.match(pattern);
      if (match) {
        result.num_floors = parseInt(match[1]);
        floorsFound = true;
        break;
      }
    }
    
    // Check for word numbers
    if (!floorsFound) {
      const wordToNumber: { [key: string]: number } = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
      };
      
      for (const [word, num] of Object.entries(wordToNumber)) {
        const wordPatterns = [
          new RegExp(`${word}\\s*stor(?:ies|ey|y)`, 'i'),
          new RegExp(`${word}[-\\s]stor(?:ies|ey|y)`, 'i'),
          new RegExp(`${word}\\s*floors?`, 'i'),
          new RegExp(`${word}[-\\s]floors?`, 'i'),
        ];
        
        for (const pattern of wordPatterns) {
          if (pattern.test(input)) {
            result.num_floors = num;
            floorsFound = true;
            break;
          }
        }
        if (floorsFound) break;
      }
    }
    
    // Check for multi-story indicators
    if (!floorsFound) {
      const multiPatterns = ['multi-story', 'multistory', 'multi-floor', 'multilevel', 'multi-level'];
      if (multiPatterns.some(term => input.toLowerCase().includes(term))) {
        result.num_floors = 2; // Conservative default
      }
    }
    
    // Check for tall building indicators
    if (!floorsFound) {
      const tallPatterns = ['high-rise', 'highrise', 'tower', 'tall building', 'skyscraper'];
      if (tallPatterns.some(term => input.toLowerCase().includes(term))) {
        result.num_floors = input.toLowerCase().includes('office') ? 10 : 5;
      }
    }
    
    // Parse restaurant service levels
    if (result.occupancy_type === 'restaurant' || 
        (result.building_mix && Object.keys(result.building_mix).includes('restaurant'))) {
      if (input.toLowerCase().includes('quick service') || 
          input.toLowerCase().includes('fast food') || 
          input.toLowerCase().includes('qsr')) {
        result.service_level = 'quick_service';
      } else if (input.toLowerCase().includes('casual dining') || 
                 input.toLowerCase().includes('family restaurant')) {
        result.service_level = 'casual_dining';
      } else if (input.toLowerCase().includes('fine dining') || 
                 input.toLowerCase().includes('upscale') || 
                 input.toLowerCase().includes('white tablecloth')) {
        result.service_level = 'fine_dining';
      } else if (input.toLowerCase().includes('full service') || 
                 input.toLowerCase().includes('full-service')) {
        result.service_level = 'full_service';
      }
      
      // Parse restaurant features
      const restaurantFeatures: string[] = [];
      if (input.toLowerCase().includes('commercial kitchen') || input.toLowerCase().includes('kitchen')) {
        restaurantFeatures.push('commercial_kitchen');
      }
      if (input.toLowerCase().includes('bar') || input.toLowerCase().includes('tavern') || input.toLowerCase().includes('pub')) {
        restaurantFeatures.push('full_bar');
      }
      if (input.toLowerCase().includes('outdoor') || input.toLowerCase().includes('patio') || input.toLowerCase().includes('terrace')) {
        restaurantFeatures.push('outdoor_dining');
      }
      if (input.toLowerCase().includes('drive-thru') || input.toLowerCase().includes('drive thru')) {
        restaurantFeatures.push('drive_thru');
      }
      if (input.toLowerCase().includes('wine cellar') || input.toLowerCase().includes('wine storage')) {
        restaurantFeatures.push('wine_cellar');
      }
      if (input.toLowerCase().includes('premium') || input.toLowerCase().includes('luxury') || input.toLowerCase().includes('high-end')) {
        restaurantFeatures.push('premium_finishes');
      }
      
      if (restaurantFeatures.length > 0) {
        result.building_features = restaurantFeatures;
      }
    }
    
    // Generate a smart project name based on parsed details
    if (!result.project_name) {
      // Build a descriptive name from the components we found
      const parts = [];
      
      // Add project classification if not ground-up
      if (result.project_classification === 'renovation') {
        parts.push('Renovation:');
      } else if (result.project_classification === 'addition') {
        parts.push('Addition:');
      }
      
      // Add square footage if available
      if (result.square_footage) {
        parts.push(`${result.square_footage.toLocaleString()} SF`);
      }
      
      // Add occupancy type
      if (result.occupancy_type) {
        const typeMap: {[key: string]: string} = {
          'office': 'Office',
          'retail': 'Retail',
          'restaurant': 'Restaurant',
          'warehouse': 'Warehouse',
          'medical': 'Medical',
          'hospital': 'Hospital',
          'surgical_center': 'Surgical Center',
          'clinic': 'Clinic',
          'urgent_care': 'Urgent Care',
          'school': 'School',
          'residential': 'Residential',
          'mixed_use': 'Mixed-Use'
        };
        parts.push(typeMap[result.occupancy_type] || result.occupancy_type);
      } else if (result.project_type) {
        parts.push(result.project_type.charAt(0).toUpperCase() + result.project_type.slice(1));
      }
      
      // Add location if available
      if (result.location) {
        parts.push('-');
        parts.push(result.location.split(',')[0]); // Just city name
      }
      
      result.project_name = parts.join(' ');
    }
    
    // Parse finish level
    if (input.toLowerCase().includes('basic finish') || 
        input.toLowerCase().includes('economy') || 
        input.toLowerCase().includes('budget finish')) {
      result.finish_level = 'basic';
    } else if (input.toLowerCase().includes('premium finish') || 
               input.toLowerCase().includes('luxury') || 
               input.toLowerCase().includes('high-end finish') ||
               input.toLowerCase().includes('high end finish')) {
      result.finish_level = 'premium';
    } else if (input.toLowerCase().includes('standard finish')) {
      result.finish_level = 'standard';
    }
    
    return result;
  };

  // Real-time NLP parsing as user types
  useEffect(() => {
    if (naturalLanguageInput && inputMode === 'natural') {
      const parsed = parseDescription(naturalLanguageInput);
      setParsedData(parsed);
      
      // Auto-populate form fields based on NLP parsing
      const updatedFormData = { ...formData };
      
      if (parsed.square_footage) {
        console.log('🔍 NLP parsed square footage:', parsed.square_footage);
        updatedFormData.square_footage = parsed.square_footage;
      }
      
      if (parsed.occupancy_type && parsed.subtype) {
        updatedFormData.building_type = parsed.occupancy_type;
        updatedFormData.building_subtype = parsed.subtype;
        // Legacy fields for compatibility
        updatedFormData.occupancy_type = parsed.occupancy_type;
        updatedFormData.subtype = parsed.subtype;
        // Map to project type for backward compatibility
        updatedFormData.project_type = parsed.occupancy_type === 'residential' ? 'residential' :
                                       parsed.occupancy_type === 'industrial' ? 'industrial' :
                                       'commercial';
        
        // Auto-estimate floors if we have square footage and building type
        // Only if user hasn't explicitly provided floors
        if (!parsed.stories && updatedFormData.square_footage) {
          const estimatedFloors = estimateFloors(
            updatedFormData.square_footage,
            parsed.occupancy_type,
            parsed.subtype
          );
          console.log('🏢 NLP Auto-estimating floors:', {
            squareFootage: updatedFormData.square_footage,
            occupancyType: parsed.occupancy_type,
            subtype: parsed.subtype,
            estimatedFloors: estimatedFloors
          });
          updatedFormData.num_floors = estimatedFloors;
        }
        
        // Auto-set ceiling height
        updatedFormData.ceiling_height = getDefaultCeilingHeight(parsed.occupancy_type, parsed.subtype);
      }
      
      if (parsed.location) {
        updatedFormData.location = parsed.location;
      }
      
      if (parsed.stories) {
        updatedFormData.num_floors = parsed.stories;
      }
      
      if (parsed.features.length > 0) {
        updatedFormData.building_features = parsed.features;
      }
      
      setFormData(updatedFormData);
    }
  }, [naturalLanguageInput, inputMode]);

  // Track if user has manually changed floors
  const [userChangedFloors, setUserChangedFloors] = useState(false);

  // Handle example prompt click
  const handleExampleClick = (prompt: string) => {
    // Remove quotes and bullet points from the prompt
    const cleanPrompt = prompt.replace(/^[•"]/g, '').replace(/"$/g, '').trim();
    
    // Set the input and parse it immediately
    setNaturalLanguageInput(cleanPrompt);
    
    // Parse the description to get building info
    const parsed = parseDescription(cleanPrompt);
    setParsedData(parsed);
    
    // Highlight the input field briefly
    setInputHighlight(true);
    setTimeout(() => setInputHighlight(false), 500);
    
    // Scroll to the input field
    const inputElement = document.querySelector('.natural-language-input');
    if (inputElement) {
      inputElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const handleNaturalLanguageSubmit = (submitImmediately = false) => {
    // Use the already parsed data from NLP service
    const enhancedParsed = parsedData || parseDescription(naturalLanguageInput);
    
    // Also use the old parser for additional data (like project classification)
    const legacyParsed = parseNaturalLanguage(naturalLanguageInput);
    
    // Combine both parsers' results
    const parsed = {
      ...legacyParsed,
      occupancy_type: enhancedParsed.occupancy_type || legacyParsed.occupancy_type,
      subtype: enhancedParsed.subtype,
      square_footage: enhancedParsed.square_footage || legacyParsed.square_footage,
      location: enhancedParsed.location || legacyParsed.location,
      num_floors: enhancedParsed.stories || legacyParsed.num_floors,
      building_features: enhancedParsed.features
    };
    
    console.log('Natural language input:', naturalLanguageInput);
    console.log('NLP Parsed result:', enhancedParsed);
    console.log('Combined result:', parsed);
    console.log('Detected occupancy type:', parsed.occupancy_type, 'subtype:', parsed.subtype);
    console.log('Detected project classification:', parsed.project_classification);
    
    // If no occupancy type was detected, use the building type detection utility
    if (!parsed.occupancy_type) {
      parsed.occupancy_type = determineOccupancyType(naturalLanguageInput);
      console.log('Fallback detected occupancy type:', parsed.occupancy_type);
    }
    
    // Include the natural language input for backend smart naming
    const updatedFormData = {
      ...formData,
      ...parsed,
      // Let backend generate smart name if not provided
      project_name: parsed.project_name || formData.project_name,
      location: parsed.location || formData.location || 'Nashville, Tennessee',
      square_footage: parsed.square_footage || formData.square_footage || 10000,
      // Map stories to num_floors if present
      num_floors: parsed.stories || formData.num_floors || 1,
      // Pass natural language for backend processing
      special_requirements: naturalLanguageInput,
    };
    
    // Safety check: ensure location is not the full input
    if (updatedFormData.location && 
        (updatedFormData.location.toLowerCase().includes('restaurant') ||
         updatedFormData.location.toLowerCase().includes('building') ||
         updatedFormData.location.toLowerCase().includes('kitchen') ||
         updatedFormData.location.length > 50)) {
      console.warn('Location appears to contain full description, clearing it');
      updatedFormData.location = '';
    }
    
    console.log('Updated form data:', updatedFormData);
    
    setFormData(updatedFormData);
    
    // Trigger visual feedback for auto-selected classification
    if (parsed.project_classification) {
      setClassificationAutoSelected(true);
      // Remove highlight after animation
      setTimeout(() => setClassificationAutoSelected(false), 3000);
    }
    
    // If submitImmediately is true, submit the form directly
    if (submitImmediately) {
      return updatedFormData;
    }
    
    // Otherwise switch to form mode to show parsed results
    setInputMode('form');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // If in natural language mode, just parse and switch to form view
    if (inputMode === 'natural' && naturalLanguageInput) {
      handleNaturalLanguageSubmit(false);
      return; // Don't submit yet, let user review the form
    }
    
    // We're in form mode, proceed with submission
    const submitData = formData;
    
    setLoading(true);
    setError('');

    // Parse building mix from special requirements if it's a mixed_use project
    const finalFormData = { ...submitData };
    if (submitData.project_type === 'mixed_use' && submitData.special_requirements && !submitData.building_mix) {
      const parsedData = parseNaturalLanguage(submitData.special_requirements);
      if (parsedData.building_mix) {
        finalFormData.building_mix = parsedData.building_mix;
        console.log('Extracted building mix from special requirements:', parsedData.building_mix);
      }
    }
    
    // Remove empty project_name to let backend auto-generate it
    if (!finalFormData.project_name || finalFormData.project_name.trim() === '') {
      delete finalFormData.project_name;
    }

    const finishSource = finalFormData.finishLevel || finalFormData.finish_level || 'standard';
    const normalizedFinish = typeof finishSource === 'string' ? finishSource.toLowerCase() : 'standard';
    finalFormData.finishLevel = normalizedFinish.charAt(0).toUpperCase() + normalizedFinish.slice(1);
    finalFormData.finish_level = normalizedFinish as ScopeRequest['finish_level'];

    console.log('Submitting form data:', finalFormData);
    console.log('📏 Square footage being submitted:', finalFormData.square_footage);

    try {
      const derivedDescription = (
        finalFormData.special_requirements ||
        naturalLanguageInput ||
        finalFormData.project_name ||
        ''
      ).trim() || 'SpecSharp Project';
      const derivedLocation = finalFormData.location?.trim() || undefined;
      const derivedSquareFootage = typeof finalFormData.square_footage === 'number'
        ? finalFormData.square_footage
        : undefined;
      const derivedFinishLevel = (finalFormData.finishLevel || finalFormData.finish_level)
        ? finalFormData.finishLevel
        : undefined;
      const derivedProjectClass = finalFormData.project_classification || undefined;
      const derivedSpecialFeatures = finalFormData.building_features || [];

      const { id } = await createProject({
        description: derivedDescription,
        location: derivedLocation,
        squareFootage: derivedSquareFootage,
        finishLevel: derivedFinishLevel,
        projectClass: derivedProjectClass,
        specialFeatures: derivedSpecialFeatures,
      });

      console.debug('[TRACE save:legacy->server]', { source: 'ScopeGenerator.tsx:925', id });
      navigate(`/project/${id}`);
    } catch (err: any) {
      console.error('Scope generation error:', err);
      let errorMessage = 'Failed to generate scope';

      const detail = err?.details || err?.response?.data;
      if (detail?.detail) {
        if (Array.isArray(detail.detail)) {
          errorMessage = detail.detail.map((e: any) => `${e.loc?.join?.(' → ') || ''}: ${e.msg || e.message || ''}`).join('\n');
        } else {
          errorMessage = detail.detail;
        }
      } else if (typeof detail === 'string') {
        errorMessage = detail;
      } else if (err?.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    if (name === 'square_footage') {
      // If empty, keep the existing value or default
      const parsedValue = value ? parseFloat(value) : formData.square_footage;
      console.log(`📐 Square footage input: "${value}" → parsed: ${parsedValue}`);
      setFormData({
        ...formData,
        square_footage: parsedValue
      });
      // Reset user floor change flag when square footage changes
      setUserChangedFloors(false);
    } else if (name === 'num_floors') {
      const parsedValue = parseFloat(value) || 1;  // Default to 1, not 0!
      setFormData({
        ...formData,
        num_floors: parsedValue
      });
      // Mark that user has manually changed floors
      setUserChangedFloors(true);
    } else {
      setFormData({
        ...formData,
        [name]: name === 'ceiling_height' 
          ? parseFloat(value) || 10  // Default ceiling height to 10
          : name === 'budget_constraint'
          ? parseFloat(value) || undefined  // Budget can be empty
          : value,
      });
    }
  };

  // Add a try-catch for the render to catch any rendering errors
  try {
    return (
      <div className="scope-generator">
        <header className="page-header">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          ← Back to Dashboard
        </button>
        <h1>Create New Scope</h1>
      </header>

      <div className="input-mode-toggle">
        <button 
          className={`mode-btn ${inputMode === 'natural' ? 'active' : ''}`}
          onClick={() => setInputMode('natural')}
        >
          Natural Language
        </button>
        <button 
          className={`mode-btn ${inputMode === 'form' ? 'active' : ''}`}
          onClick={() => setInputMode('form')}
        >
          Form Input
        </button>
      </div>

      {inputMode === 'natural' ? (
        <form onSubmit={handleSubmit} className="scope-form">
          <div className="form-section">
            <h2>Describe Your Project</h2>
            <div className="help-text">
              <p>Describe your building project in natural language. Include whether it's new construction, renovation, or addition:</p>
              
              <div className="example-prompts-section">
                <strong>New Construction (Ground-Up):</strong>
                <div className="example-prompt" onClick={() => handleExampleClick('New 200000 sf 5 story regional hospital with emergency department, 12 operating rooms, and 150 beds in Nashville, TN')}>
                  • "New 200000 sf 5 story regional hospital with emergency department, 12 operating rooms, and 150 beds in Nashville, TN"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Build 180000 sf 8 story luxury apartment complex with 120 units, rooftop pool, and underground parking in Boston, MA')}>
                  • "Build 180000 sf 8 story luxury apartment complex with 120 units, rooftop pool, and underground parking in Boston, MA"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('New 250000 sf 15 story Class A office tower with trading floors, executive suites, and fitness center in Chicago, IL')}>
                  • "New 250000 sf 15 story Class A office tower with trading floors, executive suites, and fitness center in Chicago, IL"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Ground-up 400000 sf distribution center with 40 foot clear height, 50 loading docks, and automated sorting in Memphis, TN')}>
                  • "Ground-up 400000 sf distribution center with 40 foot clear height, 50 loading docks, and automated sorting in Memphis, TN"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('New 150000 sf 3 story high school for 1200 students with gymnasium, auditorium, and STEM labs in Denver, CO')}>
                  • "New 150000 sf 3 story high school for 1200 students with gymnasium, auditorium, and STEM labs in Denver, CO"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Build 100000 sf 2 story Tier 3 data center with redundant power, 20MW capacity, and secure cages in Phoenix, AZ')}>
                  • "Build 100000 sf 2 story Tier 3 data center with redundant power, 20MW capacity, and secure cages in Phoenix, AZ"
                </div>
              </div>

              <div className="example-prompts-section">
                <strong>Renovations (Existing Buildings):</strong>
                <div className="example-prompt" onClick={() => handleExampleClick('Renovate 200 room 12 story downtown hotel including lobby, restaurant, conference center, and guest rooms in Atlanta, GA')}>
                  • "Renovate 200 room 12 story downtown hotel including lobby, restaurant, conference center, and guest rooms in Atlanta, GA"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Remodel 85000 sf strip shopping center with new facades, common areas, and anchor tenant space in Dallas, TX')}>
                  • "Remodel 85000 sf strip shopping center with new facades, common areas, and anchor tenant space in Dallas, TX"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Convert 120000 sf 4 story assisted living facility to memory care with secured units and therapy spaces in Sacramento, CA')}>
                  • "Convert 120000 sf 4 story assisted living facility to memory care with secured units and therapy spaces in Sacramento, CA"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Renovate 8000 sf full service restaurant with commercial kitchen, bar, private dining, and outdoor patio in Nashville, TN')}>
                  • "Renovate 8000 sf full service restaurant with commercial kitchen, bar, private dining, and outdoor patio in Nashville, TN"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Modernize 150000 sf 2 story manufacturing facility with clean rooms, automated production lines, and QC labs in Detroit, MI')}>
                  • "Modernize 150000 sf 2 story manufacturing facility with clean rooms, automated production lines, and QC labs in Detroit, MI"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Renovate 45000 sf 3 story medical office building for multi-specialty clinic with imaging center in Manchester, NH')}>
                  • "Renovate 45000 sf 3 story medical office building for multi-specialty clinic with imaging center in Manchester, NH"
                </div>
              </div>

              <div className="example-prompts-section">
                <strong>Additions (Expanding Buildings):</strong>
                <div className="example-prompt" onClick={() => handleExampleClick('Add 350000 sf 20 story mixed use tower with ground floor retail, 15 floors offices, and 100 apartments in Seattle, WA')}>
                  • "Add 350000 sf 20 story mixed use tower with ground floor retail, 15 floors offices, and 100 apartments in Seattle, WA"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Expand campus with 80000 sf 4 story science building containing research labs, lecture halls, and collaboration spaces in Austin, TX')}>
                  • "Expand campus with 80000 sf 4 story science building containing research labs, lecture halls, and collaboration spaces in Austin, TX"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Add 150000 sf 8 story hotel tower with 200 rooms, spa, conference facilities, and restaurants in Orlando, FL')}>
                  • "Add 150000 sf 8 story hotel tower with 200 rooms, spa, conference facilities, and restaurants in Orlando, FL"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Expand headquarters with 175000 sf 6 story office building including cafeteria, fitness center, and parking garage in San Francisco, CA')}>
                  • "Expand headquarters with 175000 sf 6 story office building including cafeteria, fitness center, and parking garage in San Francisco, CA"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Add 300000 sf fulfillment center expansion with robotics, multi-level mezzanines, and shipping hub in Columbus, OH')}>
                  • "Add 300000 sf fulfillment center expansion with robotics, multi-level mezzanines, and shipping hub in Columbus, OH"
                </div>
                <div className="example-prompt" onClick={() => handleExampleClick('Build 60000 sf 3 story biotech laboratory addition with BSL-3 labs, vivarium, and cGMP manufacturing in Cambridge, MA')}>
                  • "Build 60000 sf 3 story biotech laboratory addition with BSL-3 labs, vivarium, and cGMP manufacturing in Cambridge, MA"
                </div>
              </div>
            </div>
            
            <div className="form-group">
              <textarea
                value={naturalLanguageInput}
                onChange={(e) => setNaturalLanguageInput(e.target.value)}
                placeholder="Example: 50,000 sf office building in Manchester, New Hampshire"
                rows={6}
                className={`natural-language-input ${inputHighlight ? 'highlight' : ''}`}
                required
              />
            </div>
            
            {/* Visual feedback for detected values */}
            {parsedData && naturalLanguageInput && (
              <div className="detected-values-feedback">
                {parsedData.occupancy_type && parsedData.subtype && (
                  <div className="detected-badge success">
                    <span className="checkmark">✓</span>
                    <span className="detected-text">
                      {parsedData.occupancy_type.charAt(0).toUpperCase() + parsedData.occupancy_type.slice(1)} → {' '}
                      {parsedData.subtype.split('_').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                      ).join(' ')} detected
                    </span>
                    {parsedData.confidence > 0 && (
                      <span className="confidence">
                        ({parsedData.confidence}% confidence)
                      </span>
                    )}
                  </div>
                )}
                
                {parsedData.square_footage && (
                  <div className="detected-badge">
                    <span className="checkmark">✓</span>
                    <span className="detected-text">
                      {parsedData.square_footage.toLocaleString()} SF
                    </span>
                  </div>
                )}
                
                {parsedData.location && (
                  <div className="detected-badge">
                    <span className="checkmark">✓</span>
                    <span className="detected-text">
                      Location: {parsedData.location}
                    </span>
                  </div>
                )}
                
                {parsedData.features.length > 0 && (
                  <div className="detected-badge">
                    <span className="checkmark">✓</span>
                    <span className="detected-text">
                      Features: {parsedData.features.map(f => 
                        f.split('_').join(' ')
                      ).join(', ')}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button type="button" onClick={() => navigate('/dashboard')} className="secondary-btn">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="primary-btn">
              {loading ? 'Processing...' : 'Parse & Continue'}
            </button>
          </div>
        </form>
      ) : (
        <form onSubmit={handleSubmit} className="scope-form">
          {/* Project Classification - Most Important, at the top */}
          {classificationAutoSelected && (
            <div className="auto-detect-message">
              ✓ Project type automatically detected from your description
            </div>
          )}
          <ProjectTypeSelector
            value={formData.project_classification || 'ground_up'}
            onChange={(value) => setFormData({...formData, project_classification: value as 'ground_up' | 'addition' | 'renovation'})}
            required={true}
            autoSelected={classificationAutoSelected}
          />
          
          <div className="form-section">
            <h2>Project Information</h2>
            
            <div className="form-group">
              <label htmlFor="project_name">Project Name</label>
              <input
                id="project_name"
                name="project_name"
                type="text"
                value={formData.project_name}
                onChange={handleChange}
                placeholder="Auto-generated based on your description"
                required={false}
              />
              {!formData.project_name && (
                <small className="help-text">Name will be auto-generated from your project details</small>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="building_type">Building Category *</label>
              <select
                id="building_type"
                name="building_type"
                value={formData.building_type || ''}
                onChange={(e) => {
                  const newBuildingType = e.target.value;
                  // Reset user floor change flag when building type changes
                  setUserChangedFloors(false);
                  // Reset subtype when building type changes
                  setFormData({
                    ...formData,
                    building_type: newBuildingType,
                    building_subtype: '',
                    occupancy_type: newBuildingType,  // For backward compatibility
                    subtype: '',  // Reset legacy field too
                    // Update project_type for backward compatibility
                    project_type: newBuildingType === 'residential' ? 'residential' :
                                 newBuildingType === 'industrial' ? 'industrial' :
                                 'commercial'
                  });
                }}
                required
              >
                <option value="">Select building category...</option>
                {BUILDING_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {formData.building_type && (
              <div className="form-group">
                <label htmlFor="building_subtype">
                  Specific Type * 
                  {parsedData?.subtype && (
                    <span className="auto-detected"> (Auto-detected: {parsedData.subtype})</span>
                  )}
                </label>
                <select
                  id="building_subtype"
                  name="building_subtype"
                  value={formData.building_subtype || ''}
                  onChange={(e) => {
                    const newSubtype = e.target.value;
                    const subtypeDetails = getSubtype(formData.building_type!, newSubtype);
                    
                    // Reset user floor change flag when subtype changes
                    setUserChangedFloors(false);
                    
                    // Calculate estimated floors
                    const estimatedFloors = formData.square_footage ? 
                      estimateFloors(formData.square_footage, formData.building_type!, newSubtype) :
                      1;
                    
                    console.log('🏗️ Subtype changed - estimating floors:', {
                      squareFootage: formData.square_footage,
                      buildingType: formData.building_type,
                      newSubtype: newSubtype,
                      estimatedFloors: estimatedFloors
                    });
                    
                    setFormData({
                      ...formData,
                      building_subtype: newSubtype,
                      subtype: newSubtype,  // For backward compatibility
                      // Auto-estimate floors based on subtype
                      num_floors: estimatedFloors,
                      // Auto-set ceiling height
                      ceiling_height: getDefaultCeilingHeight(formData.building_type!, newSubtype)
                    });
                  }}
                  required
                >
                  <option value="">Select specific type...</option>
                  {getBuildingType(formData.building_type)?.subtypes.map(subtype => (
                    <option key={subtype.value} value={subtype.value}>
                      {subtype.label} - {subtype.costHint}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="location">Location *</label>
              <input
                id="location"
                name="location"
                type="text"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Nashville, Tennessee"
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h2>Building Details</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="square_footage">Square Footage</label>
                <input
                  id="square_footage"
                  name="square_footage"
                  type="number"
                  value={formData.square_footage}
                  onChange={handleChange}
                  min="100"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="num_floors">Number of Floors</label>
                <input
                  id="num_floors"
                  name="num_floors"
                  type="number"
                  value={formData.num_floors || 1}
                  onChange={handleChange}
                  min="1"
                  max="100"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="ceiling_height">Ceiling Height (ft)</label>
                <input
                  id="ceiling_height"
                  name="ceiling_height"
                  type="number"
                  value={formData.ceiling_height}
                  onChange={handleChange}
                  min="8"
                  max="30"
                  step="0.5"
                  required
                />
              </div>
            </div>


            <div className="form-group">
              <label htmlFor="special_requirements">Special Requirements</label>
              <textarea
                id="special_requirements"
                name="special_requirements"
                value={formData.special_requirements}
                onChange={handleChange}
                rows={3}
                placeholder="e.g., LEED certification, clean rooms, special HVAC requirements"
              />
            </div>

            <div className="form-group">
              <label htmlFor="finish_level">Finish Level</label>
              <select
                id="finish_level"
                name="finish_level"
                value={formData.finish_level}
                onChange={handleChange}
                required
              >
                <option value="basic">Basic (-15%)</option>
                <option value="standard">Standard (baseline)</option>
                <option value="premium">Premium (+25%)</option>
              </select>
              <p className="help-text">
                Affects quality of materials and finishes across all trades
              </p>
            </div>

            <div className="form-group">
              <label htmlFor="budget_constraint">Budget Constraint (optional)</label>
              <input
                id="budget_constraint"
                name="budget_constraint"
                type="number"
                value={formData.budget_constraint || ''}
                onChange={handleChange}
                min="0"
                placeholder="Enter budget limit"
              />
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button type="button" onClick={() => navigate('/dashboard')} className="secondary-btn">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="primary-btn">
              {loading ? 'Generating...' : 'Generate Scope'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
  } catch (renderError) {
    console.error('ScopeGenerator render error:', renderError);
    return (
      <div className="scope-generator">
        <div className="error-message">
          An error occurred while rendering the form. Please refresh the page.
          <br />
          Error: {String(renderError)}
        </div>
      </div>
    );
  }
}

export default ScopeGenerator;
