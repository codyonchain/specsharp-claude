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

export const RETAIL_SUBTYPES = ["shopping_center", "big_box"] as const;

export type RetailSubtype = (typeof RETAIL_SUBTYPES)[number];

export const RETAIL_FEATURE_COSTS_BY_SUBTYPE: Record<
  RetailSubtype,
  Record<string, number>
> = {
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
};

export const OFFICE_SUBTYPES = ["class_a", "class_b"] as const;

export type OfficeSubtype = (typeof OFFICE_SUBTYPES)[number];

export const OFFICE_FEATURE_COSTS_BY_SUBTYPE: Record<
  OfficeSubtype,
  Record<string, number>
> = {
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

export const HEALTHCARE_SUBTYPES = [
  "surgical_center",
  "imaging_center",
  "urgent_care",
  "outpatient_clinic",
  "medical_office_building",
  "dental_office",
  "hospital",
  "medical_center",
  "nursing_home",
  "rehabilitation",
] as const;

export type HealthcareSubtype = (typeof HEALTHCARE_SUBTYPES)[number];

export const HEALTHCARE_FEATURE_COSTS_BY_SUBTYPE: Record<
  HealthcareSubtype,
  Record<string, number>
> = {
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
};

export const EDUCATIONAL_SUBTYPES = [
  "elementary_school",
  "middle_school",
  "high_school",
  "university",
  "community_college",
] as const;

export type EducationalSubtype = (typeof EDUCATIONAL_SUBTYPES)[number];

export const EDUCATIONAL_FEATURE_COSTS_BY_SUBTYPE: Record<
  EducationalSubtype,
  Record<string, number>
> = {
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
};

export const CIVIC_SUBTYPES = [
  "library",
  "courthouse",
  "government_building",
  "community_center",
  "public_safety",
] as const;

export type CivicSubtype = (typeof CIVIC_SUBTYPES)[number];

export const CIVIC_FEATURE_COSTS_BY_SUBTYPE: Record<
  CivicSubtype,
  Record<string, number>
> = {
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

const RETAIL_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  covered_walkway: {
    name: "Covered Walkway",
    description: "Tenant frontage canopy and weather-protected pedestrian circulation package.",
  },
  loading_dock: {
    name: "Loading Dock",
    description: "Dedicated loading dock and back-of-house receiving improvements.",
  },
  monument_signage: {
    name: "Monument Signage",
    description: "Center-entry monument signage with lighting and utility coordination.",
  },
  outdoor_seating: {
    name: "Outdoor Seating",
    description: "Exterior seating pad with storefront utility tie-ins and circulation upgrades.",
  },
  drive_thru: {
    name: "Drive-Thru",
    description: "Drive-thru lane, order canopy, and service-window infrastructure.",
  },
  storage_units: {
    name: "Storage Units",
    description: "Tenant back-of-house storage enclosures with access-control integration.",
  },
  mezzanine: {
    name: "Mezzanine",
    description: "Sales-floor mezzanine structure and vertical-circulation package.",
  },
  auto_center: {
    name: "Auto Center",
    description: "Integrated auto-service bay and customer-dropoff buildout.",
  },
  garden_center: {
    name: "Garden Center",
    description: "Open-air garden center pad with irrigation, shade, and yard controls.",
  },
  warehouse_racking: {
    name: "Warehouse Racking",
    description: "High-bay racking and merchandising support infrastructure.",
  },
  refrigerated_storage: {
    name: "Refrigerated Storage",
    description: "Walk-in cold storage program with refrigeration and power upgrades.",
  },
  curbside_pickup: {
    name: "Curbside Pickup",
    description: "Dedicated curbside pickup stalls, signage, and back-of-house staging lanes.",
  },
};

const OFFICE_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  fitness_center: {
    name: "Fitness Center",
    description: "Tenant fitness center with locker support and mechanical/electrical upgrades.",
  },
  cafeteria: {
    name: "Cafeteria",
    description: "On-site cafeteria and pantry infrastructure for tenant amenities.",
  },
  conference_center: {
    name: "Conference Center",
    description: "Large conference-center program with divisible meeting and AV-ready spaces.",
  },
  structured_parking: {
    name: "Structured Parking",
    description: "Dedicated parking-structure scope with circulation, lighting, and access controls.",
  },
  green_roof: {
    name: "Green Roof",
    description: "Green-roof assembly with drainage, planting media, and access detailing.",
  },
  outdoor_terrace: {
    name: "Outdoor Terrace",
    description: "Tenant outdoor terrace program with decking, shade, and utility tie-ins.",
  },
  executive_floor: {
    name: "Executive Floor",
    description: "Executive floor fit-out with premium finishes and dedicated support spaces.",
  },
  data_center: {
    name: "Data Center",
    description: "Tenant data-center white-space and critical-support infrastructure package.",
  },
  concierge: {
    name: "Concierge Lobby",
    description: "Concierge-level lobby operations space with enhanced service desk configuration.",
  },
  conference_room: {
    name: "Conference Room Suite",
    description: "Class B conference-room package for collaborative tenant areas.",
  },
  surface_parking: {
    name: "Surface Parking",
    description: "Surface-parking improvements with circulation, striping, and lighting upgrades.",
  },
  storage_space: {
    name: "Storage Space",
    description: "Expandable tenant and building storage areas with secured access control.",
  },
  security_desk: {
    name: "Security Desk",
    description: "Ground-floor security desk and monitoring point at primary ingress.",
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

const HEALTHCARE_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  emergency: {
    name: "Emergency Department",
    description: "Acute-care emergency program with trauma-ready rooms and support infrastructure.",
  },
  imaging: {
    name: "Imaging Center",
    description: "Cross-modality imaging suite buildout with shielding, controls, and support spaces.",
  },
  surgery: {
    name: "Surgery Center",
    description: "Procedural and operating suite program with sterile flow and recovery support.",
  },
  operating_room: {
    name: "Operating Room",
    description: "Fully equipped operating-room buildout with anesthesia, med-gas, and sterile support.",
  },
  pre_op: {
    name: "Pre-Op Bays",
    description: "Pre-op intake and preparation bays with clinical utilities and nurse visibility.",
  },
  recovery_room: {
    name: "Recovery Room",
    description: "Post-procedure recovery room capacity with monitoring and patient-support infrastructure.",
  },
  sterile_processing: {
    name: "Sterile Processing",
    description: "Central sterile processing flow with clean/dirty zoning and instrument throughput support.",
  },
  icu: {
    name: "ICU Unit",
    description: "Critical-care unit expansion with high-acuity monitoring and redundant systems.",
  },
  lab: {
    name: "Laboratory",
    description: "Clinical lab infrastructure including specimen flow, utilities, and support spaces.",
  },
  laboratory: {
    name: "Laboratory",
    description: "Clinical laboratory program with specimen workflow, diagnostics, and support utilities.",
  },
  pharmacy: {
    name: "Pharmacy",
    description: "On-site pharmacy space with medication storage, prep zones, and clinical support systems.",
  },
  trauma_room: {
    name: "Trauma Room",
    description: "Trauma-ready acute treatment rooms with life-safety, gases, and rapid-response fitout.",
  },
  x_ray: {
    name: "X-Ray Suite",
    description: "General radiography suite with shielding, controls, and patient support spaces.",
  },
  mri_suite: {
    name: "MRI Suite",
    description: "MRI-ready room with shielding, magnet infrastructure, and patient safety support.",
  },
  ct_suite: {
    name: "CT Suite",
    description: "Computed tomography suite with imaging controls and adjacent patient prep space.",
  },
  pet_scan: {
    name: "PET Scan Suite",
    description: "PET imaging suite with radiopharmaceutical workflow and compliant support zones.",
  },
  ultrasound: {
    name: "Ultrasound Rooms",
    description: "Ultrasound room package with targeted shielding and patient workflow support.",
  },
  mammography: {
    name: "Mammography Suite",
    description: "Dedicated mammography room buildout with imaging controls and patient privacy detailing.",
  },
  emergency_department: {
    name: "Emergency Department",
    description: "Emergency department program with acute treatment rooms and trauma-flow support.",
  },
  imaging_suite: {
    name: "Imaging Suite",
    description: "Hospital imaging suite with shielding, controls, and critical-support adjacencies.",
  },
  surgical_suite: {
    name: "Surgical Suite",
    description: "Hospital surgical suite program with OR support, sterile flow, and recovery interfaces.",
  },
  cathlab: {
    name: "Cath Lab",
    description: "Cardiac cath-lab procedure room with imaging integration and advanced support systems.",
  },
  exam_rooms: {
    name: "Exam Rooms",
    description: "Expanded outpatient exam-room capacity with standardized clinical room infrastructure.",
  },
  procedure_room: {
    name: "Procedure Room",
    description: "Minor-procedure room package with clinical utilities and procedural support zoning.",
  },
  tenant_improvements: {
    name: "Tenant Improvements",
    description: "Core tenant-improvement package for clinical buildouts and delivery readiness.",
  },
  ambulatory_imaging: {
    name: "Ambulatory Imaging",
    description: "Ambulatory imaging package with shielding, controls, and outpatient workflow support.",
  },
  ambulatory_buildout: {
    name: "Ambulatory Buildout",
    description: "Ambulatory care buildout for specialist tenants and procedure-support programs.",
  },
  operatory: {
    name: "Dental Operatory",
    description: "Clinical dental operatory rooms with suction, gas, and equipment utility support.",
  },
  sterilization: {
    name: "Dental Sterilization Core",
    description: "Dental sterilization core with clean/dirty flow and instrument-processing upgrades.",
  },
  specialty_clinic: {
    name: "Specialty Clinic Wing",
    description: "Multi-specialty clinic buildout with dedicated provider and patient support spaces.",
  },
  memory_care: {
    name: "Memory Care Wing",
    description: "Secured memory-care environment with resident-safety and caregiving infrastructure.",
  },
  therapy_room: {
    name: "Therapy Rooms",
    description: "Skilled nursing therapy rooms for restorative care and clinician support operations.",
  },
  activity_room: {
    name: "Activity Room",
    description: "Resident activity rooms for programming with life-safety and accessibility upgrades.",
  },
  dining_hall: {
    name: "Dining Hall",
    description: "Congregate dining-hall upgrades for resident services and operational flow.",
  },
  therapy_gym: {
    name: "Therapy Gym",
    description: "Rehab therapy gym expansion with PT/OT equipment zones and clinician visibility.",
  },
  hydrotherapy: {
    name: "Hydrotherapy Suite",
    description: "Hydrotherapy program with pool systems, lifts, and patient-safety infrastructure.",
  },
  treatment_rooms: {
    name: "Treatment Rooms",
    description: "Rehabilitation treatment-room package for multi-disciplinary therapy services.",
  },
  assessment_suite: {
    name: "Assessment Suite",
    description: "Clinical assessment suites for intake, evaluation, and care-plan coordination.",
  },
  hc_outpatient_on_site_lab: {
    name: "On-Site Lab",
    description: "In-clinic diagnostics lab for outpatient workflows and faster turnaround.",
  },
  hc_outpatient_imaging_pod: {
    name: "Imaging Pod (X-ray/Ultrasound)",
    description: "Targeted outpatient imaging pod with shielding, controls, and patient prep areas.",
  },
  hc_outpatient_behavioral_suite: {
    name: "Behavioral Health Suite",
    description: "Dedicated behavioral-health rooms with privacy, safety, and acoustic enhancements.",
  },
  hc_urgent_on_site_lab: {
    name: "Urgent Care Lab",
    description: "Rapid-test urgent-care lab buildout for same-visit diagnostics and throughput.",
  },
  hc_urgent_imaging_suite: {
    name: "Urgent Care Imaging Suite",
    description: "Urgent-care imaging program with X-ray/CT readiness and shielding support.",
  },
  hc_urgent_observation_bays: {
    name: "Observation Bays",
    description: "Short-stay observation bays with nurse visibility and monitoring infrastructure.",
  },
  hc_imaging_second_mri: {
    name: "Second MRI Room",
    description: "Additional MRI suite with magnet support, controls, and patient safety zoning.",
  },
  hc_imaging_pet_ct_suite: {
    name: "PET/CT Suite",
    description: "PET/CT suite with hot-lab adjacency and radiation-compliant support zones.",
  },
  hc_imaging_interventional_rad: {
    name: "Interventional Radiology Room",
    description: "Interventional imaging room with procedural support and equipment integration.",
  },
  hc_asc_expanded_pacu: {
    name: "Expanded PACU",
    description: "Post-anesthesia care expansion to handle higher outpatient procedure throughput.",
  },
  hc_asc_sterile_core_upgrade: {
    name: "Sterile Core Upgrade",
    description: "Sterile-core optimization for instrument flow, storage, and infection control.",
  },
  hc_asc_pain_management_suite: {
    name: "Pain Management Suite",
    description: "Specialized outpatient procedure suite for pain-management service lines.",
  },
  hc_asc_hybrid_or_cath_lab: {
    name: "Hybrid OR / Cath Lab",
    description: "Hybrid procedural room with imaging integration and advanced support systems.",
  },
  mob_imaging_ready_shell: {
    name: "Imaging-Ready Shell",
    description: "MOB shell upgrades for future imaging tenants, vibration control, and utilities.",
  },
  mob_enhanced_mep: {
    name: "Enhanced MEP Capacity",
    description: "Expanded MEP backbone and riser capacity for higher-acuity tenant programs.",
  },
  mob_procedure_suite: {
    name: "Procedure Suite Buildout",
    description: "Procedure-suite fitout for specialist tenants requiring Class B/C room programs.",
  },
  mob_pharmacy_shell: {
    name: "Pharmacy / Retail Shell",
    description: "Ground-floor shell package for pharmacy and ambulatory-support retail tenancy.",
  },
  mob_covered_dropoff: {
    name: "Covered Drop-Off Canopy",
    description: "Patient drop-off canopy with circulation, lighting, and accessibility upgrades.",
  },
  hc_dental_pano_ceph: {
    name: "Panoramic X-ray / Ceph Suite",
    description: "Dental imaging room with shielding and workflow-ready equipment support.",
  },
  hc_dental_sedation_suite: {
    name: "Sedation / Surgery Suite",
    description: "Sedation-capable dental operatory with med-gas, monitoring, and safety upgrades.",
  },
  hc_dental_sterilization_upgrade: {
    name: "Central Sterilization Upgrade",
    description: "Expanded dental sterilization core with clean/dirty zoning and autoclave capacity.",
  },
  hc_dental_ortho_bay_expansion: {
    name: "Orthodontic Bay Expansion",
    description: "Open-bay ortho expansion with added chairs, suction, and clinical infrastructure.",
  },
  hospital_central_plant_redundancy: {
    name: "Central Plant Redundancy",
    description: "Hospital central-plant redundancy upgrades for critical-care operational resilience.",
  },
  hospital_pharmacy_cleanroom: {
    name: "Pharmacy Cleanroom",
    description: "USP-compliant pharmacy cleanroom suite for sterile compounding operations.",
  },
  medical_center_infusion_suite: {
    name: "Infusion Suite",
    description: "Outpatient infusion program with dedicated treatment bays and support spaces.",
  },
  medical_center_ambulatory_tower_fitout: {
    name: "Ambulatory Tower Fitout",
    description: "Vertical ambulatory-care fitout program for multi-specialty medical-center growth.",
  },
  nursing_memory_care_wing: {
    name: "Memory Care Wing",
    description: "Secured memory-care neighborhood with dementia-oriented layout and support zones.",
  },
  nursing_rehab_gym: {
    name: "Skilled Nursing Rehab Gym",
    description: "SNF-focused rehab gym expansion with therapy equipment and care-team support.",
  },
  nursing_nurse_call_upgrade: {
    name: "Nurse Call Upgrade",
    description: "Enhanced nurse-call and resident monitoring infrastructure for response reliability.",
  },
  nursing_wander_management_system: {
    name: "Wander Management System",
    description: "Resident wander-management controls with secured access and monitoring integration.",
  },
  nursing_dining_household_model: {
    name: "Household Dining Conversion",
    description: "Small-house dining model conversion with decentralized serving and support areas.",
  },
  rehab_hydrotherapy_pool: {
    name: "Hydrotherapy Pool",
    description: "Hydrotherapy pool program with patient lifts, controls, and safety infrastructure.",
  },
  rehab_gait_training_lab: {
    name: "Gait Training Lab",
    description: "Technology-enabled gait training and balance lab with monitoring systems.",
  },
  rehab_adl_apartment: {
    name: "ADL Training Apartment",
    description: "Activities-of-daily-living training apartment for real-world rehab progression.",
  },
  rehab_therapy_gym_expansion: {
    name: "Therapy Gym Expansion",
    description: "Expanded PT/OT therapy gym with equipment zones and care-team visibility.",
  },
  rehab_speech_neuro_suite: {
    name: "Speech + Neuro Therapy Suite",
    description: "Dedicated speech and neuro-rehab treatment suite with specialized support rooms.",
  },
};

const EDUCATIONAL_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  gymnasium: {
    name: "Gymnasium",
    description: "Athletics-ready school gym with resilient flooring, bleachers, and support zones.",
  },
  cafeteria: {
    name: "Cafeteria",
    description: "Student dining and serving infrastructure with high-throughput food service support.",
  },
  playground: {
    name: "Playground",
    description: "Age-appropriate exterior play environment with safety surfacing and site coordination.",
  },
  computer_lab: {
    name: "Computer Lab",
    description: "Instructional technology lab with power/data density and supervision-friendly layout.",
  },
  library: {
    name: "Library / Media Center",
    description: "Learning commons and media collections environment with flexible study spaces.",
  },
  science_labs: {
    name: "Science Labs",
    description: "General science laboratory classrooms with utility rough-ins and prep support.",
  },
  auditorium: {
    name: "Auditorium",
    description: "Assembly/performance venue with seating, acoustic treatment, and AV infrastructure.",
  },
  athletic_field: {
    name: "Athletic Field",
    description: "Outdoor student athletics field package with lighting, drainage, and spectator support.",
  },
  stadium: {
    name: "Stadium",
    description: "Large-capacity athletics venue with structured seating and game-day operations support.",
  },
  field_house: {
    name: "Field House",
    description: "Indoor athletics support building with training, equipment, and team facilities.",
  },
  performing_arts_center: {
    name: "Performing Arts Center",
    description: "Dedicated performance hall with stage systems, acoustic control, and back-of-house support.",
  },
  vocational_shops: {
    name: "Vocational Shops",
    description: "CTE workshop bays with specialty utilities, safety zoning, and durable interior systems.",
  },
  media_center: {
    name: "Media Center",
    description: "Integrated media production and collaboration hub with digital-learning infrastructure.",
  },
  lecture_hall: {
    name: "Lecture Hall",
    description: "Tiered higher-education lecture venue with AV backbone and acoustic performance.",
  },
  research_lab: {
    name: "Research Lab",
    description: "University research lab fitout with advanced utility support and operational controls.",
  },
  clean_room: {
    name: "Clean Room",
    description: "Controlled-environment research/teaching clean-room suite with specialty systems.",
  },
  student_center: {
    name: "Student Center",
    description: "Campus student-services and gathering hub with multipurpose program spaces.",
  },
  vocational_lab: {
    name: "Vocational Lab",
    description: "Workforce training lab with equipment-ready infrastructure for technical programs.",
  },
  student_services: {
    name: "Student Services",
    description: "Community-college advising, enrollment, and support-services suite buildout.",
  },
};

