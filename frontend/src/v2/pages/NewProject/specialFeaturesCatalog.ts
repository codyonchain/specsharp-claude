export type SpecialFeatureOption = {
  id: string;
  name: string;
  cost?: number;
  costPerSF?: number;
  costPerSFBySubtype?: Record<string, number>;
  description: string;
  allowedSubtypes?: string[];
};

export const RESTAURANT_SUBTYPES = [
  "quick_service",
  "full_service",
  "fine_dining",
  "cafe",
  "bar_tavern",
] as const;

export type RestaurantSubtype = (typeof RESTAURANT_SUBTYPES)[number];

export const RESTAURANT_FEATURE_COSTS_BY_SUBTYPE: Record<
  RestaurantSubtype,
  Record<string, number>
> = {
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
};

export const HOSPITALITY_SUBTYPES = [
  "limited_service_hotel",
  "full_service_hotel",
] as const;

export type HospitalitySubtype = (typeof HOSPITALITY_SUBTYPES)[number];

export const HOSPITALITY_FEATURE_COSTS_BY_SUBTYPE: Record<
  HospitalitySubtype,
  Record<string, number>
> = {
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
};

export const SPECIALTY_SUBTYPES = [
  "data_center",
  "laboratory",
  "self_storage",
  "car_dealership",
  "broadcast_facility",
] as const;

export type SpecialtySubtype = (typeof SPECIALTY_SUBTYPES)[number];

export const SPECIALTY_FEATURE_COSTS_BY_SUBTYPE: Record<
  SpecialtySubtype,
  Record<string, number>
> = {
  data_center: {
    utility_substation: 140,
    generator_plant: 120,
    chilled_water_plant: 110,
    dual_fiber_meet_me_room: 45,
    integrated_commissioning: 55,
  },
  laboratory: {
    cleanroom_suite: 95,
    vivarium_support: 70,
    process_gas_distribution: 65,
    redundancy_exhaust_stack: 50,
  },
  self_storage: {
    climate_control_zones: 18,
    biometric_access_control: 12,
    high_density_cctv: 10,
    rv_power_pedestals: 9,
  },
  car_dealership: {
    expanded_service_bays: 28,
    ev_fast_charging_hub: 22,
    automated_car_wash_tunnel: 18,
    inventory_photo_bay: 8,
  },
  broadcast_facility: {
    floating_studio_floors: 40,
    control_room_signal_core: 35,
    acoustic_shell_upgrade: 30,
    satellite_uplink_pad: 16,
  },
};

const RESTAURANT_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  drive_thru: {
    name: "Drive-Thru",
    description: "Site circulation, canopy, order points, and dedicated service lane buildout.",
  },
  outdoor_seating: {
    name: "Outdoor Seating",
    description: "Patio or exterior dining area with finishes, lighting, and utility coordination.",
  },
  play_area: {
    name: "Play Area",
    description: "Indoor or outdoor customer play zone with specialty flooring and safety upgrades.",
  },
  double_drive_thru: {
    name: "Double Drive-Thru",
    description: "Dual-lane drive-thru expansion with queue controls and menu order infrastructure.",
  },
  digital_menu_boards: {
    name: "Digital Menu Boards",
    description: "Integrated digital signage package for interior or drive-thru ordering.",
  },
  bar: {
    name: "Bar Program",
    description: "Front-of-house bar buildout with beverage service infrastructure.",
  },
  private_dining: {
    name: "Private Dining",
    description: "Dedicated private dining rooms with upgraded finishes and acoustic separation.",
  },
  wine_cellar: {
    name: "Wine Cellar",
    description: "Temperature-controlled wine storage and display room.",
  },
  live_kitchen: {
    name: "Live Kitchen",
    description: "Open-kitchen presentation buildout with guest-facing service counter.",
  },
  rooftop_dining: {
    name: "Rooftop Dining",
    description: "Rooftop dining deck with structural, life-safety, and service upgrades.",
  },
  valet_parking: {
    name: "Valet Parking",
    description: "Valet operations area with ingress/egress and curbside management upgrades.",
  },
  chef_table: {
    name: "Chef Table",
    description: "Premium chef-table service area integrated with kitchen operations.",
  },
  dry_aging_room: {
    name: "Dry Aging Room",
    description: "Controlled-environment dry-aging room with specialty mechanical systems.",
  },
  pastry_kitchen: {
    name: "Pastry Kitchen",
    description: "Dedicated pastry prep kitchen with specialized equipment utility requirements.",
  },
  sommelier_station: {
    name: "Sommelier Station",
    description: "Wine service station with storage, staging, and guest presentation space.",
  },
  bakery_display: {
    name: "Bakery Display",
    description: "Front counter bakery display with refrigeration and merchandising casework.",
  },
  lounge_area: {
    name: "Lounge Area",
    description: "Extended customer lounge seating with comfort and lighting upgrades.",
  },
  meeting_room: {
    name: "Meeting Room",
    description: "Small private meeting room buildout for community or co-working use.",
  },
  live_music_stage: {
    name: "Live Music Stage",
    description: "Performance stage with acoustic treatment and production support infrastructure.",
  },
  game_room: {
    name: "Game Room",
    description: "Dedicated entertainment area with specialty finishes and equipment tie-ins.",
  },
  rooftop_bar: {
    name: "Rooftop Bar",
    description: "Rooftop bar and service area with structural and MEP support.",
  },
  private_party_room: {
    name: "Private Party Room",
    description: "Dedicated event room with service access and flexible seating layout.",
  },
  craft_beer_system: {
    name: "Craft Beer System",
    description: "Specialty draft system installation with keg storage and line routing.",
  },
};

