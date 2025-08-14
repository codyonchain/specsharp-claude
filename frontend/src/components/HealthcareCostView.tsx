import React from 'react';
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
import './HealthcareCostView.css';

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
    <div className="healthcare-cost-view" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Facility Overview */}
      <div className="healthcare-card">
        <div className="card-header">
          <h3 className="card-title flex items-center gap-2">
            <Heart className="h-5 w-5" style={{ color: '#ef4444' }} />
            Healthcare Facility Overview
          </h3>
        </div>
        <div className="card-content">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Facility Type</p>
              <p style={{ fontWeight: '600' }}>{getFacilityTypeDisplay(data.facility_type)}</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Market</p>
              <p style={{ fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <MapPin style={{ height: '16px', width: '16px' }} />
                {data.market}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Size</p>
              <p style={{ fontWeight: '600' }}>{data.square_feet.toLocaleString()} SF</p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>Complexity</p>
              <p style={{ fontWeight: '600' }}>{data.classification?.complexity_multiplier.toFixed(2)}x</p>
            </div>
          </div>
        </div>
      </div>

      {/* Special Spaces */}
      {data.special_spaces && data.special_spaces.length > 0 && (
        <div className="healthcare-card">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2">
              <Activity className="h-5 w-5" style={{ color: '#3b82f6' }} />
              Specialized Healthcare Spaces
            </h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {data.special_spaces.map((space, index) => (
                <div
                  key={index}
                  style={{ padding: '0.375rem 0.75rem', backgroundColor: '#dbeafe', color: '#1d4ed8', borderRadius: '0.375rem', fontSize: '0.875rem', fontWeight: '500' }}
                >
                  {getSpecialSpaceDisplay(space)}
                </div>
              ))}
            </div>
            {data.construction.special_spaces_premium > 0 && (
              <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                Special spaces premium: {formatCurrency(data.construction.special_spaces_premium)}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Department-Level Costs */}
      <div className="healthcare-card">
        <div className="card-header">
          <h3 className="card-title flex items-center gap-2">
            <Building2 className="h-5 w-5" style={{ color: '#10b981' }} />
            Construction Costs by Department
          </h3>
        </div>
        <div className="card-content" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {Object.entries(departmentCosts).map(([dept, cost]) => (
            <div key={dept}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>{dept}</span>
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  {formatCurrency(cost)} ({formatPercentage(cost, data.construction.subtotal)})
                </span>
              </div>
              <div className="progress-bar" style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${(cost / data.construction.subtotal) * 100}%`, height: '100%', backgroundColor: '#0088FE', transition: 'width 0.3s' }} />
              </div>
            </div>
          ))}
          <div style={{ paddingTop: '1rem', borderTop: '1px solid #e5e7eb' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: '600' }}>Construction Subtotal</span>
              <span style={{ fontWeight: '600' }}>{formatCurrency(data.construction.subtotal)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
              <span className="text-sm text-muted-foreground">Contingency (10%)</span>
              <span className="text-sm text-muted-foreground">{formatCurrency(data.construction.contingency)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid #e5e7eb' }}>
              <span style={{ fontWeight: '600' }}>Total Construction</span>
              <div style={{ textAlign: 'right' }}>
                <p style={{ fontWeight: '600' }}>{formatCurrency(data.construction.total)}</p>
                <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>{formatCurrency(data.construction.cost_per_sf)}/SF</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Medical Equipment */}
      {data.equipment.total > 0 && (
        <div className="healthcare-card">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2">
              <Stethoscope className="h-5 w-5" style={{ color: '#a855f7' }} />
              Medical Equipment Costs
            </h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {data.equipment.items.map((item, index) => (
                <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Cpu style={{ height: '16px', width: '16px', color: '#a855f7' }} />
                    <span style={{ fontSize: '0.875rem' }}>{item.name}</span>
                    {item.requires_shielding && (
                      <span style={{ fontSize: '0.75rem', padding: '0.125rem 0.5rem', backgroundColor: '#fef3c7', color: '#b45309', borderRadius: '0.25rem' }}>
                        Requires Shielding
                      </span>
                    )}
                  </div>
                  <span style={{ fontWeight: '500' }}>{formatCurrency(item.cost)}</span>
                </div>
              ))}
            </div>
            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: '600' }}>Total Equipment</span>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontWeight: '600' }}>{formatCurrency(data.equipment.total)}</p>
                  <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>{formatCurrency(data.equipment.cost_per_sf)}/SF</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Compliance & Regulatory */}
      {data.compliance && Object.keys(data.compliance).length > 0 && (
        <div className="healthcare-card">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2">
              <Shield className="h-5 w-5" style={{ color: '#f97316' }} />
              Compliance & Regulatory Requirements
            </h3>
          </div>
          <div className="card-content">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
              {Object.entries(data.compliance).map(([req, status]) => (
                <div key={req} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{ height: '12px', width: '12px', borderRadius: '50%', backgroundColor: status ? '#10b981' : '#d1d5db' }} />
                  <span style={{ fontSize: '0.875rem' }}>
                    {req.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Project Total Summary */}
      <div className="healthcare-card" style={{ border: '2px solid #0088FE' }}>
        <div className="card-header">
          <h3 className="card-title flex items-center gap-2">
            <DollarSign className="h-5 w-5" style={{ color: '#0088FE' }} />
            Project Total Summary
          </h3>
        </div>
        <div className="card-content">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Construction</span>
                <span style={{ fontSize: '0.875rem' }}>{formatCurrency(data.project_total.construction_only)}</span>
              </div>
              <div className="progress-bar" style={{ height: '12px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${constructionPercentage}%`, height: '100%', backgroundColor: '#0088FE', transition: 'width 0.3s' }} />
              </div>
              <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>{constructionPercentage.toFixed(1)}% of total</p>
            </div>
            
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Equipment</span>
                <span style={{ fontSize: '0.875rem' }}>{formatCurrency(data.project_total.equipment_only)}</span>
              </div>
              <div className="progress-bar" style={{ height: '12px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${equipmentPercentage}%`, height: '100%', backgroundColor: '#a855f7', transition: 'width 0.3s' }} />
              </div>
              <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>{equipmentPercentage.toFixed(1)}% of total</p>
            </div>

            <div style={{ paddingTop: '1rem', borderTop: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '1.125rem', fontWeight: '700' }}>All-In Project Total</span>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0088FE' }}>{formatCurrency(data.project_total.all_in_total)}</p>
                  <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>{formatCurrency(data.project_total.all_in_cost_per_sf)}/SF</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};