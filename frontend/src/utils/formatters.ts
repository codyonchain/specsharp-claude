/**
 * Utility functions for formatting currency and numbers
 */

/**
 * Format a number as USD currency
 * @param value - The numeric value to format
 * @returns Formatted currency string (e.g., "$1,234.56")
 */
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

/**
 * Format a number as currency per square foot
 * @param value - The numeric value to format
 * @returns Formatted currency string with /SF suffix (e.g., "$92.03/SF")
 */
export const formatCurrencyPerSF = (value: number): string => {
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
  return `${formatted}/SF`;
};

/**
 * Format a large number with commas
 * @param value - The numeric value to format
 * @returns Formatted number string (e.g., "1,234,567")
 */
export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US').format(value);
};

/**
 * Format a percentage
 * @param value - The numeric value to format (0-100)
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string (e.g., "15.5%")
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`;
};