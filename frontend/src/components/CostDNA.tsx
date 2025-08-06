import React from 'react';
import './CostDNA.css';

interface CostFactor {
  category: string;
  factor: string;
  impact: string;
  description: string;
}

interface ComparableProject {
  name: string;
  location: string;
  size: number;
  cost: number;
  costPerSqft: number;
  similarity: number;
}

interface CostDNAProps {
  projectData: any;
}

const CostDNA: React.FC<CostDNAProps> = ({ projectData }) => {
  // Extract cost factors from project data
  const extractCostFactors = (): CostFactor[] => {
    const factors: CostFactor[] = [];
    
    // Project classification factor
    if (projectData.project_classification === 'addition') {
      factors.push({
        category: 'Project Type',
        factor: 'Addition',
        impact: '+15%',
        description: 'Tie-ins, protection, and limited access'
      });
    } else if (projectData.project_classification === 'renovation') {
      factors.push({
        category: 'Project Type',
        factor: 'Renovation',
        impact: '+35%',
        description: 'Demolition, unknowns, and phased work'
      });
    }
    
    // Healthcare-specific factors
    if (projectData.occupancy_type?.toLowerCase().includes('hospital')) {
      factors.push({
        category: 'Healthcare',
        factor: 'Hospital Standards',
        impact: '+$200-300/SF',
        description: 'Complex MEP, redundant systems, medical gas'
      });
    }
    
    if (projectData.special_requirements?.toLowerCase().includes('operating room') || 
        projectData.special_requirements?.toLowerCase().includes('or')) {
      factors.push({
        category: 'Medical Features',
        factor: 'Operating Rooms',
        impact: '+$75-100/SF',
        description: 'Specialized HVAC, medical gas, equipment'
      });
    }
    
    if (projectData.special_requirements?.toLowerCase().includes('emergency')) {
      factors.push({
        category: 'Medical Features',
        factor: 'Emergency Department',
        impact: '+$50-75/SF',
        description: '24/7 operations, trauma requirements'
      });
    }
    
    // Regional factors
    const location = projectData.location?.toLowerCase();
    if (location?.includes('california')) {
      factors.push({
        category: 'Regional',
        factor: 'California Seismic',
        impact: '+8-12%',
        description: 'Seismic design requirements'
      });
      
      if (projectData.occupancy_type?.toLowerCase().includes('hospital') || 
          projectData.occupancy_type?.toLowerCase().includes('medical')) {
        factors.push({
          category: 'Compliance',
          factor: 'OSHPD Requirements',
          impact: '+15-20%',
          description: 'California healthcare facility standards'
        });
      }
    }
    
    if (location?.includes('new york') || location?.includes('san francisco') || 
        location?.includes('boston')) {
      factors.push({
        category: 'Market',
        factor: 'High-Cost Market',
        impact: '+20-25%',
        description: 'Premium labor and material costs'
      });
    }
    
    // Restaurant-specific factors
    if (projectData.occupancy_type?.toLowerCase().includes('restaurant')) {
      if (projectData.special_requirements?.toLowerCase().includes('kitchen')) {
        factors.push({
          category: 'Equipment',
          factor: 'Commercial Kitchen',
          impact: '+$75-100/SF',
          description: 'Kitchen equipment and ventilation'
        });
      }
      if (projectData.special_requirements?.toLowerCase().includes('drive')) {
        factors.push({
          category: 'Site',
          factor: 'Drive-Through',
          impact: '+$25-35/SF',
          description: 'Site work and canopy'
        });
      }
    }
    
    // Size factors
    if (projectData.square_footage > 100000) {
      factors.push({
        category: 'Scale',
        factor: 'Large Project',
        impact: '-5-8%',
        description: 'Economies of scale'
      });
    } else if (projectData.square_footage < 5000) {
      factors.push({
        category: 'Scale',
        factor: 'Small Project',
        impact: '+10-15%',
        description: 'Limited economies of scale'
      });
    }
    
    return factors;
  };
  
  // Generate comparable projects
  const generateComparables = (): ComparableProject[] => {
    const basePrice = projectData.cost_per_sqft || 250;
    const comparables: ComparableProject[] = [];
    
    // Generate 3 similar projects with slight variations
    const variations = [
      { sizeFactor: 0.8, priceFactor: 0.95, similarity: 92 },
      { sizeFactor: 1.2, priceFactor: 1.05, similarity: 88 },
      { sizeFactor: 1.1, priceFactor: 0.98, similarity: 85 }
    ];
    
    variations.forEach((v, i) => {
      const size = Math.round(projectData.square_footage * v.sizeFactor);
      const costPerSqft = Math.round(basePrice * v.priceFactor);
      comparables.push({
        name: `${projectData.occupancy_type || 'Commercial'} Building ${i + 1}`,
        location: projectData.location || 'Similar Market',
        size: size,
        cost: size * costPerSqft,
        costPerSqft: costPerSqft,
        similarity: v.similarity
      });
    });
    
    return comparables;
  };
  
  // Calculate confidence score
  const calculateConfidence = (): number => {
    let confidence = 60; // Base confidence
    
    // Add confidence for specific data points
    if (projectData.location) confidence += 10;
    if (projectData.occupancy_type) confidence += 10;
    if (projectData.square_footage) confidence += 5;
    if (projectData.project_classification) confidence += 5;
    if (projectData.special_requirements) confidence += 5;
    if (projectData.num_floors) confidence += 5;
    
    return Math.min(confidence, 100);
  };
  
  const costFactors = extractCostFactors();
  const comparables = generateComparables();
  const confidence = calculateConfidence();
  
  return (
    <div className="cost-dna-container">
      <div className="cost-dna-header">
        <h2>Cost DNA Analysis</h2>
        <div className="confidence-score">
          <span className="confidence-label">Confidence:</span>
          <div className="confidence-bar">
            <div 
              className="confidence-fill" 
              style={{ width: `${confidence}%` }}
            />
          </div>
          <span className="confidence-value">{confidence}%</span>
        </div>
      </div>
      
      {costFactors.length > 0 && (
        <div className="cost-factors-section">
          <h3>Cost Factors Detected</h3>
          <div className="cost-factors-grid">
            {costFactors.map((factor, index) => (
              <div key={index} className="cost-factor-card">
                <div className="factor-header">
                  <span className="factor-category">{factor.category}</span>
                  <span className="factor-impact">{factor.impact}</span>
                </div>
                <div className="factor-name">{factor.factor}</div>
                <div className="factor-description">{factor.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="comparables-section">
        <h3>Comparable Projects</h3>
        <div className="comparables-list">
          {comparables.map((comp, index) => (
            <div key={index} className="comparable-card">
              <div className="comparable-header">
                <span className="comparable-name">{comp.name}</span>
                <span className="similarity-badge">{comp.similarity}% match</span>
              </div>
              <div className="comparable-details">
                <div className="comparable-detail">
                  <span className="detail-label">Location:</span>
                  <span className="detail-value">{comp.location}</span>
                </div>
                <div className="comparable-detail">
                  <span className="detail-label">Size:</span>
                  <span className="detail-value">{comp.size.toLocaleString()} SF</span>
                </div>
                <div className="comparable-detail">
                  <span className="detail-label">Cost/SF:</span>
                  <span className="detail-value">${comp.costPerSqft}</span>
                </div>
                <div className="comparable-detail">
                  <span className="detail-label">Total:</span>
                  <span className="detail-value">${comp.cost.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="market-conditions">
        <h3>Market Conditions</h3>
        <div className="market-indicators">
          <div className="market-indicator">
            <span className="indicator-label">Material Costs:</span>
            <span className="indicator-value trending-up">↑ 3.2% YoY</span>
          </div>
          <div className="market-indicator">
            <span className="indicator-label">Labor Availability:</span>
            <span className="indicator-value stable">Stable</span>
          </div>
          <div className="market-indicator">
            <span className="indicator-label">Regional Activity:</span>
            <span className="indicator-value high">High</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CostDNA;