import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { scopeService, authService } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, Cell } from 'recharts';
import { ArrowLeft, Download, Share2 } from 'lucide-react';
import { formatCurrency, formatNumber } from '../utils/formatters';
import { calculateDeveloperMetrics, formatMetricValue } from '../utils/developerMetrics';
import { getDisplayBuildingType } from '../utils/buildingTypeDisplay';
import './ComparisonPage.css';

interface Project {
  project_id: string;
  name?: string;
  project_name?: string;
  scenario_name?: string;
  total_cost: number;
  square_footage?: number;
  location: string;
  building_type?: string;
  scope_data?: any;
  cost_data?: any;
  categories?: any[];
  request_data?: any;
}

function ComparisonPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  console.log('ComparisonPage mounted');

  useEffect(() => {
    // Check authentication first
    if (!authService.isAuthenticated()) {
      console.log('User not authenticated, redirecting to login');
      navigate('/login');
      return;
    }
    loadProjects();
  }, [searchParams, navigate]);

  const loadProjects = async () => {
    try {
      const projectIds = searchParams.get('projects')?.split(',') || [];
      console.log('Loading projects for comparison:', projectIds);
      
      // Debug authentication status
      const token = localStorage.getItem('token');
      const hasCookie = document.cookie.includes('access_token');
      console.log('Auth debug - Token exists:', !!token, 'Cookie exists:', hasCookie);
      console.log('Token value:', token ? 'Present' : 'Missing');
      
      if (projectIds.length === 0) {
        console.log('No project IDs found, redirecting to dashboard');
        navigate('/dashboard');
        return;
      }

      const projectPromises = projectIds.map(id => scopeService.getProject(id));
      const loadedProjects = await Promise.all(projectPromises);
      console.log('Loaded projects:', loadedProjects);
      console.log('First project structure:', loadedProjects[0]);
      
      // Normalize project data - extract square_footage and location from nested locations
      const normalizedProjects = loadedProjects.map(project => {
        // Square footage might be in different places
        const squareFootage = project.square_footage || 
                            project.request_data?.square_footage || 
                            project.scope_data?.request_data?.square_footage ||
                            0;
        
        // Location might also be nested
        const location = project.location || 
                        project.request_data?.location || 
                        project.scope_data?.request_data?.location ||
                        'N/A';
        
        return {
          ...project,
          square_footage: squareFootage,
          location: location
        };
      });
      
      setProjects(normalizedProjects);
    } catch (err: any) {
      console.error('Failed to load projects:', err);
      console.error('Error response:', err.response);
      
      // Check if it's an auth error
      if (err.response?.status === 401) {
        console.error('Authentication error - redirecting to login');
        // Clear invalid token
        localStorage.removeItem('token');
        navigate('/login');
        return;
      }
      
      setError('Failed to load projects for comparison: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading comparison...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (projects.length === 0 && !loading) {
    return (
      <div className="comparison-page" style={{ padding: '20px', background: '#f7f7f7', minHeight: '100vh' }}>
        <header className="comparison-header">
          <button onClick={() => navigate('/dashboard')} className="back-btn">
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <h1>Project Comparison</h1>
        </header>
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
          <p style={{ fontSize: '18px', color: '#666' }}>No projects selected for comparison</p>
          <button 
            onClick={() => navigate('/dashboard')} 
            style={{ marginTop: '20px', padding: '10px 20px', background: '#667eea', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Prepare data for charts
  const costComparisonData = projects.map(p => ({
    name: p.scenario_name || p.name || p.project_name || 'Project',
    totalCost: p.total_cost,
    costPerSF: p.square_footage ? p.total_cost / p.square_footage : 0
  }));

  // Get all unique categories from projects
  const allCategories = new Set<string>();
  projects.forEach(p => {
    const categories = p.scope_data?.categories || p.categories || [];
    categories.forEach((cat: any) => {
      if (cat.name) {
        allCategories.add(cat.name);
      }
    });
  });

  // Prepare radar chart data for category breakdown
  const categoryData = Array.from(allCategories).map(category => {
    const dataPoint: any = { category };
    projects.forEach((p, index) => {
      const categories = p.scope_data?.categories || p.categories || [];
      const cat = categories.find((c: any) => c.name === category);
      dataPoint[`project${index}`] = cat ? cat.subtotal : 0;
    });
    return dataPoint;
  });

  // Calculate developer metrics for each project
  const metricsComparison = projects.map(p => {
    const metrics = calculateDeveloperMetrics(p);
    return {
      project: p,
      metrics
    };
  });

  // Find common metric types
  const commonMetricTypes = new Set<string>();
  metricsComparison.forEach(({ metrics }) => {
    metrics.forEach(m => commonMetricTypes.add(m.label));
  });

  const downloadComparison = () => {
    // Create a comprehensive comparison report
    const date = new Date();
    const dateStr = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    
    // Create CSV content for better readability
    let csvContent = 'PROJECT COMPARISON REPORT\n';
    csvContent += `Generated on: ${dateStr}\n\n`;
    
    // Summary section
    csvContent += 'SUMMARY\n';
    csvContent += '=======\n';
    const lowestCost = Math.min(...projects.map(p => p.total_cost));
    const highestCost = Math.max(...projects.map(p => p.total_cost));
    const avgCost = projects.reduce((sum, p) => sum + p.total_cost, 0) / projects.length;
    
    csvContent += `Number of Projects: ${projects.length}\n`;
    csvContent += `Lowest Cost: ${formatCurrency(lowestCost)}\n`;
    csvContent += `Highest Cost: ${formatCurrency(highestCost)}\n`;
    csvContent += `Average Cost: ${formatCurrency(avgCost)}\n`;
    csvContent += `Cost Range: ${formatCurrency(highestCost - lowestCost)}\n\n`;
    
    // Projects table
    csvContent += 'PROJECT DETAILS\n';
    csvContent += '===============\n';
    csvContent += 'Project Name,Scenario,Location,Building Type,Square Footage,Total Cost,Cost per SF\n';
    
    projects.forEach(p => {
      const name = p.name || p.project_name || 'Unnamed Project';
      const scenario = p.scenario_name || 'Base';
      const location = p.location || 'N/A';
      const buildingType = getDisplayBuildingType(p.scope_data?.request_data || p.request_data || p);
      const sqft = p.square_footage ? formatNumber(p.square_footage) : 'N/A';
      const totalCost = formatCurrency(p.total_cost);
      const costPerSF = p.square_footage ? formatCurrency(p.total_cost / p.square_footage) : 'N/A';
      
      csvContent += `"${name}","${scenario}","${location}","${buildingType}","${sqft}","${totalCost}","${costPerSF}"\n`;
    });
    
    // Developer metrics section
    csvContent += '\nDEVELOPER METRICS\n';
    csvContent += '=================\n';
    
    projects.forEach(p => {
      const metrics = calculateDeveloperMetrics(p);
      if (metrics.length > 0) {
        csvContent += `\n${p.name || p.project_name || 'Project'}:\n`;
        metrics.forEach(m => {
          csvContent += `  ${m.label}: ${formatMetricValue(m.value)}${m.unit}\n`;
        });
      }
    });
    
    // Key findings
    csvContent += '\nKEY FINDINGS\n';
    csvContent += '============\n';
    const minProject = projects.reduce((min, p) => p.total_cost < min.total_cost ? p : min);
    csvContent += `Most Cost-Effective: ${minProject.name || minProject.project_name || 'Project'} at ${formatCurrency(minProject.total_cost)}\n`;
    
    if (projects.length > 1) {
      const savings = highestCost - lowestCost;
      const savingsPercent = ((savings / highestCost) * 100).toFixed(1);
      csvContent += `Potential Savings: ${formatCurrency(savings)} (${savingsPercent}%)\n`;
    }
    
    // Create downloadable file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `SpecSharp_Comparison_${date.toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Also create a JSON file with structured data
    const jsonReport = {
      generated: date.toISOString(),
      summary: {
        projects_compared: projects.length,
        lowest_cost: lowestCost,
        highest_cost: highestCost,
        average_cost: avgCost,
        cost_range: highestCost - lowestCost
      },
      projects: projects.map(p => ({
        id: p.project_id,
        name: p.name || p.project_name || 'Unnamed Project',
        scenario_name: p.scenario_name || 'Base',
        location: p.location,
        building_type: getDisplayBuildingType(p.scope_data?.request_data || p.request_data || p),
        square_footage: p.square_footage || 0,
        total_cost: p.total_cost,
        cost_per_sf: p.square_footage ? p.total_cost / p.square_footage : null,
        metrics: calculateDeveloperMetrics(p)
      })),
      key_findings: {
        most_cost_effective: {
          name: minProject.name || minProject.project_name || 'Project',
          total_cost: minProject.total_cost
        },
        potential_savings: projects.length > 1 ? {
          amount: highestCost - lowestCost,
          percentage: ((highestCost - lowestCost) / highestCost * 100).toFixed(1)
        } : null
      }
    };
    
    // Download JSON as well
    setTimeout(() => {
      const jsonBlob = new Blob([JSON.stringify(jsonReport, null, 2)], { type: 'application/json' });
      const jsonUrl = URL.createObjectURL(jsonBlob);
      const jsonLink = document.createElement('a');
      jsonLink.href = jsonUrl;
      jsonLink.download = `SpecSharp_Comparison_Data_${date.toISOString().split('T')[0]}.json`;
      document.body.appendChild(jsonLink);
      jsonLink.click();
      document.body.removeChild(jsonLink);
    }, 500);
  };

  return (
    <div className="comparison-page" style={{ padding: '20px', background: '#f7f7f7', minHeight: '100vh' }}>
      <header className="comparison-header">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>
        <h1>Project Comparison</h1>
        <div className="header-actions">
          <button className="download-btn" onClick={downloadComparison}>
            <Download size={18} />
            Download Report
          </button>
        </div>
      </header>

      <div className="comparison-content">
        {/* Projects Overview */}
        <div className="projects-overview">
          <h2>Projects Overview</h2>
          <div className="projects-table">
            <table>
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Scenario</th>
                  <th>Location</th>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Total Cost</th>
                  <th>Cost/SF</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project, index) => (
                  <tr key={project.project_id} className={index === 0 ? 'baseline' : ''}>
                    <td>{project.name || project.project_name || 'Unnamed Project'}</td>
                    <td>{project.scenario_name || 'Base'}</td>
                    <td>{project.location}</td>
                    <td>{getDisplayBuildingType(project.scope_data?.request_data || project.request_data || project)}</td>
                    <td>{project.square_footage ? `${formatNumber(project.square_footage)} SF` : 'N/A'}</td>
                    <td className="cost">{formatCurrency(project.total_cost)}</td>
                    <td className="cost">{project.square_footage ? formatCurrency(project.total_cost / project.square_footage) : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Cost Comparison Chart */}
        {costComparisonData.length > 0 && (
          <div className="comparison-section">
            <h2>Cost Comparison</h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={costComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                  <XAxis dataKey="name" />
                  <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value)}
                    contentStyle={{ backgroundColor: '#f7faff', border: '1px solid #667eea', borderRadius: '8px' }}
                  />
                  <Bar dataKey="totalCost" name="Total Cost">
                    {costComparisonData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#667eea' : index === 1 ? '#00C49F' : '#FFBB28'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Developer Metrics Comparison */}
        {commonMetricTypes.size > 0 && (
          <div className="comparison-section">
            <h2>Developer Metrics Comparison</h2>
            <div className="metrics-comparison-grid">
              {Array.from(commonMetricTypes).map(metricType => (
                <div key={metricType} className="metric-comparison-card">
                  <h4>{metricType}</h4>
                  <div className="metric-values">
                    {metricsComparison.map(({ project, metrics }) => {
                      const metric = metrics.find(m => m.label === metricType);
                      return (
                        <div key={project.project_id} className="metric-item">
                          <span className="project-name">{project.scenario_name || project.name || project.project_name || 'Project'}</span>
                          <span className="metric-value">
                            {metric ? `${formatMetricValue(metric.value)}${metric.unit}` : 'N/A'}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category Breakdown */}
        {categoryData.length > 0 && (
          <div className="comparison-section">
            <h2>Cost Category Breakdown</h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={categoryData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="category" />
                  <PolarRadiusAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                  {projects.map((project, index) => (
                    <Radar
                      key={project.project_id}
                      name={project.scenario_name || project.name || project.project_name || `Project ${index + 1}`}
                      dataKey={`project${index}`}
                      stroke={['#667eea', '#00C49F', '#FFBB28', '#FF8042'][index % 4]}
                      fill={['#667eea', '#00C49F', '#FFBB28', '#FF8042'][index % 4]}
                      fillOpacity={0.4}
                    />
                  ))}
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
        
        {/* Detailed Cost Breakdown Table */}
        <div className="comparison-section">
          <h2>Detailed Cost Breakdown</h2>
          <div className="cost-breakdown-table">
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f7faff', borderBottom: '2px solid #667eea' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600 }}>Category</th>
                  {projects.map((project, index) => (
                    <th key={project.project_id} style={{ padding: '12px', textAlign: 'right', fontWeight: 600 }}>
                      {project.scenario_name || project.name || project.project_name || `Project ${index + 1}`}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Array.from(allCategories).map((category, catIndex) => (
                  <tr key={category} style={{ borderBottom: '1px solid #e0e7ff', backgroundColor: catIndex % 2 === 0 ? '#ffffff' : '#f8f9ff' }}>
                    <td style={{ padding: '10px', fontWeight: 500 }}>{category}</td>
                    {projects.map((project) => {
                      const categories = project.scope_data?.categories || project.categories || [];
                      const cat = categories.find((c: any) => c.name === category);
                      const value = cat ? cat.subtotal : 0;
                      return (
                        <td key={project.project_id} style={{ padding: '10px', textAlign: 'right', fontFamily: 'monospace' }}>
                          {formatCurrency(value)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
                <tr style={{ borderTop: '2px solid #667eea', backgroundColor: '#f0f7ff', fontWeight: 700 }}>
                  <td style={{ padding: '12px' }}>TOTAL</td>
                  {projects.map((project) => (
                    <td key={project.project_id} style={{ padding: '12px', textAlign: 'right', fontFamily: 'monospace', color: '#667eea' }}>
                      {formatCurrency(project.total_cost)}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Percentage Differences */}
        {projects.length > 1 && (
          <div className="comparison-section">
            <h2>Cost Comparison Analysis</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
              {projects.map((project, index) => {
                if (index === 0) return null; // Skip base project
                const baseProject = projects[0];
                const diff = project.total_cost - baseProject.total_cost;
                const percentDiff = ((diff / baseProject.total_cost) * 100).toFixed(1);
                const isHigher = diff > 0;
                
                return (
                  <div key={project.project_id} style={{
                    padding: '20px',
                    borderRadius: '8px',
                    backgroundColor: isHigher ? '#fee' : '#efe',
                    border: `2px solid ${isHigher ? '#fcc' : '#cfc'}`
                  }}>
                    <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>
                      {project.name || project.project_name} vs {baseProject.name || baseProject.project_name}
                    </h4>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: isHigher ? '#d32f2f' : '#388e3c' }}>
                      {isHigher ? '+' : ''}{percentDiff}%
                    </div>
                    <div style={{ fontSize: '18px', marginTop: '5px', color: isHigher ? '#d32f2f' : '#388e3c' }}>
                      {isHigher ? '+' : ''}{formatCurrency(diff)}
                    </div>
                    <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                      {isHigher ? 'More expensive' : 'Cost savings'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Key Findings */}
        <div className="comparison-section key-findings">
          <h2>Key Findings</h2>
          <div className="findings-grid">
            <div className="finding-card">
              <h4>Most Cost-Effective</h4>
              <p>{(() => {
                const minProject = projects.reduce((min, p) => p.total_cost < min.total_cost ? p : min);
                return minProject.name || minProject.project_name || 'Project';
              })()}</p>
              <span className="finding-value">
                {formatCurrency(Math.min(...projects.map(p => p.total_cost)))}
              </span>
            </div>
            <div className="finding-card">
              <h4>Average Cost</h4>
              <p>Across all scenarios</p>
              <span className="finding-value">
                {formatCurrency(projects.reduce((sum, p) => sum + p.total_cost, 0) / projects.length)}
              </span>
            </div>
            <div className="finding-card">
              <h4>Cost Range</h4>
              <p>Difference between highest and lowest</p>
              <span className="finding-value">
                {formatCurrency(Math.max(...projects.map(p => p.total_cost)) - Math.min(...projects.map(p => p.total_cost)))}
              </span>
            </div>
            {projects.length > 0 && projects[0].square_footage && (
              <div className="finding-card">
                <h4>Best Value</h4>
                <p>Lowest cost per SF</p>
                <span className="finding-value">
                  {(() => {
                    const withSF = projects.filter(p => p.square_footage > 0);
                    if (withSF.length === 0) return 'N/A';
                    const bestValue = withSF.reduce((best, p) => {
                      const costPerSF = p.total_cost / p.square_footage;
                      const bestCostPerSF = best.total_cost / best.square_footage;
                      return costPerSF < bestCostPerSF ? p : best;
                    });
                    return `${formatCurrency(bestValue.total_cost / bestValue.square_footage)}/SF`;
                  })()}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComparisonPage;