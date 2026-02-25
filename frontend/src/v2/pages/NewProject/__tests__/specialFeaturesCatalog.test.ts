import {
  CIVIC_FEATURE_COSTS_BY_SUBTYPE,
  CIVIC_SUBTYPES,
  EDUCATIONAL_FEATURE_COSTS_BY_SUBTYPE,
  EDUCATIONAL_SUBTYPES,
  HEALTHCARE_FEATURE_COSTS_BY_SUBTYPE,
  HEALTHCARE_SUBTYPES,
  HOSPITALITY_FEATURE_COSTS_BY_SUBTYPE,
  HOSPITALITY_SUBTYPES,
  MIXED_USE_FEATURE_COSTS_BY_SUBTYPE,
  MIXED_USE_SUBTYPES,
  OFFICE_FEATURE_COSTS_BY_SUBTYPE,
  OFFICE_SUBTYPES,
  PARKING_FEATURE_COSTS_BY_SUBTYPE,
  PARKING_SUBTYPES,
  RECREATION_FEATURE_COSTS_BY_SUBTYPE,
  RECREATION_SUBTYPES,
  RETAIL_FEATURE_COSTS_BY_SUBTYPE,
  RETAIL_SUBTYPES,
  RESTAURANT_FEATURE_COSTS_BY_SUBTYPE,
  RESTAURANT_SUBTYPES,
  civicSubtypeHasSpecialFeatures,
  detectCivicFeatureIdsFromDescription,
  detectCivicSubtypeFromDescription,
  detectEducationalFeatureIdsFromDescription,
  detectEducationalSubtypeFromDescription,
  detectHealthcareFeatureIdsFromDescription,
  detectHospitalityFeatureIdsFromDescription,
  detectMixedUseFeatureIdsFromDescription,
  detectOfficeFeatureIdsFromDescription,
  detectParkingFeatureIdsFromDescription,
  detectRecreationFeatureIdsFromDescription,
  detectRecreationSubtypeFromDescription,
  detectRetailFeatureIdsFromDescription,
  detectSpecialtyFeatureIdsFromDescription,
  educationalSubtypeHasSpecialFeatures,
  filterSpecialFeaturesBySubtype,
  getAvailableSpecialFeatures,
  getCivicSpecialFeatures,
  getEducationalSpecialFeatures,
  getHealthcareSpecialFeatures,
  getHospitalitySpecialFeatures,
  getMixedUseSpecialFeatures,
  getOfficeSpecialFeatures,
  getParkingSpecialFeatures,
  getRecreationSpecialFeatures,
  getRetailSpecialFeatures,
  getRestaurantSpecialFeatures,
  getSpecialFeatureCost,
  getSpecialtySpecialFeatures,
  healthcareSubtypeHasSpecialFeatures,
  hospitalitySubtypeHasSpecialFeatures,
  mixedUseSubtypeHasSpecialFeatures,
  officeSubtypeHasSpecialFeatures,
  parkingSubtypeHasSpecialFeatures,
  recreationSubtypeHasSpecialFeatures,
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

const REQUIRED_EDUCATIONAL_MAPPING = {
  elementary_school: {
    gymnasium: 35,
    cafeteria: 30,
    playground: 20,
    computer_lab: 25,
    library: 25,
  },
  middle_school: {
    gymnasium: 40,
    cafeteria: 30,
    science_labs: 35,
    computer_lab: 25,
    auditorium: 45,
    athletic_field: 30,
  },
  high_school: {
    stadium: 60,
    field_house: 50,
    performing_arts_center: 55,
    science_labs: 40,
    vocational_shops: 45,
    media_center: 30,
  },
  university: {
    lecture_hall: 45,
    research_lab: 75,
    clean_room: 100,
    library: 40,
    student_center: 35,
  },
  community_college: {
    vocational_lab: 40,
    computer_lab: 25,
    library: 20,
    student_services: 15,
  },
} as const;

const REQUIRED_CIVIC_MAPPING = {
  library: {
    stacks_load_reinforcement: 35,
    acoustic_treatment: 25,
    daylighting_controls: 20,
    community_rooms: 20,
    maker_space_mep: 40,
  },
  courthouse: {
    courtroom: 50,
    jury_room: 25,
    holding_cells: 40,
    judges_chambers: 30,
    security_screening: 35,
    magnetometer_screening_lanes: 20,
    sallyport: 45,
    ballistic_glazing_package: 30,
    redundant_life_safety_power: 28,
  },
  government_building: {
    council_chambers: 40,
    secure_area: 35,
    public_plaza: 25,
    records_vault: 30,
  },
  community_center: {
    gymnasium: 35,
    kitchen: 25,
    multipurpose_room: 20,
    fitness_center: 20,
    outdoor_pavilion: 15,
  },
  public_safety: {
    apparatus_bay: 45,
    dispatch_center: 50,
    training_tower: 40,
    emergency_generator: 35,
    sally_port: 30,
  },
} as const;

const REQUIRED_RECREATION_MAPPING = {
  fitness_center: {
    pool: 45,
    basketball_court: 30,
    group_fitness: 20,
    spa_area: 35,
    juice_bar: 15,
  },
  sports_complex: {
    indoor_track: 35,
    multiple_courts: 40,
    weight_room: 25,
    locker_complex: 30,
    concessions: 20,
  },
  aquatic_center: {
    competition_pool: 60,
    diving_well: 50,
    lazy_river: 40,
    water_slides: 45,
    therapy_pool: 35,
  },
  recreation_center: {
    gymnasium: 30,
    game_room: 15,
    craft_room: 12,
    dance_studio: 20,
    outdoor_courts: 25,
  },
  stadium: {
    luxury_boxes: 75,
    club_level: 50,
    press_box: 40,
    video_board: 100,
    retractable_roof: 200,
  },
} as const;

const REQUIRED_MIXED_USE_MAPPING = {
  office_residential: {
    amenity_deck: 35,
    business_center: 20,
    conference_facility: 30,
  },
  retail_residential: {
    rooftop_deck: 30,
    parking_podium: 40,
    retail_plaza: 25,
  },
  hotel_retail: {
    conference_center: 45,
    restaurant: 50,
    spa: 55,
    retail_arcade: 30,
  },
  transit_oriented: {
    transit_plaza: 35,
    bike_facility: 20,
    pedestrian_bridge: 45,
    public_art: 15,
  },
  urban_mixed: {
    public_plaza: 40,
    green_roof: 35,
    parking_structure: 45,
    transit_connection: 30,
  },
} as const;

const REQUIRED_PARKING_MAPPING = {
  surface_parking: {
    covered_parking: 25,
    valet_booth: 15,
    ev_charging: 10,
    security_system: 8,
  },
  parking_garage: {
    automated_system: 45,
    ev_charging: 12,
    car_wash: 25,
    retail_space: 30,
    green_roof: 20,
  },
  underground_parking: {
    waterproofing: 35,
    sump_pumps: 20,
    vehicle_lifts: 30,
    security_booth: 15,
    ventilation_upgrade: 25,
  },
  automated_parking: {
    retrieval_speed: 40,
    redundant_systems: 35,
    valet_interface: 20,
    ev_charging_integration: 15,
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

describe("educational special features catalog", () => {
  it("is non-empty and matches backend-aligned subtype mapping keys/values", () => {
    const educationalFeatures = getEducationalSpecialFeatures();
    expect(educationalFeatures.length).toBeGreaterThan(0);
    expect(EDUCATIONAL_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_EDUCATIONAL_MAPPING);
  });

  it("resolves expected feature IDs for every educational subtype with no duplicates", () => {
    for (const subtype of EDUCATIONAL_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_EDUCATIONAL_MAPPING[subtype]).sort();
      const resolvedIds = getAvailableSpecialFeatures("educational", subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("keeps unknown educational subtype explicit (no silent subtype coercion)", () => {
    const unknownSubtypeResolved = getAvailableSpecialFeatures(
      "educational",
      "unknown_educational_variant"
    );
    expect(unknownSubtypeResolved).toEqual([]);

    const noSubtypeResolved = getAvailableSpecialFeatures("educational");
    const allExpectedIds = Array.from(
      new Set(
        Object.values(REQUIRED_EDUCATIONAL_MAPPING).flatMap((mapping) =>
          Object.keys(mapping)
        )
      )
    );
    expect(noSubtypeResolved.map((feature) => feature.id)).toEqual(
      expect.arrayContaining(allExpectedIds)
    );
  });

  it("resolves subtype-specific costs only for valid educational subtype feature IDs", () => {
    for (const subtype of EDUCATIONAL_SUBTYPES) {
      for (const [featureId, expectedCost] of Object.entries(
        REQUIRED_EDUCATIONAL_MAPPING[subtype]
      )) {
        expect(getSpecialFeatureCost("educational", featureId, subtype)).toBe(
          expectedCost
        );
      }
    }

    expect(
      getSpecialFeatureCost("educational", "stadium", "elementary_school")
    ).toBeUndefined();
    expect(
      getSpecialFeatureCost(
        "educational",
        "community_college_workforce_program_shift",
        "community_college"
      )
    ).toBeUndefined();
  });

  it("detects educational subtype cues for all five profiles and keeps generic educational explicit", () => {
    expect(
      detectEducationalSubtypeFromDescription(
        "New 42000 sf elementary school with classroom wing in Nashville, TN"
      )
    ).toBe("elementary_school");
    expect(
      detectEducationalSubtypeFromDescription(
        "New 68000 sf middle school with media lab and gymnasium in Nashville, TN"
      )
    ).toBe("middle_school");
    expect(
      detectEducationalSubtypeFromDescription(
        "New 115000 sf high school with field house and performing arts hall in Nashville, TN"
      )
    ).toBe("high_school");
    expect(
      detectEducationalSubtypeFromDescription(
        "New 185000 sf university science and lecture complex in Nashville, TN"
      )
    ).toBe("university");
    expect(
      detectEducationalSubtypeFromDescription(
        "Renovate 62000 sf community college workforce training center in Nashville, TN"
      )
    ).toBe("community_college");

    expect(
      detectEducationalSubtypeFromDescription(
        "New 38000 sf educational building in Nashville, TN"
      )
    ).toBeUndefined();
  });

  it("detects educational feature IDs from subtype-specific scope cues", () => {
    const highSchoolDetected = detectEducationalFeatureIdsFromDescription(
      "High school program with field house, stadium, performing arts center, and science labs."
    );
    expect(highSchoolDetected).toEqual(
      expect.arrayContaining([
        "field_house",
        "stadium",
        "performing_arts_center",
        "science_labs",
      ])
    );

    const communityCollegeDetected = detectEducationalFeatureIdsFromDescription(
      "Community college expansion with vocational lab and student services modernization."
    );
    expect(communityCollegeDetected).toEqual(
      expect.arrayContaining(["vocational_lab", "student_services"])
    );
  });

  it("educational subtype helper returns true for all five educational subtypes", () => {
    for (const subtype of EDUCATIONAL_SUBTYPES) {
      expect(educationalSubtypeHasSpecialFeatures(subtype)).toBe(true);
    }
  });
});

describe("civic special features catalog", () => {
  it("is non-empty and matches backend-aligned subtype mapping keys/values", () => {
    const civicFeatures = getCivicSpecialFeatures();
    expect(civicFeatures.length).toBeGreaterThan(0);
    expect(CIVIC_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_CIVIC_MAPPING);
  });

  it("resolves expected feature IDs for each civic subtype with no duplicates", () => {
    for (const subtype of CIVIC_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_CIVIC_MAPPING[subtype]).sort();
      const resolvedIds = getAvailableSpecialFeatures("civic", subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("keeps unknown civic subtype explicit (no silent subtype coercion)", () => {
    const unknownSubtypeResolved = getAvailableSpecialFeatures(
      "civic",
      "unknown_civic_variant"
    );
    expect(unknownSubtypeResolved).toEqual([]);
  });

  it("resolves subtype-specific civic costs only for valid subtype feature IDs", () => {
    for (const subtype of CIVIC_SUBTYPES) {
      for (const [featureId, expectedCost] of Object.entries(
        REQUIRED_CIVIC_MAPPING[subtype]
      )) {
        expect(getSpecialFeatureCost("civic", featureId, subtype)).toBe(expectedCost);
      }
    }

    expect(
      getSpecialFeatureCost("civic", "courtroom", "library")
    ).toBeUndefined();
    expect(
      getSpecialFeatureCost("civic", "maker_space_mep", "courthouse")
    ).toBeUndefined();
  });

  it("detects civic subtype cues for all five profiles and keeps unknown civic subtype explicit", () => {
    expect(
      detectCivicSubtypeFromDescription(
        "New 42000 sf public library with makerspace and community rooms in Nashville, TN"
      )
    ).toBe("library");
    expect(
      detectCivicSubtypeFromDescription(
        "New 85000 sf courthouse and justice center with jury rooms in Nashville, TN"
      )
    ).toBe("courthouse");
    expect(
      detectCivicSubtypeFromDescription(
        "Renovate 65000 sf city hall government building with council chambers in Nashville, TN"
      )
    ).toBe("government_building");
    expect(
      detectCivicSubtypeFromDescription(
        "New 38000 sf community center with gymnasium and multipurpose rooms in Nashville, TN"
      )
    ).toBe("community_center");
    expect(
      detectCivicSubtypeFromDescription(
        "New 52000 sf public safety facility with fire station apparatus bay and dispatch center in Nashville, TN"
      )
    ).toBe("public_safety");

    expect(
      detectCivicSubtypeFromDescription(
        "New 36000 sf civic building in Nashville, TN"
      )
    ).toBeUndefined();
  });

  it("detects civic feature IDs from subtype-specific keywords", () => {
    const libraryDetected = detectCivicFeatureIdsFromDescription(
      "Public library with book stacks reinforcement, maker space MEP, daylighting controls, and acoustic treatment."
    );
    expect(libraryDetected).toEqual(
      expect.arrayContaining([
        "stacks_load_reinforcement",
        "maker_space_mep",
        "daylighting_controls",
        "acoustic_treatment",
      ])
    );

    const courthouseDetected = detectCivicFeatureIdsFromDescription(
      "Courthouse with courtroom expansion, jury room upgrades, magnetometer screening lanes, and ballistic glazing package."
    );
    expect(courthouseDetected).toEqual(
      expect.arrayContaining([
        "courtroom",
        "jury_room",
        "magnetometer_screening_lanes",
        "ballistic_glazing_package",
      ])
    );

    const publicSafetyDetected = detectCivicFeatureIdsFromDescription(
      "Public safety station with apparatus bay, dispatch center, emergency generator, and training tower."
    );
    expect(publicSafetyDetected).toEqual(
      expect.arrayContaining([
        "apparatus_bay",
        "dispatch_center",
        "emergency_generator",
        "training_tower",
      ])
    );
  });

  it("guards civic library detection from educational feature-ID leakage after civic filtering", () => {
    const subtype = "library";
    const allowedFeatureIds = new Set(
      getAvailableSpecialFeatures("civic", subtype).map((feature) => feature.id)
    );
    const rawDetected = [
      ...detectEducationalFeatureIdsFromDescription(
        "Public library with learning commons, maker space, and reinforced book stacks."
      ),
      ...detectCivicFeatureIdsFromDescription(
        "Public library with learning commons, maker space, and reinforced book stacks."
      ),
    ];

    const filteredDetected = rawDetected.filter((featureId) =>
      allowedFeatureIds.has(featureId)
    );
    expect(filteredDetected).not.toContain("library");
    expect(filteredDetected).toEqual(
      expect.arrayContaining(["stacks_load_reinforcement", "maker_space_mep"])
    );
  });

  it("civic subtype helper returns true for all five civic subtypes", () => {
    for (const subtype of CIVIC_SUBTYPES) {
      expect(civicSubtypeHasSpecialFeatures(subtype)).toBe(true);
    }
  });
});

describe("recreation special features catalog", () => {
  it("is non-empty and matches backend-aligned subtype mapping keys/values", () => {
    const recreationFeatures = getRecreationSpecialFeatures();
    expect(recreationFeatures.length).toBeGreaterThan(0);
    expect(RECREATION_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_RECREATION_MAPPING);
  });

  it("resolves expected feature IDs for each recreation subtype with no duplicates", () => {
    for (const subtype of RECREATION_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_RECREATION_MAPPING[subtype]).sort();
      const resolvedIds = getAvailableSpecialFeatures("recreation", subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("keeps unknown recreation subtype explicit (no silent subtype coercion)", () => {
    const unknownSubtypeResolved = getAvailableSpecialFeatures(
      "recreation",
      "unknown_recreation_variant"
    );
    expect(unknownSubtypeResolved).toEqual([]);

    expect(
      getSpecialFeatureCost("recreation", "competition_pool", "unknown_recreation_variant")
    ).toBeUndefined();
  });

  it("resolves recreation costs only for valid subtype feature IDs", () => {
    for (const subtype of RECREATION_SUBTYPES) {
      for (const [featureId, expectedCost] of Object.entries(
        REQUIRED_RECREATION_MAPPING[subtype]
      )) {
        expect(getSpecialFeatureCost("recreation", featureId, subtype)).toBe(expectedCost);
      }
    }

    expect(
      getSpecialFeatureCost("recreation", "retractable_roof", "fitness_center")
    ).toBeUndefined();
    expect(
      getSpecialFeatureCost("recreation", "pool", "stadium")
    ).toBeUndefined();
  });

  it("detects recreation subtype cues for all five profiles and keeps unknown explicit", () => {
    expect(
      detectRecreationSubtypeFromDescription(
        "New 42000 sf fitness center with cardio deck and strength rooms in Nashville, TN"
      )
    ).toBe("fitness_center");
    expect(
      detectRecreationSubtypeFromDescription(
        "Build a 95000 sf sports complex with multiple courts and indoor track in Nashville, TN"
      )
    ).toBe("sports_complex");
    expect(
      detectRecreationSubtypeFromDescription(
        "New 80000 sf aquatic center with competition pool and natatorium in Nashville, TN"
      )
    ).toBe("aquatic_center");
    expect(
      detectRecreationSubtypeFromDescription(
        "Renovate a 60000 sf recreation center with gymnasium and activity rooms in Nashville, TN"
      )
    ).toBe("recreation_center");
    expect(
      detectRecreationSubtypeFromDescription(
        "Build a 320000 sf stadium with seating bowl and event concourse in Nashville, TN"
      )
    ).toBe("stadium");

    expect(
      detectRecreationSubtypeFromDescription(
        "New 38000 sf recreation facility in Nashville, TN"
      )
    ).toBeUndefined();
  });

  it("guards recreation subtype detection from hospitality and civic collisions", () => {
    expect(
      detectRecreationSubtypeFromDescription(
        "Build a limited service hotel with rooftop pool and breakfast area in Nashville, TN"
      )
    ).toBeUndefined();
    expect(
      detectRecreationSubtypeFromDescription(
        "New municipal community center with council chambers in Nashville, TN"
      )
    ).toBeUndefined();
  });

  it("detects recreation feature IDs from subtype-specific keywords", () => {
    const fitnessDetected = detectRecreationFeatureIdsFromDescription(
      "Fitness center with basketball courts, group fitness studio, spa area, and juice bar."
    );
    expect(fitnessDetected).toEqual(
      expect.arrayContaining([
        "basketball_court",
        "group_fitness",
        "spa_area",
        "juice_bar",
      ])
    );

    const aquaticDetected = detectRecreationFeatureIdsFromDescription(
      "Aquatic center with competition pool, diving well, lazy river, and water slides."
    );
    expect(aquaticDetected).toEqual(
      expect.arrayContaining([
        "competition_pool",
        "diving_well",
        "lazy_river",
        "water_slides",
      ])
    );

    const stadiumDetected = detectRecreationFeatureIdsFromDescription(
      "Stadium with luxury boxes, club level, press box, video board, and retractable roof."
    );
    expect(stadiumDetected).toEqual(
      expect.arrayContaining([
        "luxury_boxes",
        "club_level",
        "press_box",
        "video_board",
        "retractable_roof",
      ])
    );
  });

  it("recreation subtype helper returns true for all five recreation subtypes", () => {
    for (const subtype of RECREATION_SUBTYPES) {
      expect(recreationSubtypeHasSpecialFeatures(subtype)).toBe(true);
    }
  });
});

describe("mixed_use special features catalog", () => {
  it("is non-empty and matches backend-aligned subtype mapping keys/values", () => {
    const mixedUseFeatures = getMixedUseSpecialFeatures();
    expect(mixedUseFeatures.length).toBeGreaterThan(0);
    expect(MIXED_USE_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_MIXED_USE_MAPPING);
  });

  it("resolves expected feature IDs for each mixed_use subtype with no duplicates", () => {
    const mixedUseFeatures = getMixedUseSpecialFeatures();

    for (const subtype of MIXED_USE_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_MIXED_USE_MAPPING[subtype]).sort();
      const resolvedIds = filterSpecialFeaturesBySubtype(mixedUseFeatures, subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("keeps unknown mixed_use subtype explicit and preserves hotel_residential alias", () => {
    const unknownSubtypeResolved = getAvailableSpecialFeatures(
      "mixed_use",
      "unknown_mixed_use_variant"
    );
    expect(unknownSubtypeResolved).toEqual([]);

    const aliasResolved = getAvailableSpecialFeatures("mixed_use", "hotel_residential").map(
      (feature) => feature.id
    );
    const canonicalResolved = getAvailableSpecialFeatures("mixed_use", "hotel_retail").map(
      (feature) => feature.id
    );
    expect(aliasResolved.sort()).toEqual(canonicalResolved.sort());
  });

  it("resolves mixed_use subtype-specific costs only for valid subtype feature IDs", () => {
    for (const subtype of MIXED_USE_SUBTYPES) {
      const expectedEntries = REQUIRED_MIXED_USE_MAPPING[subtype];
      for (const [featureId, expectedCost] of Object.entries(expectedEntries)) {
        expect(getSpecialFeatureCost("mixed_use", featureId, subtype)).toBe(expectedCost);
      }
    }

    expect(
      getSpecialFeatureCost("mixed_use", "retail_arcade", "office_residential")
    ).toBeUndefined();
    expect(
      getSpecialFeatureCost("mixed_use", "pedestrian_bridge", "hotel_retail")
    ).toBeUndefined();
  });

  it("detects mixed_use feature IDs from subtype-specific scope keywords", () => {
    const officeResidentialDetected = detectMixedUseFeatureIdsFromDescription(
      "Mixed-use office residential tower with amenity deck, business center, and conference facility."
    );
    expect(officeResidentialDetected).toEqual(
      expect.arrayContaining(["amenity_deck", "business_center", "conference_facility"])
    );

    const hotelRetailDetected = detectMixedUseFeatureIdsFromDescription(
      "Hotel retail podium with conference center, on-site restaurant, spa, and retail arcade."
    );
    expect(hotelRetailDetected).toEqual(
      expect.arrayContaining(["conference_center", "restaurant", "spa", "retail_arcade"])
    );

    const transitDetected = detectMixedUseFeatureIdsFromDescription(
      "Transit oriented project with transit plaza, bike facility, pedestrian bridge, and public art."
    );
    expect(transitDetected).toEqual(
      expect.arrayContaining([
        "transit_plaza",
        "bike_facility",
        "pedestrian_bridge",
        "public_art",
      ])
    );
  });

  it("mixed_use subtype helper returns true for all canonical mixed_use subtypes", () => {
    for (const subtype of MIXED_USE_SUBTYPES) {
      expect(mixedUseSubtypeHasSpecialFeatures(subtype)).toBe(true);
    }
    expect(mixedUseSubtypeHasSpecialFeatures("hotel_residential")).toBe(true);
  });
});

describe("parking special features catalog", () => {
  it("is non-empty and matches backend-aligned subtype mapping keys/values", () => {
    const parkingFeatures = getParkingSpecialFeatures();
    expect(parkingFeatures.length).toBeGreaterThan(0);
    expect(PARKING_FEATURE_COSTS_BY_SUBTYPE).toEqual(REQUIRED_PARKING_MAPPING);
  });

  it("resolves expected feature IDs for every parking subtype with no duplicates", () => {
    const parkingFeatures = getParkingSpecialFeatures();

    for (const subtype of PARKING_SUBTYPES) {
      const expectedIds = Object.keys(REQUIRED_PARKING_MAPPING[subtype]).sort();
      const resolvedIds = filterSpecialFeaturesBySubtype(parkingFeatures, subtype).map(
        (feature) => feature.id
      );
      const uniqueResolvedIds = Array.from(new Set(resolvedIds));

      expect(uniqueResolvedIds.length).toBe(resolvedIds.length);
      expect(uniqueResolvedIds.sort()).toEqual(expectedIds);
    }
  });

  it("keeps unknown parking subtype explicit", () => {
    const unknownSubtypeResolved = getAvailableSpecialFeatures(
      "parking",
      "unknown_parking_variant"
    );
    expect(unknownSubtypeResolved).toEqual([]);
  });

  it("resolves subtype-aware parking feature costs and rejects mismatched subtype feature IDs", () => {
    for (const subtype of PARKING_SUBTYPES) {
      const expectedEntries = REQUIRED_PARKING_MAPPING[subtype];
      for (const [featureId, expectedCost] of Object.entries(expectedEntries)) {
        expect(getSpecialFeatureCost("parking", featureId, subtype)).toBe(expectedCost);
      }
    }

    expect(getSpecialFeatureCost("parking", "car_wash", "surface_parking")).toBeUndefined();
    expect(getSpecialFeatureCost("parking", "vehicle_lifts", "parking_garage")).toBeUndefined();
  });

  it("detects parking feature IDs from subtype-specific parking scope cues", () => {
    const surfaceDetected = detectParkingFeatureIdsFromDescription(
      "Surface parking lot expansion with covered parking, valet booth, EV charging, and parking security system."
    );
    expect(surfaceDetected).toEqual(
      expect.arrayContaining([
        "covered_parking",
        "valet_booth",
        "ev_charging",
        "security_system",
      ])
    );

    const undergroundDetected = detectParkingFeatureIdsFromDescription(
      "Underground parking addition with waterproofing package, sump pumps, security booth, and garage ventilation upgrade."
    );
    expect(undergroundDetected).toEqual(
      expect.arrayContaining([
        "waterproofing",
        "sump_pumps",
        "security_booth",
        "ventilation_upgrade",
      ])
    );
  });

  it("parking subtype helper returns true for all canonical parking subtypes", () => {
    for (const subtype of PARKING_SUBTYPES) {
      expect(parkingSubtypeHasSpecialFeatures(subtype)).toBe(true);
    }
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
