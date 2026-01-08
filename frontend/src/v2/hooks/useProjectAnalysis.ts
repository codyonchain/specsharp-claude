import { useState } from 'react';
import { api } from '../api/client';
import { 
  ProjectAnalysis, 
  CalculationResult, 
  BuildingType, 
  ProjectClass,
  OwnershipType,
  APIError 
} from '../types';

export function useProjectAnalysis() {
  const [analyzing, setAnalyzing] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<ProjectAnalysis | null>(null);
  const [error, setError] = useState<APIError | null>(null);

  const analyzeDescription = async (
    description: string,
    overrides?: {
      squareFootage?: number;
      location?: string;
      finishLevel?: 'standard' | 'premium' | 'luxury';
      projectClass?: 'ground_up' | 'renovation' | 'addition';
      signal?: AbortSignal;
      specialFeatures?: string[];
    }
  ) => {
    if (!description.trim()) {
      setError({ message: 'Please enter a project description' });
      return null;
    }

    try {
      setAnalyzing(true);
      setError(null);
      console.log('Starting analysis for:', description);
      const finishLevel = overrides?.finishLevel
        ? (overrides.finishLevel.charAt(0).toUpperCase() + overrides.finishLevel.slice(1)) as
            'Standard' | 'Premium' | 'Luxury'
        : undefined;
      const analysis = await api.analyzeProject(description, {
        square_footage: overrides?.squareFootage,
        location: overrides?.location,
        finishLevel,
        projectClass: overrides?.projectClass,
        signal: overrides?.signal,
        special_features: overrides?.specialFeatures,
      });
      console.log('Setting result in hook:', analysis);
      setResult(analysis);
      return analysis;
    } catch (err) {
      console.error('Analysis error in hook:', err);
      setError(err as APIError);
      return null;
    } finally {
      setAnalyzing(false);
    }
  };

  const calculateDirect = async (params: {
    building_type: BuildingType;
    subtype: string;
    square_footage: number;
    location: string;
    project_class?: ProjectClass;
    ownership_type?: OwnershipType;
    floors?: number;
    special_features?: string[];
    finishLevel?: 'Standard' | 'Premium' | 'Luxury';
  }) => {
    try {
      setCalculating(true);
      setError(null);
      const finishLevel = params.finishLevel || 'Standard';
      const calculation = await api.calculateProject({
        ...params,
        finishLevel,
      });
      
      // Convert to ProjectAnalysis format
      const analysis: ProjectAnalysis = {
        parsed_input: {
          building_type: params.building_type,
          subtype: params.subtype,
          square_footage: params.square_footage,
          location: params.location,
          project_class: params.project_class || ProjectClass.GROUND_UP,
          floors: params.floors || 1,
          finish_level: finishLevel.toLowerCase(),
          confidence: 1.0
        },
        calculations: calculation,
        confidence: 1.0
      };
      
      setResult(analysis);
      return analysis;
    } catch (err) {
      setError(err as APIError);
      return null;
    } finally {
      setCalculating(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return {
    analyzing,
    calculating,
    result,
    error,
    analyzeDescription,
    calculateDirect,
    reset
  };
}
