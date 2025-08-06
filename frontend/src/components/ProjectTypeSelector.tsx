import React from 'react';
import { HardHat, Home, Hammer } from 'lucide-react';
import './ProjectTypeSelector.css';

interface ProjectTypeSelectorProps {
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  autoSelected?: boolean;
}

interface TypeOption {
  value: string;
  label: string;
  description: string;
  impact: string;
  icon: React.ReactNode;
  color: string;
}

const projectTypes: TypeOption[] = [
  {
    value: 'ground_up',
    label: 'Ground-Up Construction',
    description: 'New building on empty lot',
    impact: 'Standard pricing',
    icon: <HardHat size={32} />,
    color: '#10b981'
  },
  {
    value: 'addition',
    label: 'Addition',
    description: 'Expanding existing structure',
    impact: '+15% for tie-ins & protection',
    icon: <Home size={32} />,
    color: '#3b82f6'
  },
  {
    value: 'renovation',
    label: 'Renovation',
    description: 'Remodeling existing space',
    impact: '+35% for demo & unknowns',
    icon: <Hammer size={32} />,
    color: '#f59e0b'
  }
];

const ProjectTypeSelector: React.FC<ProjectTypeSelectorProps> = ({ 
  value, 
  onChange, 
  required = false,
  autoSelected = false 
}) => {
  return (
    <div className="project-type-selector">
      <label className="selector-label">
        Project Classification
        {required && <span className="required-indicator">*</span>}
      </label>
      
      <div className="selector-description">
        Select your project type - this significantly affects pricing
      </div>
      
      <div className="type-cards">
        {projectTypes.map((type) => (
          <div
            key={type.value}
            className={`type-card ${value === type.value ? 'selected' : ''} ${value === type.value && autoSelected ? 'auto-selected' : ''}`}
            onClick={() => onChange(type.value)}
            style={{ borderColor: value === type.value ? type.color : undefined }}
          >
            <div className="card-icon" style={{ color: type.color }}>
              {type.icon}
            </div>
            <h3 className="card-title">{type.label}</h3>
            <p className="card-description">{type.description}</p>
            <div className="card-impact" style={{ backgroundColor: `${type.color}15` }}>
              {type.impact}
            </div>
          </div>
        ))}
      </div>
      
      <div className="info-box">
        <div className="info-icon">ℹ️</div>
        <div className="info-text">
          <strong>Why does this matter?</strong>
          <ul>
            <li><strong>Ground-Up:</strong> Standard costs for new construction</li>
            <li><strong>Additions:</strong> ~15% premium for connecting to existing structures, protection, and limited access</li>
            <li><strong>Renovations:</strong> ~35% premium for demolition, unknowns, phased work, and occupied space protection</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ProjectTypeSelector;