const HOSPITALITY_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  breakfast_area: {
    name: "Breakfast Area",
    description: "Guest breakfast area with serving line and seating support buildout.",
  },
  fitness_center: {
    name: "Fitness Center",
    description: "Dedicated fitness room with flooring, ventilation, and equipment-ready utilities.",
  },
  business_center: {
    name: "Business Center",
    description: "Shared business center with workstations, print area, and connectivity infrastructure.",
  },
  pool: {
    name: "Pool",
    description: "Hospitality pool buildout with deck, life-safety systems, and support spaces.",
  },
  ballroom: {
    name: "Ballroom",
    description: "Large event ballroom with premium finishes, lighting, and acoustic treatment.",
  },
  restaurant: {
    name: "Restaurant",
    description: "On-site restaurant buildout with back-of-house and guest dining infrastructure.",
  },
  spa: {
    name: "Spa",
    description: "Spa and wellness suite with treatment rooms and specialized MEP requirements.",
  },
  conference_center: {
    name: "Conference Center",
    description: "Flexible conference center with divisible meeting rooms and AV infrastructure.",
  },
  rooftop_bar: {
    name: "Rooftop Bar",
    description: "Rooftop bar venue with structural, weatherproofing, and service utility upgrades.",
  },
};

const SPECIALTY_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  utility_substation: {
    name: "Utility Substation",
    description: "Dedicated medium-voltage utility substation and distribution yard integration.",
  },
  generator_plant: {
    name: "Generator Plant",
    description: "N+1 generator plant with day tanks, controls, and paralleling switchgear.",
  },
  chilled_water_plant: {
    name: "Chilled Water Plant",
    description: "Central chilled-water plant with CRAH loop and redundancy-ready headers.",
  },
  dual_fiber_meet_me_room: {
    name: "Dual Fiber Meet-Me Room",
    description: "Diverse carrier entry paths with hardened meet-me room buildout.",
  },
  integrated_commissioning: {
    name: "Integrated Commissioning",
    description: "Cross-system integrated testing program for power, cooling, and controls.",
  },
  cleanroom_suite: {
    name: "Cleanroom Suite",
    description: "Validated cleanroom suite with envelope controls and specialty finishes.",
  },
  vivarium_support: {
    name: "Vivarium Support",
    description: "Vivarium support spaces with dedicated MEP zoning and pressure controls.",
  },
  process_gas_distribution: {
    name: "Process Gas Distribution",
    description: "Lab-grade process gas manifold and distribution backbone.",
  },
  redundancy_exhaust_stack: {
    name: "Redundant Exhaust Stack",
    description: "Redundant exhaust stack package with monitoring and emergency bypass controls.",
  },
  climate_control_zones: {
    name: "Climate Control Zones",
    description: "Expanded climate-controlled unit zoning and controls package.",
  },
  biometric_access_control: {
    name: "Biometric Access Control",
    description: "Biometric access control at key ingress points with audit logging.",
  },
  high_density_cctv: {
    name: "High Density CCTV",
    description: "High-density camera coverage with retention and monitoring infrastructure.",
  },
  rv_power_pedestals: {
    name: "RV Power Pedestals",
    description: "Dedicated RV storage power pedestals with billing-ready metering.",
  },
  expanded_service_bays: {
    name: "Expanded Service Bays",
    description: "Additional service bays with lifts, exhaust extraction, and tooling support.",
  },
  ev_fast_charging_hub: {
    name: "EV Fast Charging Hub",
    description: "Fast-charge hub with utility upgrade, switchgear, and customer staging.",
  },
  automated_car_wash_tunnel: {
    name: "Automated Car Wash Tunnel",
    description: "Integrated car wash tunnel with water treatment and reclaim equipment.",
  },
  inventory_photo_bay: {
    name: "Inventory Photo Bay",
    description: "Controlled lighting and backdrop bay for digital inventory merchandising.",
  },
  floating_studio_floors: {
    name: "Floating Studio Floors",
    description: "Floating studio floor assemblies for vibration and noise isolation.",
  },
  control_room_signal_core: {
    name: "Control Room Signal Core",
    description: "Core control-room signal routing and monitoring infrastructure package.",
  },
  acoustic_shell_upgrade: {
    name: "Acoustic Shell Upgrade",
    description: "Acoustic shell upgrade with high-performance isolation detailing.",
  },
  satellite_uplink_pad: {
    name: "Satellite Uplink Pad",
    description: "Hardened satellite uplink pad and conduit package for field/broadcast ops.",
  },
};