const CIVIC_FEATURE_METADATA: Record<
  string,
  { name: string; description: string }
> = {
  stacks_load_reinforcement: {
    name: "Stacks Load Reinforcement",
    description: "Structural reinforcement for dense collections and long-span stack loading demands.",
  },
  acoustic_treatment: {
    name: "Acoustic Treatment",
    description: "Acoustic wall/ceiling treatments for reading rooms, study zones, and quiet commons.",
  },
  daylighting_controls: {
    name: "Daylighting Controls",
    description: "Daylight-responsive lighting controls for library public zones and collection areas.",
  },
  community_rooms: {
    name: "Community Rooms",
    description: "Flexible community meeting rooms with partitioning, AV support, and after-hours access.",
  },
  maker_space_mep: {
    name: "Maker Space MEP",
    description: "Enhanced power, ventilation, and specialty utility support for library maker spaces.",
  },
  courtroom: {
    name: "Courtroom",
    description: "Courtroom chamber fitout with judicial bench infrastructure and public gallery support.",
  },
  jury_room: {
    name: "Jury Room",
    description: "Dedicated jury deliberation rooms with secured circulation and privacy controls.",
  },
  holding_cells: {
    name: "Holding Cells",
    description: "Secure detainee holding cells with hardened finishes and life-safety systems.",
  },
  judges_chambers: {
    name: "Judges Chambers",
    description: "Judicial chambers with secure circulation, staff support, and controlled access.",
  },
  security_screening: {
    name: "Security Screening",
    description: "Public-entry screening area with queue management and threat-detection infrastructure.",
  },
  magnetometer_screening_lanes: {
    name: "Magnetometer Lanes",
    description: "Dedicated magnetometer screening lanes for courthouse ingress throughput.",
  },
  sallyport: {
    name: "Sallyport",
    description: "Secure vehicle transfer sallyport for protected detainee movement.",
  },
  ballistic_glazing_package: {
    name: "Ballistic Glazing Package",
    description: "Ballistic-rated glazing and framing package for high-risk perimeter conditions.",
  },
  redundant_life_safety_power: {
    name: "Redundant Life Safety Power",
    description: "Redundant emergency power for life-safety circuits and critical security systems.",
  },
  council_chambers: {
    name: "Council Chambers",
    description: "Council chamber buildout with dais, public comment areas, and civic hearing support.",
  },
  secure_area: {
    name: "Secure Area",
    description: "Controlled government operations zone with layered access control and monitoring.",
  },
  public_plaza: {
    name: "Public Plaza",
    description: "Civic-facing public plaza scope with paving, lighting, and integrated site utilities.",
  },
  records_vault: {
    name: "Records Vault",
    description: "Secure records vault with environmental controls and restricted archival access.",
  },
  gymnasium: {
    name: "Gymnasium",
    description: "Community recreation gymnasium with resilient flooring and spectator accommodations.",
  },
  kitchen: {
    name: "Community Kitchen",
    description: "Commercial-grade community kitchen with serving support and code-compliant systems.",
  },
  multipurpose_room: {
    name: "Multipurpose Room",
    description: "Flexible multipurpose room with divisible layouts and event support infrastructure.",
  },
  fitness_center: {
    name: "Fitness Center",
    description: "Community fitness center with enhanced MEP support and equipment-ready utility rough-ins.",
  },
  outdoor_pavilion: {
    name: "Outdoor Pavilion",
    description: "Weather-protected outdoor pavilion for community programming and events.",
  },
  apparatus_bay: {
    name: "Apparatus Bay",
    description: "Public safety apparatus bay with vehicle exhaust capture and rapid egress planning.",
  },
  dispatch_center: {
    name: "Dispatch Center",
    description: "24/7 dispatch center with hardened communications infrastructure and redundancy.",
  },
  training_tower: {
    name: "Training Tower",
    description: "Fire/rescue training tower program with durable envelope and training-ready utilities.",
  },
  emergency_generator: {
    name: "Emergency Generator",
    description: "Emergency generator plant for public safety operational continuity.",
  },
  sally_port: {
    name: "Sally Port",
    description: "Secure sally port for protected law-enforcement and emergency operations transfer.",
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

const createRetailSpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of RETAIL_SUBTYPES) {
    const entries = RETAIL_FEATURE_COSTS_BY_SUBTYPE[subtype];
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
      const metadata = RETAIL_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Retail subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: RETAIL_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const RETAIL_SPECIAL_FEATURES = createRetailSpecialFeatures();

export const getRetailSpecialFeatures = (): SpecialFeatureOption[] =>
  RETAIL_SPECIAL_FEATURES;

const createOfficeSpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of OFFICE_SUBTYPES) {
    const entries = OFFICE_FEATURE_COSTS_BY_SUBTYPE[subtype];
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
      const metadata = OFFICE_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Office subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: OFFICE_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const OFFICE_SPECIAL_FEATURES = createOfficeSpecialFeatures();

export const getOfficeSpecialFeatures = (): SpecialFeatureOption[] =>
  OFFICE_SPECIAL_FEATURES;

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

const createHealthcareSpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of HEALTHCARE_SUBTYPES) {
    const entries = HEALTHCARE_FEATURE_COSTS_BY_SUBTYPE[subtype];
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
      const metadata = HEALTHCARE_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Healthcare subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: HEALTHCARE_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const HEALTHCARE_SPECIAL_FEATURES = createHealthcareSpecialFeatures();

export const getHealthcareSpecialFeatures = (): SpecialFeatureOption[] =>
  HEALTHCARE_SPECIAL_FEATURES;

const createEducationalSpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of EDUCATIONAL_SUBTYPES) {
    const entries = EDUCATIONAL_FEATURE_COSTS_BY_SUBTYPE[subtype];
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
      const metadata = EDUCATIONAL_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Educational subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: EDUCATIONAL_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const EDUCATIONAL_SPECIAL_FEATURES = createEducationalSpecialFeatures();

export const getEducationalSpecialFeatures = (): SpecialFeatureOption[] =>
  EDUCATIONAL_SPECIAL_FEATURES;

const createCivicSpecialFeatures = (): SpecialFeatureOption[] => {
  const byFeatureId: Record<
    string,
    { costPerSFBySubtype: Record<string, number>; allowedSubtypes: string[] }
  > = {};

  for (const subtype of CIVIC_SUBTYPES) {
    const entries = CIVIC_FEATURE_COSTS_BY_SUBTYPE[subtype];
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
      const metadata = CIVIC_FEATURE_METADATA[featureId];
      return {
        id: featureId,
        name: metadata?.name ?? featureId.replace(/_/g, " "),
        description:
          metadata?.description ?? "Civic subtype specific special feature.",
        costPerSFBySubtype: featureData.costPerSFBySubtype,
        allowedSubtypes: CIVIC_SUBTYPES.filter((subtype) =>
          featureData.allowedSubtypes.includes(subtype)
        ),
      };
    });
};

export const CIVIC_SPECIAL_FEATURES = createCivicSpecialFeatures();

export const getCivicSpecialFeatures = (): SpecialFeatureOption[] =>
  CIVIC_SPECIAL_FEATURES;

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

const RETAIL_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  {
    featureId: "covered_walkway",
    patterns: [/\bcovered walkway\b/i, /\bretail canopy\b/i],
  },
  {
    featureId: "loading_dock",
    patterns: [/\bloading docks?\b/i, /\breceiving dock\b/i],
  },
  {
    featureId: "monument_signage",
    patterns: [/\bmonument sign(?:age)?\b/i, /\bpylon sign(?:age)?\b/i],
  },
  {
    featureId: "outdoor_seating",
    patterns: [/\boutdoor seating\b/i, /\bpatio seating\b/i],
  },
  {
    featureId: "drive_thru",
    patterns: [/drive[\s-]?thru/i, /drive[\s-]?through/i],
  },
  {
    featureId: "storage_units",
    patterns: [/\bback[-\s]?of[-\s]?house storage\b/i, /\bstorage units?\b/i],
  },
  {
    featureId: "mezzanine",
    patterns: [/\bmezzanine\b/i],
  },
  {
    featureId: "auto_center",
    patterns: [/\bauto center\b/i, /\bservice bays?\b/i],
  },
  {
    featureId: "garden_center",
    patterns: [/\bgarden center\b/i, /\bseasonal yard\b/i],
  },
  {
    featureId: "warehouse_racking",
    patterns: [/\bwarehouse racking\b/i, /\bhigh[-\s]?bay racking\b/i],
  },
  {
    featureId: "refrigerated_storage",
    patterns: [/\brefrigerated storage\b/i, /\bcold storage\b/i],
  },
  {
    featureId: "curbside_pickup",
    patterns: [/\bcurbside pickup\b/i, /\bpickup lanes?\b/i],
  },
];

