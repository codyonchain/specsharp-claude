import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { 
  Building2, 
  Heart, 
  Stethoscope, 
  Activity,
  Shield,
  MapPin,
  DollarSign,
  Cpu
} from 'lucide-react';

interface HealthcareCostViewProps {
  data: {
    facility_type: string;
    market: string;
    square_feet: number;
    construction: {
      base_cost_per_sf: number;
      trades: Record<string, number>;
      special_spaces_premium: number;
      subtotal: number;
      contingency: number;
      total: number;
      cost_per_sf: number;
    };
    equipment: {
      items: Array<{
        name: string;
        cost: number;
        requires_shielding?: boolean;
      }>;
      total: number;
      cost_per_sf: number;
    };
    project_total: {
      construction_only: number;
      equipment_only: number;
      all_in_total: number;
      all_in_cost_per_sf: number;
    };
    compliance: Record<string, boolean>;
    special_spaces: string[];
    classification?: {
      confidence: number;
      complexity_multiplier: number;
    };
  };
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const formatPercentage = (value: number, total: number): string => {
  return `${((value / total) * 100).toFixed(1)}%`;
};

const getFacilityTypeDisplay = (type: string): string => {
  const typeMap: Record<string, string> = {
    'general_hospital': 'General Hospital',
    'pediatric_hospital': 'Pediatric Hospital',
    'ambulatory_surgery_center': 'Ambulatory Surgery Center',
    'medical_office': 'Medical Office Building',
    'urgent_care': 'Urgent Care Center',
    'imaging_center': 'Imaging Center',
    'skilled_nursing_facility': 'Skilled Nursing Facility',
    'dental_clinic': 'Dental Clinic',
    'rehabilitation_hospital': 'Rehabilitation Hospital',
    'psychiatric_hospital': 'Psychiatric Hospital'
  };
  return typeMap[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const getSpecialSpaceDisplay = (space: string): string => {
  const spaceMap: Record<string, string> = {
    'operating_room': 'Operating Rooms',
    'emergency_dept': 'Emergency Department',
    'icu': 'Intensive Care Unit',
    'mri_suite': 'MRI Suite',
    'ct_suite': 'CT Scanner Suite',
    'xray_suite': 'X-Ray Suite',
    'laboratory': 'Laboratory',
    'pharmacy': 'Pharmacy',
    'clean_room': 'Clean Room',
    'isolation_room': 'Isolation Rooms'
  };
  return spaceMap[space] || space.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const HealthcareCostView: React.FC<HealthcareCostViewProps> = ({ data }) => {
  const constructionPercentage = (data.project_total.construction_only / data.project_total.all_in_total) * 100;
  const equipmentPercentage = (data.project_total.equipment_only / data.project_total.all_in_total) * 100;

  // Calculate department costs (estimates based on special spaces)
  const departmentCosts = {
    'Clinical Spaces': data.construction.subtotal * 0.45,
    'Support Spaces': data.construction.subtotal * 0.25,
    'Administrative': data.construction.subtotal * 0.15,
    'Infrastructure': data.construction.subtotal * 0.15
  };

  return (
    <div className="space-y-6">
      {/* Facility Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" />
            Healthcare Facility Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Facility Type</p>
              <p className="font-semibold">{getFacilityTypeDisplay(data.facility_type)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Market</p>
              <p className="font-semibold flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {data.market}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Size</p>
              <p className="font-semibold">{data.square_feet.toLocaleString()} SF</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Complexity</p>
              <p className="font-semibold">{data.classification?.complexity_multiplier.toFixed(2)}x</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Special Spaces */}
      {data.special_spaces && data.special_spaces.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-500" />
              Specialized Healthcare Spaces
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {data.special_spaces.map((space, index) => (
                <div
                  key={index}
                  className="px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-md text-sm font-medium"
                >
                  {getSpecialSpaceDisplay(space)}
                </div>
              ))}
            </div>
            {data.construction.special_spaces_premium > 0 && (
              <p className="mt-4 text-sm text-muted-foreground">
                Special spaces premium: {formatCurrency(data.construction.special_spaces_premium)}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Department-Level Costs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-green-500" />
            Construction Costs by Department
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(departmentCosts).map(([dept, cost]) => (
            <div key={dept}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">{dept}</span>
                <span className="text-sm text-muted-foreground">
                  {formatCurrency(cost)} ({formatPercentage(cost, data.construction.subtotal)})
                </span>
              </div>
              <Progress value={(cost / data.construction.subtotal) * 100} className="h-2" />
            </div>
          ))}
          <div className="pt-4 border-t">
            <div className="flex justify-between items-center">
              <span className="font-semibold">Construction Subtotal</span>
              <span className="font-semibold">{formatCurrency(data.construction.subtotal)}</span>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-muted-foreground">Contingency (10%)</span>
              <span className="text-sm text-muted-foreground">{formatCurrency(data.construction.contingency)}</span>
            </div>
            <div className="flex justify-between items-center mt-2 pt-2 border-t">
              <span className="font-semibold">Total Construction</span>
              <div className="text-right">
                <p className="font-semibold">{formatCurrency(data.construction.total)}</p>
                <p className="text-sm text-muted-foreground">{formatCurrency(data.construction.cost_per_sf)}/SF</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Medical Equipment */}
      {data.equipment.total > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Stethoscope className="h-5 w-5 text-purple-500" />
              Medical Equipment Costs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.equipment.items.map((item, index) => (
                <div key={index} className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-purple-500" />
                    <span className="text-sm">{item.name}</span>
                    {item.requires_shielding && (
                      <span className="text-xs px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300 rounded">
                        Requires Shielding
                      </span>
                    )}
                  </div>
                  <span className="font-medium">{formatCurrency(item.cost)}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t">
              <div className="flex justify-between items-center">
                <span className="font-semibold">Total Equipment</span>
                <div className="text-right">
                  <p className="font-semibold">{formatCurrency(data.equipment.total)}</p>
                  <p className="text-sm text-muted-foreground">{formatCurrency(data.equipment.cost_per_sf)}/SF</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Compliance & Regulatory */}
      {data.compliance && Object.keys(data.compliance).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-orange-500" />
              Compliance & Regulatory Requirements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(data.compliance).map(([req, status]) => (
                <div key={req} className="flex items-center gap-2">
                  <div className={`h-3 w-3 rounded-full ${status ? 'bg-green-500' : 'bg-gray-300'}`} />
                  <span className="text-sm">
                    {req.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Project Total Summary */}
      <Card className="border-2 border-primary">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-primary" />
            Project Total Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Construction</span>
                <span className="text-sm">{formatCurrency(data.project_total.construction_only)}</span>
              </div>
              <Progress value={constructionPercentage} className="h-3" />
              <p className="text-xs text-muted-foreground mt-1">{constructionPercentage.toFixed(1)}% of total</p>
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Equipment</span>
                <span className="text-sm">{formatCurrency(data.project_total.equipment_only)}</span>
              </div>
              <Progress value={equipmentPercentage} className="h-3" />
              <p className="text-xs text-muted-foreground mt-1">{equipmentPercentage.toFixed(1)}% of total</p>
            </div>

            <div className="pt-4 border-t">
              <div className="flex justify-between items-center">
                <span className="text-lg font-bold">All-In Project Total</span>
                <div className="text-right">
                  <p className="text-2xl font-bold text-primary">{formatCurrency(data.project_total.all_in_total)}</p>
                  <p className="text-sm text-muted-foreground">{formatCurrency(data.project_total.all_in_cost_per_sf)}/SF</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};