import React, { useEffect, useState } from 'react';
import './CostDNA.css';

interface CostDNAProps {
  projectData: any;
  costDNA?: any;  // Optional - won't break if not provided
}

export const CostDNADisplay: React.FC<CostDNAProps> = ({ projectData, costDNA }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [dnaData, setDnaData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Log for debugging
  console.log('🧬 CostDNADisplay mounted with projectData:', projectData);
  
  // If Cost DNA not provided, fetch it
  useEffect(() => {
    console.log('🧬 Cost DNA useEffect triggered', { costDNA, projectData });
    if (!costDNA && projectData && projectData.square_footage) {
      fetchCostDNA();
    } else if (costDNA) {
      setDnaData(costDNA);
    }
  }, [costDNA, projectData?.square_footage, projectData?.occupancy_type, projectData?.location]);
  
  const fetchCostDNA = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('token');
      
      const requestData = {
        square_footage: projectData.square_footage || projectData.request_data?.square_footage || 0,
        occupancy_type: projectData.occupancy_type || projectData.request_data?.occupancy_type || 'office',
        location: projectData.location || projectData.request_data?.location || 'Unknown',
        project_classification: projectData.project_classification || projectData.request_data?.project_classification || 'ground_up',
        description: projectData.description || projectData.request_data?.description || '',
        total_cost: projectData.total_cost || 0
      };
      
      console.log('🧬 Fetching Cost DNA with data:', requestData);
      
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      const response = await fetch('/api/v1/cost-dna/generate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      console.log('🧬 Cost DNA response status:', response.status);
      const data = await response.json();
      console.log('🧬 Cost DNA response data:', data);
      
      if (data.success && data.cost_dna) {
        setDnaData(data.cost_dna);
        console.log('✅ Cost DNA data set successfully');
      } else {
        console.error('❌ Cost DNA response unsuccessful:', data);
        setError(data.error || 'Failed to load Cost DNA');
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.error('❌ Cost DNA request timed out');
        setError('Request timed out - API may be unavailable');
      } else {
        console.error('❌ Error fetching Cost DNA:', error);
        setError('Failed to fetch Cost DNA visualization');
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Show loading state
  if (loading) {
    return (
      <div className="cost-dna-container">
        <div className="dna-visualization">
          <h3 className="dna-title">
            <span className="dna-icon">🧬</span>
            Loading Cost DNA Analysis...
          </h3>
        </div>
      </div>
    );
  }
  
  // Show error state if needed
  if (error) {
    console.error('🧬 Cost DNA Error State:', error);
    return (
      <div className="cost-dna-container">
        <div className="dna-visualization">
          <h3 className="dna-title">
            <span className="dna-icon">🧬</span>
            Cost DNA Analysis
          </h3>
          <p style={{ color: '#666', fontSize: '14px' }}>Unable to load cost analysis visualization.</p>
        </div>
      </div>
    );
  }
  
  // If no DNA data yet, show placeholder
  if (!dnaData) {
    console.log('🧬 No DNA data available yet');
    return (
      <div className="cost-dna-container">
        <div className="dna-visualization">
          <h3 className="dna-title">
            <span className="dna-icon">🧬</span>
            Cost DNA Analysis
          </h3>
          <p style={{ color: '#666', fontSize: '14px' }}>Initializing cost analysis...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="cost-dna-container">
      {/* Visual DNA Bar Chart */}
      <div className="dna-visualization">
        <h3 className="dna-title">
          <span className="dna-icon">🧬</span>
          Cost DNA Fingerprint
        </h3>
        <div className="dna-bars">
          {dnaData.visual_dna?.map((item: any, idx: number) => (
            <div 
              key={idx} 
              className="dna-bar-wrapper"
              title={`${item.label}: ${item.value}%`}
            >
              <div 
                className="dna-bar"
                style={{
                  height: `${Math.min(item.value * 3, 100)}px`,
                  backgroundColor: item.color,
                  animationDelay: `${idx * 0.05}s`
                }}
              />
              <span className="dna-bar-label">{item.value.toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Detected Factors */}
      {dnaData.detected_factors?.length > 0 && (
        <div className="detected-factors">
          <h4 className="section-title">✓ What We Detected</h4>
          <div className="factors-list">
            {dnaData.detected_factors?.map((factor: any, idx: number) => (
              <div key={idx} className="factor-item">
                <div className="factor-header">
                  <span className="factor-name">{factor.factor}</span>
                  <span className="factor-impact">{factor.impact_percentage}</span>
                </div>
                <div className="factor-description">{factor.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Confidence Score */}
      <div className="confidence-section">
        <h4 className="section-title">Estimate Confidence</h4>
        <div className="confidence-bar-container">
          <div className="confidence-bar">
            <div 
              className="confidence-fill"
              style={{ 
                width: `${dnaData.confidence_score}%`,
                backgroundColor: dnaData.confidence_score > 80 ? '#10B981' : 
                                dnaData.confidence_score > 60 ? '#F59E0B' : '#EF4444'
              }}
            />
          </div>
          <span className="confidence-score">{dnaData.confidence_score}%</span>
        </div>
        
        <div className="confidence-factors">
          {dnaData.confidence_factors?.map((factor: any, idx: number) => (
            <div key={idx} className={`confidence-factor ${factor.status}`}>
              <span className="factor-icon">
                {factor.status === 'positive' ? '✓' : 
                 factor.status === 'caution' ? '⚠' : 'ℹ'}
              </span>
              <span>{factor.factor}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Why This Price - Expandable */}
      <div className="why-price-section">
        <button 
          className="expand-button"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <span>💡 Why this price?</span>
          <span className={`arrow ${isExpanded ? 'expanded' : ''}`}>▼</span>
        </button>
        
        {isExpanded && (
          <div className="price-breakdown">
            <div className="adjustments-list">
              {dnaData.applied_adjustments?.map((adj: any, idx: number) => (
                <div key={idx} className="adjustment-item">
                  <div className="adjustment-header">
                    <span>{adj.type}</span>
                    <span className="adjustment-impact">{adj.impact_percentage}</span>
                  </div>
                  <div className="adjustment-reason">{adj.reason}</div>
                  <div className="adjustment-source">Source: {adj.source}</div>
                </div>
              ))}
            </div>
            
            <div className="market-context">
              <p className="context-text">
                Data: {dnaData.market_context?.data_version} | 
                Regional Index: {dnaData.market_context?.regional_index}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CostDNADisplay;