export const detectRetailFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of RETAIL_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

const OFFICE_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  {
    featureId: "executive_floor",
    patterns: [/\bexecutive floor\b/i, /\bclass a office\b/i, /\bgrade a office\b/i],
  },
  {
    featureId: "conference_center",
    patterns: [/\bconference center\b/i, /\btenant conference center\b/i],
  },
  {
    featureId: "structured_parking",
    patterns: [/\bstructured parking\b/i, /\bparking structure\b/i, /\bparking deck\b/i],
  },
  {
    featureId: "green_roof",
    patterns: [/\bgreen roof\b/i],
  },
  {
    featureId: "outdoor_terrace",
    patterns: [/\boutdoor terrace\b/i, /\btenant terrace\b/i],
  },
  {
    featureId: "data_center",
    patterns: [/\btenant data center\b/i, /\boffice data center\b/i],
  },
  {
    featureId: "concierge",
    patterns: [/\bconcierge\b/i, /\bconcierge desk\b/i],
  },
  {
    featureId: "conference_room",
    patterns: [/\bconference room\b/i, /\bclass b office\b/i, /\bgrade b office\b/i],
  },
  {
    featureId: "surface_parking",
    patterns: [/\bsurface parking\b/i],
  },
  {
    featureId: "storage_space",
    patterns: [/\bstorage space\b/i, /\btenant storage\b/i],
  },
  {
    featureId: "security_desk",
    patterns: [/\bsecurity desk\b/i, /\bsecurity lobby\b/i],
  },
  {
    featureId: "fitness_center",
    patterns: [/\bfitness center\b/i, /\boffice gym\b/i],
  },
  {
    featureId: "cafeteria",
    patterns: [/\bcafeteria\b/i, /\btenant cafe\b/i],
  },
];

