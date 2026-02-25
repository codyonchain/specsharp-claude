export const MIXED_USE_SUBTYPES = [
  "office_residential",
  "retail_residential",
  "hotel_retail",
  "transit_oriented",
  "urban_mixed",
] as const;

export type MixedUseSubtype = (typeof MIXED_USE_SUBTYPES)[number];

export const MIXED_USE_COMPONENTS = [
  "office",
  "residential",
  "retail",
  "hotel",
  "transit",
] as const;

export type MixedUseComponent = (typeof MIXED_USE_COMPONENTS)[number];

export type MixedUseSplitPattern =
  | "component_percent"
  | "ratio_pair"
  | "mostly_component"
  | "heavy_component"
  | "balanced_pair";

export type MixedUseSplitSource = "user_input" | "nlp_detected" | "default";

export type MixedUseSplitValue = Record<MixedUseComponent, number>;

export type MixedUseAliasMapping = {
  from: "hotel_residential";
  to: "hotel_retail";
  reason: "hotel_residential_alias";
  matched_pattern: string;
};

export type MixedUseSubtypeDetection = {
  subtype?: MixedUseSubtype;
  aliasMapping?: MixedUseAliasMapping;
};

export type MixedUseSplitHint = {
  components: Partial<Record<MixedUseComponent, number>>;
  pattern: MixedUseSplitPattern;
};

export type MixedUseSplitInvalid = {
  reason: string;
  details?: string;
};

export type MixedUseSplitContract = {
  value: MixedUseSplitValue;
  source: MixedUseSplitSource;
  normalization_applied: boolean;
  inference_applied: boolean;
  pattern?: MixedUseSplitPattern;
  invalid_mix?: MixedUseSplitInvalid;
};

export const PARKING_SUBTYPES = [
  "surface_parking",
  "parking_garage",
  "underground_parking",
  "automated_parking",
] as const;

export type ParkingSubtype = (typeof PARKING_SUBTYPES)[number];

export type ParkingIntentResolution = {
  shouldRouteToParking: boolean;
  subtype?: ParkingSubtype;
  detectionSource: string;
  conflictOutcome: string;
};

const MIXED_USE_COMPONENT_SET = new Set<string>(MIXED_USE_COMPONENTS);
const MIXED_USE_SUBTYPE_SET = new Set<string>(MIXED_USE_SUBTYPES);
const MIXED_USE_HINT_SUFFIX = /\s*\[mixed_use_split:[^\]]+\]\s*$/i;
const PARKING_SUBTYPE_SET = new Set<string>(PARKING_SUBTYPES);

const HOTEL_RESIDENTIAL_ALIAS_PATTERNS = [
  /\bhotel[-\s]?residential\b/i,
  /\bhotel\s*(?:\+|and|\/)\s*residential\b/i,
  /\bresidential\s*(?:\+|and|\/)\s*hotel\b/i,
  /\bmixed[-\s]?use\s+hotel[-\s]?residential\b/i,
] as const;

const MIXED_USE_SUBTYPE_PATTERNS: Array<{
  subtype: MixedUseSubtype;
  patterns: readonly RegExp[];
}> = [
  {
    subtype: "office_residential",
    patterns: [
      /\boffice[-\s]?residential\b/i,
      /\boffice\s*(?:\+|and|\/)\s*residential\b/i,
      /\bresidential\s*(?:\+|and|\/)\s*office\b/i,
      /\bwork\s*live\b/i,
    ],
  },
  {
    subtype: "retail_residential",
    patterns: [
      /\bretail[-\s]?residential\b/i,
      /\bretail\s*(?:\+|and|\/)\s*residential\b/i,
      /\bresidential\s*(?:\+|and|\/)\s*retail\b/i,
      /\bshops?\s+and\s+apartments?\b/i,
      /\bground\s+floor\s+retail\b/i,
    ],
  },
  {
    subtype: "hotel_retail",
    patterns: [
      /\bhotel[-\s]?retail\b/i,
      /\bhotel\s*(?:\+|and|\/)\s*retail\b/i,
      /\bretail\s*(?:\+|and|\/)\s*hotel\b/i,
      /\bhotel\s+with\s+shops\b/i,
    ],
  },
  {
    subtype: "transit_oriented",
    patterns: [
      /\btransit[-\s]?oriented\b/i,
      /\btransit[-\s]?oriented\s+development\b/i,
      /\btod\b/i,
      /\bstation\s+area\b/i,
      /\btransit\s+village\b/i,
    ],
  },
  {
    subtype: "urban_mixed",
    patterns: [
      /\burban\s+mixed\b/i,
      /\bdowntown\s+mixed\b/i,
      /\bvertical\s+mixed\b/i,
      /\blive\s*work\s*play\b/i,
      /\bmixed[-\s]?use\s+development\b/i,
    ],
  },
];

