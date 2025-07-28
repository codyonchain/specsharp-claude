export interface ExampleProject {
  description: string;
  squareFootage: number;
  floors: number;
  location: string;
  buildingType: string;
  category: string;
}

export const EXAMPLE_PROJECTS: ExampleProject[] = [
  // Healthcare
  {
    description: "100,000 sf hospital 4 stories with emergency department in Houston, Texas",
    squareFootage: 100000,
    floors: 4,
    location: "Houston, TX",
    buildingType: "healthcare",
    category: "Healthcare"
  },
  {
    description: "25,000 sf medical office building with surgery center in Dallas, Texas",
    squareFootage: 25000,
    floors: 2,
    location: "Dallas, TX",
    buildingType: "healthcare",
    category: "Healthcare"
  },
  
  // Educational
  {
    description: "45,000 sf elementary school with 30 classrooms in Dallas, Texas",
    squareFootage: 45000,
    floors: 2,
    location: "Dallas, TX",
    buildingType: "educational",
    category: "Educational"
  },
  {
    description: "120,000 sf high school with gymnasium and cafeteria in Austin, Texas",
    squareFootage: 120000,
    floors: 3,
    location: "Austin, TX",
    buildingType: "educational",
    category: "Educational"
  },
  
  // Hospitality
  {
    description: "150 room hotel with conference center in Austin, Texas",
    squareFootage: 67500,
    floors: 5,
    location: "Austin, TX",
    buildingType: "hospitality",
    category: "Hospitality"
  },
  {
    description: "75 room extended stay hotel in San Antonio, Texas",
    squareFootage: 33750,
    floors: 4,
    location: "San Antonio, TX",
    buildingType: "hospitality",
    category: "Hospitality"
  },
  
  // Retail
  {
    description: "25,000 sf strip center with 5 tenant spaces in San Antonio, Texas",
    squareFootage: 25000,
    floors: 1,
    location: "San Antonio, TX",
    buildingType: "retail",
    category: "Retail"
  },
  {
    description: "50,000 sf grocery store with pharmacy in Houston, Texas",
    squareFootage: 50000,
    floors: 1,
    location: "Houston, TX",
    buildingType: "retail",
    category: "Retail"
  },
  
  // Office
  {
    description: "75,000 sf office building 5 stories in downtown Dallas, Texas",
    squareFootage: 75000,
    floors: 5,
    location: "Dallas, TX",
    buildingType: "office",
    category: "Office"
  },
  {
    description: "30,000 sf corporate headquarters 3 stories in Austin, Texas",
    squareFootage: 30000,
    floors: 3,
    location: "Austin, TX",
    buildingType: "office",
    category: "Office"
  },
  
  // Restaurant
  {
    description: "6,000 sf full service restaurant with bar in Houston, Texas",
    squareFootage: 6000,
    floors: 1,
    location: "Houston, TX",
    buildingType: "restaurant",
    category: "Restaurant"
  },
  {
    description: "3,500 sf quick service restaurant with drive-thru in San Antonio, Texas",
    squareFootage: 3500,
    floors: 1,
    location: "San Antonio, TX",
    buildingType: "restaurant",
    category: "Restaurant"
  },
  
  // Multi-Family
  {
    description: "200 unit luxury apartment complex 4 stories in Austin, Texas",
    squareFootage: 250000,
    floors: 4,
    location: "Austin, TX",
    buildingType: "multi_family_residential",
    category: "Multi-Family"
  },
  {
    description: "100 unit apartment building with amenities in Dallas, Texas",
    squareFootage: 100000,
    floors: 3,
    location: "Dallas, TX",
    buildingType: "multi_family_residential",
    category: "Multi-Family"
  },
  
  // Industrial/Warehouse
  {
    description: "100,000 sf distribution center with 20 loading docks in Houston, Texas",
    squareFootage: 100000,
    floors: 1,
    location: "Houston, TX",
    buildingType: "warehouse",
    category: "Industrial"
  },
  {
    description: "50,000 sf manufacturing facility with clean rooms in Austin, Texas",
    squareFootage: 50000,
    floors: 1,
    location: "Austin, TX",
    buildingType: "industrial",
    category: "Industrial"
  }
];

// Get random examples
export const getRandomExamples = (count: number = 4): ExampleProject[] => {
  const shuffled = [...EXAMPLE_PROJECTS].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

// Get examples by category
export const getExamplesByCategory = (category: string): ExampleProject[] => {
  return EXAMPLE_PROJECTS.filter(project => project.category === category);
};

// Get featured examples (one from each major category)
export const getFeaturedExamples = (): ExampleProject[] => {
  const categories = ['Healthcare', 'Educational', 'Hospitality', 'Retail', 'Office', 'Multi-Family'];
  const featured: ExampleProject[] = [];
  
  for (const category of categories) {
    const categoryProjects = getExamplesByCategory(category);
    if (categoryProjects.length > 0) {
      featured.push(categoryProjects[0]);
    }
  }
  
  return featured;
};