export const detectOfficeFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of OFFICE_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

const EDUCATIONAL_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  { featureId: "gymnasium", patterns: [/\bgymnasium\b/i, /\bschool gym\b/i] },
  { featureId: "cafeteria", patterns: [/\bcafeteria\b/i, /\bschool dining\b/i] },
  { featureId: "playground", patterns: [/\bplayground\b/i] },
  { featureId: "computer_lab", patterns: [/\bcomputer lab\b/i] },
  { featureId: "library", patterns: [/\blibrary\b/i, /\blearning commons\b/i] },
  { featureId: "science_labs", patterns: [/\bscience labs?\b/i] },
  { featureId: "auditorium", patterns: [/\bauditorium\b/i] },
  { featureId: "athletic_field", patterns: [/\bathletic fields?\b/i] },
  { featureId: "stadium", patterns: [/\bstadium\b/i] },
  { featureId: "field_house", patterns: [/\bfield house\b/i] },
  {
    featureId: "performing_arts_center",
    patterns: [/\bperforming arts center\b/i, /\bperforming arts hall\b/i],
  },
  { featureId: "vocational_shops", patterns: [/\bvocational shops?\b/i] },
  { featureId: "media_center", patterns: [/\bmedia center\b/i] },
  { featureId: "lecture_hall", patterns: [/\blecture hall\b/i] },
  { featureId: "research_lab", patterns: [/\bresearch labs?\b/i, /\bresearch complex\b/i] },
  { featureId: "clean_room", patterns: [/\bclean room\b/i, /\bcleanroom\b/i] },
  { featureId: "student_center", patterns: [/\bstudent center\b/i] },
  { featureId: "vocational_lab", patterns: [/\bvocational lab\b/i, /\bworkforce training\b/i] },
  { featureId: "student_services", patterns: [/\bstudent services\b/i] },
];

