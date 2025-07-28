export interface CommonSize {
  label: string;
  value: number;
  category: string;
}

export const COMMON_SIZES: CommonSize[] = [
  // Office Buildings
  { label: "Small Office (10k SF)", value: 10000, category: "office" },
  { label: "Medium Office (50k SF)", value: 50000, category: "office" },
  { label: "Large Office (100k SF)", value: 100000, category: "office" },
  { label: "Corporate Campus (250k SF)", value: 250000, category: "office" },
  
  // Retail
  { label: "Small Retail (2.5k SF)", value: 2500, category: "retail" },
  { label: "Retail Store (5k SF)", value: 5000, category: "retail" },
  { label: "Strip Center (25k SF)", value: 25000, category: "retail" },
  { label: "Big Box Store (100k SF)", value: 100000, category: "retail" },
  { label: "Grocery Store (50k SF)", value: 50000, category: "retail" },
  
  // Restaurant
  { label: "Small Restaurant (3k SF)", value: 3000, category: "restaurant" },
  { label: "Typical Restaurant (6k SF)", value: 6000, category: "restaurant" },
  { label: "Large Restaurant (10k SF)", value: 10000, category: "restaurant" },
  
  // Healthcare
  { label: "Medical Clinic (10k SF)", value: 10000, category: "healthcare" },
  { label: "Surgery Center (25k SF)", value: 25000, category: "healthcare" },
  { label: "Small Hospital (100k SF)", value: 100000, category: "healthcare" },
  { label: "Regional Hospital (300k SF)", value: 300000, category: "healthcare" },
  
  // Educational
  { label: "Elementary School (50k SF)", value: 50000, category: "educational" },
  { label: "Middle School (100k SF)", value: 100000, category: "educational" },
  { label: "High School (200k SF)", value: 200000, category: "educational" },
  
  // Multi-Family Residential
  { label: "Small Apartment (20 units)", value: 20000, category: "multi_family" },
  { label: "Medium Apartment (50 units)", value: 50000, category: "multi_family" },
  { label: "Large Apartment (100 units)", value: 100000, category: "multi_family" },
  { label: "Luxury Apartment (200 units)", value: 250000, category: "multi_family" },
  
  // Industrial/Warehouse
  { label: "Small Warehouse (25k SF)", value: 25000, category: "warehouse" },
  { label: "Distribution Center (100k SF)", value: 100000, category: "warehouse" },
  { label: "Manufacturing (50k SF)", value: 50000, category: "industrial" },
  { label: "Large Industrial (200k SF)", value: 200000, category: "industrial" },
  
  // Hospitality
  { label: "Small Hotel (50 rooms)", value: 22500, category: "hospitality" },
  { label: "Business Hotel (150 rooms)", value: 67500, category: "hospitality" },
  { label: "Resort Hotel (300 rooms)", value: 150000, category: "hospitality" },
];

export const getCommonSizesByCategory = (category: string): CommonSize[] => {
  return COMMON_SIZES.filter(size => size.category === category);
};

export const getAllCategories = (): string[] => {
  return [...new Set(COMMON_SIZES.map(size => size.category))];
};