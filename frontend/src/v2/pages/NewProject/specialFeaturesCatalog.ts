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

export const restaurantSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(RESTAURANT_SPECIAL_FEATURES, subtype).length > 0;
