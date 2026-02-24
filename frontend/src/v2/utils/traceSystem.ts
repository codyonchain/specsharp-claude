/**
 * Comprehensive tracing system to debug data flow
 */

const DEBUG_TRACE =
  typeof window !== 'undefined' &&
  (window as any).__SPECSHARP_DEBUG_FLAGS__?.includes('trace') === true;

class TraceSystem {
  private traces: any[] = [];
  
  trace(location: string, action: string, data: any) {
    const trace = {
      timestamp: new Date().toISOString(),
      location,
      action,
      data: JSON.parse(JSON.stringify(data || {})), // Deep clone to prevent mutations
      stack: new Error().stack
    };
    
    this.traces.push(trace);
    
    if (DEBUG_TRACE) {
      // Color-coded console output
      const colors: Record<string, string> = {
        'FORM': 'color: blue',
        'API': 'color: green', 
        'STORAGE': 'color: purple',
        'VIEW': 'color: orange',
        'BACKEND': 'color: red'
      };
      
      const prefix = location.split('_')[0];
      console.group(`%c[${prefix}] ${location} - ${action}`, colors[prefix] || 'color: gray');
      console.log('Data:', data);
      console.log('Timestamp:', trace.timestamp);
      console.groupEnd();
    }
    
    // Save to window for debugging
    if (typeof window !== 'undefined') {
      (window as any).__traces = this.traces;
    }
  }
  
  getTraces() {
    return this.traces;
  }
  
  findBreakpoint() {
    if (!DEBUG_TRACE) {
      return;
    }
    console.group('🔍 FINDING BREAKPOINT');
    
    // Check where building_type changes or gets lost
    for (let i = 0; i < this.traces.length; i++) {
      const trace = this.traces[i];
      const buildingType = trace.data?.building_type || 
                          trace.data?.parsed?.building_type ||
                          trace.data?.parsed_input?.building_type ||
                          trace.data?.analysis?.parsed?.building_type ||
                          trace.data?.analysis?.parsed_input?.building_type;
      
      console.log(`Step ${i}: ${trace.location} - Building Type: ${buildingType || 'MISSING'}`);
      
      if (i > 0) {
        const prevTrace = this.traces[i-1];
        const prevBuildingType = prevTrace.data?.building_type || 
                                prevTrace.data?.parsed?.building_type ||
                                prevTrace.data?.parsed_input?.building_type ||
                                prevTrace.data?.analysis?.parsed?.building_type ||
                                prevTrace.data?.analysis?.parsed_input?.building_type;
        
        if (prevBuildingType && !buildingType) {
          console.error(`❌ DATA LOST at ${trace.location}!`);
          console.log('Previous:', prevTrace);
          console.log('Current:', trace);
        }
        
        if (prevBuildingType !== buildingType && buildingType && prevBuildingType) {
          console.warn(`⚠️ DATA CHANGED at ${trace.location}!`);
          console.log(`Changed from ${prevBuildingType} to ${buildingType}`);
        }
      }
    }
    
    console.groupEnd();
  }
  
  clear() {
    this.traces = [];
    if (DEBUG_TRACE) {
      console.log('✅ Traces cleared');
    }
  }
}

export const tracer = new TraceSystem();

// Add to window for console access
if (typeof window !== 'undefined') {
  (window as any).tracer = tracer;
}