export const detectEducationalFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of EDUCATIONAL_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

const EDUCATIONAL_SUBTYPE_CUE_ORDER: Array<{
  subtype: EducationalSubtype;
  patterns: RegExp[];
}> = [
  {
    subtype: "community_college",
    patterns: [/\bcommunity college\b/i, /\bjunior college\b/i, /\btwo-year college\b/i],
  },
  {
    subtype: "elementary_school",
    patterns: [/\belementary school\b/i, /\bprimary school\b/i, /\bgrade school\b/i],
  },
  {
    subtype: "middle_school",
    patterns: [/\bmiddle school\b/i, /\bjunior high\b/i, /\bintermediate school\b/i],
  },
  {
    subtype: "high_school",
    patterns: [/\bhigh school\b/i, /\bsecondary school\b/i, /\bsenior high\b/i],
  },
  {
    subtype: "university",
    patterns: [/\buniversity\b/i, /\bcampus\b/i, /\bhigher education\b/i],
  },
];

export const detectEducationalSubtypeFromDescription = (
  description: string
): EducationalSubtype | undefined => {
  for (const { subtype, patterns } of EDUCATIONAL_SUBTYPE_CUE_ORDER) {
    if (patterns.some((pattern) => pattern.test(description))) {
      return subtype;
    }
  }
  return undefined;
};

