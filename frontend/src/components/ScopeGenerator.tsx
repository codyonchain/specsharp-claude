import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { scopeService } from '../services/api';
import './ScopeGenerator.css';

// Temporary type definition
interface ScopeRequest {
  project_name: string;
  project_type: 'residential' | 'commercial' | 'industrial' | 'mixed_use';
  square_footage: number;
  location: string;
  climate_zone?: string;
  num_floors?: number;
  ceiling_height?: number;
  occupancy_type?: string;
  special_requirements?: string;
  budget_constraint?: number;
  building_mix?: { [key: string]: number };
}

function ScopeGenerator() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inputMode, setInputMode] = useState<'natural' | 'form'>('natural');
  const [naturalLanguageInput, setNaturalLanguageInput] = useState('');
  const [formData, setFormData] = useState<ScopeRequest>({
    project_name: '',
    project_type: 'commercial',
    square_footage: 10000,
    location: '',
    num_floors: 1,
    ceiling_height: 9,
    occupancy_type: 'office',
    special_requirements: '',
  });

  // Natural language parser
  const parseNaturalLanguage = (input: string): Partial<ScopeRequest> => {
    const result: Partial<ScopeRequest> = {};
    
    // Parse dimensions (e.g., "150x300" or "10000 SF" or "10,000 square feet")
    const dimensionMatch = input.match(/(\d+)\s*x\s*(\d+)/i);
    const sqftMatch = input.match(/(\d+,?\d*)\s*(sf|sq\.?\s*ft\.?|square\s*feet)/i);
    
    if (dimensionMatch) {
      const width = parseInt(dimensionMatch[1]);
      const length = parseInt(dimensionMatch[2]);
      result.square_footage = width * length;
    } else if (sqftMatch) {
      result.square_footage = parseInt(sqftMatch[1].replace(/,/g, ''));
    }
    
    // Parse building types with percentages
    const buildingTypes: { [key: string]: number } = {};
    const typePattern = /(warehouse|office|retail|residential|industrial|commercial)\s*\(?\s*(\d+)?\s*%?\s*\)?/gi;
    let typeMatch;
    let totalPercentage = 0;
    
    while ((typeMatch = typePattern.exec(input)) !== null) {
      const type = typeMatch[1].toLowerCase();
      const percentage = typeMatch[2] ? parseInt(typeMatch[2]) : 100;
      buildingTypes[type] = percentage;
      totalPercentage += percentage;
    }
    
    // Determine primary project type
    if (Object.keys(buildingTypes).length > 0) {
      if (totalPercentage > 100 || Object.keys(buildingTypes).length > 1) {
        result.project_type = 'mixed_use';
        // Add building mix to special requirements
        const mixDescription = Object.entries(buildingTypes)
          .map(([type, pct]) => `${type} (${pct}%)`)
          .join(', ');
        result.special_requirements = `Building mix: ${mixDescription}`;
        // Normalize percentages to fractions and add to building_mix
        const normalizedMix: { [key: string]: number } = {};
        Object.entries(buildingTypes).forEach(([type, pct]) => {
          normalizedMix[type] = pct / 100;
        });
        result.building_mix = normalizedMix;
      } else {
        const primaryType = Object.keys(buildingTypes)[0];
        result.project_type = primaryType === 'warehouse' ? 'industrial' : 
                            primaryType === 'office' ? 'commercial' : 
                            primaryType as any;
      }
    }
    
    // Parse location (state names or city, state format)
    const stateMap: { [key: string]: string } = {
      'california': 'CA', 'texas': 'TX', 'new york': 'NY', 'florida': 'FL',
      'washington': 'WA', 'oregon': 'OR', 'arizona': 'AZ', 'nevada': 'NV',
      'colorado': 'CO', 'illinois': 'IL', 'georgia': 'GA', 'massachusetts': 'MA'
    };
    
    // Look for state names
    for (const [stateName, stateCode] of Object.entries(stateMap)) {
      if (input.toLowerCase().includes(stateName)) {
        result.location = `${stateName.charAt(0).toUpperCase() + stateName.slice(1)}, ${stateCode}`;
        break;
      }
    }
    
    // Look for city, state pattern
    const cityStateMatch = input.match(/in\s+([A-Za-z\s]+),\s*([A-Z]{2})/);
    if (cityStateMatch && !result.location) {
      result.location = `${cityStateMatch[1].trim()}, ${cityStateMatch[2]}`;
    }
    
    // Parse special requirements
    const requirements: string[] = [];
    if (input.toLowerCase().includes('hvac')) requirements.push('HVAC system');
    if (input.toLowerCase().includes('bathroom')) requirements.push('Bathrooms');
    if (input.toLowerCase().includes('kitchen')) requirements.push('Kitchen facilities');
    if (input.toLowerCase().includes('parking')) requirements.push('Parking');
    if (input.toLowerCase().includes('elevator')) requirements.push('Elevators');
    
    if (requirements.length > 0) {
      const existingReqs = result.special_requirements || '';
      result.special_requirements = existingReqs 
        ? `${existingReqs}. ${requirements.join(', ')}`
        : requirements.join(', ');
    }
    
    // Parse floors
    const floorMatch = input.match(/(\d+)\s*(floor|story|storey|level)/i);
    if (floorMatch) {
      result.num_floors = parseInt(floorMatch[1]);
    }
    
    // Generate project name if not specified
    if (!result.project_name && result.project_type) {
      result.project_name = `${result.project_type.charAt(0).toUpperCase() + result.project_type.slice(1)} Building Project`;
    }
    
    return result;
  };

  const handleNaturalLanguageSubmit = () => {
    const parsed = parseNaturalLanguage(naturalLanguageInput);
    
    // Merge with form data
    const updatedFormData = {
      ...formData,
      ...parsed,
      // Ensure required fields have values
      project_name: parsed.project_name || formData.project_name || 'New Project',
      location: parsed.location || formData.location || 'Seattle, WA',
      square_footage: parsed.square_footage || formData.square_footage || 10000,
    };
    
    setFormData(updatedFormData);
    
    // Switch to form mode to show parsed results
    setInputMode('form');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // If in natural language mode, parse first
    if (inputMode === 'natural' && naturalLanguageInput) {
      handleNaturalLanguageSubmit();
      return;
    }
    
    setLoading(true);
    setError('');

    try {
      const response = await scopeService.generate(formData);
      navigate(`/project/${response.project_id}`);
    } catch (err: any) {
      console.error('Scope generation error:', err);
      let errorMessage = 'Failed to generate scope';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data) {
        errorMessage = JSON.stringify(err.response.data);
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'square_footage' || name === 'num_floors' || name === 'ceiling_height' || name === 'budget_constraint' 
        ? parseFloat(value) || 0 
        : value,
    });
  };

  return (
    <div className="scope-generator">
      <header className="page-header">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          ← Back to Dashboard
        </button>
        <h1>Create New Scope</h1>
      </header>

      <div className="input-mode-toggle">
        <button 
          className={`mode-btn ${inputMode === 'natural' ? 'active' : ''}`}
          onClick={() => setInputMode('natural')}
        >
          Natural Language
        </button>
        <button 
          className={`mode-btn ${inputMode === 'form' ? 'active' : ''}`}
          onClick={() => setInputMode('form')}
        >
          Form Input
        </button>
      </div>

      {inputMode === 'natural' ? (
        <form onSubmit={handleSubmit} className="scope-form">
          <div className="form-section">
            <h2>Describe Your Project</h2>
            <p className="help-text">
              Describe your building project in natural language. For example:
              <br />• "150x300 warehouse (70%) + office(30%) with HVAC and bathrooms in California"
              <br />• "10000 SF office with HVAC and bathrooms in Texas"
              <br />• "50000 square feet mixed commercial and retail space in Seattle"
            </p>
            
            <div className="form-group">
              <textarea
                value={naturalLanguageInput}
                onChange={(e) => setNaturalLanguageInput(e.target.value)}
                placeholder="Describe your construction project..."
                rows={6}
                className="natural-language-input"
                required
              />
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button type="button" onClick={() => navigate('/dashboard')} className="secondary-btn">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="primary-btn">
              {loading ? 'Processing...' : 'Parse & Continue'}
            </button>
          </div>
        </form>
      ) : (
        <form onSubmit={handleSubmit} className="scope-form">
          <div className="form-section">
            <h2>Project Information</h2>
            
            <div className="form-group">
              <label htmlFor="project_name">Project Name</label>
              <input
                id="project_name"
                name="project_name"
                type="text"
                value={formData.project_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="project_type">Project Type</label>
              <select
                id="project_type"
                name="project_type"
                value={formData.project_type}
                onChange={handleChange}
                required
              >
                <option value="residential">Residential</option>
                <option value="commercial">Commercial</option>
                <option value="industrial">Industrial</option>
                <option value="mixed_use">Mixed Use</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input
                id="location"
                name="location"
                type="text"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Seattle, WA"
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h2>Building Details</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="square_footage">Square Footage</label>
                <input
                  id="square_footage"
                  name="square_footage"
                  type="number"
                  value={formData.square_footage}
                  onChange={handleChange}
                  min="100"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="num_floors">Number of Floors</label>
                <input
                  id="num_floors"
                  name="num_floors"
                  type="number"
                  value={formData.num_floors}
                  onChange={handleChange}
                  min="1"
                  max="100"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="ceiling_height">Ceiling Height (ft)</label>
                <input
                  id="ceiling_height"
                  name="ceiling_height"
                  type="number"
                  value={formData.ceiling_height}
                  onChange={handleChange}
                  min="8"
                  max="30"
                  step="0.5"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="occupancy_type">Occupancy Type</label>
              <input
                id="occupancy_type"
                name="occupancy_type"
                type="text"
                value={formData.occupancy_type}
                onChange={handleChange}
                placeholder="e.g., office, retail, warehouse"
              />
            </div>

            <div className="form-group">
              <label htmlFor="special_requirements">Special Requirements</label>
              <textarea
                id="special_requirements"
                name="special_requirements"
                value={formData.special_requirements}
                onChange={handleChange}
                rows={3}
                placeholder="e.g., LEED certification, clean rooms, special HVAC requirements"
              />
            </div>

            <div className="form-group">
              <label htmlFor="budget_constraint">Budget Constraint (optional)</label>
              <input
                id="budget_constraint"
                name="budget_constraint"
                type="number"
                value={formData.budget_constraint || ''}
                onChange={handleChange}
                min="0"
                placeholder="Enter budget limit"
              />
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button type="button" onClick={() => navigate('/dashboard')} className="secondary-btn">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="primary-btn">
              {loading ? 'Generating...' : 'Generate Scope'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default ScopeGenerator;