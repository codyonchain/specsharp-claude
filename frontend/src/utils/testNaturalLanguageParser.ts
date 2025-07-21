// Test cases for natural language parser
export const testNaturalLanguageParser = (parseFunction: (input: string) => any) => {
  const testCases = [
    {
      input: "300x400 industrial facility (80%) + office space (20%) with multiple dock doors in Texas",
      expected: {
        square_footage: 120000,
        project_type: 'mixed_use',
        location: 'Texas, TX',
        special_requirements: 'Building mix: industrial (80%), office (20%), Multiple dock doors',
        building_mix: { industrial: 0.8, office: 0.2 }
      }
    },
    {
      input: "warehouse (70%) + office (30%)",
      expected: {
        project_type: 'mixed_use',
        special_requirements: 'Building mix: warehouse (70%), office (30%)',
        building_mix: { warehouse: 0.7, office: 0.3 }
      }
    },
    {
      input: "60% retail 40% office building",
      expected: {
        project_type: 'mixed_use',
        special_requirements: 'Building mix: retail (60%), office (40%)',
        building_mix: { retail: 0.6, office: 0.4 }
      }
    },
    {
      input: "manufacturing facility with 25% office space",
      expected: {
        project_type: 'mixed_use',
        special_requirements: 'Building mix: industrial (75%), office (25%)',
        building_mix: { industrial: 0.75, office: 0.25 }
      }
    },
    {
      input: "10000 SF office with HVAC and bathrooms in Texas",
      expected: {
        square_footage: 10000,
        project_type: 'commercial',
        location: 'Texas, TX',
        special_requirements: 'HVAC system, Bathrooms',
        occupancy_type: 'office'
      }
    }
  ];

  testCases.forEach(({ input, expected }, index) => {
    console.log(`\n=== Test Case ${index + 1} ===`);
    console.log('Input:', input);
    const result = parseFunction(input);
    console.log('Result:', result);
    console.log('Expected:', expected);
    
    // Check each expected field
    Object.entries(expected).forEach(([key, value]) => {
      if (JSON.stringify(result[key]) !== JSON.stringify(value)) {
        console.error(`❌ Mismatch in ${key}:`, {
          got: result[key],
          expected: value
        });
      } else {
        console.log(`✅ ${key} matches`);
      }
    });
  });
};