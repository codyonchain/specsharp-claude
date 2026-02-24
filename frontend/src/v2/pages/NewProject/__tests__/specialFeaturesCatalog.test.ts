import {
  HOSPITALITY_FEATURE_COSTS_BY_SUBTYPE,
  HOSPITALITY_SUBTYPES,
  RESTAURANT_FEATURE_COSTS_BY_SUBTYPE,
  RESTAURANT_SUBTYPES,
  detectHospitalityFeatureIdsFromDescription,
  detectSpecialtyFeatureIdsFromDescription,
  filterSpecialFeaturesBySubtype,
  getHospitalitySpecialFeatures,
  getRestaurantSpecialFeatures,
  getSpecialtySpecialFeatures,
  hospitalitySubtypeHasSpecialFeatures,
  restaurantSubtypeHasSpecialFeatures,
} from "../specialFeaturesCatalog";

const REQUIRED_RESTAURANT_MAPPING = {
  quick_service: {
    drive_thru: 40,
    outdoor_seating: 20,
    play_area: 35,
    double_drive_thru: 55,
    digital_menu_boards: 15,
  },
  full_service: {
    outdoor_seating: 25,
    bar: 35,
    private_dining: 30,
    wine_cellar: 45,
    live_kitchen: 25,
    rooftop_dining: 50,
    valet_parking: 20,
  },
  fine_dining: {
    wine_cellar: 60,
    private_dining: 45,
    chef_table: 40,
    dry_aging_room: 50,
    pastry_kitchen: 35,
    sommelier_station: 30,
    valet_parking: 25,
  },
  cafe: {
    outdoor_seating: 20,
    drive_thru: 35,
    bakery_display: 15,
    lounge_area: 20,
    meeting_room: 25,
  },
  bar_tavern: {
    outdoor_seating: 25,
    live_music_stage: 30,
    game_room: 25,
    rooftop_bar: 50,
    private_party_room: 30,
    craft_beer_system: 35,
  },
} as const;

const REQUIRED_HOSPITALITY_MAPPING = {
  limited_service_hotel: {
    breakfast_area: 20,
    fitness_center: 15,
    business_center: 10,
    pool: 25,
  },
  full_service_hotel: {
    ballroom: 50,
    restaurant: 75,
    spa: 60,
    conference_center: 45,
    rooftop_bar: 55,
  },
} as const;

const resolveFeatureCostPerSF = (
  feature: ReturnType<typeof getSpecialtySpecialFeatures>[number],
  subtype: string
): number => {
  const subtypeCost =
    feature.costPerSFBySubtype && subtype in feature.costPerSFBySubtype
      ? feature.costPerSFBySubtype[subtype]
      : undefined;
  if (typeof subtypeCost === "number" && Number.isFinite(subtypeCost)) {
    return subtypeCost;
  }
  if (typeof feature.costPerSF === "number" && Number.isFinite(feature.costPerSF)) {
    return feature.costPerSF;
  }
  return 0;
};

