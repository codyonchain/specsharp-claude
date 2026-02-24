import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectAnalysis } from '../../hooks/useProjectAnalysis';
import { api, createProject } from '../../api/client';
import { tracer } from '../../utils/traceSystem';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import { BuildingTaxonomy } from '../../../core/buildingTaxonomy';
import {
  detectRestaurantFeatureIdsFromDescription,
  filterSpecialFeaturesBySubtype,
  getRestaurantSpecialFeatures,
  type SpecialFeatureOption,
} from './specialFeaturesCatalog';

// Lucide icons
import { 
  Building2, Sparkles, ArrowRight, Check, AlertCircle,
  Calculator, MapPin, Layers, Tag, Loader2, ChevronDown,
  TrendingUp, DollarSign, Clock, Square, FileText,
  Zap, RefreshCw, Save, Building, GraduationCap, Heart,
  Home, Factory, ShoppingBag, Plus, X, Settings, Info,
  UtensilsCrossed, Briefcase, Hotel, Warehouse, ShoppingCart,
  Shield, Dumbbell, Car, Box
} from 'lucide-react';

const CITY_STATE_REGEX = /^.+,\s*[A-Za-z]{2}$/i;

const detectCityStateInDescription = (text: string): string | null => {
  if (!text) return null;

  // Strictly extract canonical "City, ST" (use the LAST match in the string).
  // City rules:
  // - 1 to 4 tokens
  // - each token letters/periods/hyphens only (no digits)
  const pattern =
    /(?:^|[\s(])([A-Z][a-zA-Z.\-]*(?:\s+[A-Z][a-zA-Z.\-]*){0,3}),\s*([A-Z]{2})(?:\b|[\s).,;:!?\"'])/g;

  const forbiddenTokens = new Set([
    "SF", "SQ", "SQFT", "FT",
    "OFFICE", "WAREHOUSE", "DISTRIBUTION", "CENTER",
    "CLINIC", "HOSPITAL", "HOTEL", "RESTAURANT", "SCHOOL",
    "APARTMENT", "INDUSTRIAL", "CLASS", "BUILDING",
    "NEW", "REMODEL", "RENOVATION", "IN",
  ]);

  let match: RegExpExecArray | null;
  let lastValid: { city: string; state: string } | null = null;

  while ((match = pattern.exec(text)) !== null) {
    const cityRaw = (match[1] || "").trim();
    const stateRaw = (match[2] || "").trim().toUpperCase();
    if (!cityRaw || !stateRaw) continue;
    if (cityRaw.length > 40) continue;
    if (/\d/.test(cityRaw)) continue;

    const tokens = cityRaw.toUpperCase().split(/\s+/).filter(Boolean);
    if (tokens.some(token => forbiddenTokens.has(token))) continue;

    lastValid = { city: cityRaw, state: stateRaw };
  }

  return lastValid ? `${lastValid.city}, ${lastValid.state}` : null;
};



export const NewProject: React.FC = () => {
  const navigate = useNavigate();
  const resultsRef = useRef<HTMLDivElement>(null);
  const { analyzing, result, error, analyzeDescription, reset } = useProjectAnalysis();
  
  // Form state
  const [description, setDescription] = useState('');
  const [squareFootageInput, setSquareFootageInput] = useState('');
  const [locationInput, setLocationInput] = useState('');
  const [activeStep, setActiveStep] = useState<'input' | 'analyzing' | 'results'>('input');
  const [saving, setSaving] = useState(false);
  
  // Project configuration state
  const [specialFeatures, setSpecialFeatures] = useState<string[]>([]);
  const [finishLevel, setFinishLevel] = useState<'standard' | 'premium'>('standard');
  const [finishLevelLocked, setFinishLevelLocked] = useState(false);
  const [projectComplexity, setProjectComplexity] = useState<'ground_up' | 'renovation' | 'addition'>('ground_up');
  const [projectClassLocked, setProjectClassLocked] = useState(false);
  const [locationTouched, setLocationTouched] = useState(false);
  const [locationAutoFilled, setLocationAutoFilled] = useState(false);
  const [locationSubmitAttempted, setLocationSubmitAttempted] = useState(false);
  // Finish level options (universal v1) – keep only one upgrade tier for underwriting comparisons
  const FINISH_LEVELS = [
    { label: 'Standard', value: 'standard', multiplierLabel: '1.0x' },
    { label: 'Premium', value: 'premium', multiplierLabel: '1.2x' },
  ] as const;

  // Live preview state
  const [previewData, setPreviewData] = useState<{
    totalCost?: number;
    annualRevenue?: number;
    noi?: number;
    roi?: number;
    payback?: number;
  } | null>(null);
  const [previewStatus, setPreviewStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [previewError, setPreviewError] = useState<string | null>(null);
  const previewTimeoutRef = useRef<number | null>(null);
  const previewAbortRef = useRef<AbortController | null>(null);

  const normalizedDescription = description.trim();
  const normalizedLocationInput = locationInput.trim();
  const isLocationFormatValid = CITY_STATE_REGEX.test(normalizedLocationInput);
  const shouldShowLocationError =
    (!isLocationFormatValid && (locationSubmitAttempted || normalizedLocationInput.length > 0));
  const canAnalyze = Boolean(normalizedDescription) && isLocationFormatValid && !analyzing;
  const liveDetectedLocation = useMemo(() => detectCityStateInDescription(description), [description]);
  
  // NLP detection state
  const [detectedFeatures, setDetectedFeatures] = useState({
    size: false,
    type: false,
    location: false
  });
  
  // Monitor input for NLP detection
  useEffect(() => {
    const input = description.toLowerCase();
    const cityKeywordDetected = /(nashville|franklin|brentwood|murfreesboro|manchester|nashua|concord|bedford|salem)/i.test(input);
    setDetectedFeatures({
      size: /\d+[\s,]*(?:sf|square|feet|unit|key|bed|room)/i.test(description),
      type: /(apartment|office|hospital|school|retail|industrial|hotel|restaurant|warehouse|medical|clinic|surgery|emergency|distribution|strip\s*mall)/i.test(input),
      location: Boolean(liveDetectedLocation || cityKeywordDetected)
    });
  }, [description, liveDetectedLocation]);
  
  // Example prompts covering all 13 building types
  const examplePrompts = [
    {
      icon: <Heart className="h-6 w-6" />,
      text: '200,000 sf hospital with emergency department in Nashville, TN',
      highlights: ['200,000 sf', 'hospital', 'emergency department', 'Nashville, TN'],
      type: 'healthcare',
      color: 'text-red-600 bg-red-50',
      squareFootage: 200000,
      location: 'Nashville, TN'
    },
    {
      icon: <UtensilsCrossed className="h-6 w-6" />,
      text: '5,000 sf full service restaurant in Nashville, TN',
      highlights: ['5,000 sf', 'full service restaurant', 'Nashville, TN'],
      type: 'restaurant',
      color: 'text-orange-600 bg-orange-50',
      squareFootage: 5000,
      location: 'Nashville, TN'
    },
    {
      icon: <Building className="h-6 w-6" />,
      text: '250,000 sf luxury apartments complex with 250 units and amenity deck in Brentwood, TN',
      highlights: ['250,000 sf', 'luxury apartments', '250 units', 'Brentwood, TN'],
      type: 'multifamily',
      color: 'text-purple-600 bg-purple-50',
      squareFootage: 250000,
      location: 'Brentwood, TN'
    },
    {
      icon: <Briefcase className="h-6 w-6" />,
      text: '50,000 sf class A office in Nashville, TN',
      highlights: ['50,000 sf', 'class A office', 'Nashville, TN'],
      type: 'office',
      color: 'text-blue-600 bg-blue-50',
      squareFootage: 50000,
      location: 'Nashville, TN'
    },
    {
      icon: <Hotel className="h-6 w-6" />,
      text: '120,000 sf full service hotel with 200 rooms in downtown Nashville, TN',
      highlights: ['120,000 sf', 'full service hotel', '200 rooms', 'Nashville, TN'],
      type: 'hospitality',
      color: 'text-indigo-600 bg-indigo-50',
      squareFootage: 120000,
      location: 'Nashville, TN'
    },
    {
      icon: <Warehouse className="h-6 w-6" />,
      text: '120,000 sf warehouse with twenty four docks in La Vergne, TN',
      highlights: ['120,000 sf', 'warehouse', 'twenty four docks', 'La Vergne, TN'],
      type: 'industrial',
      color: 'text-gray-600 bg-gray-50',
      squareFootage: 120000,
      location: 'La Vergne, TN'
    },
    {
      icon: <ShoppingCart className="h-6 w-6" />,
      text: '35,000 sf shopping center with grocery anchor in Franklin, TN',
      highlights: ['35,000 sf', 'shopping center', 'grocery anchor', 'Franklin, TN'],
      type: 'retail',
      color: 'text-pink-600 bg-pink-50',
      squareFootage: 35000,
      location: 'Franklin, TN'
    },
    {
      icon: <GraduationCap className="h-6 w-6" />,
      text: '65,000 sf middle school for 800 students in Bedford, NH',
      highlights: ['65,000 sf', 'middle school', '800 students', 'Bedford, NH'],
      type: 'educational',
      color: 'text-green-600 bg-green-50',
      squareFootage: 65000,
      location: 'Bedford, NH'
    },
    {
      icon: <Shield className="h-6 w-6" />,
      text: '25,000 sf public safety building with fire station in Murfreesboro, TN',
      highlights: ['25,000 sf', 'public safety', 'fire station', 'Murfreesboro, TN'],
      type: 'civic',
      color: 'text-amber-600 bg-amber-50',
      squareFootage: 25000,
      location: 'Murfreesboro, TN'
    },
    {
      icon: <Dumbbell className="h-6 w-6" />,
      text: '45,000 sf fitness center with pool and basketball courts in Brentwood, TN',
      highlights: ['45,000 sf', 'fitness center', 'pool', 'Brentwood, TN'],
      type: 'recreation',
      color: 'text-teal-600 bg-teal-50',
      squareFootage: 45000,
      location: 'Brentwood, TN'
    },
    {
      icon: <Building2 className="h-6 w-6" />,
      text: '180,000 sf urban mixed development with retail and residential in Nashville, TN',
      highlights: ['180,000 sf', 'urban mixed', 'retail and residential', 'Nashville, TN'],
      type: 'mixed_use',
      color: 'text-violet-600 bg-violet-50',
      squareFootage: 180000,
      location: 'Nashville, TN'
    },
    {
      icon: <Car className="h-6 w-6" />,
      text: '100,000 sf parking garage with 300 spaces in downtown Nashville, TN',
      highlights: ['100,000 sf', 'parking garage', '300 spaces', 'Nashville, TN'],
      type: 'parking',
      color: 'text-slate-600 bg-slate-50',
      squareFootage: 100000,
      location: 'Nashville, TN'
    },
    {
      icon: <Box className="h-6 w-6" />,
      text: '80,000 sf self storage facility with climate control in Antioch, TN',
      highlights: ['80,000 sf', 'self storage', 'climate control', 'Antioch, TN'],
      type: 'specialty',
      color: 'text-stone-600 bg-stone-50',
      squareFootage: 80000,
      location: 'Antioch, TN'
    }
  ];
  
  // Special features by building type
  const getAvailableFeatures = (buildingType: string): SpecialFeatureOption[] => {
    const features: Record<string, SpecialFeatureOption[]> = {
      healthcare: [
        {
          id: 'emergency',
          name: 'Emergency Department',
          cost: 10000000,
          description: 'Full 24/7 emergency room with trauma center',
          allowedSubtypes: ['hospital', 'medical_center']
        },
        {
          id: 'imaging',
          name: 'Imaging Center',
          cost: 5000000,
          description: 'MRI, CT, X-ray equipment and rooms',
          allowedSubtypes: ['hospital', 'medical_center']
        },
        {
          id: 'surgery',
          name: 'Surgery Center',
          cost: 8000000,
          description: 'Operating rooms and recovery areas',
          allowedSubtypes: ['hospital', 'medical_center']
        },
        {
          id: 'icu',
          name: 'ICU Unit',
          cost: 6000000,
          description: 'Intensive care unit with specialized equipment',
          allowedSubtypes: ['hospital', 'medical_center']
        },
        {
          id: 'lab',
          name: 'Laboratory',
          cost: 3000000,
          description: 'Full medical testing laboratory',
          allowedSubtypes: ['outpatient_clinic', 'urgent_care', 'imaging_center', 'medical_center', 'hospital']
        },
        // Outpatient clinic specials
        {
          id: 'hc_outpatient_on_site_lab',
          name: 'On-Site Lab',
          cost: 600000,
          description: 'Adds a small on-site laboratory for basic bloodwork and diagnostics.',
          allowedSubtypes: ['outpatient_clinic']
        },
        {
          id: 'hc_outpatient_imaging_pod',
          name: 'Imaging Pod (X-ray/Ultrasound)',
          cost: 1200000,
          description: 'Adds a small imaging pod with X-ray and ultrasound for in-clinic diagnostics.',
          allowedSubtypes: ['outpatient_clinic']
        },
        {
          id: 'hc_outpatient_behavioral_suite',
          name: 'Behavioral Health Suite',
          cost: 500000,
          description: 'Builds out dedicated rooms for behavioral health and counseling.',
          allowedSubtypes: ['outpatient_clinic']
        },
        // Urgent care specials
        {
          id: 'hc_urgent_on_site_lab',
          name: 'On-Site Lab',
          cost: 750000,
          description: 'Full CLIA-waived urgent-care lab for rapid tests and basic diagnostics.',
          allowedSubtypes: ['urgent_care']
        },
        {
          id: 'hc_urgent_imaging_suite',
          name: 'Imaging Suite (X-ray/CT)',
          cost: 1500000,
          description: 'Adds dedicated X-ray and CT equipment with control room and shielding.',
          allowedSubtypes: ['urgent_care']
        },
        {
          id: 'hc_urgent_observation_bays',
          name: 'Observation Bays',
          cost: 500000,
          description: 'Adds short-stay observation bays for 4–8 hour monitoring.',
          allowedSubtypes: ['urgent_care']
        },
        // Imaging center specials
        {
          id: 'hc_imaging_second_mri',
          name: 'Second MRI Room',
          cost: 2000000,
          description: 'Adds a second MRI gantry with control room and support spaces.',
          allowedSubtypes: ['imaging_center']
        },
        {
          id: 'hc_imaging_pet_ct_suite',
          name: 'PET/CT Suite',
          cost: 3000000,
          description: 'Adds a PET/CT suite including hot lab and shielding.',
          allowedSubtypes: ['imaging_center']
        },
        {
          id: 'hc_imaging_interventional_rad',
          name: 'Interventional Radiology Room',
          cost: 2500000,
          description: 'Builds an interventional radiology / angio room with procedure support.',
          allowedSubtypes: ['imaging_center']
        },
        // Surgical center specials
        {
          id: 'hc_asc_expanded_pacu',
          name: 'Expanded PACU',
          cost: 1500000,
          description: 'Larger post-anesthesia care unit for higher case volume or longer recoveries.',
          allowedSubtypes: ['surgical_center']
        },
        {
          id: 'hc_asc_sterile_core_upgrade',
          name: 'Sterile Core Upgrade',
          cost: 1000000,
          description: 'Upgrades sterile processing, clean/dirty cores, and instrument storage.',
          allowedSubtypes: ['surgical_center']
        },
        {
          id: 'hc_asc_pain_management_suite',
          name: 'Pain Management Suite',
          cost: 1200000,
          description: 'Adds dedicated pain management procedure rooms within the ASC.',
          allowedSubtypes: ['surgical_center']
        },
        {
          id: 'hc_asc_hybrid_or_cath_lab',
          name: 'Hybrid OR / Cath Lab',
          cost: 2500000,
          description: 'Builds a hybrid OR or cath lab with advanced imaging and structural support.',
          allowedSubtypes: ['surgical_center']
        },
        // --- Medical Office Building (MOB) Special Features ---
        {
          id: 'mob_imaging_ready_shell',
          name: 'Imaging-Ready Shell',
          cost: 800000,
          description: 'Structural, vibration, and electrical upgrades to support future MRI/CT tenants.',
          allowedSubtypes: ['medical_office']
        },
        {
          id: 'mob_enhanced_mep',
          name: 'Enhanced MEP Capacity',
          cost: 400000,
          description: 'Upgrades to HVAC, electrical, med-gas routing, and risers for specialty tenants.',
          allowedSubtypes: ['medical_office']
        },
        {
          id: 'mob_procedure_suite',
          name: 'Procedure Suite Buildout',
          cost: 600000,
          description: 'Adds 1–2 Class B/C procedure rooms for multi-specialty and high-acuity tenants.',
          allowedSubtypes: ['medical_office']
        },
        {
          id: 'mob_pharmacy_shell',
          name: 'Pharmacy / Retail Shell',
          cost: 250000,
          description: 'First-floor shell space for pharmacy or medical retail tenants.',
          allowedSubtypes: ['medical_office']
        },
        {
          id: 'mob_covered_dropoff',
          name: 'Covered Drop-Off Canopy',
          cost: 300000,
          description: 'Adds a patient drop-off canopy with lighting and accessibility upgrades.',
          allowedSubtypes: ['medical_office']
        },
        // Dental office specials
        {
          id: 'hc_dental_pano_ceph',
          name: 'Panoramic X-ray / Ceph Suite',
          cost: 250000,
          description: 'Dedicated pano/ceph room with shielding, mechanical, and positioning equipment.',
          allowedSubtypes: ['dental_office']
        },
        {
          id: 'hc_dental_sedation_suite',
          name: 'Sedation / Surgery Suite',
          cost: 350000,
          description: 'Upgrades one operatory to IV sedation standards with gases, exhaust, and monitoring.',
          allowedSubtypes: ['dental_office']
        },
        {
          id: 'hc_dental_sterilization_upgrade',
          name: 'Central Sterilization Upgrade',
          cost: 150000,
          description: 'Expanded sterilization core with added autoclaves, casework, and clean/dirty zoning.',
          allowedSubtypes: ['dental_office']
        },
        {
          id: 'hc_dental_ortho_bay_expansion',
          name: 'Orthodontic Bay Expansion',
          cost: 200000,
          description: 'Open-bay ortho layout with additional chairs, suction, power, and task lighting.',
          allowedSubtypes: ['dental_office']
        }
      ],
      educational: [
        { id: 'gymnasium', name: 'Gymnasium', cost: 2000000, description: 'Full-size gym with bleachers' },
        { id: 'auditorium', name: 'Auditorium', cost: 3000000, description: 'Performance space with seating' },
        { id: 'cafeteria', name: 'Cafeteria & Kitchen', cost: 1500000, description: 'Commercial kitchen and dining' },
        { id: 'science_labs', name: 'Science Labs', cost: 2500000, description: 'Specialized laboratory classrooms' },
        { id: 'athletic_fields', name: 'Athletic Fields', cost: 1000000, description: 'Outdoor sports facilities' }
      ],
      residential: [
        { id: 'parking_garage', name: 'Parking Garage', cost: 5000000, description: 'Structured parking facility' },
        { id: 'pool', name: 'Pool & Amenity Deck', cost: 2000000, description: 'Swimming pool and deck area' },
        { id: 'fitness', name: 'Fitness Center', cost: 500000, description: 'Gym and workout facilities' },
        { id: 'clubhouse', name: 'Clubhouse', cost: 1000000, description: 'Community gathering space' },
        { id: 'rooftop', name: 'Rooftop Terrace', cost: 1500000, description: 'Rooftop amenity space' }
      ],
      multifamily: [
        {
          id: 'parking_garage',
          name: 'Parking Garage',
          costPerSFBySubtype: {
            luxury_apartments: 45,
            market_rate_apartments: 32,
            affordable_housing: 26,
          },
          description: 'Structured resident and guest parking',
          allowedSubtypes: ['market_rate_apartments', 'luxury_apartments', 'affordable_housing']
        },
        {
          id: 'pool',
          name: 'Pool',
          costPerSFBySubtype: {
            luxury_apartments: 25,
            market_rate_apartments: 18,
            affordable_housing: 12,
          },
          description: 'Outdoor pool with code-compliant deck and support spaces',
          allowedSubtypes: ['market_rate_apartments', 'luxury_apartments', 'affordable_housing']
        },
        {
          id: 'fitness_center',
          name: 'Fitness Center',
          costPerSFBySubtype: {
            luxury_apartments: 20,
            market_rate_apartments: 14,
            affordable_housing: 10,
          },
          description: 'Resident fitness room with specialty flooring and MEP upgrades',
          allowedSubtypes: ['market_rate_apartments', 'luxury_apartments', 'affordable_housing']
        },
        {
          id: 'rooftop_amenity',
          name: 'Rooftop Amenity',
          costPerSFBySubtype: {
            luxury_apartments: 35,
            market_rate_apartments: 24,
            affordable_housing: 18,
          },
          description: 'Rooftop gathering area with shade structures and utility tie-ins',
          allowedSubtypes: ['market_rate_apartments', 'luxury_apartments', 'affordable_housing']
        },
        {
          id: 'concierge',
          name: 'Concierge Lobby',
          costPerSFBySubtype: {
            luxury_apartments: 15,
          },
          description: 'Enhanced staffed lobby and service desk buildout',
          allowedSubtypes: ['luxury_apartments']
        }
      ],
      commercial: [
        { id: 'data_center', name: 'Data Center', cost: 5000000, description: 'Server room with redundant systems' },
        { id: 'cafeteria', name: 'Cafeteria', cost: 1000000, description: 'Employee dining facility' },
        { id: 'fitness', name: 'Fitness Center', cost: 750000, description: 'Employee gym' },
        { id: 'conference', name: 'Conference Center', cost: 2000000, description: 'Large meeting spaces' },
        { id: 'parking_deck', name: 'Parking Deck', cost: 4000000, description: 'Multi-level parking' }
      ],
      industrial: [
        { id: 'loading_docks', name: 'Extra Loading Docks', cost: 500000, description: 'Additional truck bays' },
        { id: 'cold_storage', name: 'Cold Storage', cost: 3000000, description: 'Refrigerated warehouse space' },
        { id: 'office_buildout', name: 'Office Build-out', cost: 1000000, description: 'Administrative space' },
        { id: 'cranes', name: 'Overhead Cranes', cost: 2000000, description: 'Heavy lifting equipment' }
      ],
      retail: [
        { id: 'food_court', name: 'Food Court', cost: 2000000, description: 'Multi-vendor dining area' },
        { id: 'anchor_fitout', name: 'Anchor Tenant Fit-out', cost: 3000000, description: 'Major retailer customization' },
        { id: 'parking_deck', name: 'Parking Deck', cost: 4000000, description: 'Structured parking' }
      ],
      restaurant: getRestaurantSpecialFeatures(),
    };
    
    return features[buildingType] || [];
  };
  
  // Parse description to detect features automatically
  const parseDescription = (desc: string) => {
    const lower = desc.toLowerCase();
    
    // Detect special features in description
    const detectedFeatures = new Set<string>();
    if (lower.includes('emergency')) detectedFeatures.add('emergency');
    if (lower.includes('imaging')) detectedFeatures.add('imaging');
    if (lower.includes('gymnasium') || lower.includes('gym')) detectedFeatures.add('gymnasium');
    if (lower.includes('parking garage') || lower.includes('garage')) detectedFeatures.add('parking_garage');
    if (lower.includes('pool')) detectedFeatures.add('pool');
    if (lower.includes('cafeteria')) detectedFeatures.add('cafeteria');
    if (lower.includes('loading dock')) detectedFeatures.add('loading_docks');
    if (lower.includes('cold storage')) detectedFeatures.add('cold_storage');
    if (lower.includes('food court')) detectedFeatures.add('food_court');
    for (const featureId of detectRestaurantFeatureIdsFromDescription(desc)) {
      detectedFeatures.add(featureId);
    }
    
    // Detect finish level (luxury/high-end terms map into premium)
    let detectedFinish: 'standard' | 'premium' = 'standard';
    if (
      lower.includes('luxury') ||
      lower.includes('high-end') ||
      lower.includes('premium') ||
      lower.includes('class a')
    ) {
      detectedFinish = 'premium';
    }
    
    // Detect project complexity
    let detectedComplexity: 'ground_up' | 'renovation' | 'addition' = 'ground_up';
    if (lower.includes('renovation') || lower.includes('renovate') || lower.includes('remodel')) detectedComplexity = 'renovation';
    else if (lower.includes('addition') || lower.includes('expansion') || lower.includes('expand')) detectedComplexity = 'addition';
    
    return {
      specialFeatures: Array.from(detectedFeatures),
      finishLevel: detectedFinish,
      projectComplexity: detectedComplexity
    };
  };

  const parseSquareFootageValue = (value: string): number | undefined => {
    if (!value) return undefined;
    const cleaned = value.replace(/,/g, '').trim().toLowerCase();
    if (!cleaned) return undefined;

    let multiplier = 1;
    let numericPortion = cleaned;
    if (cleaned.endsWith('k')) {
      multiplier = 1000;
      numericPortion = numericPortion.slice(0, -1);
    }

    const numeric = Number(numericPortion);
    if (Number.isFinite(numeric) && numeric > 0) {
      return numeric * multiplier;
    }
    return undefined;
  };

  const finishLevelForApi = (level: typeof finishLevel) =>
    (level === 'premium' ? 'Premium' : 'Standard');

  const formatPreviewCurrency = (value?: number) => {
    if (typeof value === 'number' && Number.isFinite(value)) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(value);
    }
    return '—';
  };

  const formatPreviewPercent = (value?: number) => {
    if (typeof value === 'number' && Number.isFinite(value)) {
      return `${value.toFixed(2)}%`;
    }
    return '—';
  };

  const formatPreviewYears = (value?: number) => {
    if (typeof value === 'number' && Number.isFinite(value)) {
      return `${value.toFixed(2)} yrs`;
    }
    return '—';
  };

  const isFiniteNumber = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value);

  const extractNumber = (value: unknown): number | undefined => (isFiniteNumber(value) ? value : undefined);

  const formatCurrencySafe = (value?: number) => (isFiniteNumber(value) ? formatCurrency(value) : '—');

  const formatCurrencyPerSF = (value?: number) => (isFiniteNumber(value) ? `${formatCurrency(value)}/SF` : '—');

  const formatMultiplierSegment = (label: string, value?: number) => {
    if (!isFiniteNumber(value)) {
      return null;
    }
    const formatted = value.toFixed(3).replace(/(?:\.0+|(\.\d+?)0+)$/, '$1');
    return `${label} ×${formatted}`;
  };

  const parsedInput = result?.parsed_input;

  useEffect(() => {
    if (!liveDetectedLocation) return;
    if (locationTouched) return;

    const normalizedLocation = locationInput.trim();
    const shouldAutofill = normalizedLocation.length === 0 || locationAutoFilled;

    if (!shouldAutofill) return;
    if (normalizedLocation === liveDetectedLocation) return;
    if (!CITY_STATE_REGEX.test(liveDetectedLocation)) return;

    if (process.env.NODE_ENV === 'development') {
      console.debug('[NewProject] autofilling location from description', {
        liveDetectedLocation,
        autofillValue: liveDetectedLocation,
        normalizedLocation,
        locationAutoFilled
      });
    }

    setLocationInput(liveDetectedLocation);
    setLocationAutoFilled(true);
  }, [liveDetectedLocation, locationTouched, locationInput, locationAutoFilled]);
  const currentSubtype = parsedInput?.subtype || parsedInput?.building_subtype;
  const availableSpecialFeatures = parsedInput ? getAvailableFeatures(parsedInput.building_type) : [];
  const applicableSpecialFeatures = filterSpecialFeaturesBySubtype(availableSpecialFeatures, currentSubtype);

  // Live preview effect
  useEffect(() => {
    if (previewTimeoutRef.current) {
      window.clearTimeout(previewTimeoutRef.current);
      previewTimeoutRef.current = null;
    }
    if (previewAbortRef.current) {
      previewAbortRef.current.abort();
      previewAbortRef.current = null;
    }

    if (!normalizedDescription || !isLocationFormatValid) {
      setPreviewStatus('idle');
      setPreviewData(null);
      setPreviewError(null);
      return;
    }

    setPreviewStatus('loading');
    setPreviewError(null);

    const timeoutId = window.setTimeout(async () => {
      const controller = new AbortController();
      previewAbortRef.current = controller;

      try {
        const squareValue = parseSquareFootageValue(squareFootageInput);
        const locationValue = normalizedLocationInput || undefined;
        const analysis = await api.analyzeProject(description, {
          square_footage: squareValue,
          location: locationValue,
          finishLevel: finishLevelForApi(finishLevel),
          projectClass: projectComplexity,
          special_features: specialFeatures,
          signal: controller.signal,
        });

        const totals = (analysis as any)?.totals ?? (analysis as any)?.calculations?.totals;
        const revenueAnalysis =
          (analysis as any)?.revenue_analysis ?? (analysis as any)?.calculations?.revenue_analysis;
        const returnMetrics =
          (analysis as any)?.return_metrics ?? (analysis as any)?.calculations?.return_metrics;

        setPreviewData({
          totalCost: totals?.total_project_cost,
          annualRevenue: revenueAnalysis?.annual_revenue,
          noi: revenueAnalysis?.net_income,
          roi: returnMetrics?.cash_on_cash_return,
          payback: returnMetrics?.payback_period,
        });
        setPreviewStatus('success');
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }
        console.error('Preview error:', err);
        setPreviewData(null);
        setPreviewStatus('error');
        setPreviewError(err instanceof Error ? err.message : 'Preview unavailable');
      } finally {
        previewAbortRef.current = null;
      }
    }, 400);

    previewTimeoutRef.current = timeoutId;

    return () => {
      window.clearTimeout(timeoutId);
      if (previewAbortRef.current) {
        previewAbortRef.current.abort();
        previewAbortRef.current = null;
      }
    };
  }, [normalizedDescription, squareFootageInput, normalizedLocationInput, isLocationFormatValid, finishLevel, finishLevelLocked, projectComplexity, specialFeatures]);
  
  // Calculate total cost including features
  const handleExampleClick = (example: any) => {
    setDescription(example.text);
    setSquareFootageInput(example.squareFootage ? formatNumber(example.squareFootage) : '');
    setLocationInput(example.location || '');
    setLocationTouched(false);
    setLocationAutoFilled(Boolean(example.location));
    setLocationSubmitAttempted(false);
    // Reset configuration when using example
    setSpecialFeatures([]);
    setFinishLevel('standard');
    setFinishLevelLocked(false);
    setProjectComplexity('ground_up');
    setProjectClassLocked(false);
    // Auto-scroll to show the form is filled
    window.scrollTo({ top: 200, behavior: 'smooth' });
  };
  
  const handleAnalyze = async () => {
    if (!normalizedDescription) return;
    setLocationSubmitAttempted(true);
    if (!isLocationFormatValid) return;
    
    setActiveStep('analyzing');
    tracer.trace('ANALYZE_START', 'Starting analysis', { description });
    
    const squareValue = parseSquareFootageValue(squareFootageInput);
    const analysis = await analyzeDescription(description, {
      squareFootage: squareValue,
      location: normalizedLocationInput,
      finishLevel,
      projectClass: projectComplexity,
      specialFeatures,
    });
    
    if (analysis) {
      // Auto-detect features from description
      const parsed = parseDescription(description);
      const parsedBuildingType = analysis.parsed_input?.building_type;
      const parsedSubtype = analysis.parsed_input?.subtype || analysis.parsed_input?.building_subtype;
      const allowedFeatureIds = new Set(
        filterSpecialFeaturesBySubtype(
          getAvailableFeatures(parsedBuildingType || ''),
          parsedSubtype
        ).map((feature) => feature.id)
      );
      const parsedSpecialFeatures = parsed.specialFeatures.filter((featureId) =>
        allowedFeatureIds.has(featureId)
      );
      if (specialFeatures.length === 0 && parsedSpecialFeatures.length > 0) {
        setSpecialFeatures(parsedSpecialFeatures);
      }
      if (!finishLevelLocked) {
        const engineFinish = analysis.calculations?.project_info?.finish_level;
        const normalizedEngineFinish =
          typeof engineFinish === 'string' ? engineFinish.toLowerCase() : undefined;
        const sanitizedEngineFinish: 'standard' | 'premium' | undefined =
          normalizedEngineFinish === 'standard'
            ? 'standard'
            : normalizedEngineFinish === 'premium' || normalizedEngineFinish === 'luxury'
              ? 'premium'
              : undefined;
        if (sanitizedEngineFinish) {
          setFinishLevel(sanitizedEngineFinish);
        } else if (parsed.finishLevel) {
          setFinishLevel(parsed.finishLevel);
        }
      }
      if (!projectClassLocked && parsed.projectComplexity) {
        setProjectComplexity(parsed.projectComplexity);
      }
      if (analysis.parsed_input?.square_footage) {
        setSquareFootageInput(formatNumber(analysis.parsed_input.square_footage));
      }
      
      setActiveStep('results');
      tracer.trace('ANALYZE_SUCCESS', 'Analysis complete', analysis);
      
      // Smooth scroll to results after a brief delay
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 100);
    } else {
      setActiveStep('input');
      tracer.trace('ANALYZE_ERROR', 'Analysis failed', { error });
    }
  };
  
  const normalizeFinishLevel = (
    level?: string
  ): 'Standard' | 'Premium' | undefined => {
    if (!level) return undefined;
    const lower = level.toLowerCase();
    if (lower === 'standard') return 'Standard';
    if (lower === 'premium' || lower === 'luxury') return 'Premium';
    return undefined;
  };

  const handleSaveProject = async () => {
    if (!result) return;
    
    setSaving(true);
    tracer.trace('SAVE_START', 'Saving project', result);
    
    try {
      // ---- Project Class: UI selection must win on SAVE ----
      const uiSelectedClass = projectComplexity;
      const nlpDetectedClass =
        result.parsed_input?.project_classification ??
        result.parsed_input?.project_class ??
        (result as any)?.project_classification ??
        (result as any)?.projectClassification ??
        'ground_up';
      const finalProjectClass = (uiSelectedClass || nlpDetectedClass || 'ground_up') as 'ground_up' | 'renovation' | 'addition';

      const squareValueFromInput = parseSquareFootageValue(squareFootageInput);
      const parsedSquareFootage = Number(result.parsed_input?.square_footage) || 0;
      const derivedSquareFootage = parsedSquareFootage > 0 ? parsedSquareFootage : squareValueFromInput;
      const derivedLocation = result.parsed_input?.location || locationInput.trim() || undefined;
      const engineFinish = typeof result.calculations?.project_info?.finish_level === 'string'
        ? result.calculations?.project_info?.finish_level
        : undefined;
      const uiFinish = normalizeFinishLevel(finishLevel);
      const derivedFinishLevel = uiFinish || normalizeFinishLevel(engineFinish) || 'Standard';
      const derivedDescription = description.trim() || result.calculations?.project_info?.display_name || 'SpecSharp Project';
      const engineFeatures = (result.calculations?.project_info as any)?.special_features;
      const derivedSpecialFeatures = specialFeatures.length
        ? specialFeatures
        : Array.isArray(engineFeatures)
          ? engineFeatures
          : [];

      console.log('[SAVE] finalProjectClass =', finalProjectClass);

      const { id } = await createProject({
        description: derivedDescription,
        location: derivedLocation,
        squareFootage: derivedSquareFootage,
        finishLevel: derivedFinishLevel,
        projectClass: finalProjectClass,
        specialFeatures: derivedSpecialFeatures,
      });

      console.debug('[TRACE save:legacy->server]', { source: 'NewProject.tsx:514', id });
      tracer.trace('SAVE_SUCCESS', 'Project saved', { id });
      navigate(`/project/${id}`);
    } catch (err) {
      console.error('Failed to save project:', err);
      tracer.trace('SAVE_ERROR', 'Save failed', err);
    } finally {
      setSaving(false);
    }
  };
  
  const handleReset = () => {
    reset();
    setDescription('');
    setSquareFootageInput('');
    setLocationInput('');
    setLocationTouched(false);
    setLocationAutoFilled(false);
    setActiveStep('input');
    setSpecialFeatures([]);
    setFinishLevel('standard');
    setFinishLevelLocked(false);
    setProjectComplexity('ground_up');
    setProjectClassLocked(false);
    setPreviewData(null);
    setPreviewStatus('idle');
    setPreviewError(null);
    if (previewTimeoutRef.current) {
      window.clearTimeout(previewTimeoutRef.current);
      previewTimeoutRef.current = null;
    }
    if (previewAbortRef.current) {
      previewAbortRef.current.abort();
      previewAbortRef.current = null;
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const summaryCalculations = result?.calculations;
  const summaryConstruction = summaryCalculations?.construction_costs;
  const summaryTotals = summaryCalculations?.totals;
  const parsedSummarySF = extractNumber(result?.parsed_input?.square_footage ?? summaryConstruction?.square_footage);
  const squareFootageSummary = parsedSummarySF && parsedSummarySF > 0
    ? parsedSummarySF
    : parseSquareFootageValue(squareFootageInput);
  const regionalMultiplierValue = extractNumber(summaryConstruction?.regional_multiplier);
  const complexityMultiplierValue = extractNumber(summaryConstruction?.class_multiplier);
  const finishMultiplierValue = extractNumber(summaryConstruction?.finish_cost_factor);
  const multiplierSegments = [
    formatMultiplierSegment('Regional', regionalMultiplierValue),
    formatMultiplierSegment('Complexity', complexityMultiplierValue),
    formatMultiplierSegment('Finish', finishMultiplierValue),
  ].filter(Boolean) as string[];
  const multipliersText = multiplierSegments.length ? multiplierSegments.join(' · ') : '—';
  const multiplierValues = [regionalMultiplierValue, complexityMultiplierValue, finishMultiplierValue];
  const derivedMultiplier = multiplierValues.every((val) => isFiniteNumber(val) && val !== 0)
    ? (multiplierValues as number[]).reduce((acc, val) => acc * val, 1)
    : undefined;
  const baseCostPerSFRaw = extractNumber(summaryConstruction?.base_cost_per_sf);
  const finalCostPerSFValue = extractNumber(summaryConstruction?.final_cost_per_sf);
  const baseCostPerSFValue = baseCostPerSFRaw ?? ((derivedMultiplier && derivedMultiplier !== 0 && finalCostPerSFValue !== undefined)
    ? finalCostPerSFValue / derivedMultiplier
    : undefined);
  const totalProjectCostValue = extractNumber(summaryTotals?.total_project_cost);
  const costPerSFValue = totalProjectCostValue !== undefined && squareFootageSummary && squareFootageSummary > 0
    ? totalProjectCostValue / squareFootageSummary
    : finalCostPerSFValue;
  
  // Get display-friendly names for building types
  const getDisplayName = (type: string, subtype: string) => {
    const typeDisplay = BuildingTaxonomy.getDisplayName(type);
    
    // Format subtype for display
    const subtypeDisplay = subtype
      ?.replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
    
    return `${typeDisplay} - ${subtypeDisplay}`;
  };

  type FeatureDisplayPricing = {
    amountLabel: string;
    detailLabel?: string;
    totalCost?: number;
    isEstimate: boolean;
    isPlaceholder: boolean;
  };

  const usesSubtypeCostPerSF = ['multifamily', 'restaurant'].includes(
    parsedInput?.building_type ?? ''
  );
  const isRestaurantProject = parsedInput?.building_type === 'restaurant';
  const hasFeatureSquareFootage = typeof squareFootageSummary === 'number' && squareFootageSummary > 0;

  const resolveFeatureCostPerSF = (feature: SpecialFeatureOption): number | undefined => {
    const subtypeCost = currentSubtype && feature.costPerSFBySubtype
      ? feature.costPerSFBySubtype[currentSubtype]
      : undefined;
    if (typeof subtypeCost === 'number' && Number.isFinite(subtypeCost)) {
      return subtypeCost;
    }
    if (typeof feature.costPerSF === 'number' && Number.isFinite(feature.costPerSF)) {
      return feature.costPerSF;
    }
    if (feature.costPerSFBySubtype) {
      const fallback = Object.values(feature.costPerSFBySubtype).find(
        (value) => typeof value === 'number' && Number.isFinite(value)
      );
      if (typeof fallback === 'number') {
        return fallback;
      }
    }
    return undefined;
  };

  const getFeatureDisplayPricing = (feature: SpecialFeatureOption): FeatureDisplayPricing => {
    const costPerSF = resolveFeatureCostPerSF(feature);
    if (usesSubtypeCostPerSF && typeof costPerSF === 'number') {
      if (hasFeatureSquareFootage && squareFootageSummary) {
        const totalCost = costPerSF * squareFootageSummary;
        return {
          amountLabel: `+${formatCurrency(totalCost)}`,
          detailLabel: `${formatCurrency(costPerSF)}/SF × ${formatNumber(squareFootageSummary)} SF`,
          totalCost,
          isEstimate: false,
          isPlaceholder: false,
        };
      }
      return {
        amountLabel: `+${formatCurrency(costPerSF)}/SF`,
        detailLabel: 'Estimate until project SF is provided',
        isEstimate: true,
        isPlaceholder: false,
      };
    }

    if (typeof feature.cost === 'number' && Number.isFinite(feature.cost)) {
      return {
        amountLabel: `+${formatCurrency(feature.cost)}`,
        detailLabel: usesSubtypeCostPerSF ? 'Estimate placeholder' : 'Static placeholder value',
        totalCost: feature.cost,
        isEstimate: true,
        isPlaceholder: true,
      };
    }

    return {
      amountLabel: '+—',
      detailLabel: 'Pricing unavailable',
      isEstimate: true,
      isPlaceholder: true,
    };
  };

  const selectedFeatureDetails = applicableSpecialFeatures
    .filter((feature) => specialFeatures.includes(feature.id))
    .map((feature) => ({ feature, pricing: getFeatureDisplayPricing(feature) }));
  const selectedFeatureKnownTotal = selectedFeatureDetails.reduce(
    (sum, item) => sum + (item.pricing.totalCost ?? 0),
    0
  );
  const selectedFeatureHasUnknownTotal = selectedFeatureDetails.some(
    (item) => item.pricing.totalCost === undefined
  );
  const selectedFeatureHasEstimate = selectedFeatureDetails.some(
    (item) => item.pricing.isEstimate
  );
  const hasStaticFeaturePlaceholders = applicableSpecialFeatures.some(
    (feature) => getFeatureDisplayPricing(feature).isPlaceholder
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button 
                onClick={() => navigate('/dashboard')}
                className="text-gray-500 hover:text-gray-700 transition"
              >
                ← Back
              </button>
              <div className="h-6 w-px bg-gray-300" />
              <h1 className="text-xl font-bold text-gray-900">Create New Project Estimate</h1>
            </div>
            
            {/* Progress indicator */}
            <div className="flex items-center gap-2">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full transition ${
                activeStep === 'input' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'
              }`}>
                <FileText className="h-4 w-4" />
                <span className="text-sm font-medium">1. Describe</span>
              </div>
              <ChevronDown className="h-4 w-4 text-gray-400 rotate-[-90deg]" />
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full transition ${
                activeStep === 'analyzing' ? 'bg-blue-100 text-blue-700 animate-pulse' : 
                activeStep === 'results' ? 'bg-green-100 text-green-700' : 
                'bg-gray-100 text-gray-500'
              }`}>
                <Calculator className="h-4 w-4" />
                <span className="text-sm font-medium">2. Analyze</span>
              </div>
              <ChevronDown className="h-4 w-4 text-gray-400 rotate-[-90deg]" />
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full transition ${
                result ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
              }`}>
                <Save className="h-4 w-4" />
                <span className="text-sm font-medium">3. Save</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Input Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Sparkles className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Describe Your Project</h2>
              <p className="text-sm text-gray-500">Use natural language to describe what you want to build</p>
            </div>
          </div>
          
          {/* Input guidance */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-sm font-medium text-blue-900 mb-2">Include these key details for accurate analysis:</p>
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 border border-blue-300 rounded-full text-xs font-medium text-blue-700">
                📏 Size (SF or units)
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 border border-blue-300 rounded-full text-xs font-medium text-blue-700">
                🏢 Building type
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 border border-blue-300 rounded-full text-xs font-medium text-blue-700">
                📍 City, State
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 border border-gray-300 rounded-full text-xs font-medium text-gray-700">
                ✨ Finish level
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 border border-gray-300 rounded-full text-xs font-medium text-gray-700">
                🚗 Parking needs
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 border border-gray-300 rounded-full text-xs font-medium text-gray-700">
                ⚡ Special features
              </span>
            </div>
            <p className="text-xs text-blue-800">
              <strong>Good example:</strong> "200-unit luxury apartment complex with parking garage and amenity deck in Nashville, TN"
            </p>
          </div>
          
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Start with: [Size] [Type] in [Location]..."
            className="w-full h-32 px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition"
            disabled={analyzing}
          />
          
          {/* Detection status */}
          {description.length > 0 && (
            <div className="flex items-center gap-4 mt-2">
              <span className={`inline-flex items-center gap-1 text-xs ${detectedFeatures.size ? 'text-green-600' : 'text-gray-400'}`}>
                {detectedFeatures.size ? '✓' : '○'} Size detected
              </span>
              <span className={`inline-flex items-center gap-1 text-xs ${detectedFeatures.type ? 'text-green-600' : 'text-gray-400'}`}>
                {detectedFeatures.type ? '✓' : '○'} Building type detected
              </span>
              <span className={`inline-flex items-center gap-1 text-xs ${detectedFeatures.location ? 'text-green-600' : 'text-gray-400'}`}>
                {detectedFeatures.location ? '✓' : '○'} Location detected
              </span>
            </div>
          )}

          {/* Key details inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                Square Footage (optional)
              </label>
              <input
                value={squareFootageInput}
                onChange={(e) => setSquareFootageInput(e.target.value)}
                placeholder="e.g. 50,000"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
                inputMode="numeric"
                autoComplete="off"
                disabled={analyzing}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                Location (City, State)
              </label>
              <input
                value={locationInput}
                onChange={(e) => {
                  setLocationTouched(true);
                  setLocationAutoFilled(false);
                  setLocationInput(e.target.value);
                }}
                placeholder="City, ST (e.g., Dallas, TX)"
                className={`w-full px-3 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm ${
                  shouldShowLocationError ? 'border-red-400' : 'border-gray-200'
                }`}
                aria-invalid={shouldShowLocationError}
                autoComplete="off"
                disabled={analyzing}
              />
              {shouldShowLocationError && (
                <p className="mt-1 text-xs text-red-600">Enter location like Dallas, TX.</p>
              )}
            </div>
          </div>

          {/* Live preview */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-semibold text-gray-700">Live Preview</p>
              <span className="text-xs text-gray-400">Live based on inputs</span>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              {previewStatus === 'idle' && (
                <p className="text-xs text-gray-500">
                  Start adding project details to see real-time cost and ROI insights.
                </p>
              )}
              {previewStatus === 'loading' && (
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded animate-pulse" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse" />
                  <div className="h-3 bg-gray-200 rounded animate-pulse" />
                  <p className="text-xs text-gray-500">Calculating…</p>
                </div>
              )}
              {previewStatus === 'success' && previewData && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Total Cost</p>
                    <p className="text-sm font-semibold text-gray-900">{formatPreviewCurrency(previewData.totalCost)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Annual Revenue</p>
                    <p className="text-sm font-semibold text-gray-900">{formatPreviewCurrency(previewData.annualRevenue)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">NOI</p>
                    <p className="text-sm font-semibold text-gray-900">{formatPreviewCurrency(previewData.noi)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Cash-on-Cash ROI</p>
                    <p className="text-sm font-semibold text-gray-900">{formatPreviewPercent(previewData.roi)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Payback Period</p>
                    <p className="text-sm font-semibold text-gray-900">{formatPreviewYears(previewData.payback)}</p>
                  </div>
                </div>
              )}
              {previewStatus === 'error' && (
                <p className="text-xs text-gray-500">Preview unavailable at the moment.</p>
              )}
            </div>
            {previewStatus === 'error' && (
              <p className="mt-2 text-xs text-amber-600">
                Preview unavailable. Continue filling the form or try again.
              </p>
            )}
            {previewStatus === 'error' && previewError && (
              <p className="mt-1 text-[11px] text-gray-400">{previewError}</p>
            )}
          </div>
          
          {/* Example prompts */}
          <div className="mt-6">
            <p className="text-sm text-gray-500 mb-3">Try an example:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {examplePrompts.map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => handleExampleClick(example)}
                  disabled={analyzing}
                  className={`flex items-start gap-3 p-3 rounded-lg transition text-left group hover:shadow-md border border-gray-200 ${
                    analyzing ? 'opacity-50 cursor-not-allowed' : 'hover:scale-[1.02] hover:border-blue-300'
                  }`}
                >
                  <div className={`p-2 rounded-lg flex-shrink-0 ${example.color}`}>
                    {example.icon}
                  </div>
                  <div className="text-sm text-gray-600 group-hover:text-gray-900 line-clamp-2">
                    {example.text.split(' ').map((word, i) => {
                      const isHighlighted = example.highlights?.some(h => 
                        h.toLowerCase().includes(word.toLowerCase()) || 
                        word.toLowerCase().includes(h.toLowerCase().replace(/[^a-z0-9]/g, ''))
                      );
                      return (
                        <span key={i}>
                          {isHighlighted ? (
                            <strong className="font-semibold text-gray-900">{word}</strong>
                          ) : (
                            word
                          )}
                          {i < example.text.split(' ').length - 1 && ' '}
                        </span>
                      );
                    })}
                  </div>
                </button>
              ))}
            </div>
          </div>
          
          {/* Error display */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-900">Analysis Error</p>
                <p className="text-sm text-red-700">{error.message || 'Failed to analyze project'}</p>
              </div>
            </div>
          )}
          
          {/* Analyze button */}
          <div className="mt-8 flex justify-center">
            <button
              onClick={handleAnalyze}
              disabled={!canAnalyze}
              className={`
                px-8 py-3 rounded-lg font-medium flex items-center gap-3 transition transform
                ${!canAnalyze 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                  : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl hover:scale-105'
                }
              `}
            >
              {analyzing ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Analyzing Project...
                </>
              ) : (
                <>
                  <Calculator className="h-5 w-5" />
                  Analyze Project
                </>
              )}
            </button>
          </div>
        </div>

        {/* Analyzing State */}
        {analyzing && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
            <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyzing Your Project</h3>
            <p className="text-gray-500">Parsing requirements and calculating costs...</p>
            <div className="mt-4 flex justify-center gap-2">
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce" />
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && !analyzing && (
          <div ref={resultsRef} className="space-y-6">
            {/* Success Banner */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3 animate-in fade-in slide-in-from-bottom duration-500">
              <div className="p-2 bg-green-100 rounded-lg">
                <Check className="h-5 w-5 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-green-900">Analysis Complete!</h3>
                <p className="text-sm text-green-700">Review your project details below and save when ready</p>
              </div>
            </div>

            {/* Project Summary */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 animate-in fade-in slide-in-from-bottom duration-500 delay-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Project Analysis Results</h3>
              
              {/* Project Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="flex items-start gap-3">
                  <Building2 className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Building Type</p>
                    <p className="font-semibold text-gray-900">
                      {result.parsed_input && getDisplayName(
                        result.parsed_input.building_type,
                        result.parsed_input.subtype || result.parsed_input.building_subtype
                      )}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <Square className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Square Footage</p>
                    <p className="font-semibold text-gray-900">
                      {formatNumber(result.parsed_input?.square_footage || 0)} SF
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Location</p>
                    <p className="font-semibold text-gray-900">
                      {result.parsed_input?.location || 'Nashville'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <Layers className="h-5 w-5 text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Floors</p>
                    <p className="font-semibold text-gray-900">
                      {result.parsed_input?.floors || 1}
                    </p>
                  </div>
                </div>
              </div>

            </div>

            {/* Project Configuration Section */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 animate-in fade-in slide-in-from-bottom duration-500 delay-200">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Project Configuration</h3>
                <div className="text-sm text-gray-500 flex items-center gap-1">
                  <Info className="h-4 w-4" />
                  Detected from your description - adjust as needed
                </div>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Column - Project Options */}
                <div className="space-y-6">
                  {/* Project Complexity */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-3">Project Type</p>
                    <div className="grid grid-cols-3 gap-2">
                      {(['ground_up', 'renovation', 'addition'] as const).map(type => (
                        <button
                          key={type}
                          onClick={() => {
                            setProjectComplexity(type);
                            setProjectClassLocked(true);
                          }}
                          className={`px-3 py-3 rounded-lg text-sm font-medium transition ${
                            projectComplexity === type
                              ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-500'
                              : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                          }`}
                        >
                          <div className="text-center">
                            <div className="font-semibold">
                              {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </div>
                            <div className="text-xs mt-1 opacity-75">
                              {type === 'ground_up' && '1.0x'}
                              {type === 'addition' && '1.12x'}
                              {type === 'renovation' && '0.92x'}
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Finish Level */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-3">Finish Level</p>
                    <div className="grid grid-cols-2 gap-2">
                      {FINISH_LEVELS.map(({ label, value, multiplierLabel }) => (
                        <button
                          key={value}
                          onClick={() => {
                            setFinishLevel(value);
                            setFinishLevelLocked(true);
                          }}
                          className={`px-3 py-3 rounded-lg text-sm font-medium transition ${
                            finishLevel === value
                              ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-500'
                              : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                          }`}
                        >
                          <div className="text-center">
                            <div className="font-semibold">{label}</div>
                            <div className="text-xs mt-1 opacity-75">{multiplierLabel}</div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Right Column - Special Features */}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-3">Special Features</p>
                  <div className="mb-3 rounded-lg border border-blue-100 bg-blue-50 px-3 py-2">
                    <p className="text-[11px] text-blue-700">
                      Feature costs are applied as $/SF × project SF in final estimate.
                    </p>
                    {usesSubtypeCostPerSF && !hasFeatureSquareFootage && (
                      <p className="mt-1 text-[11px] text-blue-700">
                        {isRestaurantProject
                          ? 'Restaurant values below are estimates until square footage is provided.'
                          : 'Multifamily values below are estimates until square footage is provided.'}
                      </p>
                    )}
                    {hasStaticFeaturePlaceholders && (
                      <p className="mt-1 text-[11px] text-blue-700">
                        Some card values are static placeholders and may differ from backend-applied totals.
                      </p>
                    )}
                  </div>
                  <div className="space-y-2 max-h-80 overflow-y-auto border border-gray-100 rounded-lg p-3">
                    {parsedInput && applicableSpecialFeatures.length > 0 ? (
                      applicableSpecialFeatures.map(feature => {
                        const pricing = getFeatureDisplayPricing(feature);
                        return (
                          <label
                            key={feature.id}
                            className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer border border-transparent hover:border-gray-200 transition"
                          >
                            <input
                              type="checkbox"
                              checked={specialFeatures.includes(feature.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSpecialFeatures([...specialFeatures, feature.id]);
                                } else {
                                  setSpecialFeatures(specialFeatures.filter(f => f !== feature.id));
                                }
                              }}
                              className="mt-1 h-4 w-4 text-blue-600 rounded"
                            />
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-gray-900">{feature.name}</span>
                                <span className="text-xs text-green-600 font-semibold">
                                  {pricing.amountLabel}
                                </span>
                              </div>
                              <span className="text-xs text-gray-500">{feature.description}</span>
                              {pricing.detailLabel && (
                                <p className="mt-1 text-[11px] text-gray-500">{pricing.detailLabel}</p>
                              )}
                            </div>
                          </label>
                        );
                      })
                    ) : (
                      <div className="text-center py-8 text-gray-400">
                        <Settings className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No special features available for this building type</p>
                      </div>
                    )}
                  </div>
                  <div className="mt-3 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
                    <p className="text-[11px] uppercase tracking-wide text-gray-500">Selected Feature Impact</p>
                    {selectedFeatureDetails.length === 0 ? (
                      <p className="text-sm text-gray-700">No special features selected.</p>
                    ) : selectedFeatureHasUnknownTotal ? (
                      <p className="text-sm text-gray-700">
                        {selectedFeatureDetails.length} selected. Impact shown as estimate.
                      </p>
                    ) : (
                      <p className="text-sm font-semibold text-gray-900">
                        +{formatCurrency(selectedFeatureKnownTotal)}
                        {selectedFeatureHasEstimate && <span className="ml-1 text-gray-600">(estimate)</span>}
                      </p>
                    )}
                    {!selectedFeatureHasUnknownTotal && hasFeatureSquareFootage && selectedFeatureKnownTotal > 0 && (
                      <p className="text-[11px] text-gray-500">
                        {formatCurrency(selectedFeatureKnownTotal / squareFootageSummary!)} / SF combined impact
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Updated Cost Display */}
              {result.calculations && (
                <div className="mt-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white">
                  <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    Project Cost Summary
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-blue-100 text-sm mb-1">Base Cost (per SF)</p>
                      <p className="text-xl font-bold">{formatCurrencyPerSF(baseCostPerSFValue)}</p>
                    </div>
                    <div>
                      <p className="text-blue-100 text-sm mb-1">Cost Multipliers</p>
                      <p className="text-sm font-semibold md:text-lg">
                        {multipliersText}
                      </p>
                    </div>
                    <div>
                      <p className="text-blue-100 text-sm mb-1">Total Project Cost</p>
                      <p className="text-2xl font-bold">{formatCurrencySafe(totalProjectCostValue)}</p>
                    </div>
                    <div>
                      <p className="text-blue-100 text-sm mb-1">All-in Cost per SF</p>
                      <p className="text-2xl font-bold">{formatCurrencyPerSF(costPerSFValue)}</p>
                      {squareFootageSummary && (
                        <p className="text-blue-200 text-xs mt-1">{formatNumber(squareFootageSummary)} SF</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4 mt-8">
                <button
                  onClick={handleSaveProject}
                  disabled={saving}
                  className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-5 w-5" />
                      Save Project & View Details
                    </>
                  )}
                </button>
                <button
                  onClick={handleReset}
                  disabled={saving}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium flex items-center justify-center gap-2 transition"
                >
                  <RefreshCw className="h-5 w-5" />
                  Start Over
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NewProject;
