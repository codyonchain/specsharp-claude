import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Zap, ArrowRight, CheckCircle, Sparkles } from 'lucide-react';
import { scopeService } from '../services/api';
import { formatCurrency, formatCurrencyPerSF } from '../utils/formatters';
import './OnboardingFlow.css';

interface OnboardingExample {
  id: number;
  title: string;
  description: string;
  prefilledData: {
    naturalLanguageInput: string;
    project_name: string;
    square_footage: number;
    location: string;
    building_type: string;
    num_floors?: number;
  };
  estimatedTimeSaved: number; // in hours
}

const ONBOARDING_EXAMPLES: OnboardingExample[] = [
  {
    id: 1,
    title: "Healthcare Facility",
    description: "See how quickly we can estimate a large hospital project",
    prefilledData: {
      naturalLanguageInput: "150,000 sf hospital in Dallas",
      project_name: "Dallas Medical Center",
      square_footage: 150000,
      location: "Dallas, TX",
      building_type: "healthcare",
      num_floors: 5
    },
    estimatedTimeSaved: 3
  },
  {
    id: 2,
    title: "Office Building",
    description: "Watch us calculate costs for a mid-rise office",
    prefilledData: {
      naturalLanguageInput: "45,000 sf office building in Houston",
      project_name: "Houston Corporate Plaza",
      square_footage: 45000,
      location: "Houston, TX",
      building_type: "office",
      num_floors: 4
    },
    estimatedTimeSaved: 3
  },
  {
    id: 3,
    title: "Your Own Project",
    description: "Now try creating your own estimate",
    prefilledData: {
      naturalLanguageInput: "",
      project_name: "",
      square_footage: 0,
      location: "",
      building_type: "",
    },
    estimatedTimeSaved: 3
  }
];

