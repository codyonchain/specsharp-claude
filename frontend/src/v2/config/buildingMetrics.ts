/**
 * Building metrics configuration matching backend master_config.py
 * This provides display metrics for each building type/subtype
 */

export interface BuildingMetrics {
  unitLabel: string;
  unitType: string;
  sfPerUnit: number;
  revenuePerUnit?: number;
  departments: Array<{
    name: string;
    percentage: number;
    icon: string;
    color: string;
  }>;
}

export const BUILDING_METRICS: Record<string, Record<string, BuildingMetrics>> = {
  healthcare: {
    hospital: {
      unitLabel: 'Beds Capacity',
      unitType: 'beds',
      sfPerUnit: 1333,
      revenuePerUnit: 553000,
      departments: [
        { name: 'Clinical Department', percentage: 0.60, icon: 'Heart', color: 'blue' },
        { name: 'Support Department', percentage: 0.30, icon: 'Headphones', color: 'green' },
        { name: 'Infrastructure', percentage: 0.10, icon: 'Cpu', color: 'purple' }
      ]
    },
    surgical_center: {
      unitLabel: 'Operating Rooms',
      unitType: 'ORs',
      sfPerUnit: 2500,
      revenuePerUnit: 1200000,
      departments: [
        { name: 'Surgical Suite', percentage: 0.50, icon: 'Heart', color: 'red' },
        { name: 'Pre/Post Op', percentage: 0.30, icon: 'Clock', color: 'blue' },
        { name: 'Support Services', percentage: 0.20, icon: 'Users', color: 'green' }
      ]
    },
    medical_office: {
      unitLabel: 'Exam Rooms',
      unitType: 'rooms',
      sfPerUnit: 150,
      revenuePerUnit: 85000,
      departments: [
        { name: 'Clinical Space', percentage: 0.65, icon: 'Stethoscope', color: 'blue' },
        { name: 'Office/Admin', percentage: 0.25, icon: 'Briefcase', color: 'gray' },
        { name: 'Support', percentage: 0.10, icon: 'Settings', color: 'purple' }
      ]
    }
  },
  
  multifamily: {
    luxury_apartments: {
      unitLabel: 'Apartment Units',
      unitType: 'units',
      sfPerUnit: 950,
      revenuePerUnit: 30000, // Annual rent
      departments: [
        { name: 'Residential Units', percentage: 0.70, icon: 'Home', color: 'blue' },
        { name: 'Common Areas', percentage: 0.20, icon: 'Users', color: 'green' },
        { name: 'Amenities', percentage: 0.10, icon: 'Building2', color: 'purple' }
      ]
    },
    market_rate_apartments: {
      unitLabel: 'Apartment Units',
      unitType: 'units',
      sfPerUnit: 850,
      revenuePerUnit: 18000,
      departments: [
        { name: 'Residential Units', percentage: 0.75, icon: 'Home', color: 'blue' },
        { name: 'Common Areas', percentage: 0.20, icon: 'Users', color: 'green' },
        { name: 'Parking/Storage', percentage: 0.05, icon: 'Car', color: 'gray' }
      ]
    },
    affordable_housing: {
      unitLabel: 'Housing Units',
      unitType: 'units',
      sfPerUnit: 750,
      revenuePerUnit: 12000,
      departments: [
        { name: 'Residential Units', percentage: 0.80, icon: 'Home', color: 'blue' },
        { name: 'Common Areas', percentage: 0.15, icon: 'Users', color: 'green' },
        { name: 'Services', percentage: 0.05, icon: 'Heart', color: 'red' }
      ]
    }
  },
  
  office: {
    corporate_hq: {
      unitLabel: 'Floors',
      unitType: 'floors',
      sfPerUnit: 25000,
      revenuePerUnit: 625000,
      departments: [
        { name: 'Office Space', percentage: 0.65, icon: 'Building', color: 'blue' },
        { name: 'Meeting/Collab', percentage: 0.20, icon: 'Users', color: 'green' },
        { name: 'Amenities', percentage: 0.15, icon: 'Coffee', color: 'brown' }
      ]
    },
    professional_office: {
      unitLabel: 'Suites',
      unitType: 'suites',
      sfPerUnit: 2500,
      revenuePerUnit: 50000,
      departments: [
        { name: 'Office Space', percentage: 0.70, icon: 'Briefcase', color: 'blue' },
        { name: 'Conference', percentage: 0.20, icon: 'Users', color: 'green' },
        { name: 'Support', percentage: 0.10, icon: 'Settings', color: 'gray' }
      ]
    }
  },
  
  retail: {
    shopping_center: {
      unitLabel: 'Stores',
      unitType: 'stores',
      sfPerUnit: 5000,
      revenuePerUnit: 150000,
      departments: [
        { name: 'Retail Space', percentage: 0.75, icon: 'ShoppingBag', color: 'blue' },
        { name: 'Common Areas', percentage: 0.15, icon: 'Users', color: 'green' },
        { name: 'Service/Loading', percentage: 0.10, icon: 'Truck', color: 'gray' }
      ]
    },
    big_box: {
      unitLabel: 'Anchor Stores',
      unitType: 'anchors',
      sfPerUnit: 50000,
      revenuePerUnit: 1000000,
      departments: [
        { name: 'Sales Floor', percentage: 0.70, icon: 'ShoppingCart', color: 'blue' },
        { name: 'Storage', percentage: 0.20, icon: 'Package', color: 'brown' },
        { name: 'Operations', percentage: 0.10, icon: 'Settings', color: 'gray' }
      ]
    }
  },
  
  industrial: {
    warehouse: {
      unitLabel: 'Loading Bays',
      unitType: 'bays',
      sfPerUnit: 10000,
      revenuePerUnit: 60000,
      departments: [
        { name: 'Storage Space', percentage: 0.80, icon: 'Package', color: 'brown' },
        { name: 'Loading/Staging', percentage: 0.15, icon: 'Truck', color: 'blue' },
        { name: 'Office', percentage: 0.05, icon: 'Briefcase', color: 'gray' }
      ]
    },
    manufacturing: {
      unitLabel: 'Production Lines',
      unitType: 'lines',
      sfPerUnit: 25000,
      revenuePerUnit: 500000,
      departments: [
        { name: 'Production Floor', percentage: 0.65, icon: 'Factory', color: 'blue' },
        { name: 'Warehouse', percentage: 0.20, icon: 'Package', color: 'brown' },
        { name: 'Office/QC', percentage: 0.15, icon: 'ClipboardCheck', color: 'green' }
      ]
    }
  },
  
  hospitality: {
    hotel: {
      unitLabel: 'Guest Rooms',
      unitType: 'rooms',
      sfPerUnit: 400,
      revenuePerUnit: 36500, // $100/night * 365
      departments: [
        { name: 'Guest Rooms', percentage: 0.65, icon: 'Bed', color: 'blue' },
        { name: 'Public Areas', percentage: 0.25, icon: 'Users', color: 'green' },
        { name: 'Back of House', percentage: 0.10, icon: 'Settings', color: 'gray' }
      ]
    }
  },
  
  educational: {
    k12_school: {
      unitLabel: 'Classrooms',
      unitType: 'classrooms',
      sfPerUnit: 900,
      revenuePerUnit: 0, // Public funding
      departments: [
        { name: 'Classrooms', percentage: 0.50, icon: 'GraduationCap', color: 'blue' },
        { name: 'Common/Athletic', percentage: 0.35, icon: 'Users', color: 'green' },
        { name: 'Admin/Support', percentage: 0.15, icon: 'Briefcase', color: 'gray' }
      ]
    },
    university: {
      unitLabel: 'Lecture Halls',
      unitType: 'halls',
      sfPerUnit: 2500,
      revenuePerUnit: 0,
      departments: [
        { name: 'Academic Space', percentage: 0.55, icon: 'GraduationCap', color: 'blue' },
        { name: 'Research Labs', percentage: 0.25, icon: 'Flask', color: 'purple' },
        { name: 'Support/Admin', percentage: 0.20, icon: 'Building', color: 'gray' }
      ]
    }
  },
  
  // Default fallback
  default: {
    default: {
      unitLabel: 'Spaces',
      unitType: 'spaces',
      sfPerUnit: 1000,
      departments: [
        { name: 'Primary Space', percentage: 0.70, icon: 'Building2', color: 'blue' },
        { name: 'Support Space', percentage: 0.20, icon: 'Users', color: 'green' },
        { name: 'Infrastructure', percentage: 0.10, icon: 'Settings', color: 'gray' }
      ]
    }
  }
};

export function getBuildingMetrics(buildingType?: string, buildingSubtype?: string): BuildingMetrics {
  if (!buildingType) return BUILDING_METRICS.default.default;
  
  const typeConfig = BUILDING_METRICS[buildingType];
  if (!typeConfig) return BUILDING_METRICS.default.default;
  
  if (!buildingSubtype) {
    // Return first subtype for this type
    const firstSubtype = Object.keys(typeConfig)[0];
    return typeConfig[firstSubtype] || BUILDING_METRICS.default.default;
  }
  
  return typeConfig[buildingSubtype] || BUILDING_METRICS.default.default;
}