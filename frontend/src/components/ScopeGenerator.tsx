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
  service_level?: string;
  building_features?: string[];
}

function ScopeGenerator() {
  console.log('ScopeGenerator component mounted');
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
    
    // First, try to match patterns like "industrial (80%)" or "60% retail"
    const percentagePatterns = [
      /(warehouse|office|retail|residential|industrial|commercial|manufacturing|facility|restaurant|kitchen|dining)\s*\((\d+)%\)/gi,
      /(\d+)%\s+(warehouse|office|retail|residential|industrial|commercial|manufacturing|restaurant|kitchen|dining)/gi,
      /(warehouse|office|retail|residential|industrial|commercial|manufacturing|restaurant|kitchen|dining)\s+(\d+)%/gi
    ];
    
    let hasPercentages = false;
    let totalPercentage = 0;
    
    // Try each pattern to find percentages
    for (const pattern of percentagePatterns) {
      let match;
      while ((match = pattern.exec(input)) !== null) {
        let type, percentage;
        if (match[1] && isNaN(parseInt(match[1]))) {
          // Pattern like "industrial (80%)"
          type = match[1].toLowerCase();
          percentage = parseInt(match[2]);
        } else {
          // Pattern like "60% retail"
          percentage = parseInt(match[1]);
          type = match[2].toLowerCase();
        }
        
        // Normalize type names
        if (type === 'manufacturing' || type === 'facility') {
          type = 'industrial';
        }
        // Handle restaurant-related terms
        if (type === 'kitchen' || type === 'dining') {
          type = 'restaurant';
        }
        
        buildingTypes[type] = percentage;
        totalPercentage += percentage;
        hasPercentages = true;
      }
    }
    
    // Look for patterns like "manufacturing facility with 25% office space"
    if (hasPercentages && totalPercentage < 100) {
      // Find building types mentioned without percentages
      const simpleTypePattern = /(warehouse|office|retail|residential|industrial|commercial|manufacturing|facility|restaurant|kitchen|dining)(?:\s+(?:space|building|area|facility|room))?/gi;
      let typeMatch;
      
      while ((typeMatch = simpleTypePattern.exec(input)) !== null) {
        let type = typeMatch[1].toLowerCase();
        if (type === 'manufacturing' || type === 'facility') {
          type = 'industrial';
        }
        // Handle restaurant-related terms
        if (type === 'kitchen' || type === 'dining') {
          type = 'restaurant';
        }
        // If this type doesn't have a percentage assigned yet
        if (!buildingTypes[type]) {
          buildingTypes[type] = 100 - totalPercentage;
          totalPercentage = 100;
          break;
        }
      }
    }
    
    // If no percentages found, look for building types without percentages
    if (!hasPercentages) {
      const simpleTypePattern = /(warehouse|office|retail|residential|industrial|commercial|manufacturing|facility|restaurant|kitchen|dining)(?:\s+(?:space|building|area|room))?/gi;
      let typeMatch;
      const foundTypes: string[] = [];
      
      while ((typeMatch = simpleTypePattern.exec(input)) !== null) {
        let type = typeMatch[1].toLowerCase();
        if (type === 'manufacturing' || type === 'facility') {
          type = 'industrial';
        }
        // Handle restaurant-related terms
        if (type === 'kitchen' || type === 'dining') {
          type = 'restaurant';
        }
        if (!foundTypes.includes(type)) {
          foundTypes.push(type);
        }
      }
      
      // If multiple types found without percentages, assume equal distribution
      if (foundTypes.length > 1) {
        const equalPercentage = Math.floor(100 / foundTypes.length);
        foundTypes.forEach((type, index) => {
          // Give any remainder to the first type
          buildingTypes[type] = index === 0 ? equalPercentage + (100 % foundTypes.length) : equalPercentage;
        });
        totalPercentage = 100;
      } else if (foundTypes.length === 1) {
        buildingTypes[foundTypes[0]] = 100;
        totalPercentage = 100;
      }
    }
    
    // Determine primary project type
    if (Object.keys(buildingTypes).length > 0) {
      if (Object.keys(buildingTypes).length > 1) {
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
        
        // Set occupancy type to the dominant type
        const dominantType = Object.entries(buildingTypes).reduce((a, b) => 
          b[1] > a[1] ? b : a
        )[0];
        result.occupancy_type = dominantType;
      } else {
        const primaryType = Object.keys(buildingTypes)[0];
        result.project_type = primaryType === 'warehouse' ? 'industrial' : 
                            primaryType === 'office' ? 'commercial' : 
                            primaryType === 'industrial' ? 'industrial' :
                            primaryType === 'retail' ? 'commercial' :
                            primaryType === 'restaurant' ? 'commercial' :
                            primaryType === 'residential' ? 'residential' :
                            'commercial';
        result.occupancy_type = primaryType;
      }
    }
    
    // Parse location (state names or city, state format)
    const stateMap: { [key: string]: string } = {
      'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
      'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
      'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
      'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
      'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
      'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
      'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
      'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
      'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
      'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
      'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
      'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
      'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC', 'dc': 'DC'
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
    
    // Look for state codes (e.g., "in NH" or "NH location")
    if (!result.location) {
      const stateCodeMatch = input.match(/\b([A-Z]{2})\b/);
      if (stateCodeMatch) {
        const stateCode = stateCodeMatch[1];
        // Verify it's a valid state code
        const validStateCodes = Object.values(stateMap);
        if (validStateCodes.includes(stateCode)) {
          // Find the full state name
          const stateName = Object.entries(stateMap).find(([name, code]) => code === stateCode)?.[0];
          if (stateName) {
            result.location = `${stateName.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}, ${stateCode}`;
          }
        }
      }
    }
    
    // Parse special requirements
    const requirements: string[] = [];
    if (input.toLowerCase().includes('hvac')) requirements.push('HVAC system');
    if (input.toLowerCase().includes('bathroom')) requirements.push('Bathrooms');
    if (input.toLowerCase().includes('commercial kitchen')) {
      requirements.push('Commercial kitchen');
    } else if (input.toLowerCase().includes('kitchen')) {
      requirements.push('Kitchen facilities');
    }
    if (input.toLowerCase().includes('dining')) requirements.push('Dining area');
    if (input.toLowerCase().includes('bar')) requirements.push('Bar area');
    if (input.toLowerCase().includes('parking')) requirements.push('Parking');
    if (input.toLowerCase().includes('elevator')) requirements.push('Elevators');
    if (input.toLowerCase().includes('dock door')) requirements.push('Multiple dock doors');
    if (input.toLowerCase().includes('loading dock')) requirements.push('Loading docks');
    if (input.toLowerCase().includes('crane')) requirements.push('Overhead crane');
    if (input.toLowerCase().includes('high ceiling') || input.toLowerCase().includes('clear height')) {
      requirements.push('High ceilings');
    }
    
    if (requirements.length > 0) {
      const existingReqs = result.special_requirements || '';
      // If we already have building mix in special requirements, append other requirements
      if (existingReqs.includes('Building mix:')) {
        result.special_requirements = `${existingReqs}, ${requirements.join(', ')}`;
      } else {
        result.special_requirements = existingReqs 
          ? `${existingReqs}. ${requirements.join(', ')}`
          : requirements.join(', ');
      }
    }
    
    // Parse floors
    const floorMatch = input.match(/(\d+)\s*(floor|story|storey|level)/i);
    if (floorMatch) {
      result.num_floors = parseInt(floorMatch[1]);
    }
    
    // Parse restaurant service levels
    if (result.occupancy_type === 'restaurant' || 
        (result.building_mix && Object.keys(result.building_mix).includes('restaurant'))) {
      if (input.toLowerCase().includes('quick service') || 
          input.toLowerCase().includes('fast food') || 
          input.toLowerCase().includes('qsr')) {
        result.service_level = 'quick_service';
      } else if (input.toLowerCase().includes('casual dining') || 
                 input.toLowerCase().includes('family restaurant')) {
        result.service_level = 'casual_dining';
      } else if (input.toLowerCase().includes('fine dining') || 
                 input.toLowerCase().includes('upscale') || 
                 input.toLowerCase().includes('white tablecloth')) {
        result.service_level = 'fine_dining';
      } else if (input.toLowerCase().includes('full service') || 
                 input.toLowerCase().includes('full-service')) {
        result.service_level = 'full_service';
      }
      
      // Parse restaurant features
      const restaurantFeatures: string[] = [];
      if (input.toLowerCase().includes('commercial kitchen') || input.toLowerCase().includes('kitchen')) {
        restaurantFeatures.push('commercial_kitchen');
      }
      if (input.toLowerCase().includes('bar') || input.toLowerCase().includes('tavern') || input.toLowerCase().includes('pub')) {
        restaurantFeatures.push('full_bar');
      }
      if (input.toLowerCase().includes('outdoor') || input.toLowerCase().includes('patio') || input.toLowerCase().includes('terrace')) {
        restaurantFeatures.push('outdoor_dining');
      }
      if (input.toLowerCase().includes('drive-thru') || input.toLowerCase().includes('drive thru')) {
        restaurantFeatures.push('drive_thru');
      }
      if (input.toLowerCase().includes('wine cellar') || input.toLowerCase().includes('wine storage')) {
        restaurantFeatures.push('wine_cellar');
      }
      if (input.toLowerCase().includes('premium') || input.toLowerCase().includes('luxury') || input.toLowerCase().includes('high-end')) {
        restaurantFeatures.push('premium_finishes');
      }
      
      if (restaurantFeatures.length > 0) {
        result.building_features = restaurantFeatures;
      }
    }
    
    // Generate project name if not specified
    if (!result.project_name && result.project_type) {
      result.project_name = `${result.project_type.charAt(0).toUpperCase() + result.project_type.slice(1)} Building Project`;
    }
    
    return result;
  };

  const handleNaturalLanguageSubmit = () => {
    const parsed = parseNaturalLanguage(naturalLanguageInput);
    
    console.log('Natural language input:', naturalLanguageInput);
    console.log('Parsed result:', parsed);
    
    // Merge with form data
    const updatedFormData = {
      ...formData,
      ...parsed,
      // Ensure required fields have values
      project_name: parsed.project_name || formData.project_name || 'New Project',
      location: parsed.location || formData.location || 'Seattle, WA',
      square_footage: parsed.square_footage || formData.square_footage || 10000,
    };
    
    console.log('Updated form data:', updatedFormData);
    
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

    console.log('Submitting form data:', formData);

    try {
      const response = await scopeService.generate(formData);
      navigate(`/project/${response.project_id}`);
    } catch (err: any) {
      console.error('Scope generation error:', err);
      console.error('Error response:', err.response);
      let errorMessage = 'Failed to generate scope';
      
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          // Pydantic validation errors come as an array
          errorMessage = err.response.data.detail.map((e: any) => 
            `${e.loc.join(' → ')}: ${e.msg}`
          ).join('\n');
        } else {
          errorMessage = err.response.data.detail;
        }
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

  // Add a try-catch for the render to catch any rendering errors
  try {
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
              <br />• "4000 sf full-service restaurant with commercial kitchen and dining room in New Hampshire"
              <br />• "20000 sf mixed office (60%) + restaurant (40%) in Boston"
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
                placeholder="e.g., office, retail, warehouse, restaurant"
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
  } catch (renderError) {
    console.error('ScopeGenerator render error:', renderError);
    return (
      <div className="scope-generator">
        <div className="error-message">
          An error occurred while rendering the form. Please refresh the page.
          <br />
          Error: {String(renderError)}
        </div>
      </div>
    );
  }
}

export default ScopeGenerator;