export const filterSpecialFeaturesBySubtype = (
  features: SpecialFeatureOption[],
  subtype?: string
): SpecialFeatureOption[] => {
  return features.filter((feature) => {
    if (!feature.allowedSubtypes || feature.allowedSubtypes.length === 0) {
      return true;
    }
    if (!subtype) {
      return true;
    }
    return feature.allowedSubtypes.includes(subtype);
  });
};

const createRestaurantSpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of RESTAURANT_SUBTYPES) {
    const entries = RESTAURANT_FEATURE_COSTS_BY_SUBTYPE[subtype];
    for (const [featureId, costPerSF] of Object.entries(entries)) {
      if (!byFeatureId[featureId]) {
        byFeatureId[featureId] = {
          costPerSFBySubtype: {},
          allowedSubtypes: [],
        };
      }
      byFeatureId[featureId].costPerSFBySubtype[subtype] = costPerSF;
      byFeatureId[featureId].allowedSubtypes.push(subtype);
    }
  }

  return Object.entries(byFeatureId)
    .sort(([featureA], [featureB]) => featureA.localeCompare(featureB))
    .map(([featureId, featureData]) => {
      const metadata = RESTAURANT_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Restaurant subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: RESTAURANT_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const RESTAURANT_SPECIAL_FEATURES = createRestaurantSpecialFeatures();

export const getRestaurantSpecialFeatures = (): SpecialFeatureOption[] =>
  RESTAURANT_SPECIAL_FEATURES;

const createHospitalitySpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of HOSPITALITY_SUBTYPES) {
    const entries = HOSPITALITY_FEATURE_COSTS_BY_SUBTYPE[subtype];
    for (const [featureId, costPerSF] of Object.entries(entries)) {
      if (!byFeatureId[featureId]) {
        byFeatureId[featureId] = {
          costPerSFBySubtype: {},
          allowedSubtypes: [],
        };
      }
      byFeatureId[featureId].costPerSFBySubtype[subtype] = costPerSF;
      byFeatureId[featureId].allowedSubtypes.push(subtype);
    }
  }

  return Object.entries(byFeatureId)
    .sort(([featureA], [featureB]) => featureA.localeCompare(featureB))
    .map(([featureId, featureData]) => {
      const metadata = HOSPITALITY_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Hospitality subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: HOSPITALITY_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const HOSPITALITY_SPECIAL_FEATURES = createHospitalitySpecialFeatures();

export const getHospitalitySpecialFeatures = (): SpecialFeatureOption[] =>
  HOSPITALITY_SPECIAL_FEATURES;

const createSpecialtySpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of SPECIALTY_SUBTYPES) {
    const entries = SPECIALTY_FEATURE_COSTS_BY_SUBTYPE[subtype];
    for (const [featureId, costPerSF] of Object.entries(entries)) {
      if (!byFeatureId[featureId]) {
        byFeatureId[featureId] = {
          costPerSFBySubtype: {},
          allowedSubtypes: [],
        };
      }
      byFeatureId[featureId].costPerSFBySubtype[subtype] = costPerSF;
      byFeatureId[featureId].allowedSubtypes.push(subtype);
    }
  }

  return Object.entries(byFeatureId)
    .sort(([featureA], [featureB]) => featureA.localeCompare(featureB))
    .map(([featureId, featureData]) => {
      const metadata = SPECIALTY_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Specialty subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: SPECIALTY_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const SPECIALTY_SPECIAL_FEATURES = createSpecialtySpecialFeatures();

export const getSpecialtySpecialFeatures = (): SpecialFeatureOption[] =>
  SPECIALTY_SPECIAL_FEATURES;

const RESTAURANT_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  {
    featureId: "drive_thru",
    patterns: [/drive[\s-]?thru/i, /drive[\s-]?through/i],
  },
  {
    featureId: "outdoor_seating",
    patterns: [/outdoor seating/i, /\bpatio\b/i],
  },
  {
    featureId: "bar",
    patterns: [/\bfull bar\b/i, /\bbar program\b/i],
  },
  {
    featureId: "wine_cellar",
    patterns: [/\bwine cellar\b/i],
  },
  {
    featureId: "chef_table",
    patterns: [/\bchef'?s table\b/i, /\bchef table\b/i],
  },
  {
    featureId: "bakery_display",
    patterns: [/\bbakery display\b/i],
  },
  {
    featureId: "live_music_stage",
    patterns: [/\blive music\b/i],
  },
  {
    featureId: "rooftop_dining",
    patterns: [/\brooftop\b/i],
  },
  {
    featureId: "rooftop_bar",
    patterns: [/\brooftop\b/i],
  },
  {
    featureId: "private_dining",
    patterns: [/\bprivate dining\b/i],
  },
  {
    featureId: "private_party_room",
    patterns: [/\bprivate party room\b/i, /\bparty room\b/i],
  },
];

export const detectRestaurantFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of RESTAURANT_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

const HOSPITALITY_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  {
    featureId: "breakfast_area",
    patterns: [/\bbreakfast area\b/i, /\bcomplimentary breakfast\b/i],
  },
  {
    featureId: "fitness_center",
    patterns: [/\bfitness center\b/i, /\bhotel gym\b/i],
  },
  {
    featureId: "business_center",
    patterns: [/\bbusiness center\b/i],
  },
  {
    featureId: "pool",
    patterns: [/\bpool\b/i],
  },
  {
    featureId: "ballroom",
    patterns: [/\bballroom\b/i],
  },
  {
    featureId: "restaurant",
    patterns: [/\bsignature restaurant\b/i, /\bon[-\s]?site restaurant\b/i, /\bhotel restaurant\b/i],
  },
  {
    featureId: "spa",
    patterns: [/\bspa\b/i],
  },
  {
    featureId: "conference_center",
    patterns: [/\bconference center\b/i, /\bconference facilities?\b/i],
  },
  {
    featureId: "rooftop_bar",
    patterns: [/\brooftop bar\b/i, /\broof[\s-]?top bar\b/i],
  },
];

export const detectHospitalityFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of HOSPITALITY_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

const SPECIALTY_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  {
    featureId: "utility_substation",
    patterns: [/\bsubstation\b/i, /\bmedium[-\s]?voltage\b/i],
  },
  {
    featureId: "generator_plant",
    patterns: [/\bgenerator plant\b/i, /\bbackup generators?\b/i, /\bn\+1\b/i],
  },
  {
    featureId: "chilled_water_plant",
    patterns: [/\bchilled water\b/i, /\bcooling plant\b/i, /\bcrah\b/i],
  },
  {
    featureId: "dual_fiber_meet_me_room",
    patterns: [/\bdual fiber\b/i, /\bmeet[-\s]?me room\b/i, /\bdiverse carrier\b/i],
  },
  {
    featureId: "integrated_commissioning",
    patterns: [/\bintegrated commissioning\b/i, /\bist\b/i],
  },
  {
    featureId: "cleanroom_suite",
    patterns: [/\bclean[-\s]?room\b/i],
  },
  {
    featureId: "process_gas_distribution",
    patterns: [/\bprocess gas\b/i, /\blab gases?\b/i],
  },
  {
    featureId: "climate_control_zones",
    patterns: [/\bclimate[-\s]?control(?:led)?\b/i],
  },
  {
    featureId: "biometric_access_control",
    patterns: [/\bbiometric\b/i, /\baccess control\b/i],
  },
  {
    featureId: "expanded_service_bays",
    patterns: [/\bservice bays?\b/i, /\bservice lanes?\b/i],
  },
  {
    featureId: "ev_fast_charging_hub",
    patterns: [/\bev fast charging\b/i, /\bdc fast charger\b/i],
  },
  {
    featureId: "floating_studio_floors",
    patterns: [/\bfloating floor\b/i, /\bstudio floor isolation\b/i],
  },
  {
    featureId: "control_room_signal_core",
    patterns: [/\bcontrol room\b/i, /\bsignal core\b/i],
  },
  {
    featureId: "acoustic_shell_upgrade",
    patterns: [/\bacoustic shell\b/i, /\bsound isolation\b/i],
  },
];

export const detectSpecialtyFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of SPECIALTY_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

export const restaurantSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(RESTAURANT_SPECIAL_FEATURES, subtype).length > 0;

export const hospitalitySubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(HOSPITALITY_SPECIAL_FEATURES, subtype).length > 0;

export const specialtySubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(SPECIALTY_SPECIAL_FEATURES, subtype).length > 0;
