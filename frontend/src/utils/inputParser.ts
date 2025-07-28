/**
 * Smart input parser for natural language descriptions
 * Handles common abbreviations, typos, and shorthand
 */

export const parseDescription = (input: string): string => {
  if (!input) return '';
  
  return input
    // Square footage abbreviations
    .replace(/(\d+)k\s*sf/gi, (_, num) => `${num}000 sf`)
    .replace(/(\d+)k\s*sqft/gi, (_, num) => `${num}000 sf`)
    .replace(/(\d+)k\s*sq\s*ft/gi, (_, num) => `${num}000 sf`)
    .replace(/\bsq\s*ft\b/gi, 'sf')
    .replace(/\bsqft\b/gi, 'sf')
    .replace(/\bsquare\s*feet\b/gi, 'sf')
    
    // Building type abbreviations
    .replace(/\bmed\s+office\b/gi, 'medical office building')
    .replace(/\bmob\b/gi, 'medical office building')
    .replace(/\bhosp\b/gi, 'hospital')
    .replace(/\bapt\b/gi, 'apartment')
    .replace(/\bapts\b/gi, 'apartments')
    .replace(/\bwhse\b/gi, 'warehouse')
    .replace(/\bdist\s+center\b/gi, 'distribution center')
    .replace(/\belem\b/gi, 'elementary')
    .replace(/\bhs\b/gi, 'high school')
    .replace(/\bms\b/gi, 'middle school')
    
    // Common misspellings
    .replace(/\brestaraunt\b/gi, 'restaurant')
    .replace(/\bresturant\b/gi, 'restaurant')
    .replace(/\brestuarant\b/gi, 'restaurant')
    .replace(/\bgrocery\s*store\b/gi, 'grocery store')
    .replace(/\bconvience\b/gi, 'convenience')
    .replace(/\bconvienence\b/gi, 'convenience')
    
    // Story/floor normalization
    .replace(/\b(\d+)\s*story\b/gi, '$1 stories')
    .replace(/\b(\d+)\s*floor\b/gi, '$1 floors')
    .replace(/\b(\d+)\s*flr\b/gi, '$1 floors')
    .replace(/\bone\s*story\b/gi, '1 story')
    .replace(/\btwo\s*story\b/gi, '2 stories')
    .replace(/\bthree\s*story\b/gi, '3 stories')
    .replace(/\bfour\s*story\b/gi, '4 stories')
    .replace(/\bfive\s*story\b/gi, '5 stories')
    
    // Room count normalization
    .replace(/\b(\d+)\s*rm\b/gi, '$1 room')
    .replace(/\b(\d+)\s*rms\b/gi, '$1 rooms')
    
    // Unit count normalization
    .replace(/\b(\d+)\s*unit\b/gi, '$1 units')
    .replace(/\b(\d+)\s*u\b/gi, '$1 units')
    
    // Tenant/space normalization
    .replace(/\b(\d+)\s*tenant\b/gi, '$1 tenants')
    .replace(/\b(\d+)\s*space\b/gi, '$1 spaces')
    
    // Location abbreviations
    .replace(/\btx\b/gi, 'Texas')
    .replace(/\bca\b/gi, 'California')
    .replace(/\bny\b/gi, 'New York')
    .replace(/\bfl\b/gi, 'Florida')
    .replace(/\bil\b/gi, 'Illinois')
    .replace(/\bwa\b/gi, 'Washington')
    .replace(/\baz\b/gi, 'Arizona')
    .replace(/\bco\b/gi, 'Colorado')
    .replace(/\bga\b/gi, 'Georgia')
    .replace(/\bnc\b/gi, 'North Carolina')
    
    // City abbreviations
    .replace(/\bsf\b/gi, 'San Francisco')
    .replace(/\bla\b/gi, 'Los Angeles')
    .replace(/\bnyc\b/gi, 'New York City')
    .replace(/\bchi\b/gi, 'Chicago')
    .replace(/\bhou\b/gi, 'Houston')
    .replace(/\bdal\b/gi, 'Dallas')
    .replace(/\batx\b/gi, 'Austin')
    .replace(/\bsat\b/gi, 'San Antonio')
    
    // Clean up extra spaces
    .replace(/\s+/g, ' ')
    .trim();
};

/**
 * Parse square footage from description
 */
export const parseSquareFootage = (input: string): number | null => {
  const patterns = [
    /(\d+,?\d*)\s*(?:sf|sqft|sq\s*ft|square\s*feet)/i,
    /(\d+)k\s*(?:sf|sqft|sq\s*ft)/i,
  ];
  
  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) {
      const value = match[1].replace(',', '');
      if (match[0].includes('k')) {
        return parseInt(value) * 1000;
      }
      return parseInt(value);
    }
  }
  
  return null;
};

/**
 * Parse number of floors/stories from description
 */
export const parseFloors = (input: string): number | null => {
  const patterns = [
    /(\d+)\s*(?:story|stories|floor|floors|flr)/i,
    /(one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:story|stories|floor|floors)/i,
  ];
  
  const wordToNumber: Record<string, number> = {
    one: 1, two: 2, three: 3, four: 4, five: 5,
    six: 6, seven: 7, eight: 8, nine: 9, ten: 10
  };
  
  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) {
      const value = match[1].toLowerCase();
      if (wordToNumber[value]) {
        return wordToNumber[value];
      }
      return parseInt(value);
    }
  }
  
  return null;
};

/**
 * Parse room count (for hotels)
 */
export const parseRoomCount = (input: string): number | null => {
  const patterns = [
    /(\d+)\s*(?:room|rooms|rm|rms)\s*hotel/i,
    /hotel\s*with\s*(\d+)\s*(?:room|rooms|rm|rms)/i,
  ];
  
  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) {
      return parseInt(match[1]);
    }
  }
  
  return null;
};

/**
 * Parse unit count (for apartments)
 */
export const parseUnitCount = (input: string): number | null => {
  const patterns = [
    /(\d+)\s*(?:unit|units|u)\s*(?:apartment|apt|complex)/i,
    /(?:apartment|apt|complex)\s*with\s*(\d+)\s*(?:unit|units|u)/i,
  ];
  
  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) {
      return parseInt(match[1]);
    }
  }
  
  return null;
};