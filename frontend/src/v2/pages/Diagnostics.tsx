import React, { useState, useEffect } from 'react';
import { tracer } from '../utils/traceSystem';

export const Diagnostics: React.FC = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [traces, setTraces] = useState<any[]>([]);
  
  useEffect(() => {
    // Load all projects
    const stored = localStorage.getItem('specsharp_projects');
    if (stored) {
      setProjects(JSON.parse(stored));
    }
    
    // Get traces
    setTraces(tracer.getTraces());
  }, []);
  
  const runDiagnostics = () => {
    console.group('🏥 FULL DIAGNOSTICS');
    
    // Check each project
    projects.forEach((project, idx) => {
      console.group(`Project ${idx + 1}: ${project.id}`);
      
      // Check for data presence
      const checks = {
        'Has ID': !!project.id,
        'Has Description': !!project.description,
        'Has Analysis': !!project.analysis,
        'Has parsed_input': !!project.analysis?.parsed_input,
        'Has Building Type': !!project.analysis?.parsed_input?.building_type,
        'Has Building Subtype': !!project.analysis?.parsed_input?.building_subtype,
        'Has Square Footage': !!project.analysis?.parsed_input?.square_footage,
        'Has Calculations': !!project.analysis?.calculations,
        'Has Totals': !!project.analysis?.calculations?.totals,
        'Has Trade Breakdown': !!project.analysis?.calculations?.trade_breakdown,
        'Has Soft Costs': !!project.analysis?.calculations?.soft_costs
      };
      
      Object.entries(checks).forEach(([check, passed]) => {
        if (!passed) {
          console.error(`❌ ${check}`);
        } else {
          console.log(`✅ ${check}`);
        }
      });
      
      // Show actual values
      console.log('Building Type:', project.analysis?.parsed_input?.building_type || 'MISSING');
      console.log('Subtype:', project.analysis?.parsed_input?.building_subtype || 'MISSING');
      console.log('Square Footage:', project.analysis?.parsed_input?.square_footage || 'MISSING');
      console.log('Total Cost:', project.analysis?.calculations?.totals?.total_project_cost || 'MISSING');
      
      console.groupEnd();
    });
    
    // Find breakpoint
    tracer.findBreakpoint();
    
    console.groupEnd();
  };
  
  const clearStorage = () => {
    if (window.confirm('This will delete all projects. Are you sure?')) {
      localStorage.removeItem('specsharp_projects');
      setProjects([]);
      tracer.clear();
      setTraces([]);
      console.log('✅ Storage cleared');
    }
  };
  
  const refreshTraces = () => {
    setTraces(tracer.getTraces());
  };
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">System Diagnostics</h1>
      
      <div className="flex gap-4 mb-6">
        <button 
          onClick={runDiagnostics}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Run Full Diagnostics
        </button>
        <button 
          onClick={refreshTraces}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Refresh Traces
        </button>
        <button 
          onClick={clearStorage}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Clear All Storage
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Projects in Storage ({projects.length})</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {projects.map((project, idx) => (
              <div key={idx} className="p-3 bg-gray-100 rounded">
                <p className="font-mono text-xs mb-1">ID: {project.id}</p>
                <p className="text-sm font-semibold">{project.description?.slice(0, 50)}...</p>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">Type:</span>{' '}
                    <span className={project.analysis?.parsed_input?.building_type ? 'text-green-600' : 'text-red-600'}>
                      {project.analysis?.parsed_input?.building_type || 'MISSING'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Subtype:</span>{' '}
                    <span className={project.analysis?.parsed_input?.building_subtype ? 'text-green-600' : 'text-red-600'}>
                      {project.analysis?.parsed_input?.building_subtype || 'MISSING'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">SF:</span>{' '}
                    <span className={project.analysis?.parsed_input?.square_footage ? 'text-green-600' : 'text-red-600'}>
                      {project.analysis?.parsed_input?.square_footage || 'MISSING'}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Cost:</span>{' '}
                    <span className={project.analysis?.calculations?.totals?.total_project_cost ? 'text-green-600' : 'text-red-600'}>
                      ${(project.analysis?.calculations?.totals?.total_project_cost / 1000000)?.toFixed(1)}M
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <h2 className="text-lg font-semibold mb-4">Recent Traces ({traces.length})</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {traces.slice(-20).reverse().map((trace, idx) => (
              <div key={idx} className="p-2 bg-gray-50 rounded text-xs border border-gray-200">
                <div className="flex justify-between items-start mb-1">
                  <p className="font-semibold">{trace.location}</p>
                  <p className="text-gray-400">{new Date(trace.timestamp).toLocaleTimeString()}</p>
                </div>
                <p className="text-gray-600">{trace.action}</p>
                {trace.data?.building_type && (
                  <p className="text-green-600 mt-1">Building Type: {trace.data.building_type}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="mt-8 p-4 bg-gray-900 text-white rounded-lg">
        <h3 className="font-semibold mb-2">Console Commands:</h3>
        <pre className="text-xs">
          tracer.findBreakpoint()  // Find where data gets lost{'\n'}
          tracer.getTraces()       // Get all traces{'\n'}
          tracer.clear()           // Clear all traces{'\n'}
          window.__traces          // Access traces directly
        </pre>
      </div>
    </div>
  );
};