describe("restaurant special features catalog", () => {
  it("is non-empty and matches required subtype mapping keys/values", () => {
    const restaurantFeatures = getRestaurantSpecialFeatures();
    expect(restaurantFeatures.length).toBeGreaterThan(0);
    expect(RESTAURANT_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_RESTAURANT_MAPPING);
  });

  it("resolves expected feature IDs for every restaurant subtype with no duplicates", () => {
    const restaurantFeatures = getRestaurantSpecialFeatures();

    for (const subtype of RESTAURANT_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_RESTAURANT_MAPPING[subtype]).sort();
      const resolvedIds = filterSpecialFeaturesBySubtype(restaurantFeatures, subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("has valid cost-per-subtype entries for all allowed restaurant feature subtype combinations", () => {
    const restaurantFeatures = getRestaurantSpecialFeatures();

    for (const feature of restaurantFeatures) {
      expect(feature.costPerSFBySubtype).toBeDefined();
      expect(feature.allowedSubtypes && feature.allowedSubtypes.length > 0).toBe(true);

      for (const subtype of feature.allowedSubtypes || []) {
        const expectedCost = REQUIRED_RESTAURANT_MAPPING[
          subtype as keyof typeof REQUIRED_RESTAURANT_MAPPING
        ][feature.id as keyof (typeof REQUIRED_RESTAURANT_MAPPING)[keyof typeof REQUIRED_RESTAURANT_MAPPING]];

        expect(typeof expectedCost).toBe("number");
        expect(expectedCost).toBeGreaterThan(0);
        expect(feature.costPerSFBySubtype?.[subtype]).toBe(expectedCost);
      }
    }
  });

  it("never resolves to the no-special-features path for hardened restaurant subtypes", () => {
    const restaurantFeatures = getRestaurantSpecialFeatures();

    for (const subtype of RESTAURANT_SUBTYPES) {
      expect(restaurantSubtypeHasSpecialFeatures(subtype)).toBe(true);
      expect(filterSpecialFeaturesBySubtype(restaurantFeatures, subtype).length).toBeGreaterThan(0);
    }
  });
});

describe("hospitality special features catalog", () => {
  it("is non-empty and matches required subtype mapping keys/values", () => {
    const hospitalityFeatures = getHospitalitySpecialFeatures();
    expect(hospitalityFeatures.length).toBeGreaterThan(0);
    expect(HOSPITALITY_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_HOSPITALITY_MAPPING);
  });

  it("resolves expected feature IDs for every hospitality subtype with no duplicates", () => {
    const hospitalityFeatures = getHospitalitySpecialFeatures();

    for (const subtype of HOSPITALITY_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_HOSPITALITY_MAPPING[subtype]).sort();
      const resolvedIds = filterSpecialFeaturesBySubtype(hospitalityFeatures, subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("has valid cost-per-subtype entries for all allowed hospitality feature subtype combinations", () => {
    const hospitalityFeatures = getHospitalitySpecialFeatures();

    for (const feature of hospitalityFeatures) {
      expect(feature.costPerSFBySubtype).toBeDefined();
      expect(feature.allowedSubtypes && feature.allowedSubtypes.length > 0).toBe(true);

      for (const subtype of feature.allowedSubtypes || []) {
        const expectedCost = REQUIRED_HOSPITALITY_MAPPING[
          subtype as keyof typeof REQUIRED_HOSPITALITY_MAPPING
        ][feature.id as keyof (typeof REQUIRED_HOSPITALITY_MAPPING)[keyof typeof REQUIRED_HOSPITALITY_MAPPING]];

        expect(typeof expectedCost).toBe("number");
        expect(expectedCost).toBeGreaterThan(0);
        expect(feature.costPerSFBySubtype?.[subtype]).toBe(expectedCost);
      }
    }
  });

  it("hospitality subtype helper returns true for both hotel subtypes", () => {
    expect(hospitalitySubtypeHasSpecialFeatures("limited_service_hotel")).toBe(true);
    expect(hospitalitySubtypeHasSpecialFeatures("full_service_hotel")).toBe(true);
  });

  it("detects hospitality feature IDs from limited and full service amenity language", () => {
    const limitedServiceDetected = detectHospitalityFeatureIdsFromDescription(
      "breakfast area, fitness center, business center, pool"
    );
    expect(limitedServiceDetected).toEqual(
      expect.arrayContaining([
        "breakfast_area",
        "fitness_center",
        "business_center",
        "pool",
      ])
    );

    const fullServiceDetected = detectHospitalityFeatureIdsFromDescription(
      "ballroom, conference center, spa, rooftop bar, signature restaurant"
    );
    expect(fullServiceDetected).toEqual(
      expect.arrayContaining([
        "ballroom",
        "conference_center",
        "spa",
        "rooftop_bar",
        "restaurant",
      ])
    );
  });
});

describe("specialty special feature catalog", () => {
  it("exposes operationally credible data-center features with subtype filtering", () => {
    const allSpecialtyFeatures = getSpecialtySpecialFeatures();
    const dataCenterFeatures = filterSpecialFeaturesBySubtype(
      allSpecialtyFeatures,
      "data_center"
    );
    const dataCenterIds = dataCenterFeatures.map((feature) => feature.id);

    expect(dataCenterIds).toEqual(
      expect.arrayContaining([
        "utility_substation",
        "generator_plant",
        "chilled_water_plant",
        "dual_fiber_meet_me_room",
        "integrated_commissioning",
      ])
    );
    expect(
      dataCenterFeatures.every((feature) =>
        feature.allowedSubtypes?.includes("data_center")
      )
    ).toBe(true);
  });

  it("detects specialty feature IDs from description cues", () => {
    const detected = detectSpecialtyFeatureIdsFromDescription(
      "Tier IV data center with dedicated substation, generator plant, chilled water CRAH loop, dual fiber meet-me room, and integrated commissioning."
    );

    expect(detected).toEqual(
      expect.arrayContaining([
        "utility_substation",
        "generator_plant",
        "chilled_water_plant",
        "dual_fiber_meet_me_room",
        "integrated_commissioning",
      ])
    );
  });

  it("increases total modeled special-feature cost when specialty features are selected", () => {
    const squareFootage = 100_000;
    const subtype = "data_center";
    const applicable = filterSpecialFeaturesBySubtype(
      getSpecialtySpecialFeatures(),
      subtype
    );

    const selected = [
      "utility_substation",
      "generator_plant",
      "chilled_water_plant",
    ];
    const selectedCost = applicable
      .filter((feature) => selected.includes(feature.id))
      .reduce(
        (sum, feature) =>
          sum + resolveFeatureCostPerSF(feature, subtype) * squareFootage,
        0
      );

    const baselineTotalCost = 150_000_000;
    const totalWithFeatures = baselineTotalCost + selectedCost;

    expect(selectedCost).toBeGreaterThan(0);
    expect(totalWithFeatures).toBeGreaterThan(baselineTotalCost);
  });
});
