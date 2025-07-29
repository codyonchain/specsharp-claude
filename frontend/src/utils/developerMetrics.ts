export interface DeveloperMetrics {
  label: string;
  value: number;
  unit: string;
  description?: string;
}

export function calculateDeveloperMetrics(
  project: any
): DeveloperMetrics[] {
  const metrics: DeveloperMetrics[] = [];
  const totalCost = project.total_cost || 0;
  const squareFootage = project.square_footage || 0;
  const requestData = project.scope_data?.request_data || project.request_data || {};
  const buildingType = requestData.occupancy_type || requestData.building_type || project.building_type || '';
  
  // Always show cost per square foot
  if (squareFootage > 0) {
    metrics.push({
      label: 'Cost per SF',
      value: totalCost / squareFootage,
      unit: '/SF',
      description: 'Cost per square foot'
    });
  }
  
  // Building-specific metrics
  switch (buildingType.toLowerCase()) {
    case 'hotel':
    case 'hospitality':
      const hotelRooms = extractNumber(requestData.special_requirements, /(\d+)\s*(?:rooms?|guest\s*rooms?)/i) || 
                        Math.floor(squareFootage / 400); // Estimate 400 SF per room
      if (hotelRooms > 0) {
        metrics.push({
          label: 'Cost per Room',
          value: totalCost / hotelRooms,
          unit: '/room',
          description: `Based on ${hotelRooms} rooms`
        });
      }
      break;
      
    case 'medical':
    case 'hospital':
    case 'healthcare':
      const beds = extractNumber(requestData.special_requirements, /(\d+)\s*(?:beds?|patient\s*beds?)/i) || 
                   Math.floor(squareFootage / 800); // Estimate 800 SF per bed
      if (beds > 0) {
        metrics.push({
          label: 'Cost per Bed',
          value: totalCost / beds,
          unit: '/bed',
          description: `Based on ${beds} beds`
        });
      }
      break;
      
    case 'office':
    case 'commercial':
      // Calculate RSF (Rentable Square Feet) - typically 85-90% of gross
      const rsf = squareFootage * 0.87;
      metrics.push({
        label: 'Cost per RSF',
        value: totalCost / rsf,
        unit: '/RSF',
        description: 'Cost per rentable square foot'
      });
      
      // Estimate desks based on 150 SF per person
      const desks = Math.floor(rsf / 150);
      if (desks > 0) {
        metrics.push({
          label: 'Cost per Desk',
          value: totalCost / desks,
          unit: '/desk',
          description: `Based on ${desks} workstations`
        });
      }
      break;
      
    case 'multifamily':
    case 'multi-family':
    case 'apartment':
    case 'residential':
      const units = extractNumber(requestData.special_requirements, /(\d+)\s*(?:units?|apartments?)/i) || 
                    Math.floor(squareFootage / 850); // Estimate 850 SF per unit
      if (units > 0) {
        metrics.push({
          label: 'Cost per Unit',
          value: totalCost / units,
          unit: '/unit',
          description: `Based on ${units} units`
        });
      }
      break;
      
    case 'school':
    case 'education':
    case 'educational':
      const students = extractNumber(requestData.special_requirements, /(\d+)\s*(?:students?|pupils?)/i) || 
                       Math.floor(squareFootage / 100); // Estimate 100 SF per student
      if (students > 0) {
        metrics.push({
          label: 'Cost per Student',
          value: totalCost / students,
          unit: '/student',
          description: `Based on ${students} student capacity`
        });
      }
      break;
      
    case 'retail':
      // Show cost per leasable SF
      const leasableSF = squareFootage * 0.85;
      metrics.push({
        label: 'Cost per Leasable SF',
        value: totalCost / leasableSF,
        unit: '/LSF',
        description: 'Cost per leasable square foot'
      });
      break;
      
    case 'warehouse':
    case 'industrial':
      // Show cost per clear height foot
      const clearHeight = extractNumber(requestData.special_requirements, /(\d+)\s*(?:ft|foot|feet)\s*clear/i) || 
                         requestData.ceiling_height || 24;
      metrics.push({
        label: 'Cost per Clear Height',
        value: totalCost / squareFootage / clearHeight,
        unit: '/SF/ft',
        description: `Based on ${clearHeight}ft clear height`
      });
      
      // Dock doors if industrial
      const dockDoors = extractNumber(requestData.special_requirements, /(\d+)\s*dock\s*doors?/i);
      if (dockDoors > 0) {
        metrics.push({
          label: 'Cost per Dock Door',
          value: totalCost / dockDoors,
          unit: '/door',
          description: `Based on ${dockDoors} dock doors`
        });
      }
      break;
      
    case 'restaurant':
    case 'restaurant - full service':
    case 'restaurant - quick service':
    case 'food service':
    case 'dining':
      // Restaurant metrics
      const seats = extractNumber(requestData.special_requirements, /(\d+)\s*(?:seats?|diners?|covers?)/i) || 
                    Math.floor(squareFootage / 15); // Industry standard: 15 SF per seat
      if (seats > 0) {
        metrics.push({
          label: 'Cost per Seat',
          value: totalCost / seats,
          unit: '/seat',
          description: `Based on ${seats} seats`
        });
      }
      
      // Kitchen size (typically 30-40% of total for full service)
      const kitchenSF = squareFootage * 0.35;
      metrics.push({
        label: 'Kitchen Cost',
        value: (totalCost * 0.45) / kitchenSF, // Kitchen is ~45% of restaurant cost
        unit: '/SF',
        description: 'Estimated kitchen cost per SF'
      });
      
      // Annual revenue potential (industry avg $150-300/SF/year)
      const revenuePerSF = 225; // Mid-range estimate
      const annualRevenue = squareFootage * revenuePerSF;
      const roi = (annualRevenue / totalCost) * 100;
      metrics.push({
        label: 'First Year ROI',
        value: roi,
        unit: '%',
        description: 'Based on $225/SF annual revenue'
      });
      break;
  }
  
  return metrics;
}

function extractNumber(text: string | undefined, pattern: RegExp): number | null {
  if (!text) return null;
  const match = text.match(pattern);
  return match ? parseInt(match[1]) : null;
}

export function formatMetricValue(value: number): string {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(2)}M`;
  } else if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`;
  } else {
    return `$${value.toFixed(0)}`;
  }
}