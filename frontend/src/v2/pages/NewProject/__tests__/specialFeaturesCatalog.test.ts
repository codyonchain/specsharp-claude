import {
  RESTAURANT_FEATURE_COSTS_BY_SUBTYPE,
  RESTAURANT_SUBTYPES,
  filterSpecialFeaturesBySubtype,
  getRestaurantSpecialFeatures,
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