const CIVIC_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  {
    featureId: "stacks_load_reinforcement",
    patterns: [/\bstack loads?\b/i, /\bbook stacks?\b/i, /\bstacks? reinforcement\b/i],
  },
  {
    featureId: "acoustic_treatment",
    patterns: [/\bacoustic treatment\b/i, /\bacoustic panels?\b/i, /\bsound attenuation\b/i],
  },
  {
    featureId: "daylighting_controls",
    patterns: [/\bdaylighting controls?\b/i, /\bdaylight sensors?\b/i],
  },
  {
    featureId: "community_rooms",
    patterns: [/\bcommunity rooms?\b/i, /\bmeeting rooms?\b/i],
  },
  {
    featureId: "maker_space_mep",
    patterns: [/\bmakers?\s?space\b/i, /\bfab lab\b/i, /\bmaker space mep\b/i],
  },
  {
    featureId: "courtroom",
    patterns: [/\bcourtrooms?\b/i],
  },
  {
    featureId: "jury_room",
    patterns: [/\bjury rooms?\b/i, /\bdeliberation room\b/i],
  },
  {
    featureId: "holding_cells",
    patterns: [/\bholding cells?\b/i, /\bdetainee holding\b/i],
  },
  {
    featureId: "judges_chambers",
    patterns: [/\bjudges? chambers?\b/i],
  },
  {
    featureId: "security_screening",
    patterns: [/\bsecurity screening\b/i, /\bscreening checkpoint\b/i],
  },
  {
    featureId: "magnetometer_screening_lanes",
    patterns: [/\bmagnetometer\b/i, /\bscreening lanes?\b/i],
  },
  {
    featureId: "sallyport",
    patterns: [/\bsallyport\b/i, /\bsally port\b/i],
  },
  {
    featureId: "ballistic_glazing_package",
    patterns: [/\bballistic glazing\b/i, /\bbullet[-\s]?resistant glazing\b/i],
  },
  {
    featureId: "redundant_life_safety_power",
    patterns: [/\bredundant life[-\s]?safety power\b/i, /\blife safety backup power\b/i],
  },
  {
    featureId: "council_chambers",
    patterns: [/\bcouncil chambers?\b/i, /\bcity council\b/i],
  },
  {
    featureId: "secure_area",
    patterns: [/\bsecure areas?\b/i, /\brestricted government area\b/i],
  },
  {
    featureId: "public_plaza",
    patterns: [/\bpublic plaza\b/i, /\bcivic plaza\b/i],
  },
  {
    featureId: "records_vault",
    patterns: [/\brecords vault\b/i, /\barchival vault\b/i],
  },
  {
    featureId: "gymnasium",
    patterns: [/\bgymnasium\b/i, /\bcommunity gym\b/i],
  },
  {
    featureId: "kitchen",
    patterns: [/\bcommunity kitchen\b/i, /\bcommercial kitchen\b/i],
  },
  {
    featureId: "multipurpose_room",
    patterns: [/\bmultipurpose rooms?\b/i, /\bmulti[-\s]?purpose rooms?\b/i],
  },
  {
    featureId: "fitness_center",
    patterns: [/\bfitness center\b/i, /\bcommunity fitness\b/i],
  },
  {
    featureId: "outdoor_pavilion",
    patterns: [/\boutdoor pavilion\b/i, /\bcommunity pavilion\b/i],
  },
  {
    featureId: "apparatus_bay",
    patterns: [/\bapparatus bays?\b/i, /\bfire apparatus\b/i],
  },
  {
    featureId: "dispatch_center",
    patterns: [/\bdispatch center\b/i, /\b911 center\b/i, /\bpublic safety dispatch\b/i],
  },
  {
    featureId: "training_tower",
    patterns: [/\btraining tower\b/i, /\bfire training tower\b/i],
  },
  {
    featureId: "emergency_generator",
    patterns: [/\bemergency generator\b/i, /\bbackup generator\b/i],
  },
  {
    featureId: "sally_port",
    patterns: [/\bsally port\b/i],
  },
];

export const detectCivicFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of CIVIC_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