const MIXED_USE_INTENT_PATTERNS = [
  /\bmixed[-\s]?use\b/i,
  /\bmulti[-\s]?use\b/i,
  /\bmixed\s+development\b/i,
  /\boffice\s*(?:\+|and|\/)\s*residential\b/i,
  /\bresidential\s*(?:\+|and|\/)\s*office\b/i,
  /\bretail\s*(?:\+|and|\/)\s*residential\b/i,
  /\bresidential\s*(?:\+|and|\/)\s*retail\b/i,
  /\bhotel\s*(?:\+|and|\/)\s*retail\b/i,
  /\bretail\s*(?:\+|and|\/)\s*hotel\b/i,
  /\bhotel\s*(?:\+|and|\/)\s*residential\b/i,
  /\bresidential\s*(?:\+|and|\/)\s*hotel\b/i,
  /\btransit[-\s]?oriented\b/i,
] as const;

const ZERO_SPLIT_VALUE: MixedUseSplitValue = {
  office: 0,
  residential: 0,
  retail: 0,
  hotel: 0,
  transit: 0,
};

const roundToTwo = (value: number): number => Math.round(value * 100) / 100;

const formatPercent = (value: number): string => {
  const rounded = roundToTwo(value);
  if (Number.isInteger(rounded)) {
    return `${rounded}`;
  }
  return rounded.toFixed(2).replace(/0+$/, "").replace(/\.$/, "");
};

export const detectParkingSubtypeFromDescription = (
  description: string
): ParkingSubtype | undefined => {
  if (!description || typeof description !== "string") {
    return undefined;
  }

  const subtypeCueOrder: Array<{ subtype: ParkingSubtype; patterns: readonly RegExp[] }> = [
    {
      subtype: "automated_parking",
      patterns: [
        /\bautomated parking\b/i,
        /\bautomated parking structure\b/i,
        /\brobotic parking\b/i,
        /\bmechanized parking\b/i,
      ],
    },
    {
      subtype: "underground_parking",
      patterns: [
        /\bunderground parking\b/i,
        /\bbelow[-\s]?grade parking\b/i,
        /\bsubterranean parking\b/i,
      ],
    },
    {
      subtype: "surface_parking",
      patterns: [
        /\bsurface parking\b/i,
        /\bsurface lot\b/i,
        /\bparking lot\b/i,
      ],
    },
    {
      subtype: "parking_garage",
      patterns: [
        /\bparking garage\b/i,
        /\bparking structure\b/i,
        /\bstructured parking\b/i,
        /\bparking deck\b/i,
        /\bparking ramp\b/i,
        /\bstandalone garage\b/i,
      ],
    },
  ];

  for (const { subtype, patterns } of subtypeCueOrder) {
    if (patterns.some((pattern) => pattern.test(description))) {
      return subtype;
    }
  }
  return undefined;
};

