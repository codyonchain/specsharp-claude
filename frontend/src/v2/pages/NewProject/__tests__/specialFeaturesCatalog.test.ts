import {
  HEALTHCARE_FEATURE_COSTS_BY_SUBTYPE,
  HEALTHCARE_SUBTYPES,
  HOSPITALITY_FEATURE_COSTS_BY_SUBTYPE,
  HOSPITALITY_SUBTYPES,
  OFFICE_FEATURE_COSTS_BY_SUBTYPE,
  OFFICE_SUBTYPES,
  RETAIL_FEATURE_COSTS_BY_SUBTYPE,
  RETAIL_SUBTYPES,
  RESTAURANT_FEATURE_COSTS_BY_SUBTYPE,
  RESTAURANT_SUBTYPES,
  detectHealthcareFeatureIdsFromDescription,
  detectHospitalityFeatureIdsFromDescription,
  detectOfficeFeatureIdsFromDescription,
  detectRetailFeatureIdsFromDescription,
  detectSpecialtyFeatureIdsFromDescription,
  filterSpecialFeaturesBySubtype,
  getHealthcareSpecialFeatures,
  getHospitalitySpecialFeatures,
  getOfficeSpecialFeatures,
  getRetailSpecialFeatures,
  getRestaurantSpecialFeatures,
  getSpecialtySpecialFeatures,
  healthcareSubtypeHasSpecialFeatures,
  hospitalitySubtypeHasSpecialFeatures,
  officeSubtypeHasSpecialFeatures,
  retailSubtypeHasSpecialFeatures,
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

const REQUIRED_RETAIL_MAPPING = {
  shopping_center: {
    covered_walkway: 20,
    loading_dock: 25,
    monument_signage: 15,
    outdoor_seating: 20,
    drive_thru: 40,
    storage_units: 15,
  },
  big_box: {
    loading_dock: 20,
    mezzanine: 25,
    auto_center: 45,
    garden_center: 30,
    warehouse_racking: 15,
    refrigerated_storage: 35,
    curbside_pickup: 20,
  },
} as const;

const REQUIRED_OFFICE_MAPPING = {
  class_a: {
    fitness_center: 35,
    cafeteria: 30,
    conference_center: 40,
    structured_parking: 45,
    green_roof: 35,
    outdoor_terrace: 25,
    executive_floor: 45,
    data_center: 55,
    concierge: 20,
  },
  class_b: {
    fitness_center: 30,
    cafeteria: 25,
    conference_room: 20,
    surface_parking: 15,
    storage_space: 10,
    security_desk: 15,
  },
} as const;

const REQUIRED_HEALTHCARE_MAPPING = {
  surgical_center: {
    operating_room: 100,
    pre_op: 35,
    recovery_room: 40,
    sterile_processing: 60,
    hc_asc_expanded_pacu: 75,
    hc_asc_sterile_core_upgrade: 50,
    hc_asc_pain_management_suite: 60,
    hc_asc_hybrid_or_cath_lab: 125,
  },
  imaging_center: {
    mri_suite: 80,
    ct_suite: 60,
    pet_scan: 90,
    ultrasound: 20,
    mammography: 35,
    hc_imaging_second_mri: 100,
    hc_imaging_pet_ct_suite: 150,
    hc_imaging_interventional_rad: 125,
  },
  urgent_care: {
    x_ray: 25,
    laboratory: 20,
    trauma_room: 30,
    pharmacy: 25,
    hc_urgent_on_site_lab: 38,
    hc_urgent_imaging_suite: 75,
    hc_urgent_observation_bays: 25,
  },
  outpatient_clinic: {
    exam_rooms: 15,
    procedure_room: 25,
    laboratory: 20,
    pharmacy: 30,
    hc_outpatient_on_site_lab: 30,
    hc_outpatient_imaging_pod: 60,
    hc_outpatient_behavioral_suite: 25,
  },
  medical_office_building: {
    tenant_improvements: 40,
    ambulatory_imaging: 35,
    ambulatory_buildout: 60,
    mob_imaging_ready_shell: 40,
    mob_enhanced_mep: 20,
    mob_procedure_suite: 30,
    mob_pharmacy_shell: 15,
    mob_covered_dropoff: 15,
  },
  dental_office: {
    operatory: 15,
    x_ray: 12,
    sterilization: 10,
    lab: 15,
    hc_dental_pano_ceph: 45,
    hc_dental_sedation_suite: 60,
    hc_dental_sterilization_upgrade: 25,
    hc_dental_ortho_bay_expansion: 35,
  },
  hospital: {
    emergency_department: 50,
    surgical_suite: 75,
    imaging_suite: 40,
    icu: 60,
    laboratory: 25,
    cathlab: 90,
    pharmacy: 40,
  },
  medical_center: {
    emergency: 45,
    surgery: 60,
    imaging: 35,
    specialty_clinic: 30,
    laboratory: 25,
  },
  nursing_home: {
    memory_care: 30,
    therapy_room: 20,
    activity_room: 12,
    dining_hall: 15,
  },
  rehabilitation: {
    therapy_gym: 40,
    hydrotherapy: 50,
    treatment_rooms: 20,
    assessment_suite: 25,
  },
} as const;

const resolveFeatureCostPerSF = (
  feature: {
    costPerSFBySubtype?: Record<string, number>;
    costPerSF?: number;
  },
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

describe("retail special features catalog", () => {
  it("is non-empty and matches backend-aligned subtype mapping keys/values", () => {
    const retailFeatures = getRetailSpecialFeatures();
    expect(retailFeatures.length).toBeGreaterThan(0);
    expect(RETAIL_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_RETAIL_MAPPING);
  });

  it("resolves expected feature IDs for shopping_center and big_box with no duplicates", () => {
    const retailFeatures = getRetailSpecialFeatures();

    for (const subtype of RETAIL_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_RETAIL_MAPPING[subtype]).sort();
      const resolvedIds = filterSpecialFeaturesBySubtype(retailFeatures, subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("has valid cost-per-subtype entries for all allowed retail feature subtype combinations", () => {
    const retailFeatures = getRetailSpecialFeatures();

    for (const feature of retailFeatures) {
      expect(feature.costPerSFBySubtype).toBeDefined();
      expect(feature.allowedSubtypes && feature.allowedSubtypes.length > 0).toBe(true);

      for (const subtype of feature.allowedSubtypes || []) {
        const expectedCost = REQUIRED_RETAIL_MAPPING[
          subtype as keyof typeof REQUIRED_RETAIL_MAPPING
        ][feature.id as keyof (typeof REQUIRED_RETAIL_MAPPING)[keyof typeof REQUIRED_RETAIL_MAPPING]];

        expect(typeof expectedCost).toBe("number");
        expect(expectedCost).toBeGreaterThan(0);
        expect(feature.costPerSFBySubtype?.[subtype]).toBe(expectedCost);
      }
    }
  });

  it("retail subtype helper returns true for shopping_center and big_box", () => {
    expect(retailSubtypeHasSpecialFeatures("shopping_center")).toBe(true);
    expect(retailSubtypeHasSpecialFeatures("big_box")).toBe(true);
  });

  it("detects retail feature IDs from shopping-center and big-box scope cues", () => {
    const shoppingCenterDetected = detectRetailFeatureIdsFromDescription(
      "Neighborhood shopping center with covered walkway, monument signage, drive thru, and outdoor seating."
    );
    expect(shoppingCenterDetected).toEqual(
      expect.arrayContaining([
        "covered_walkway",
        "monument_signage",
        "drive_thru",
        "outdoor_seating",
      ])
    );

    const bigBoxDetected = detectRetailFeatureIdsFromDescription(
      "Big box retail shell with mezzanine, garden center, refrigerated storage, and curbside pickup lanes."
    );
    expect(bigBoxDetected).toEqual(
      expect.arrayContaining([
        "mezzanine",
        "garden_center",
        "refrigerated_storage",
        "curbside_pickup",
      ])
    );
  });

  it("keeps subtype filtering and cost resolution consistent for shared retail features", () => {
    const retailFeatures = getRetailSpecialFeatures();
    const shoppingLoadingDock = filterSpecialFeaturesBySubtype(retailFeatures, "shopping_center").find(
      (feature) => feature.id === "loading_dock"
    );
    const bigBoxLoadingDock = filterSpecialFeaturesBySubtype(retailFeatures, "big_box").find(
      (feature) => feature.id === "loading_dock"
    );

    expect(shoppingLoadingDock).toBeDefined();
    expect(bigBoxLoadingDock).toBeDefined();

    const shoppingCost = resolveFeatureCostPerSF(shoppingLoadingDock!, "shopping_center");
    const bigBoxCost = resolveFeatureCostPerSF(bigBoxLoadingDock!, "big_box");

    expect(shoppingCost).toBe(25);
    expect(bigBoxCost).toBe(20);
    expect(shoppingCost).not.toBe(bigBoxCost);
  });
});

describe("office special features catalog", () => {
  it("is non-empty and matches backend-aligned subtype mapping keys/values", () => {
    const officeFeatures = getOfficeSpecialFeatures();
    expect(officeFeatures.length).toBeGreaterThan(0);
    expect(OFFICE_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_OFFICE_MAPPING);
  });

  it("resolves expected feature IDs for class_a and class_b with no duplicates", () => {
    const officeFeatures = getOfficeSpecialFeatures();

    for (const subtype of OFFICE_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_OFFICE_MAPPING[subtype]).sort();
      const resolvedIds = filterSpecialFeaturesBySubtype(officeFeatures, subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("keeps unknown office subtype explicit by resolving the full inventory (no class_b fallback)", () => {
    const officeFeatures = getOfficeSpecialFeatures();
    const unknownSubtypeResolved = filterSpecialFeaturesBySubtype(officeFeatures, undefined).map(
      (feature) => feature.id
    );

    const classAIds = Object.keys(REQUIRED_OFFICE_MAPPING.class_a);
    const classBIds = Object.keys(REQUIRED_OFFICE_MAPPING.class_b);

    expect(unknownSubtypeResolved).toEqual(
      expect.arrayContaining([...classAIds, ...classBIds])
    );
    expect(unknownSubtypeResolved).toContain("executive_floor");
    expect(unknownSubtypeResolved).toContain("conference_room");
  });

  it("has valid cost-per-subtype entries for all allowed office feature subtype combinations", () => {
    const officeFeatures = getOfficeSpecialFeatures();

    for (const feature of officeFeatures) {
      expect(feature.costPerSFBySubtype).toBeDefined();
      expect(feature.allowedSubtypes && feature.allowedSubtypes.length > 0).toBe(true);

      for (const subtype of feature.allowedSubtypes || []) {
        const expectedCost = REQUIRED_OFFICE_MAPPING[
          subtype as keyof typeof REQUIRED_OFFICE_MAPPING
        ][feature.id as keyof (typeof REQUIRED_OFFICE_MAPPING)[keyof typeof REQUIRED_OFFICE_MAPPING]];

        expect(typeof expectedCost).toBe("number");
        expect(expectedCost).toBeGreaterThan(0);
        expect(feature.costPerSFBySubtype?.[subtype]).toBe(expectedCost);
      }
    }
  });

  it("office subtype helper returns true for class_a and class_b", () => {
    expect(officeSubtypeHasSpecialFeatures("class_a")).toBe(true);
    expect(officeSubtypeHasSpecialFeatures("class_b")).toBe(true);
  });

  it("detects office feature IDs from class-signaled prompts", () => {
    const classADetected = detectOfficeFeatureIdsFromDescription(
      "New 65000 sf class A office with executive floor, conference center, structured parking, concierge desk, and green roof."
    );
    expect(classADetected).toEqual(
      expect.arrayContaining([
        "executive_floor",
        "conference_center",
        "structured_parking",
        "concierge",
        "green_roof",
      ])
    );

    const classBDetected = detectOfficeFeatureIdsFromDescription(
      "Renovate 42000 sf class B office with conference room suite, surface parking, tenant storage space, and security desk."
    );
    expect(classBDetected).toEqual(
      expect.arrayContaining([
        "conference_room",
        "surface_parking",
        "storage_space",
        "security_desk",
      ])
    );
  });

  it("keeps subtype filtering and cost resolution consistent for shared office features", () => {
    const officeFeatures = getOfficeSpecialFeatures();
    const squareFootage = 50_000;

    const classAFitness = filterSpecialFeaturesBySubtype(officeFeatures, "class_a").find(
      (feature) => feature.id === "fitness_center"
    );
    const classBFitness = filterSpecialFeaturesBySubtype(officeFeatures, "class_b").find(
      (feature) => feature.id === "fitness_center"
    );

    expect(classAFitness).toBeDefined();
    expect(classBFitness).toBeDefined();

    const classACostPerSF = resolveFeatureCostPerSF(classAFitness!, "class_a");
    const classBCostPerSF = resolveFeatureCostPerSF(classBFitness!, "class_b");
    expect(classACostPerSF).toBe(35);
    expect(classBCostPerSF).toBe(30);

    const classATotal = classACostPerSF * squareFootage;
    const classBTotal = classBCostPerSF * squareFootage;
    expect(classATotal).toBeGreaterThan(classBTotal);
  });
});

describe("healthcare special features catalog", () => {
  it("is non-empty and matches required subtype mapping keys/values", () => {
    const healthcareFeatures = getHealthcareSpecialFeatures();
    expect(healthcareFeatures.length).toBeGreaterThan(0);
    expect(HEALTHCARE_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_HEALTHCARE_MAPPING);
  });

  it("resolves expected feature IDs for every healthcare subtype with no duplicates", () => {
    const healthcareFeatures = getHealthcareSpecialFeatures();

    for (const subtype of HEALTHCARE_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_HEALTHCARE_MAPPING[subtype]).sort();
      const resolvedIds = filterSpecialFeaturesBySubtype(healthcareFeatures, subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("has valid cost-per-subtype entries for all allowed healthcare feature subtype combinations", () => {
    const healthcareFeatures = getHealthcareSpecialFeatures();

    for (const feature of healthcareFeatures) {
      expect(feature.costPerSFBySubtype).toBeDefined();
      expect(feature.allowedSubtypes && feature.allowedSubtypes.length > 0).toBe(true);

      for (const subtype of feature.allowedSubtypes || []) {
        const expectedCost = REQUIRED_HEALTHCARE_MAPPING[
          subtype as keyof typeof REQUIRED_HEALTHCARE_MAPPING
        ][feature.id as keyof (typeof REQUIRED_HEALTHCARE_MAPPING)[keyof typeof REQUIRED_HEALTHCARE_MAPPING]];

        expect(typeof expectedCost).toBe("number");
        expect(expectedCost).toBeGreaterThan(0);
        expect(feature.costPerSFBySubtype?.[subtype]).toBe(expectedCost);
      }
    }
  });

  it("healthcare subtype helper returns true for all ten healthcare subtypes", () => {
    for (const subtype of HEALTHCARE_SUBTYPES) {
      expect(healthcareSubtypeHasSpecialFeatures(subtype)).toBe(true);
    }
  });

  it("detects healthcare feature IDs from clinical scope cues", () => {
    const detected = detectHealthcareFeatureIdsFromDescription(
      "New acute care hospital with emergency department, ICU beds, OR suites, imaging center, lab, central plant redundancy, and pharmacy cleanroom."
    );

    expect(detected).toEqual(
      expect.arrayContaining([
        "emergency_department",
        "icu",
        "surgical_suite",
        "imaging_suite",
        "laboratory",
        "pharmacy",
      ])
    );
  });

  it("detects canonical hospital OR/surgical feature IDs from healthcare prompt language", () => {
    const detected = detectHealthcareFeatureIdsFromDescription(
      "New 240,000 SF hospital with 12 OR surgical suite, emergency department, imaging suite, laboratory, and ICU in Nashville, TN"
    );

    expect(detected).toEqual(
      expect.arrayContaining([
        "surgical_suite",
        "emergency_department",
        "imaging_suite",
        "laboratory",
        "icu",
      ])
    );
  });

  it("increases total modeled special-feature cost when healthcare features are selected across all subtypes", () => {
    const squareFootage = 60_000;
    const allHealthcareFeatures = getHealthcareSpecialFeatures();

    for (const subtype of HEALTHCARE_SUBTYPES) {
      const applicable = filterSpecialFeaturesBySubtype(allHealthcareFeatures, subtype);
      expect(applicable.length).toBeGreaterThan(0);

      const selected = applicable.slice(0, Math.min(3, applicable.length));
      const selectedCost = selected.reduce(
        (sum, feature) =>
          sum + resolveFeatureCostPerSF(feature, subtype) * squareFootage,
        0
      );

      const baselineTotalCost = 95_000_000;
      const totalWithFeatures = baselineTotalCost + selectedCost;

      expect(selectedCost).toBeGreaterThan(0);
      expect(totalWithFeatures).toBeGreaterThan(baselineTotalCost);
    }
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
