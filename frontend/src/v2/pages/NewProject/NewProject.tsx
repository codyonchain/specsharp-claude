import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectAnalysis } from '../../hooks/useProjectAnalysis';
import { api } from '../../api/client';
import { tracer } from '../../utils/traceSystem';
import { formatCurrency, formatNumber } from '../../utils/formatters';
import { BuildingTaxonomy } from '../../../core/buildingTaxonomy';

// Lucide icons
import { 
  Building2, Sparkles, ArrowRight, Check, AlertCircle,
  Calculator, MapPin, Layers, Tag, Loader2, ChevronDown,
  TrendingUp, DollarSign, Clock, Square, FileText,
  Zap, RefreshCw, Save, Building, GraduationCap, Heart,
  Home, Factory, ShoppingBag, Plus, X, Settings, Info
} from 'lucide-react';

export const NewProject: React.FC = () => {
  const navigate = useNavigate();
  const resultsRef = useRef<HTMLDivElement>(null);
  const { analyzing, result, error, analyzeDescription, reset } = useProjectAnalysis();
  
  // Form state
  const [description, setDescription] = useState('');
  const [activeStep, setActiveStep] = useState<'input' | 'analyzing' | 'results'>('input');
  const [saving, setSaving] = useState(false);
  
  // Project configuration state
  const [specialFeatures, setSpecialFeatures] = useState<string[]>([]);
  const [finishLevel, setFinishLevel] = useState<'standard' | 'premium' | 'luxury'>('standard');
  const [projectComplexity, setProjectComplexity] = useState<'ground_up' | 'renovation' | 'addition'>('ground_up');
  
  // NLP detection state
  const [detectedFeatures, setDetectedFeatures] = useState({
    size: false,
    type: false,
    location: false
  });
  
  // Monitor input for NLP detection
  useEffect(() => {
    const input = description.toLowerCase();
    setDetectedFeatures({
      size: /\d+[\s,]*(?:sf|square|feet|unit|key|bed|room)/i.test(description),
      type: /(apartment|office|hospital|school|retail|industrial|hotel|restaurant|warehouse|medical|clinic|surgery|emergency|distribution|strip\s*mall)/i.test(input),
      location: /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s*[A-Z]{2}\b/.test(description) || 
                /(nashville|memphis|austin|atlanta|denver|dallas|franklin|murfreesboro)/i.test(input)
    });
  }, [description]);
  
  // Example prompts with better structure
  const examplePrompts = [
    { 
      icon: <Heart className="h-6 w-6" />, 
      text: '200,000 SF hospital with emergency department in Nashville', 
      highlights: ['200,000 SF', 'hospital', 'emergency department', 'Nashville'],
      type: 'healthcare',
      color: 'text-red-600 bg-red-50'
    },
    { 
      icon: <Building2 className="h-6 w-6" />, 
      text: '95,000 SF Class A office building with structured parking in Memphis', 
      highlights: ['95,000 SF', 'Class A office', 'structured parking', 'Memphis'],
      type: 'commercial',
      color: 'text-blue-600 bg-blue-50'
    },
    { 
      icon: <Home className="h-6 w-6" />, 
      text: '300-unit luxury apartment complex with amenities and garage in Austin', 
      highlights: ['300-unit', 'luxury apartment', 'amenities', 'garage', 'Austin'],
      type: 'residential',
      color: 'text-purple-600 bg-purple-50'
    },
    { 
      icon: <Factory className="h-6 w-6" />, 
      text: '150,000 SF distribution center with 30 loading docks in Atlanta', 
      highlights: ['150,000 SF', 'distribution center', '30 loading docks', 'Atlanta'],
      type: 'industrial',
      color: 'text-gray-600 bg-gray-50'
    },
    { 
      icon: <ShoppingBag className="h-6 w-6" />, 
      text: '25,000 SF strip mall with 5 retail spaces in suburban Dallas', 
      highlights: ['25,000 SF', 'strip mall', '5 retail spaces', 'Dallas'],
      type: 'retail',
      color: 'text-orange-600 bg-orange-50'
    },
    { 
      icon: <GraduationCap className="h-6 w-6" />, 
      text: '75,000 SF elementary school for 500 students in Denver', 
      highlights: ['75,000 SF', 'elementary school', '500 students', 'Denver'],
      type: 'educational',
      color: 'text-green-600 bg-green-50'
    }
  ];
  
  // Special features by building type
  const getAvailableFeatures = (buildingType: string) => {
    const features: Record<string, Array<{id: string, name: string, cost: number, description: string}>> = {
      healthcare: [
        { id: 'emergency', name: 'Emergency Department', cost: 10000000, description: 'Full 24/7 emergency room with trauma center' },
        { id: 'imaging', name: 'Imaging Center', cost: 5000000, description: 'MRI, CT, X-ray equipment and rooms' },
        { id: 'surgery', name: 'Surgery Center', cost: 8000000, description: 'Operating rooms and recovery areas' },
        { id: 'icu', name: 'ICU Unit', cost: 6000000, description: 'Intensive care unit with specialized equipment' },
        { id: 'lab', name: 'Laboratory', cost: 3000000, description: 'Full medical testing laboratory' }
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
      ]
    };
    
    return features[buildingType] || [];
  };
  
  // Parse description to detect features automatically
  const parseDescription = (desc: string) => {
    const lower = desc.toLowerCase();
    
    // Detect special features in description
    const detectedFeatures: string[] = [];
    if (lower.includes('emergency')) detectedFeatures.push('emergency');
    if (lower.includes('imaging')) detectedFeatures.push('imaging');
    if (lower.includes('gymnasium') || lower.includes('gym')) detectedFeatures.push('gymnasium');
    if (lower.includes('parking garage') || lower.includes('garage')) detectedFeatures.push('parking_garage');
    if (lower.includes('pool')) detectedFeatures.push('pool');
    if (lower.includes('cafeteria')) detectedFeatures.push('cafeteria');
    if (lower.includes('loading dock')) detectedFeatures.push('loading_docks');
    if (lower.includes('cold storage')) detectedFeatures.push('cold_storage');
    if (lower.includes('food court')) detectedFeatures.push('food_court');
    
    // Detect finish level
    let detectedFinish: 'standard' | 'premium' | 'luxury' = 'standard';
    if (lower.includes('luxury') || lower.includes('high-end')) detectedFinish = 'luxury';
    else if (lower.includes('premium') || lower.includes('class a')) detectedFinish = 'premium';
    
    // Detect project complexity
    let detectedComplexity: 'ground_up' | 'renovation' | 'addition' = 'ground_up';
    if (lower.includes('renovation') || lower.includes('renovate') || lower.includes('remodel')) detectedComplexity = 'renovation';
    else if (lower.includes('addition') || lower.includes('expansion') || lower.includes('expand')) detectedComplexity = 'addition';
    
    return {
      specialFeatures: detectedFeatures,
      finishLevel: detectedFinish,
      projectComplexity: detectedComplexity
    };
  };
  
  // Calculate total cost including features
  const calculateTotalWithFeatures = () => {
    if (!result) return 0;
    
    let total = result.calculations?.total_cost || 0;
    
    // Add special features costs
    const buildingType = result.parsed_input?.building_type || 'commercial';
    const availableFeatures = getAvailableFeatures(buildingType);
    specialFeatures.forEach(featureId => {
      const feature = availableFeatures.find(f => f.id === featureId);
      if (feature) total += feature.cost;
    });
    
    // Apply finish level multiplier
    const finishMultipliers = {
      standard: 1.0,
      premium: 1.15,
      luxury: 1.35
    };
    total *= finishMultipliers[finishLevel];
    
    // Apply complexity multiplier
    const complexityMultipliers = {
      ground_up: 1.0,
      renovation: 1.35,
      addition: 1.15
    };
    total *= complexityMultipliers[projectComplexity];
    
    return total;
  };
  
  const handleExampleClick = (example: any) => {
    setDescription(example.text);
    // Reset configuration when using example
    setSpecialFeatures([]);
    setFinishLevel('standard');
    setProjectComplexity('ground_up');
    // Auto-scroll to show the form is filled
    window.scrollTo({ top: 200, behavior: 'smooth' });
  };
  
  const handleAnalyze = async () => {
    if (!description.trim()) return;
    
    setActiveStep('analyzing');
    tracer.trace('ANALYZE_START', 'Starting analysis', { description });
    
    const analysis = await analyzeDescription(description);
    
    if (analysis) {
      // Auto-detect features from description
      const parsed = parseDescription(description);
      setSpecialFeatures(parsed.specialFeatures);
      setFinishLevel(parsed.finishLevel);
      setProjectComplexity(parsed.projectComplexity);
      
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
  
  const handleSaveProject = async () => {
    if (!result) return;
    
    setSaving(true);
    tracer.trace('SAVE_START', 'Saving project', result);
    
    try {
      const projectData = {
        name: description.slice(0, 100),
        description: description,
        analysis: result,
        user_id: 'user_1', // Would come from auth
        is_shared: false,
        createdAt: new Date().toISOString()
      };
      
      const project = await api.saveProject(projectData);
      tracer.trace('SAVE_SUCCESS', 'Project saved', { id: project.id });
      
      // Navigate to project view
      navigate(`/project/${project.id}`);
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
    setActiveStep('input');
    setSpecialFeatures([]);
    setFinishLevel('standard');
    setProjectComplexity('ground_up');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  // Get display-friendly names for building types
  const getDisplayName = (type: string, subtype: string) => {
    const typeDisplay = BuildingTaxonomy.getDisplayName(type);
    
    // Format subtype for display
    const subtypeDisplay = subtype
      ?.replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
    
    return `${typeDisplay} - ${subtypeDisplay}`;
  };

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
              disabled={!description || analyzing}
              className={`
                px-8 py-3 rounded-lg font-medium flex items-center gap-3 transition transform
                ${!description || analyzing 
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
                          onClick={() => setProjectComplexity(type)}
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
                              {type === 'addition' && '1.15x'}
                              {type === 'renovation' && '1.35x'}
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Finish Level */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-3">Finish Level</p>
                    <div className="grid grid-cols-3 gap-2">
                      {(['standard', 'premium', 'luxury'] as const).map(level => (
                        <button
                          key={level}
                          onClick={() => setFinishLevel(level)}
                          className={`px-3 py-3 rounded-lg text-sm font-medium transition ${
                            finishLevel === level
                              ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-500'
                              : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                          }`}
                        >
                          <div className="text-center">
                            <div className="font-semibold capitalize">{level}</div>
                            <div className="text-xs mt-1 opacity-75">
                              {level === 'standard' && '1.0x'}
                              {level === 'premium' && '1.15x'}
                              {level === 'luxury' && '1.35x'}
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Right Column - Special Features */}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-3">Special Features</p>
                  <div className="space-y-2 max-h-80 overflow-y-auto border border-gray-100 rounded-lg p-3">
                    {result.parsed_input && getAvailableFeatures(result.parsed_input.building_type).length > 0 ? (
                      getAvailableFeatures(result.parsed_input.building_type).map(feature => (
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
                                +{formatCurrency(feature.cost)}
                              </span>
                            </div>
                            <span className="text-xs text-gray-500">{feature.description}</span>
                          </div>
                        </label>
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-400">
                        <Settings className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No special features available for this building type</p>
                      </div>
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
                      <p className="text-blue-100 text-sm mb-1">Base Cost</p>
                      <p className="text-xl font-bold">
                        {formatCurrency(result.calculations.total_cost)}
                      </p>
                    </div>
                    {specialFeatures.length > 0 && (
                      <div>
                        <p className="text-blue-100 text-sm mb-1">+ Features</p>
                        <p className="text-xl font-bold">
                          {formatCurrency(
                            specialFeatures.reduce((sum, fId) => {
                              const buildingType = result.parsed_input?.building_type || 'commercial';
                              const f = getAvailableFeatures(buildingType).find(feat => feat.id === fId);
                              return sum + (f?.cost || 0);
                            }, 0)
                          )}
                        </p>
                      </div>
                    )}
                    <div>
                      <p className="text-blue-100 text-sm mb-1">Multipliers</p>
                      <p className="text-xl font-bold">
                        {(finishLevel === 'standard' ? 1.0 : finishLevel === 'premium' ? 1.15 : 1.35) * 
                         (projectComplexity === 'ground_up' ? 1.0 : projectComplexity === 'addition' ? 1.15 : 1.35)}x
                      </p>
                    </div>
                    <div>
                      <p className="text-blue-100 text-sm mb-1">Total Project Cost</p>
                      <p className="text-2xl font-bold">
                        {formatCurrency(calculateTotalWithFeatures())}
                      </p>
                      <p className="text-blue-200 text-sm mt-1">
                        {formatCurrency(calculateTotalWithFeatures() / (result.parsed_input?.square_footage || 1))}/SF
                      </p>
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