export const resolveParkingIntentFromDescription = (
  description: string
): ParkingIntentResolution => {
  if (!description || typeof description !== "string") {
    return {
      shouldRouteToParking: false,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "no_signal",
    };
  }

  const subtype = detectParkingSubtypeFromDescription(description);
  const hasParkingSignal =
    /\bparking\b/i.test(description) ||
    /\bparking garage\b/i.test(description) ||
    /\bparking structure\b/i.test(description) ||
    /\bparking lot\b/i.test(description) ||
    /\bstructured parking\b/i.test(description);

  if (!hasParkingSignal) {
    return {
      shouldRouteToParking: false,
      subtype,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "no_signal",
    };
  }

  const hasStandaloneSignal =
    /\bstandalone parking\b/i.test(description) ||
    /\bstandalone parking garage\b/i.test(description) ||
    /\bdedicated parking (?:facility|structure|garage)\b/i.test(description) ||
    /\bparking (?:facility|structure|garage) only\b/i.test(description);

  const hasPrimaryActionSignal = /\b(new|build|construct|develop|redevelop|expand|expansion|replacement)\b.{0,40}\bparking\b/i.test(
    description
  );

  const hasExplicitParkingAssetSignal =
    /\bautomated parking\b/i.test(description) ||
    /\bunderground parking\b/i.test(description) ||
    /\bsurface parking\b/i.test(description) ||
    /\bparking garage\b/i.test(description) ||
    /\bparking structure\b/i.test(description) ||
    /\bstructured parking\b/i.test(description) ||
    /\bparking lot\b/i.test(description);

  if (
    /\b(apartment|apartments|multifamily|multi-family|residential tower)\b/i.test(description) &&
    !hasStandaloneSignal
  ) {
    return {
      shouldRouteToParking: false,
      subtype,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "parking_demoted_multifamily_primary",
    };
  }
  if (
    /\b(hotel|motel|inn|hospitality|lodging)\b/i.test(description) &&
    !hasStandaloneSignal
  ) {
    return {
      shouldRouteToParking: false,
      subtype,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "parking_demoted_hospitality_primary",
    };
  }
  if (
    /\b(class a|class b|office tower|office building|corporate office)\b/i.test(description) &&
    !hasStandaloneSignal
  ) {
    return {
      shouldRouteToParking: false,
      subtype,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "parking_demoted_office_primary",
    };
  }

  if (hasStandaloneSignal) {
    return {
      shouldRouteToParking: true,
      subtype,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "parking_primary_standalone",
    };
  }
  if (hasPrimaryActionSignal) {
    return {
      shouldRouteToParking: true,
      subtype,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "parking_primary_action",
    };
  }
  if (hasExplicitParkingAssetSignal) {
    return {
      shouldRouteToParking: true,
      subtype,
      detectionSource: "buildingTypeDetection.parking_intent",
      conflictOutcome: "parking_primary_asset_intent",
    };
  }

  return {
    shouldRouteToParking: false,
    subtype,
    detectionSource: "buildingTypeDetection.parking_intent",
    conflictOutcome: "parking_context_only",
  };
};

export const normalizeMixedUseSubtypeAlias = (subtype?: string): string | undefined => {
  if (!subtype) {
    return undefined;
  }
  const normalized = subtype.trim().toLowerCase();
  if (!normalized) {
    return undefined;
  }
  if (normalized === "hotel_residential") {
    return "hotel_retail";
  }
  return normalized;
};

const defaultMixedUsePair = (subtype?: string): [MixedUseComponent, MixedUseComponent] => {
  const normalized = normalizeMixedUseSubtypeAlias(subtype);
  if (normalized === "office_residential") {
    return ["office", "residential"];
  }
  if (normalized === "retail_residential") {
    return ["retail", "residential"];
  }
  if (normalized === "hotel_retail") {
    return ["hotel", "retail"];
  }
  if (normalized === "transit_oriented") {
    return ["transit", "residential"];
  }
  return ["office", "residential"];
};

export const defaultMixedUseSplitValue = (subtype?: string): MixedUseSplitValue => {
  const [first, second] = defaultMixedUsePair(subtype);
  return {
    ...ZERO_SPLIT_VALUE,
    [first]: 50,
    [second]: 50,
  };
};

export const detectMixedUseIntent = (description: string): boolean => {
  if (!description || typeof description !== "string") {
    return false;
  }
  return MIXED_USE_INTENT_PATTERNS.some((pattern) => pattern.test(description));
};

export const detectMixedUseSubtypeFromDescription = (
  description: string
): MixedUseSubtypeDetection => {
  if (!description || typeof description !== "string") {
    return {};
  }

  for (const pattern of HOTEL_RESIDENTIAL_ALIAS_PATTERNS) {
    if (pattern.test(description)) {
      return {
        subtype: "hotel_retail",
        aliasMapping: {
          from: "hotel_residential",
          to: "hotel_retail",
          reason: "hotel_residential_alias",
          matched_pattern: pattern.source,
        },
      };
    }
  }

  for (const { subtype, patterns } of MIXED_USE_SUBTYPE_PATTERNS) {
    if (patterns.some((pattern) => pattern.test(description))) {
      return { subtype };
    }
  }

  return {};
};

export const detectMixedUseSplitHintFromDescription = (
  description: string,
  subtype?: string
): MixedUseSplitHint | undefined => {
  if (!description || typeof description !== "string") {
    return undefined;
  }

  const pair = defaultMixedUsePair(subtype);
  const labeled = Array.from(
    description.matchAll(/(\d{1,3}(?:\.\d+)?)\s*%\s*(office|residential|retail|hotel|transit)\b/gi)
  );
  if (labeled.length > 0) {
    const hinted: Partial<Record<MixedUseComponent, number>> = {};
    for (const match of labeled) {
      const pctText = match[1];
      const component = match[2]?.toLowerCase() as MixedUseComponent;
      const pct = Number.parseFloat(pctText);
      if (!Number.isFinite(pct) || pct < 0 || !MIXED_USE_COMPONENT_SET.has(component)) {
        continue;
      }
      hinted[component] = (hinted[component] ?? 0) + pct;
    }
    if (Object.keys(hinted).length > 0) {
      return { components: hinted, pattern: "component_percent" };
    }
  }

  const ratioMatch = description.match(/(?<!\d)(\d{1,3}(?:\.\d+)?)\s*\/\s*(\d{1,3}(?:\.\d+)?)(?!\d)/);
  if (ratioMatch) {
    const first = Number.parseFloat(ratioMatch[1]);
    const second = Number.parseFloat(ratioMatch[2]);
    if (Number.isFinite(first) && Number.isFinite(second) && first >= 0 && second >= 0) {
      return {
        components: {
          [pair[0]]: first,
          [pair[1]]: second,
        },
        pattern: "ratio_pair",
      };
    }
  }

  const mostlyMatch = description.match(/\bmostly\s+(office|residential|retail|hotel|transit)\b/i);
  if (mostlyMatch) {
    const dominant = mostlyMatch[1].toLowerCase() as MixedUseComponent;
    const counterpart = pair[0] === dominant ? pair[1] : pair[0];
    return {
      components: {
        [dominant]: 70,
        [counterpart]: 30,
      },
      pattern: "mostly_component",
    };
  }

  const heavyMatch = description.match(/\b(office|residential|retail|hotel|transit)[-\s]?heavy\b/i);
  if (heavyMatch) {
    const dominant = heavyMatch[1].toLowerCase() as MixedUseComponent;
    const counterpart = pair[0] === dominant ? pair[1] : pair[0];
    return {
      components: {
        [dominant]: 70,
        [counterpart]: 30,
      },
      pattern: "heavy_component",
    };
  }

  if (/\bbalanced\b/i.test(description)) {
    return {
      components: {
        [pair[0]]: 50,
        [pair[1]]: 50,
      },
      pattern: "balanced_pair",
    };
  }

  return undefined;
};

type NormalizedSplitResult = {
  value: MixedUseSplitValue;
  normalization_applied: boolean;
  inference_applied: boolean;
  invalid_mix?: MixedUseSplitInvalid;
};

export const normalizeMixedUseSplitComponents = (
  rawComponents: Partial<Record<string, number>>,
  subtype?: string
): NormalizedSplitResult => {
  if (!rawComponents || typeof rawComponents !== "object") {
    return {
      value: defaultMixedUseSplitValue(subtype),
      normalization_applied: false,
      inference_applied: false,
      invalid_mix: { reason: "invalid_payload" },
    };
  }

  const components: Partial<Record<MixedUseComponent, number>> = {};
  for (const [key, rawValue] of Object.entries(rawComponents)) {
    if (!MIXED_USE_COMPONENT_SET.has(key)) {
      return {
        value: defaultMixedUseSplitValue(subtype),
        normalization_applied: false,
        inference_applied: false,
        invalid_mix: { reason: "unsupported_component", details: key },
      };
    }
    const numericValue = Number(rawValue);
    if (!Number.isFinite(numericValue) || numericValue < 0) {
      return {
        value: defaultMixedUseSplitValue(subtype),
        normalization_applied: false,
        inference_applied: false,
        invalid_mix: { reason: "invalid_value", details: key },
      };
    }
    if (numericValue > 0) {
      components[key as MixedUseComponent] = numericValue;
    }
  }

  if (Object.keys(components).length === 0) {
    return {
      value: defaultMixedUseSplitValue(subtype),
      normalization_applied: false,
      inference_applied: false,
      invalid_mix: { reason: "empty_components" },
    };
  }

  let inferenceApplied = false;
  const nonZeroEntries = Object.entries(components) as Array<[MixedUseComponent, number]>;
  if (nonZeroEntries.length === 1) {
    const [existingComponent, existingValue] = nonZeroEntries[0];
    const pair = defaultMixedUsePair(subtype);
    const counterpart = pair[0] === existingComponent ? pair[1] : pair[0];
    components[counterpart] = Math.max(0, 100 - existingValue);
    inferenceApplied = true;
  }

  const total = (Object.values(components) as number[]).reduce((sum, value) => sum + value, 0);
  if (!(total > 0)) {
    return {
      value: defaultMixedUseSplitValue(subtype),
      normalization_applied: false,
      inference_applied: false,
      invalid_mix: { reason: "zero_total" },
    };
  }

  const needsScale = Math.abs(total - 100) > 0.0001;
  const scaledEntries = (Object.entries(components) as Array<[MixedUseComponent, number]>).map(
    ([component, value]) => [component, needsScale ? (value / total) * 100 : value] as const
  );

  const rounded: MixedUseSplitValue = { ...ZERO_SPLIT_VALUE };
  for (const [component, value] of scaledEntries) {
    rounded[component] = roundToTwo(value);
  }

  let roundedTotal = MIXED_USE_COMPONENTS.reduce((sum, component) => sum + rounded[component], 0);
  let adjusted = false;
  if (Math.abs(roundedTotal - 100) >= 0.01) {
    let dominant: MixedUseComponent | undefined;
    for (const component of MIXED_USE_COMPONENTS) {
      if (rounded[component] <= 0) {
        continue;
      }
      if (!dominant || rounded[component] > rounded[dominant]) {
        dominant = component;
      }
    }
    if (dominant) {
      rounded[dominant] = roundToTwo(rounded[dominant] + (100 - roundedTotal));
      roundedTotal = MIXED_USE_COMPONENTS.reduce((sum, component) => sum + rounded[component], 0);
      adjusted = true;
    }
  }

  if (Math.abs(roundedTotal - 100) >= 0.01) {
    return {
      value: defaultMixedUseSplitValue(subtype),
      normalization_applied: false,
      inference_applied: false,
      invalid_mix: { reason: "normalization_failed" },
    };
  }

  return {
    value: rounded,
    normalization_applied: inferenceApplied || needsScale || adjusted,
    inference_applied: inferenceApplied,
  };
};

