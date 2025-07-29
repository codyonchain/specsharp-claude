export interface ExampleProject {
  description: string;
  squareFootage: number;
  floors: number;
  location: string;
  buildingType: string;
  category: string;
}

export const EXAMPLE_PROJECTS: ExampleProject[] = [
  // Healthcare - New Hampshire Focus
  {
    description: "100,000 sf medical office building with surgery center in Nashua, New Hampshire",
    squareFootage: 100000,
    floors: 4,
    location: "Nashua, NH",
    buildingType: "healthcare",
    category: "Healthcare"
  },
  {
    description: "75,000 sf outpatient clinic with imaging center in Manchester, New Hampshire",
    squareFootage: 75000,
    floors: 3,
    location: "Manchester, NH",
    buildingType: "healthcare",
    category: "Healthcare"
  },
  
  // Educational - New Hampshire Focus
  {
    description: "45,000 sf K-12 school with gymnasium in Concord, New Hampshire",
    squareFootage: 45000,
    floors: 2,
    location: "Concord, NH",
    buildingType: "educational",
    category: "Educational"
  },
  {
    description: "85,000 sf high school with cafeteria and auditorium in Portsmouth, New Hampshire",
    squareFootage: 85000,
    floors: 3,
    location: "Portsmouth, NH",
    buildingType: "educational",
    category: "Educational"
  },
  
  // Hospitality - Nashville Focus
  {
    description: "200 room hotel with conference center in Nashville, Tennessee",
    squareFootage: 90000,
    floors: 6,
    location: "Nashville, TN",
    buildingType: "hospitality",
    category: "Hospitality"
  },
  {
    description: "125 room extended stay hotel in Franklin, Tennessee",
    squareFootage: 56250,
    floors: 4,
    location: "Franklin, TN",
    buildingType: "hospitality",
    category: "Hospitality"
  },
  
  // Retail - Mixed NH and Nashville
  {
    description: "50,000 sf mixed-use retail and office in Portsmouth, New Hampshire",
    squareFootage: 50000,
    floors: 3,
    location: "Portsmouth, NH",
    buildingType: "retail",
    category: "Retail"
  },
  {
    description: "25,000 sf grocery store with pharmacy in Franklin, Tennessee",
    squareFootage: 25000,
    floors: 1,
    location: "Franklin, TN",
    buildingType: "retail",
    category: "Retail"
  },
  
  // Office - Mixed NH and Nashville
  {
    description: "75,000 sf office building 4 stories in downtown Manchester, New Hampshire",
    squareFootage: 75000,
    floors: 4,
    location: "Manchester, NH",
    buildingType: "office",
    category: "Office"
  },
  {
    description: "60,000 sf corporate headquarters 3 stories in Nashville, Tennessee",
    squareFootage: 60000,
    floors: 3,
    location: "Nashville, TN",
    buildingType: "office",
    category: "Office"
  },
  
  // Restaurant - New Hampshire Focus
  {
    description: "4,000 sf full-service restaurant with commercial kitchen in Manchester, New Hampshire",
    squareFootage: 4000,
    floors: 1,
    location: "Manchester, NH",
    buildingType: "restaurant",
    category: "Restaurant"
  },
  {
    description: "3,000 sf casual dining restaurant with bar in Nashua, New Hampshire",
    squareFootage: 3000,
    floors: 1,
    location: "Nashua, NH",
    buildingType: "restaurant",
    category: "Restaurant"
  },
  
  // Multi-Family - Mixed Focus
  {
    description: "150 unit luxury apartment complex 4 stories in Manchester, New Hampshire",
    squareFootage: 187500,
    floors: 4,
    location: "Manchester, NH",
    buildingType: "multi_family_residential",
    category: "Multi-Family"
  },
  {
    description: "200 unit apartment building with amenities in Nashville, Tennessee",
    squareFootage: 250000,
    floors: 5,
    location: "Nashville, TN",
    buildingType: "multi_family_residential",
    category: "Multi-Family"
  },
  
  // Industrial/Warehouse - Mixed Focus
  {
    description: "75,000 sf warehouse distribution center in Nashville, Tennessee",
    squareFootage: 75000,
    floors: 1,
    location: "Nashville, TN",
    buildingType: "warehouse",
    category: "Industrial"
  },
  {
    description: "40,000 sf manufacturing facility with office space in Salem, New Hampshire",
    squareFootage: 40000,
    floors: 1,
    location: "Salem, NH",
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