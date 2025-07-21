import React, { useState, useRef, useEffect } from 'react';
import './ArchitecturalFloorPlan.css';
import { ZoomIn, ZoomOut, Maximize2, Layers, FileDown } from 'lucide-react';

interface Point {
  x: number;
  y: number;
}

interface Wall {
  id: string;
  type: 'exterior' | 'interior' | 'partition';
  start: Point;
  end: Point;
  thickness: number;
}

interface Door {
  id: string;
  type: 'single' | 'double' | 'overhead' | 'sliding';
  position: Point;
  width: number;
  wall_id: string;
  swing_direction: string;
  swing_side: string;
}

interface Window {
  id: string;
  position: Point;
  width: number;
  wall_id: string;
}

interface Fixture {
  id: string;
  type: 'toilet' | 'sink' | 'urinal' | 'water_fountain';
  position: Point;
  rotation: number;
}

interface Space {
  id: string;
  name: string;
  type: string;
  points: Point[];
  area: number;
  height: number;
}

interface DimensionLine {
  id: string;
  start: Point;
  end: Point;
  offset: number;
  text: string;
}

interface TradeZone {
  id: string;
  trade: string;
  type: string;
  points: Point[];
  equipment_id?: string;
  description?: string;
}

interface FloorPlanData {
  building_width: number;
  building_height: number;
  walls: Wall[];
  doors: Door[];
  windows: Window[];
  fixtures: Fixture[];
  spaces: Space[];
  dimensions: DimensionLine[];
  trade_zones: TradeZone[];
  scale: string;
  units: string;
  rotated?: boolean;
}

interface ArchitecturalFloorPlanProps {
  floorPlan: FloorPlanData;
  projectName: string;
}

