import { Project } from '../types';

interface FilenameOptions {
  includeDate?: boolean;
  includeTime?: boolean;
  includeVersion?: boolean;
  separator?: string;
  maxLength?: number;
}

/**
 * Generate smart, descriptive filenames for project exports
 */
export const generateFilename = (
  project: Partial<Project>,
  extension?: string,
  options: FilenameOptions = {}
): string => {
  const {
    includeDate = true,
    includeTime = false,
    includeVersion = false,
    separator = '_',
    maxLength = 255
  } = options;

  const parts: string[] = [];

  // Building type
  if (project.buildingType) {
    const type = sanitizeForFilename(project.buildingType)
      .replace(/\s+/g, separator)
      .toLowerCase();
    parts.push(type);
  }

  // Location (city only)
  if (project.location) {
    const city = project.location
      .split(',')[0]
      .trim()
      .replace(/\s+/g, separator)
      .toLowerCase();
    parts.push(sanitizeForFilename(city));
  }

  // Size (rounded to nearest 1k)
  if (project.squareFootage) {
    const size = Math.round(project.squareFootage / 1000);
    parts.push(`${size}k${separator}sf`);
  }

  // Number of floors
  if (project.numFloors && project.numFloors > 1) {
    parts.push(`${project.numFloors}floors`);
  }

  // Date
  if (includeDate) {
    const date = new Date();
    const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
    parts.push(dateStr);
  }

  // Time
  if (includeTime) {
    const date = new Date();
    const timeStr = date.toTimeString().split(' ')[0].replace(/:/g, ''); // HHMMSS
    parts.push(timeStr);
  }

  // Version
  if (includeVersion && project.version) {
    parts.push(`v${project.version}`);
  }

  // Join parts
  let filename = parts.join(separator);

  // Ensure filename doesn't exceed max length
  if (filename.length > maxLength - (extension?.length || 0) - 1) {
    filename = filename.substring(0, maxLength - (extension?.length || 0) - 1);
  }

  // Add extension if provided
  if (extension) {
    filename += `.${extension.replace('.', '')}`;
  }

  return filename;
};

/**
 * Generate filename for specific export types
 */
export const generateExportFilename = (
  project: Partial<Project>,
  exportType: 'excel' | 'pdf' | 'csv' | 'json',
  options?: FilenameOptions
): string => {
  const extensionMap = {
    excel: 'xlsx',
    pdf: 'pdf',
    csv: 'csv',
    json: 'json'
  };

  const typePrefix = {
    excel: 'estimate',
    pdf: 'report',
    csv: 'data',
    json: 'export'
  };

  const baseFilename = generateFilename(project, undefined, options);
  const prefix = typePrefix[exportType];
  const extension = extensionMap[exportType];

  return `${prefix}_${baseFilename}.${extension}`;
};

/**
 * Generate filename for trade package exports
 */
export const generateTradePackageFilename = (
  project: Partial<Project>,
  tradeName: string,
  options?: FilenameOptions
): string => {
  const sanitizedTrade = sanitizeForFilename(tradeName)
    .replace(/\s+/g, '_')
    .toLowerCase();
  
  const baseFilename = generateFilename(project, undefined, {
    ...options,
    includeDate: true
  });

  return `${sanitizedTrade}_package_${baseFilename}.xlsx`;
};

/**
 * Generate descriptive project name from details
 */
export const generateProjectName = (project: Partial<Project>): string => {
  const parts: string[] = [];

  // Size descriptor
  if (project.squareFootage) {
    const size = project.squareFootage;
    let sizeDesc = '';
    if (size < 10000) sizeDesc = 'Small';
    else if (size < 50000) sizeDesc = 'Medium';
    else if (size < 100000) sizeDesc = 'Large';
    else sizeDesc = 'Mega';
    parts.push(sizeDesc);
  }

  // Building type
  if (project.buildingType) {
    parts.push(formatBuildingType(project.buildingType));
  }

  // Location
  if (project.location) {
    const city = project.location.split(',')[0].trim();
    parts.push(`in ${city}`);
  }

  return parts.join(' ') || 'New Project';
};

/**
 * Format building type for display
 */
const formatBuildingType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'office': 'Office Building',
    'retail': 'Retail Space',
    'warehouse': 'Warehouse',
    'industrial': 'Industrial Facility',
    'healthcare': 'Healthcare Facility',
    'educational': 'Educational Building',
    'hospitality': 'Hotel',
    'restaurant': 'Restaurant',
    'multi_family_residential': 'Multi-Family Residential',
    'grocery_store': 'Grocery Store',
    'strip_center': 'Strip Center',
    'shopping_mall': 'Shopping Mall',
    'big_box': 'Big Box Retail',
    'standalone_retail': 'Retail Building'
  };

  return typeMap[type.toLowerCase()] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Sanitize string for use in filename
 */
const sanitizeForFilename = (str: string): string => {
  // Remove or replace invalid filename characters
  return str
    .replace(/[<>:"/\\|?*]/g, '') // Remove invalid chars
    .replace(/\s+/g, '_') // Replace spaces with underscores
    .replace(/[^\w\-_.]/g, '') // Keep only word chars, hyphens, underscores, dots
    .replace(/_+/g, '_') // Replace multiple underscores with single
    .trim();
};

/**
 * Generate a unique filename by appending a number if needed
 */
export const ensureUniqueFilename = (
  filename: string,
  existingFilenames: string[]
): string => {
  if (!existingFilenames.includes(filename)) {
    return filename;
  }

  // Extract name and extension
  const lastDotIndex = filename.lastIndexOf('.');
  const name = lastDotIndex > -1 ? filename.substring(0, lastDotIndex) : filename;
  const extension = lastDotIndex > -1 ? filename.substring(lastDotIndex) : '';

  // Find unique number
  let counter = 1;
  let uniqueFilename = filename;
  
  while (existingFilenames.includes(uniqueFilename)) {
    uniqueFilename = `${name}_${counter}${extension}`;
    counter++;
  }

  return uniqueFilename;
};

// Type definitions for better IDE support
export interface Project {
  id?: string;
  projectName?: string;
  buildingType?: string;
  location?: string;
  squareFootage?: number;
  numFloors?: number;
  version?: string;
  createdAt?: string;
  updatedAt?: string;
}