const CIVIC_SUBTYPE_CUE_ORDER: Array<{
  subtype: CivicSubtype;
  patterns: RegExp[];
}> = [
  {
    subtype: "courthouse",
    patterns: [/\bcourthouse\b/i, /\bcourt house\b/i, /\bjustice center\b/i, /\bjudicial center\b/i],
  },
  {
    subtype: "public_safety",
    patterns: [
      /\bpublic safety\b/i,
      /\bfire station\b/i,
      /\bpolice station\b/i,
      /\bsheriff\b/i,
      /\bdispatch center\b/i,
      /\b911 center\b/i,
      /\bemergency services\b/i,
      /\beoc\b/i,
    ],
  },
  {
    subtype: "library",
    patterns: [
      /\bpublic library\b/i,
      /\bbranch library\b/i,
      /\bcommunity library\b/i,
      /\blibrary makerspace\b/i,
      /\blearning commons\b/i,
      /\blibrary\b/i,
    ],
  },
  {
    subtype: "community_center",
    patterns: [
      /\bcommunity center\b/i,
      /\brec center\b/i,
      /\bsenior center\b/i,
      /\byouth center\b/i,
      /\bcultural center\b/i,
      /\bactivity center\b/i,
      /\bcivic center\b/i,
    ],
  },
  {
    subtype: "government_building",
    patterns: [
      /\bcity hall\b/i,
      /\bmunicipal building\b/i,
      /\bgovernment center\b/i,
      /\bfederal building\b/i,
      /\bstate building\b/i,
      /\bcapitol\b/i,
      /\badministration building\b/i,
      /\bgovernment building\b/i,
    ],
  },
];