const buildDefaultSplitContract = (
  subtype?: string,
  invalidMix?: MixedUseSplitInvalid
): MixedUseSplitContract => ({
  value: defaultMixedUseSplitValue(subtype),
  source: "default",
  normalization_applied: false,
  inference_applied: false,
  ...(invalidMix ? { invalid_mix: invalidMix } : {}),
});

export const resolveMixedUseSplitContract = (options: {
  subtype?: string;
  description?: string;
  userComponents?: Partial<Record<string, number>>;
}): MixedUseSplitContract => {
  const normalizedSubtype = normalizeMixedUseSubtypeAlias(options.subtype);

  if (options.userComponents) {
    const normalized = normalizeMixedUseSplitComponents(options.userComponents, normalizedSubtype);
    if (normalized.invalid_mix) {
      return buildDefaultSplitContract(normalizedSubtype, normalized.invalid_mix);
    }
    return {
      value: normalized.value,
      source: "user_input",
      normalization_applied: normalized.normalization_applied,
      inference_applied: normalized.inference_applied,
    };
  }

  const detectedHint = detectMixedUseSplitHintFromDescription(
    options.description ?? "",
    normalizedSubtype
  );
  if (detectedHint) {
    const normalized = normalizeMixedUseSplitComponents(
      detectedHint.components as Partial<Record<string, number>>,
      normalizedSubtype
    );
    if (normalized.invalid_mix) {
      return buildDefaultSplitContract(normalizedSubtype, normalized.invalid_mix);
    }
    return {
      value: normalized.value,
      source: "nlp_detected",
      normalization_applied: normalized.normalization_applied,
      inference_applied: normalized.inference_applied,
      pattern: detectedHint.pattern,
    };
  }

  return buildDefaultSplitContract(normalizedSubtype);
};

export const formatMixedUseSplitValue = (value: MixedUseSplitValue): string => {
  const ordered = MIXED_USE_COMPONENTS
    .filter((component) => Number.isFinite(value[component]) && value[component] > 0)
    .sort((a, b) => {
      if (value[b] !== value[a]) {
        return value[b] - value[a];
      }
      return MIXED_USE_COMPONENTS.indexOf(a) - MIXED_USE_COMPONENTS.indexOf(b);
    });

  if (ordered.length === 0) {
    return "50% office / 50% residential";
  }

  return ordered
    .map((component) => `${formatPercent(value[component])}% ${component}`)
    .join(" / ");
};

export const appendMixedUseSplitHintToDescription = (
  description: string,
  contract?: MixedUseSplitContract | null
): string => {
  const baseDescription = (description ?? "").replace(MIXED_USE_HINT_SUFFIX, "").trim();
  if (!contract) {
    return baseDescription;
  }
  return `${baseDescription} [mixed_use_split: ${formatMixedUseSplitValue(contract.value)}]`.trim();
};

export const isCanonicalMixedUseSubtype = (subtype?: string): subtype is MixedUseSubtype => {
  if (!subtype) {
    return false;
  }
  return MIXED_USE_SUBTYPE_SET.has(subtype);
};

export const isCanonicalParkingSubtype = (subtype?: string): subtype is ParkingSubtype => {
  if (!subtype) {
    return false;
  }
  return PARKING_SUBTYPE_SET.has(subtype);
};
