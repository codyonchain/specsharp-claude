interface SchedulingRules {
  baseDuration: Record<string, number>;
  sizeMultipliers: Record<string, number>;
  complexityMultipliers: Record<string, number>;
  tradeSequence: Record<string, TradePhase>;
}

interface TradePhase {
  startPercent: number;
  durationPercent: number;
  color: string;
}

interface ProjectData {
  buildingType: string;
  squareFootage: number;
  projectClassification: string;
  tradeCosts: Record<string, number>;
}

interface ScheduleItem {
  phase: string;
  startMonth: number;
  endMonth: number;
  duration: number;
  cost: number;
  color: string;
  percentOfTimeline: number;
}

interface ProjectSchedule {
  totalDuration: number;
  schedule: ScheduleItem[];
  criticalPath: string[];
  startDate: Date;
  endDate: Date;
}

const SCHEDULING_RULES: SchedulingRules = {
  // Base duration by project type (in months)
  baseDuration: {
    healthcare: 18,
    office: 12,
    retail: 8,
    multifamily: 15,
    educational: 14,
    education: 14, // alias for educational
    hospitality: 13,
    industrial: 10,
    warehouse: 8,
    restaurant: 6,
    mixed_use: 14
  },
  
  // Size adjustments
  sizeMultipliers: {
    under50k: 0.8,
    '50k-100k': 1.0,
    '100k-200k': 1.2,
    '200k-500k': 1.5,
    over500k: 1.8
  },
  
  // Complexity adjustments
  complexityMultipliers: {
    ground_up: 1.0,
    tenant_improvement: 0.6,
    addition: 0.8,
    renovation: 1.3
  },
  
  // Trade sequence percentages (of total duration)
  tradeSequence: {
    site_foundation: {
      startPercent: 0,
      durationPercent: 0.17,
      color: '#3B82F6' // blue
    },
    structural: {
      startPercent: 0.11,
      durationPercent: 0.39,
      color: '#10B981' // green
    },
    exterior_envelope: {
      startPercent: 0.28,
      durationPercent: 0.33,
      color: '#F59E0B' // orange
    },
    mep_rough: {
      startPercent: 0.33,
      durationPercent: 0.33,
      color: '#8B5CF6' // purple
    },
    interior_finishes: {
      startPercent: 0.56,
      durationPercent: 0.44,
      color: '#EC4899' // pink
    },
    mep_finishes: {
      startPercent: 0.67,
      durationPercent: 0.33,
      color: '#06B6D4' // cyan
    }
  }
};

export function calculateProjectSchedule(projectData: ProjectData): ProjectSchedule {
  const { 
    buildingType, 
    squareFootage, 
    projectClassification,
    tradeCosts 
  } = projectData;
  
  // 1. Calculate total duration
  const baseDuration = SCHEDULING_RULES.baseDuration[buildingType] || 12;
  
  // Apply size multiplier
  let sizeMultiplier = 1.0;
  if (squareFootage < 50000) sizeMultiplier = 0.8;
  else if (squareFootage < 100000) sizeMultiplier = 1.0;
  else if (squareFootage < 200000) sizeMultiplier = 1.2;
  else if (squareFootage < 500000) sizeMultiplier = 1.5;
  else sizeMultiplier = 1.8;
  
  // Apply complexity multiplier
  const complexityMultiplier = SCHEDULING_RULES.complexityMultipliers[projectClassification] || 1.0;
  
  // Calculate total project duration
  const totalDuration = Math.round(baseDuration * sizeMultiplier * complexityMultiplier);
  
  // 2. Generate trade schedule
  const schedule: ScheduleItem[] = [];
  
  // For each trade phase, calculate timing
  Object.entries(SCHEDULING_RULES.tradeSequence).forEach(([phase, config]) => {
    const startMonth = Math.round(totalDuration * config.startPercent);
    const duration = Math.round(totalDuration * config.durationPercent);
    const endMonth = Math.min(startMonth + duration, totalDuration);
    
    // Find corresponding cost
    let phaseCost = 0;
    if (phase === 'site_foundation') {
      phaseCost = (tradeCosts.structural || 0) * 0.15; // Foundation is ~15% of structural
    } else if (phase === 'structural') {
      phaseCost = (tradeCosts.structural || 0) * 0.85; // Rest of structural
    } else if (phase === 'exterior_envelope') {
      phaseCost = (tradeCosts.finishes || 0) * 0.3; // Part of finishes
    } else if (phase === 'mep_rough') {
      phaseCost = ((tradeCosts.mechanical || 0) + (tradeCosts.plumbing || 0)) * 0.6;
    } else if (phase === 'interior_finishes') {
      phaseCost = (tradeCosts.finishes || 0) * 0.7;
    } else if (phase === 'mep_finishes') {
      phaseCost = ((tradeCosts.mechanical || 0) + (tradeCosts.electrical || 0) + (tradeCosts.plumbing || 0)) * 0.4;
    }
    
    // Format phase name
    const phaseName = phase
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    schedule.push({
      phase: phaseName,
      startMonth: startMonth + 1, // Convert to 1-based
      endMonth: endMonth,
      duration: endMonth - startMonth,
      cost: phaseCost,
      color: config.color,
      percentOfTimeline: ((endMonth - startMonth) / totalDuration) * 100
    });
  });
  
  // 3. Identify critical path
  const criticalPath = ['Site Foundation', 'Structural', 'MEP Rough', 'Interior Finishes'];
  
  return {
    totalDuration,
    schedule,
    criticalPath,
    startDate: new Date(), // Could be passed in
    endDate: new Date(Date.now() + totalDuration * 30 * 24 * 60 * 60 * 1000) // Rough calculation
  };
}

// Helper function to get long-lead items by building type
export function getLongLeadItems(buildingType: string): string | null {
  const longLeadWarnings: Record<string, string> = {
    healthcare: '⚠️ Long-lead items: Medical equipment and AHUs require 16-20 week lead time. Order by Month 3.',
    hospital: '⚠️ Long-lead items: MRI/CT equipment and medical gas systems require 20-24 week lead time.',
    education: '⚠️ Long-lead items: Kitchen equipment and auditorium systems require 12-16 week lead time.',
    hospitality: '⚠️ Long-lead items: FF&E and kitchen equipment require 14-18 week lead time.',
    office: '⚠️ Long-lead items: Elevators and curtain wall systems require 12-16 week lead time.'
  };
  
  return longLeadWarnings[buildingType] || null;
}