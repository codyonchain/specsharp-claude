/**
 * Universal display formatters for backend data
 * Handles all number formatting, null checks, and edge cases
 */

export const formatters = {
  // Currency formatters
  currency: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    const absVal = Math.abs(val);
    
    if (absVal >= 1000000) {
      return `$${val < 0 ? '-' : ''}${(absVal / 1000000).toFixed(1)}M`;
    } else if (absVal >= 1000) {
      return `$${val < 0 ? '-' : ''}${(absVal / 1000).toFixed(0)}K`;
    }
    return `$${val < 0 ? '-' : ''}${absVal.toFixed(0)}`;
  },
  
  currencyExact: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    return `$${val < 0 ? '-' : ''}${Math.abs(val).toLocaleString()}`;
  },
  
  // Percentage formatters
  percentage: (val: number | undefined | null, decimals: number = 1): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    // Handle if value is already in percentage form (e.g., 8.2 instead of 0.082)
    const value = val > 1 ? val : val * 100;
    return `${value.toFixed(decimals)}%`;
  },
  
  // Number formatters
  decimal: (val: number | undefined | null, decimals: number = 2): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    return val.toFixed(decimals);
  },
  
  years: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    if (val === Infinity || val > 999) return '∞ yrs';
    if (val < 0) return 'N/A';
    return `${val.toFixed(1)} yrs`;
  },
  
  multiplier: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    return `${val.toFixed(2)}x`;
  },
  
  units: (val: number | undefined | null): number => {
    if (val === undefined || val === null || isNaN(val)) return 0;
    return Math.round(val);
  },
  
  squareFeet: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    return `${Math.round(val).toLocaleString()} SF`;
  },
  
  // Special formatters
  costPerSF: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    return `$${Math.round(val)}/SF`;
  },
  
  monthlyRent: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    return `$${Math.round(val).toLocaleString()}/mo`;
  },
  
  number: (val: number | undefined | null): string => {
    if (val === undefined || val === null || isNaN(val)) return 'N/A';
    return Math.round(val).toLocaleString();
  }
};

// Safely extract nested values from backend response
export const safeGet = (
  obj: any, 
  path: string, 
  fallback: any = undefined
): any => {
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    result = result?.[key];
    if (result === undefined) return fallback;
  }
  
  return result;
};

// Check if value exists and is valid
export const hasValue = (val: any): boolean => {
  return val !== undefined && val !== null && val !== '' && !isNaN(val);
};

// Format a label based on value existence
export const formatLabel = (label: string, value: any): string => {
  if (!hasValue(value)) return label;
  return label;
};