interface OnboardingFlowProps {
  onComplete: () => void;
  currentEstimateCount: number;
}

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete, currentEstimateCount }) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [totalTimeSaved, setTotalTimeSaved] = useState(0);
  const [generationTime, setGenerationTime] = useState<number>(0);
  const [naturalLanguageInput, setNaturalLanguageInput] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [lastGeneratedProject, setLastGeneratedProject] = useState<any>(null);

  const currentExample = ONBOARDING_EXAMPLES[currentStep];
  const isLastStep = currentStep === ONBOARDING_EXAMPLES.length - 1;
  const isCustomStep = currentStep === 2;

  useEffect(() => {
    // Prefill the input for guided examples
    if (!isCustomStep && currentExample) {
      setNaturalLanguageInput(currentExample.prefilledData.naturalLanguageInput);
    } else {
      setNaturalLanguageInput('');
    }
  }, [currentStep, isCustomStep, currentExample]);

  const handleGenerateEstimate = async () => {
    if (isCustomStep && !naturalLanguageInput.trim()) {
      alert('Please enter a project description');
      return;
    }

    setIsGenerating(true);
    const startTime = Date.now();

    try {
      // Parse the input or use prefilled data
      let requestData;
      
      if (isCustomStep) {
        // Parse custom input
        const parsed = parseNaturalLanguageInput(naturalLanguageInput);
        requestData = {
          project_name: parsed.project_name || `Custom Project ${currentEstimateCount + 1}`,
          project_type: 'commercial' as const,
          square_footage: parsed.square_footage || 50000,
          location: parsed.location || 'United States',
          occupancy_type: parsed.occupancy_type || 'office',
          num_floors: parsed.num_floors || 1,
          special_requirements: naturalLanguageInput,
          finish_level: 'standard',
          finishLevel: 'Standard'
        };
      } else {
        // Use prefilled data
        requestData = {
          project_name: currentExample.prefilledData.project_name,
          project_type: 'commercial' as const,
          square_footage: currentExample.prefilledData.square_footage,
          location: currentExample.prefilledData.location,
          occupancy_type: currentExample.prefilledData.building_type,
          num_floors: currentExample.prefilledData.num_floors || 1,
          special_requirements: currentExample.prefilledData.naturalLanguageInput,
          finish_level: 'standard',
          finishLevel: 'Standard'
        };
      }

      const response = await scopeService.generate(requestData);
      
      const endTime = Date.now();
      const timeInSeconds = (endTime - startTime) / 1000;
      setGenerationTime(timeInSeconds);
      
      // Add time saved
      const timeSaved = currentExample.estimatedTimeSaved;
      setTotalTimeSaved(prev => prev + timeSaved);
      
      // Mark step as completed
      setCompletedSteps(prev => [...prev, currentStep]);
      
      // Store the generated project
      setLastGeneratedProject(response);
      setShowResults(true);
      
    } catch (error) {
      console.error('Failed to generate estimate:', error);
      alert('Failed to generate estimate. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const parseNaturalLanguageInput = (input: string): any => {
    const result: any = {};
    
    // Parse square footage
    const sqftMatch = input.match(/(\d+,?\d*)\s*(k|thousand|sf|sq\.?\s*ft\.?|square\s*feet)/i);
    if (sqftMatch) {
      let sqft = parseInt(sqftMatch[1].replace(/,/g, ''));
      if (sqftMatch[2].toLowerCase() === 'k' || sqftMatch[2].toLowerCase() === 'thousand') {
        sqft *= 1000;
      }
      result.square_footage = sqft;
    }
    
    // Parse location
    const locationMatch = input.match(/in\s+([A-Za-z\s,]+?)(?:\s+|$)/i);
    if (locationMatch) {
      result.location = locationMatch[1].trim();
    }
    
    // Parse building type
    const buildingTypes = ['office', 'hospital', 'school', 'warehouse', 'retail', 'restaurant', 'residential'];
    for (const type of buildingTypes) {
      if (input.toLowerCase().includes(type)) {
        result.occupancy_type = type === 'hospital' ? 'healthcare' : type;
        break;
      }
    }
    
    // Parse floors
    const floorsMatch = input.match(/(\d+)\s*(?:story|stories|floor|floors)/i);
    if (floorsMatch) {
      result.num_floors = parseInt(floorsMatch[1]);
    }
    
    return result;
  };

  const handleContinue = () => {
    setShowResults(false);
    
    if (currentStep < ONBOARDING_EXAMPLES.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Onboarding complete
      onComplete();
    }
  };

  const handleViewProject = () => {
    if (lastGeneratedProject) {
      navigate(`/project/${lastGeneratedProject.project_id}`);
    }
  };

  return (
    <div className="onboarding-flow">
      <div className="onboarding-container">
        {/* Progress indicator */}
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${((currentStep + 1) / ONBOARDING_EXAMPLES.length) * 100}%` }}
            />
          </div>
          <div className="progress-text">
            Example {currentStep + 1} of {ONBOARDING_EXAMPLES.length}
          </div>
        </div>

        {/* Main content */}
        {!showResults ? (
          <div className="onboarding-content">
            <div className="onboarding-header">
              <h1>
                {currentStep === 0 
                  ? "Let's Create 3 Estimates in 2 Minutes!" 
                  : isCustomStep 
                    ? "Now It's Your Turn!" 
                    : "Let's Continue!"}
              </h1>
              <p className="subtitle">
                {currentStep === 0 
                  ? "Watch how SpecSharp saves hours on every estimate" 
                  : isCustomStep
                    ? "Create your own estimate - anything you can imagine!"
                    : "See how fast we can estimate different project types"}
              </p>
            </div>

            <div className="example-card">
              <div className="example-header">
                <h2>{currentExample.title}</h2>
                <p>{currentExample.description}</p>
              </div>

              <div className="input-section">
                <label>Project Description</label>
                <textarea
                  value={naturalLanguageInput}
                  onChange={(e) => setNaturalLanguageInput(e.target.value)}
                  placeholder={isCustomStep ? "Try: 75,000 sf retail center in Phoenix with 3 floors" : ""}
                  rows={4}
                  className="natural-input"
                  disabled={!isCustomStep}
                />
                {!isCustomStep && (
                  <div className="prefilled-indicator">
                    <Sparkles size={16} />
                    Pre-filled example
                  </div>
                )}
              </div>

              <button 
                className="generate-btn"
                onClick={handleGenerateEstimate}
                disabled={isGenerating || (isCustomStep && !naturalLanguageInput.trim())}
              >
                {isGenerating ? (
                  <>
                    <div className="spinner" />
                    Generating Estimate...
                  </>
                ) : (
                  <>
                    <Zap size={20} />
                    Generate Estimate
                  </>
                )}
              </button>
            </div>

            {/* Time saved indicator */}
            {totalTimeSaved > 0 && (
              <div className="time-saved-indicator">
                <Clock size={24} />
                <div>
                  <div className="time-saved-value">{totalTimeSaved} hours saved so far!</div>
                  <div className="time-saved-label">Compared to manual estimation</div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="results-content">
            <div className="success-animation">
              <CheckCircle size={80} className="success-icon" />
            </div>

            <h2>Estimate Generated in {generationTime.toFixed(1)} Seconds!</h2>
            
            <div className="results-summary">
              <div className="result-card">
                <h3>{lastGeneratedProject?.project_name}</h3>
                <div className="result-metrics">
                  <div className="metric">
                    <span className="metric-label">Total Cost</span>
                    <span className="metric-value">
                      {formatCurrency(lastGeneratedProject?.total_cost || 0)}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Cost per Sq Ft</span>
                    <span className="metric-value">
                      {formatCurrencyPerSF(lastGeneratedProject?.request_data?.square_footage ? lastGeneratedProject.total_cost / lastGeneratedProject.request_data.square_footage : 0)}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Time Saved</span>
                    <span className="metric-value highlight">
                      {currentExample.estimatedTimeSaved} hours
                    </span>
                  </div>
                </div>
              </div>

              <div className="time-comparison">
                <div className="comparison-item manual">
                  <Clock size={20} />
                  <span>Manual: ~3 hours</span>
                </div>
                <ArrowRight size={24} />
                <div className="comparison-item specsharp">
                  <Zap size={20} />
                  <span>SpecSharp: {generationTime.toFixed(1)}s</span>
                </div>
              </div>
            </div>

            <div className="action-buttons">
              <button className="secondary-btn" onClick={handleViewProject}>
                View Full Details
              </button>
              <button className="primary-btn" onClick={handleContinue}>
                {isLastStep ? 'Complete Onboarding' : 'Continue to Next Example'}
                <ArrowRight size={20} />
              </button>
            </div>

            {/* Cumulative savings */}
            <div className="cumulative-savings">
              <h3>Total Time Saved: {totalTimeSaved} Hours</h3>
              <p>That's ${totalTimeSaved * 75} worth of time at $75/hour!</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OnboardingFlow;