const ArchitecturalFloorPlan: React.FC<ArchitecturalFloorPlanProps> = ({ floorPlan, projectName }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Handle missing floor plan data or convert old format
  if (!floorPlan) {
    return (
      <div className="architectural-floor-plan">
        <div className="floor-plan-canvas" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p>No floor plan data available</p>
        </div>
      </div>
    );
  }
  
  // Check if this is old format floor plan data
  if (!floorPlan.walls && floorPlan.building_dimensions) {
    return (
      <div className="architectural-floor-plan">
        <div className="floor-plan-canvas" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
          <p>Legacy floor plan format detected</p>
          <p style={{ fontSize: '0.875rem', color: '#666' }}>
            This project uses the legacy floor plan format. 
            <br />
            The system will automatically use the appropriate viewer.
          </p>
        </div>
      </div>
    );
  }
  
  // Handle new format but missing walls
  if (!floorPlan.walls) {
    return (
      <div className="architectural-floor-plan">
        <div className="floor-plan-canvas" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <p>Floor plan data is incomplete</p>
        </div>
      </div>
    );
  }
  
  // Constants
  const PIXELS_PER_FOOT = 4; // Base scale
  const LINE_WEIGHTS = {
    exterior: 2,
    interior: 1.5,
    partition: 1,
    dimension: 0.5,
    symbol: 0.75
  };
  
  // State
  const [scale, setScale] = useState(1);
  const [viewMode, setViewMode] = useState<'architectural' | 'trade'>('architectural');
  const [activeTrades, setActiveTrades] = useState({
    hvac: true,
    electrical: true,
    plumbing: true,
    structural: true
  });
  const [hoveredElement, setHoveredElement] = useState<any>(null);
  const [showLegend, setShowLegend] = useState(false);
  
  // Trade colors with transparency
  const TRADE_COLORS = {
    hvac: 'rgba(59, 130, 246, 0.3)',       // Blue
    electrical: 'rgba(251, 191, 36, 0.3)',  // Yellow
    plumbing: 'rgba(34, 197, 94, 0.3)',     // Green
    structural: 'rgba(239, 68, 68, 0.3)'    // Red
  };
  
  // Calculate optimal scale on mount and resize
  useEffect(() => {
    const calculateOptimalScale = () => {
      if (containerRef.current && floorPlan) {
        const container = containerRef.current.getBoundingClientRect();
        const padding = 40; // 20px padding on each side
        
        const buildingWidth = floorPlan.building_width * PIXELS_PER_FOOT;
        const buildingHeight = floorPlan.building_height * PIXELS_PER_FOOT;
        
        const availableWidth = container.width - padding * 2;
        const availableHeight = container.height - padding * 2;
        
        const scaleX = availableWidth / buildingWidth;
        const scaleY = availableHeight / buildingHeight;
        
        const optimalScale = Math.min(scaleX, scaleY) * 0.9; // 90% to leave some margin
        setScale(optimalScale);
      }
    };
    
    calculateOptimalScale();
    window.addEventListener('resize', calculateOptimalScale);
    return () => window.removeEventListener('resize', calculateOptimalScale);
  }, [floorPlan]);
  
  // Zoom handlers
  const handleZoomIn = () => setScale(s => Math.min(s * 1.2, 5));
  const handleZoomOut = () => setScale(s => Math.max(s * 0.8, 0.5));
  const handleFitToScreen = () => {
    const container = containerRef.current?.getBoundingClientRect();
    if (container) {
      const buildingWidth = floorPlan.building_width * PIXELS_PER_FOOT;
      const buildingHeight = floorPlan.building_height * PIXELS_PER_FOOT;
      const scaleX = (container.width - 80) / buildingWidth;
      const scaleY = (container.height - 80) / buildingHeight;
      setScale(Math.min(scaleX, scaleY) * 0.9);
    }
  };
  
  // Export to PDF
  const exportToPDF = () => {
    // In production, would use a library like jsPDF with svg2pdf
    alert('PDF export would be implemented here');
  };
  
  // Toggle trade layer
  const toggleTrade = (trade: keyof typeof activeTrades) => {
    setActiveTrades(prev => ({ ...prev, [trade]: !prev[trade] }));
  };
  
  // Render wall
  const renderWall = (wall: Wall) => {
    const weight = LINE_WEIGHTS[wall.type];
    return (
      <line
        key={wall.id}
        x1={wall.start.x * PIXELS_PER_FOOT}
        y1={wall.start.y * PIXELS_PER_FOOT}
        x2={wall.end.x * PIXELS_PER_FOOT}
        y2={wall.end.y * PIXELS_PER_FOOT}
        stroke="black"
        strokeWidth={weight}
        strokeLinecap="square"
      />
    );
  };
  
  // Render door with architectural symbol
  const renderDoor = (door: Door) => {
    const x = door.position.x * PIXELS_PER_FOOT;
    const y = door.position.y * PIXELS_PER_FOOT;
    const width = door.width * PIXELS_PER_FOOT;
    
    if (door.type === 'overhead') {
      // Overhead door symbol
      return (
        <g key={door.id}>
          <rect
            x={x - width/2}
            y={y - 2}
            width={width}
            height={4}
            fill="white"
            stroke="black"
            strokeWidth={LINE_WEIGHTS.symbol}
          />
          {/* Dashed lines for overhead door */}
          <line
            x1={x - width/2}
            y1={y}
            x2={x + width/2}
            y2={y}
            stroke="black"
            strokeWidth={LINE_WEIGHTS.symbol}
            strokeDasharray="2,2"
          />
        </g>
      );
    } else if (door.type === 'single' || door.type === 'double') {
      // Swing door with arc
      const swingRadius = width * 0.8;
      const isDouble = door.type === 'double';
      
      return (
        <g key={door.id}>
          {/* Door opening (white fill to break wall) */}
          <rect
            x={x - width/2}
            y={y - 3}
            width={width}
            height={6}
            fill="white"
          />
          
          {/* Door panel(s) */}
          <line
            x1={x - width/2}
            y1={y}
            x2={x + (isDouble ? 0 : width/2)}
            y2={y}
            stroke="black"
            strokeWidth={LINE_WEIGHTS.symbol}
          />
          
          {isDouble && (
            <line
              x1={x}
              y1={y}
              x2={x + width/2}
              y2={y}
              stroke="black"
              strokeWidth={LINE_WEIGHTS.symbol}
            />
          )}
          
          {/* Swing arc(s) */}
          <path
            d={`M ${x - width/2} ${y} A ${swingRadius} ${swingRadius} 0 0 1 ${x - width/2 + swingRadius} ${y + swingRadius}`}
            fill="none"
            stroke="black"
            strokeWidth={LINE_WEIGHTS.symbol * 0.5}
          />
          
          {isDouble && (
            <path
              d={`M ${x + width/2} ${y} A ${swingRadius} ${swingRadius} 0 0 0 ${x + width/2 - swingRadius} ${y + swingRadius}`}
              fill="none"
              stroke="black"
              strokeWidth={LINE_WEIGHTS.symbol * 0.5}
            />
          )}
        </g>
      );
    }
    
    return null;
  };
  
  // Render window
  const renderWindow = (window: Window) => {
    const x = window.position.x * PIXELS_PER_FOOT;
    const y = window.position.y * PIXELS_PER_FOOT;
    const width = window.width * PIXELS_PER_FOOT;
    
    return (
      <g key={window.id}>
        {/* Window symbol - parallel lines */}
        <line
          x1={x - width/2}
          y1={y - 2}
          x2={x + width/2}
          y2={y - 2}
          stroke="black"
          strokeWidth={LINE_WEIGHTS.symbol}
        />
        <line
          x1={x - width/2}
          y1={y + 2}
          x2={x + width/2}
          y2={y + 2}
          stroke="black"
          strokeWidth={LINE_WEIGHTS.symbol}
        />
      </g>
    );
  };
  
  // Render fixture with architectural symbols
  const renderFixture = (fixture: Fixture) => {
    const x = fixture.position.x * PIXELS_PER_FOOT;
    const y = fixture.position.y * PIXELS_PER_FOOT;
    
    const transform = `translate(${x}, ${y}) rotate(${fixture.rotation})`;
    
    switch (fixture.type) {
      case 'toilet':
        return (
          <g key={fixture.id} transform={transform}>
            <ellipse
              cx={0}
              cy={0}
              rx={7}
              ry={9}
              fill="white"
              stroke="black"
              strokeWidth={LINE_WEIGHTS.symbol}
            />
            <ellipse
              cx={0}
              cy={-3}
              rx={5}
              ry={6}
              fill="white"
              stroke="black"
              strokeWidth={LINE_WEIGHTS.symbol}
            />
          </g>
        );
      
      case 'sink':
        return (
          <g key={fixture.id} transform={transform}>
            <rect
              x={-8}
              y={-6}
              width={16}
              height={12}
              fill="white"
              stroke="black"
              strokeWidth={LINE_WEIGHTS.symbol}
              rx={2}
            />
            <circle
              cx={0}
              cy={0}
              r={3}
              fill="white"
              stroke="black"
              strokeWidth={LINE_WEIGHTS.symbol}
            />
          </g>
        );
      
      case 'urinal':
        return (
          <g key={fixture.id} transform={transform}>
            <rect
              x={-4}
              y={-6}
              width={8}
              height={12}
              fill="white"
              stroke="black"
              strokeWidth={LINE_WEIGHTS.symbol}
              rx={2}
            />
          </g>
        );
      
      default:
        return null;
    }
  };
  
  // Render space label
  const renderSpaceLabel = (space: Space) => {
    // Calculate centroid
    const centroid = space.points.reduce(
      (acc, point) => ({
        x: acc.x + point.x,
        y: acc.y + point.y
      }),
      { x: 0, y: 0 }
    );
    centroid.x = (centroid.x / space.points.length) * PIXELS_PER_FOOT;
    centroid.y = (centroid.y / space.points.length) * PIXELS_PER_FOOT;
    
    // Calculate appropriate font size based on space size
    const fontSize = Math.max(12, Math.min(18, Math.sqrt(space.area) * 0.5));
    
    return (
      <g key={`label-${space.id}`}>
        <text
          x={centroid.x}
          y={centroid.y}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={fontSize / scale} // Adjust for zoom
          fontFamily="Arial, sans-serif"
          fill="black"
          fontWeight="500"
        >
          {space.name}
        </text>
        {space.area > 200 && (
          <text
            x={centroid.x}
            y={centroid.y + fontSize / scale + 2}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize={(fontSize - 2) / scale}
            fontFamily="Arial, sans-serif"
            fill="#666"
          >
            {space.area} SF
          </text>
        )}
      </g>
    );
  };
  
  // Render dimension line
  const renderDimension = (dim: DimensionLine) => {
    const x1 = dim.start.x * PIXELS_PER_FOOT;
    const y1 = dim.start.y * PIXELS_PER_FOOT;
    const x2 = dim.end.x * PIXELS_PER_FOOT;
    const y2 = dim.end.y * PIXELS_PER_FOOT;
    
    const isHorizontal = Math.abs(y2 - y1) < Math.abs(x2 - x1);
    const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
    
    return (
      <g key={dim.id}>
        {/* Main dimension line */}
        <line
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke="black"
          strokeWidth={LINE_WEIGHTS.dimension}
        />
        
        {/* End ticks */}
        <line
          x1={x1}
          y1={y1 - 3}
          x2={x1}
          y2={y1 + 3}
          stroke="black"
          strokeWidth={LINE_WEIGHTS.dimension}
        />
        <line
          x1={x2}
          y1={y2 - 3}
          x2={x2}
          y2={y2 + 3}
          stroke="black"
          strokeWidth={LINE_WEIGHTS.dimension}
        />
        
        {/* Dimension text */}
        <text
          x={midX}
          y={isHorizontal ? midY - 5 : midY}
          textAnchor="middle"
          dominantBaseline={isHorizontal ? "bottom" : "middle"}
          fontSize={10 / scale}
          fontFamily="Arial, sans-serif"
          fill="black"
        >
          {dim.text}
        </text>
      </g>
    );
  };
  
  // Render trade zone overlay
  const renderTradeZone = (zone: TradeZone) => {
    if (!activeTrades[zone.trade as keyof typeof activeTrades]) return null;
    
    const pathData = zone.points
      .map((point, index) => {
        const x = point.x * PIXELS_PER_FOOT;
        const y = point.y * PIXELS_PER_FOOT;
        return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
      })
      .join(' ') + ' Z';
    
    return (
      <g 
        key={zone.id}
        onMouseEnter={() => setHoveredElement(zone)}
        onMouseLeave={() => setHoveredElement(null)}
      >
        <path
          d={pathData}
          fill={TRADE_COLORS[zone.trade as keyof typeof TRADE_COLORS]}
          stroke={TRADE_COLORS[zone.trade as keyof typeof TRADE_COLORS]}
          strokeWidth={1}
          opacity={hoveredElement?.id === zone.id ? 0.5 : 0.3}
        />
      </g>
    );
  };
  
  // Render north arrow
  const renderNorthArrow = () => {
    const x = (floorPlan.building_width - 10) * PIXELS_PER_FOOT;
    const y = 10 * PIXELS_PER_FOOT;
    
    return (
      <g transform={`translate(${x}, ${y})`}>
        {/* Arrow */}
        <path
          d="M 0,-15 L -5,5 L 0,0 L 5,5 Z"
          fill="black"
          stroke="black"
          strokeWidth={1}
        />
        {/* N label */}
        <text
          x={0}
          y={-20}
          textAnchor="middle"
          fontSize={14 / scale}
          fontFamily="Arial, sans-serif"
          fontWeight="bold"
          fill="black"
        >
          N
        </text>
        {/* Circle */}
        <circle
          cx={0}
          cy={0}
          r={20}
          fill="none"
          stroke="black"
          strokeWidth={1}
        />
      </g>
    );
  };
  
  // Render scale notation
  const renderScale = () => {
    const x = 10 * PIXELS_PER_FOOT;
    const y = (floorPlan.building_height - 5) * PIXELS_PER_FOOT;
    
    return (
      <text
        x={x}
        y={y}
        fontSize={12 / scale}
        fontFamily="Arial, sans-serif"
        fill="black"
      >
        Scale: {floorPlan.scale}
      </text>
    );
  };
  
  // Calculate viewBox with padding
  const viewBox = `${-20} ${-20} ${(floorPlan.building_width + 40) * PIXELS_PER_FOOT} ${(floorPlan.building_height + 40) * PIXELS_PER_FOOT}`;
  
  return (
    <div className="architectural-floor-plan">
      {/* Floating Controls */}
      <div className="floor-plan-controls top-left">
        <button onClick={handleZoomIn} title="Zoom In">
          <ZoomIn size={18} />
        </button>
        <button onClick={handleZoomOut} title="Zoom Out">
          <ZoomOut size={18} />
        </button>
        <button onClick={handleFitToScreen} title="Fit to Screen">
          <Maximize2 size={18} />
        </button>
      </div>
      
      <div className="floor-plan-controls top-right">
        <button
          className={`view-toggle ${viewMode === 'architectural' ? 'active' : ''}`}
          onClick={() => setViewMode('architectural')}
        >
          Architectural View
        </button>
        <button
          className={`view-toggle ${viewMode === 'trade' ? 'active' : ''}`}
          onClick={() => setViewMode('trade')}
        >
          Trade Overlays
        </button>
      </div>
      
      {viewMode === 'trade' && (
        <div className="trade-toggles">
          {Object.entries(activeTrades).map(([trade, active]) => (
            <label key={trade} className="trade-toggle">
              <input
                type="checkbox"
                checked={active}
                onChange={() => toggleTrade(trade as keyof typeof activeTrades)}
              />
              <span 
                className="trade-label"
                style={{ 
                  backgroundColor: active ? TRADE_COLORS[trade as keyof typeof TRADE_COLORS] : 'transparent' 
                }}
              >
                {trade.toUpperCase()}
              </span>
            </label>
          ))}
        </div>
      )}
      
      <button 
        className="legend-toggle"
        onClick={() => setShowLegend(!showLegend)}
      >
        <Layers size={18} />
      </button>
      
      {showLegend && (
        <div className="floor-plan-legend">
          <h3>Legend</h3>
          <div className="legend-section">
            <h4>Line Types</h4>
            <div className="legend-item">
              <svg width="30" height="10">
                <line x1="0" y1="5" x2="30" y2="5" stroke="black" strokeWidth={2} />
              </svg>
              <span>Exterior Wall</span>
            </div>
            <div className="legend-item">
              <svg width="30" height="10">
                <line x1="0" y1="5" x2="30" y2="5" stroke="black" strokeWidth={1} />
              </svg>
              <span>Interior Wall</span>
            </div>
          </div>
          
          {viewMode === 'trade' && (
            <div className="legend-section">
              <h4>Trade Overlays</h4>
              {Object.entries(TRADE_COLORS).map(([trade, color]) => (
                <div key={trade} className="legend-item">
                  <div 
                    className="color-swatch"
                    style={{ backgroundColor: color }}
                  />
                  <span>{trade.toUpperCase()}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      <button 
        className="export-button"
        onClick={exportToPDF}
        title="Export PDF"
      >
        <FileDown size={18} />
      </button>
      
      {/* Main Drawing Area */}
      <div 
        className="floor-plan-canvas"
        ref={containerRef}
      >
        <svg
          ref={svgRef}
          viewBox={viewBox}
          preserveAspectRatio="xMidYMid meet"
          style={{
            width: `${(floorPlan.building_width + 40) * PIXELS_PER_FOOT * scale}px`,
            height: `${(floorPlan.building_height + 40) * PIXELS_PER_FOOT * scale}px`,
            maxWidth: '100%',
            maxHeight: '100%',
          }}
        >
          {/* Background */}
          <rect
            x={0}
            y={0}
            width={floorPlan.building_width * PIXELS_PER_FOOT}
            height={floorPlan.building_height * PIXELS_PER_FOOT}
            fill="white"
          />
          
          {/* Trade zones (if in trade mode) */}
          {viewMode === 'trade' && floorPlan.trade_zones && floorPlan.trade_zones.map(zone => renderTradeZone(zone))}
          
          {/* Walls */}
          {floorPlan.walls.map(wall => renderWall(wall))}
          
          {/* Doors */}
          {floorPlan.doors && floorPlan.doors.map(door => renderDoor(door))}
          
          {/* Windows */}
          {floorPlan.windows && floorPlan.windows.map(window => renderWindow(window))}
          
          {/* Fixtures */}
          {floorPlan.fixtures && floorPlan.fixtures.map(fixture => renderFixture(fixture))}
          
          {/* Space labels */}
          {floorPlan.spaces && floorPlan.spaces.map(space => renderSpaceLabel(space))}
          
          {/* Dimensions */}
          {floorPlan.dimensions && floorPlan.dimensions.map(dim => renderDimension(dim))}
          
          {/* North arrow */}
          {renderNorthArrow()}
          
          {/* Scale */}
          {renderScale()}
        </svg>
      </div>
      
      {/* Hover tooltip */}
      {hoveredElement && hoveredElement.description && (
        <div 
          className="floor-plan-tooltip"
          style={{
            left: '50%',
            top: '50%'
          }}
        >
          {hoveredElement.description}
        </div>
      )}
    </div>
  );
};

export default ArchitecturalFloorPlan;