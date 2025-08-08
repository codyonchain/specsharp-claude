/**
 * Shared helper to get consistent pie/fingerprint breakdown from project data
 * This ensures CostDNA fingerprint matches any pie chart exactly
 */

export type PieItem = { trade: string; amount: number };

/**
 * Extracts trade breakdown from project data in a consistent way
 * @param project - The project object containing categories or trade data
 * @returns Array of trade items with normalized names and amounts
 */
export function getPieBreakdown(project: any): PieItem[] {
  if (!project) return [];

  // Try multiple possible sources for category data
  const categories = 
    project.categories || 
    project.category_breakdown || 
    project.trade_breakdown ||
    project.cost_breakdown ||
    [];

  if (!Array.isArray(categories)) return [];

  // Normalize the data structure - handle different field names
  const normalized = categories
    .map((item: any) => {
      // Extract trade name from various possible fields
      const trade = String(
        item.trade || 
        item.name || 
        item.category || 
        item.label || 
        ""
      ).trim();

      // Extract amount from various possible fields
      const amount = Number(
        item.amount || 
        item.value || 
        item.total || 
        item.total_cost ||
        item.subtotal ||
        0
      );

      return { trade, amount };
    })
    .filter((item: PieItem) => item.trade && isFinite(item.amount) && item.amount > 0);

  // Define canonical trade order (must match pie chart)
  const TRADE_ORDER = [
    "Structural",
    "Mechanical", 
    "Electrical",
    "Plumbing",
    "General Conditions"
  ];

  // Helper to normalize trade names for matching
  const normalizeName = (s: string) => 
    String(s || "").toLowerCase().replace(/[^a-z]/g, "");

  // Create index of normalized data
  const dataByNorm = Object.fromEntries(
    normalized.map((item: PieItem) => [normalizeName(item.trade), item])
  );

  // Build result in canonical order
  const result: PieItem[] = [];
  
  for (const canonicalTrade of TRADE_ORDER) {
    const normalizedKey = normalizeName(canonicalTrade);
    const match = dataByNorm[normalizedKey];
    
    if (match) {
      // Use canonical name but actual amount
      result.push({
        trade: canonicalTrade,
        amount: match.amount
      });
    }
  }

  // Add any trades not in canonical order (preserving original names)
  const canonicalNormalized = new Set(TRADE_ORDER.map(normalizeName));
  for (const item of normalized) {
    if (!canonicalNormalized.has(normalizeName(item.trade))) {
      result.push(item);
    }
  }

  return result;
}

/**
 * Get pie colors matching the standard trade colors
 */
export const TRADE_COLORS: Record<string, string> = {
  Structural: "#4F81BD",           // blue
  Mechanical: "#9BBB59",           // green  
  Electrical: "#8064A2",           // purple
  Plumbing: "#C0504D",             // red
  "General Conditions": "#F79646", // orange
};

/**
 * Helper to get color for a trade
 */
export function getTradeColor(trade: string): string {
  return TRADE_COLORS[trade] || "#999999";
}