export const detectCivicSubtypeFromDescription = (
  description: string
): CivicSubtype | undefined => {
  for (const { subtype, patterns } of CIVIC_SUBTYPE_CUE_ORDER) {
    if (patterns.some((pattern) => pattern.test(description))) {
      return subtype;
    }
  }
  return undefined;
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

const HEALTHCARE_KEYWORD_DETECTION: Array<{
  featureId: string;
  patterns: RegExp[];
}> = [
  {
    featureId: "emergency_department",
    patterns: [/\bemergency department\b/i, /\btrauma center\b/i, /\bemergency services?\b/i],
  },
  {
    featureId: "emergency",
    patterns: [/\bemergency department\b/i, /\btrauma center\b/i, /\bemergency services?\b/i],
  },
  {
    featureId: "imaging_suite",
    patterns: [/\bimaging suite\b/i, /\bimaging center\b/i, /\bmri\b/i, /\bct\b/i, /\bpet\b/i],
  },
  {
    featureId: "imaging",
    patterns: [/\bimaging center\b/i, /\bimaging suite\b/i, /\bmri\b/i, /\bct\b/i, /\bpet\b/i],
  },
  {
    featureId: "surgical_suite",
    patterns: [/\bsurgical suite\b/i, /\boperating rooms?\b/i, /\bOR suites?\b/i, /\bOR surgical suite\b/i],
  },
  {
    featureId: "surgery",
    patterns: [/\bsurgery center\b/i, /\bsurgical suite\b/i, /\boperating rooms?\b/i, /\bOR suites?\b/i],
  },
  {
    featureId: "icu",
    patterns: [/\bicu\b/i, /\bintensive care\b/i],
  },
  {
    featureId: "laboratory",
    patterns: [/\blaboratory\b/i, /\blab\b/i, /\bon[-\s]?site lab\b/i, /\bpathology\b/i],
  },
  {
    featureId: "lab",
    patterns: [/\bdental lab\b/i],
  },
  {
    featureId: "operating_room",
    patterns: [/\boperating room\b/i, /\bOR room\b/i],
  },
  {
    featureId: "pre_op",
    patterns: [/\bpre[-\s]?op\b/i],
  },
  {
    featureId: "recovery_room",
    patterns: [/\brecovery room\b/i, /\bpacu\b/i],
  },
  {
    featureId: "sterile_processing",
    patterns: [/\bsterile processing\b/i],
  },
  {
    featureId: "mri_suite",
    patterns: [/\bmri suite\b/i],
  },
  {
    featureId: "ct_suite",
    patterns: [/\bct suite\b/i],
  },
  {
    featureId: "pet_scan",
    patterns: [/\bpet scan\b/i],
  },
  {
    featureId: "ultrasound",
    patterns: [/\bultrasound\b/i],
  },
  {
    featureId: "mammography",
    patterns: [/\bmammography\b/i],
  },
  {
    featureId: "trauma_room",
    patterns: [/\btrauma room\b/i],
  },
  {
    featureId: "x_ray",
    patterns: [/\bx[-\s]?ray\b/i],
  },
  {
    featureId: "exam_rooms",
    patterns: [/\bexam rooms?\b/i],
  },
  {
    featureId: "procedure_room",
    patterns: [/\bprocedure rooms?\b/i],
  },
  {
    featureId: "tenant_improvements",
    patterns: [/\btenant improvements?\b/i, /\bti package\b/i],
  },
  {
    featureId: "ambulatory_imaging",
    patterns: [/\bambulatory imaging\b/i],
  },
  {
    featureId: "ambulatory_buildout",
    patterns: [/\bambulatory build(?:out)?\b/i, /\bambulatory tower\b/i, /\bambulatory fit[-\s]?out\b/i],
  },
  {
    featureId: "operatory",
    patterns: [/\bdental operator(?:y|ies)\b/i, /\boperatory\b/i],
  },
  {
    featureId: "sterilization",
    patterns: [/\bdental sterilization\b/i],
  },
  {
    featureId: "cathlab",
    patterns: [/\bcath[\s-]?lab\b/i, /\bcatheterization lab\b/i],
  },
  {
    featureId: "pharmacy",
    patterns: [/\bpharmacy\b/i, /\bsterile compounding\b/i],
  },
  {
    featureId: "specialty_clinic",
    patterns: [/\bspecialty clinic\b/i, /\binfusion suite\b/i],
  },
  {
    featureId: "memory_care",
    patterns: [/\bmemory care\b/i, /\bmemory care wing\b/i, /\bwander management\b/i],
  },
  {
    featureId: "therapy_room",
    patterns: [/\btherapy room\b/i, /\brehab gym\b/i, /\bnurse call\b/i],
  },
  {
    featureId: "activity_room",
    patterns: [/\bactivity room\b/i],
  },
  {
    featureId: "dining_hall",
    patterns: [/\bdining hall\b/i, /\bhousehold dining\b/i, /\bsmall house model\b/i],
  },
  {
    featureId: "therapy_gym",
    patterns: [/\btherapy gym\b/i],
  },
  {
    featureId: "hydrotherapy",
    patterns: [/\bhydrotherapy\b/i, /\bhydrotherapy pool\b/i],
  },
  {
    featureId: "treatment_rooms",
    patterns: [/\btreatment rooms?\b/i, /\badl apartment\b/i, /\bactivities of daily living\b/i, /\bspeech(?:\s+and)? neuro\b/i, /\bneuro rehab suite\b/i],
  },
  {
    featureId: "assessment_suite",
    patterns: [/\bassessment suite\b/i, /\bgait training\b/i],
  },
  {
    featureId: "hc_imaging_second_mri",
    patterns: [/\bsecond mri\b/i, /\badditional mri\b/i],
  },
  {
    featureId: "hc_imaging_pet_ct_suite",
    patterns: [/\bpet\/?ct\b/i, /\bpet ct\b/i],
  },
  {
    featureId: "hc_imaging_interventional_rad",
    patterns: [/\binterventional radiology\b/i, /\bangio\b/i],
  },
  {
    featureId: "hc_asc_hybrid_or_cath_lab",
    patterns: [/\bhybrid or\b/i, /\bcath lab\b/i],
  },
  {
    featureId: "mob_imaging_ready_shell",
    patterns: [/\bimaging-ready shell\b/i, /\bimaging ready shell\b/i],
  },
  {
    featureId: "mob_enhanced_mep",
    patterns: [/\benhanced mep\b/i, /\bupgraded mep\b/i],
  },
  {
    featureId: "mob_procedure_suite",
    patterns: [/\bprocedure suite\b/i],
  },
  {
    featureId: "mob_pharmacy_shell",
    patterns: [/\bpharmacy shell\b/i, /\bpharmacy space\b/i],
  },
  {
    featureId: "mob_covered_dropoff",
    patterns: [/\bcovered drop[-\s]?off\b/i, /\bpatient canopy\b/i],
  },
  {
    featureId: "hc_dental_pano_ceph",
    patterns: [/\bpano\b/i, /\bceph\b/i, /\bpanoramic x-ray\b/i],
  },
  {
    featureId: "hc_dental_sedation_suite",
    patterns: [/\bsedation suite\b/i, /\biv sedation\b/i],
  },
  {
    featureId: "hc_dental_sterilization_upgrade",
    patterns: [/\bsterilization\b/i],
  },
  {
    featureId: "hc_dental_ortho_bay_expansion",
    patterns: [/\borthodontic\b/i, /\bortho bay\b/i],
  },
];

export const detectHealthcareFeatureIdsFromDescription = (
  description: string
): string[] => {
  const detectedFeatureIds = new Set<string>();
  for (const { featureId, patterns } of HEALTHCARE_KEYWORD_DETECTION) {
    if (patterns.some((pattern) => pattern.test(description))) {
      detectedFeatureIds.add(featureId);
    }
  }
  return Array.from(detectedFeatureIds);
};

const SPECIAL_FEATURES_BY_BUILDING_TYPE: Record<string, SpecialFeatureOption[]> = {
  restaurant: RESTAURANT_SPECIAL_FEATURES,
  hospitality: HOSPITALITY_SPECIAL_FEATURES,
  retail: RETAIL_SPECIAL_FEATURES,
  office: OFFICE_SPECIAL_FEATURES,
  specialty: SPECIALTY_SPECIAL_FEATURES,
  healthcare: HEALTHCARE_SPECIAL_FEATURES,
  educational: EDUCATIONAL_SPECIAL_FEATURES,
  civic: CIVIC_SPECIAL_FEATURES,
};

const VALID_SUBTYPES_BY_BUILDING_TYPE: Record<string, readonly string[]> = {
  restaurant: RESTAURANT_SUBTYPES,
  hospitality: HOSPITALITY_SUBTYPES,
  retail: RETAIL_SUBTYPES,
  office: OFFICE_SUBTYPES,
  specialty: SPECIALTY_SUBTYPES,
  healthcare: HEALTHCARE_SUBTYPES,
  educational: EDUCATIONAL_SUBTYPES,
  civic: CIVIC_SUBTYPES,
};

export const getAvailableSpecialFeatures = (
  buildingType?: string,
  subtype?: string
): SpecialFeatureOption[] => {
  if (!buildingType) {
    return [];
  }
  const features = SPECIAL_FEATURES_BY_BUILDING_TYPE[buildingType] || [];
  if (!subtype) {
    return features;
  }
  const validSubtypes = VALID_SUBTYPES_BY_BUILDING_TYPE[buildingType];
  if (Array.isArray(validSubtypes) && !validSubtypes.includes(subtype)) {
    // Explicitly preserve unknown-subtype behavior; do not coerce to a known subtype.
    return [];
  }
  return filterSpecialFeaturesBySubtype(features, subtype);
};

export const getSpecialFeatureCost = (
  buildingType: string,
  featureId: string,
  subtype?: string
): number | undefined => {
  if (!buildingType || !featureId) {
    return undefined;
  }
  const feature = getAvailableSpecialFeatures(buildingType, subtype).find(
    (entry) => entry.id === featureId
  );
  if (!feature) {
    return undefined;
  }

  const subtypeCost =
    subtype && feature.costPerSFBySubtype
      ? feature.costPerSFBySubtype[subtype]
      : undefined;
  if (typeof subtypeCost === "number" && Number.isFinite(subtypeCost)) {
    return subtypeCost;
  }
  if (typeof feature.costPerSF === "number" && Number.isFinite(feature.costPerSF)) {
    return feature.costPerSF;
  }
  if (typeof feature.cost === "number" && Number.isFinite(feature.cost)) {
    return feature.cost;
  }
  return undefined;
};

export const restaurantSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(RESTAURANT_SPECIAL_FEATURES, subtype).length > 0;

export const hospitalitySubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(HOSPITALITY_SPECIAL_FEATURES, subtype).length > 0;

export const retailSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(RETAIL_SPECIAL_FEATURES, subtype).length > 0;

export const specialtySubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(SPECIALTY_SPECIAL_FEATURES, subtype).length > 0;

export const healthcareSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(HEALTHCARE_SPECIAL_FEATURES, subtype).length > 0;

export const officeSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(OFFICE_SPECIAL_FEATURES, subtype).length > 0;

export const educationalSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(EDUCATIONAL_SPECIAL_FEATURES, subtype).length > 0;

export const civicSubtypeHasSpecialFeatures = (subtype?: string): boolean =>
  filterSpecialFeaturesBySubtype(CIVIC_SPECIAL_FEATURES, subtype).length > 0;
