import React, { useState, useRef, useEffect, useMemo } from 'react';
import './ProfessionalFloorPlan.css';

interface Position {
  x: number;
  y: number;
}

interface Dimensions {
  width: number;
  length: number;
}

interface Room {
  id: string;
  name: string;
  type: string;
  size: number;
  position: Position;
  dimensions: Dimensions;
}

interface Equipment {
  id: string;
  type: string;
  name: string;
  location: string | Position;
}

interface BuildingArea {
  type: string;
  dimensions: Dimensions;
  position: Position;
  features: string[];
  rooms: Room[];
}

interface FloorPlanData {
  building_dimensions: Dimensions;
  areas: BuildingArea[];
  equipment: Equipment[];
  grid_size: number;
}

interface ProfessionalFloorPlanProps {
  floorPlan: FloorPlanData;
  projectName: string;
}

// Architectural symbols for equipment
const EQUIPMENT_SYMBOLS: Record<string, string> = {
  hvac: 'M -20,-20 L 20,-20 L 20,20 L -20,20 Z M -15,-15 L 15,-15 L 15,15 L -15,15 Z M 0,-15 L 0,15 M -15,0 L 15,0',
  electrical: 'M -20,-20 L 20,-20 L 20,20 L -20,20 Z M -10,-10 L 10,-10 L 10,10 L -10,10 Z M 0,-20 L 0,-10 M 0,10 L 0,20 M -20,0 L -10,0 M 10,0 L 20,0',
  plumbing: 'M 0,-20 A 20,20 0 0,1 0,20 A 20,20 0 0,1 0,-20 M -14,-14 L 14,14 M -14,14 L 14,-14',
  fire: 'M -15,-15 L 15,-15 L 15,15 L -15,15 Z M -10,-10 L 10,-10 L 10,10 L -10,10 Z M 0,-10 L 0,10 M -10,0 L 10,0',
};

// Door symbols
const DOOR_ARC = 'M 0,0 A 30,30 0 0,1 30,0';
const DOOR_LINE = 'M 0,0 L 30,0';

// Window symbol
const WINDOW_SYMBOL = 'M -15,0 L 15,0 M -15,-2 L -15,2 M 15,-2 L 15,2';

const ProfessionalFloorPlan: React.FC<ProfessionalFloorPlanProps> = ({ floorPlan, projectName }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Constants for professional drawing
  const SCALE = 10; // 1:10 scale (1 pixel = 0.1 feet)
  const WALL_THICKNESS = 0.5; // 6 inches in feet
  const GRID_SPACING = 10; // 10 feet grid
  
  // State
  const [viewMode, setViewMode] = useState<'architectural' | 'mechanical' | 'electrical' | 'plumbing'>('architectural');
  const [showDimensions, setShowDimensions] = useState(true);
  const [showGrid, setShowGrid] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  
  // Calculate if building should be rotated for optimal view (landscape orientation)
  const shouldRotate = useMemo(() => {
    if (!autoRotate) return false;
    // Rotate if height is greater than width to achieve landscape orientation
    return floorPlan.building_dimensions.length > floorPlan.building_dimensions.width;
  }, [floorPlan, autoRotate]);
  
  // Get actual dimensions accounting for rotation
  const displayDimensions = useMemo(() => {
    if (shouldRotate) {
      return {
        width: floorPlan.building_dimensions.length,
        height: floorPlan.building_dimensions.width
      };
    }
    return {
      width: floorPlan.building_dimensions.width,
      height: floorPlan.building_dimensions.length
    };
  }, [floorPlan, shouldRotate]);
  
  // Transform coordinates if rotated
  const transformPosition = (pos: Position): Position => {
    if (!shouldRotate) return pos;
    return {
      x: pos.y,
      y: floorPlan.building_dimensions.width - pos.x
    };
  };
  
  const transformDimensions = (dim: Dimensions): Dimensions => {
    if (!shouldRotate) return dim;
    return {
      width: dim.length,
      length: dim.width
    };
  };
  
  // Professional line styles
  const getLineStyle = (type: string) => {
    switch (type) {
      case 'exterior':
        return { strokeWidth: WALL_THICKNESS * SCALE, stroke: '#000000' };
      case 'interior':
        return { strokeWidth: WALL_THICKNESS * SCALE * 0.6, stroke: '#000000' };
      case 'hidden':
        return { strokeWidth: 1, stroke: '#666666', strokeDasharray: '5,5' };
      case 'dimension':
        return { strokeWidth: 0.5, stroke: '#000000' };
      case 'grid':
        return { strokeWidth: 0.25, stroke: '#cccccc' };
      default:
        return { strokeWidth: 1, stroke: '#000000' };
    }
  };
  
  // Render professional grid
  const renderGrid = () => {
    if (!showGrid) return null;
    
    const gridLines = [];
    const style = getLineStyle('grid');
    
    // Vertical lines
    for (let x = 0; x <= displayDimensions.width; x += GRID_SPACING) {
      gridLines.push(
        <line
          key={`v-${x}`}
          x1={x * SCALE}
          y1={0}
          x2={x * SCALE}
          y2={displayDimensions.height * SCALE}
          {...style}
        />
      );
    }
    
    // Horizontal lines
    for (let y = 0; y <= displayDimensions.height; y += GRID_SPACING) {
      gridLines.push(
        <line
          key={`h-${y}`}
          x1={0}
          y1={y * SCALE}
          x2={displayDimensions.width * SCALE}
          y2={y * SCALE}
          {...style}
        />
      );
    }
    
    return <g className="grid-layer">{gridLines}</g>;
  };
  
  // Render dimension lines with arrows
  const renderDimension = (x1: number, y1: number, x2: number, y2: number, text: string, offset: number = 3) => {
    const isHorizontal = y1 === y2;
    const style = getLineStyle('dimension');
    
    const arrowSize = 3;
    const tickSize = 0.8 * SCALE;
    const textOffset = 2 * SCALE;
    
    if (isHorizontal) {
      const y = y1 - offset * SCALE;
      return (
        <g className="dimension">
          {/* Main dimension line */}
          <line x1={x1} y1={y} x2={x2} y2={y} {...style} />
          
          {/* Extension lines */}
          <line x1={x1} y1={y - tickSize} x2={x1} y2={y + tickSize} {...style} />
          <line x1={x2} y1={y - tickSize} x2={x2} y2={y + tickSize} {...style} />
          
          {/* Leader lines */}
          <line x1={x1} y1={y1} x2={x1} y2={y} {...style} strokeDasharray="2,2" />
          <line x1={x2} y1={y2} x2={x2} y2={y} {...style} strokeDasharray="2,2" />
          
          {/* Arrows */}
          <path d={`M ${x1},${y} L ${x1 + arrowSize},${y - arrowSize} L ${x1 + arrowSize},${y + arrowSize} Z`} fill="#000000" />
          <path d={`M ${x2},${y} L ${x2 - arrowSize},${y - arrowSize} L ${x2 - arrowSize},${y + arrowSize} Z`} fill="#000000" />
          
          {/* Dimension text */}
          <rect
            x={(x1 + x2) / 2 - 30}
            y={y - textOffset - 8}
            width={60}
            height={16}
            fill="#ffffff"
            stroke="none"
          />
          <text
            x={(x1 + x2) / 2}
            y={y - textOffset}
            textAnchor="middle"
            fontSize={12}
            fill="#000000"
            fontFamily="Arial, sans-serif"
            fontWeight="normal"
          >
            {text}
          </text>
        </g>
      );
    } else {
      const x = x1 - offset * SCALE;
      return (
        <g className="dimension">
          {/* Main dimension line */}
          <line x1={x} y1={y1} x2={x} y2={y2} {...style} />
          
          {/* Extension lines */}
          <line x1={x - tickSize} y1={y1} x2={x + tickSize} y2={y1} {...style} />
          <line x1={x - tickSize} y1={y2} x2={x + tickSize} y2={y2} {...style} />
          
          {/* Leader lines */}
          <line x1={x1} y1={y1} x2={x} y2={y1} {...style} strokeDasharray="2,2" />
          <line x1={x2} y1={y2} x2={x} y2={y2} {...style} strokeDasharray="2,2" />
          
          {/* Arrows */}
          <path d={`M ${x},${y1} L ${x - arrowSize},${y1 + arrowSize} L ${x + arrowSize},${y1 + arrowSize} Z`} fill="#000000" />
          <path d={`M ${x},${y2} L ${x - arrowSize},${y2 - arrowSize} L ${x + arrowSize},${y2 - arrowSize} Z`} fill="#000000" />
          
          {/* Dimension text */}
          <rect
            x={x - textOffset - 40}
            y={(y1 + y2) / 2 - 8}
            width={35}
            height={16}
            fill="#ffffff"
            stroke="none"
          />
          <text
            x={x - textOffset}
            y={(y1 + y2) / 2}
            textAnchor="middle"
            fontSize={12}
            fill="#000000"
            fontFamily="Arial, sans-serif"
            transform={`rotate(-90, ${x - textOffset}, ${(y1 + y2) / 2})`}
          >
            {text}
          </text>
        </g>
      );
    }
  };
  
  // Render trade overlay zones
  const renderTradeOverlays = () => {
    if (viewMode === 'architectural') return null;
    
    const overlays = [];
    
    floorPlan.areas.forEach((area, areaIndex) => {
      area.rooms.forEach((room, roomIndex) => {
        const pos = transformPosition(room.position);
        const dim = transformDimensions(room.dimensions);
        const x = pos.x * SCALE;
        const y = pos.y * SCALE;
        const width = dim.width * SCALE;
        const height = dim.length * SCALE;
        
        if (viewMode === 'mechanical') {
          // HVAC zones - show RTU coverage areas
          if (room.type === 'warehouse' || room.type === 'office' || room.type === 'open_office') {
            overlays.push(
              <g key={`hvac-${areaIndex}-${roomIndex}`}>
                <rect
                  x={x}
                  y={y}
                  width={width}
                  height={height}
                  fill="#2196f3"
                  fillOpacity={0.2}
                  stroke="#2196f3"
                  strokeWidth={2}
                  strokeDasharray="5,5"
                />
                <text
                  x={x + width / 2}
                  y={y + 20}
                  textAnchor="middle"
                  fontSize={10}
                  fill="#1976d2"
                  fontWeight="bold"
                >
                  HVAC ZONE {roomIndex + 1}
                </text>
              </g>
            );
          }
        } else if (viewMode === 'electrical') {
          // Electrical zones - show panel coverage
          if (room.type === 'electrical' || room.type === 'office' || room.type === 'warehouse') {
            overlays.push(
              <g key={`elec-${areaIndex}-${roomIndex}`}>
                <rect
                  x={x}
                  y={y}
                  width={width}
                  height={height}
                  fill="#ffc107"
                  fillOpacity={0.2}
                  stroke="#ffc107"
                  strokeWidth={2}
                  strokeDasharray="5,5"
                />
                {room.type === 'electrical' && (
                  <text
                    x={x + width / 2}
                    y={y + height / 2}
                    textAnchor="middle"
                    fontSize={12}
                    fill="#f57c00"
                    fontWeight="bold"
                  >
                    MAIN PANEL
                  </text>
                )}
              </g>
            );
          }
        } else if (viewMode === 'plumbing') {
          // Plumbing zones - show wet walls
          if (room.type === 'restroom' || room.type === 'kitchen') {
            overlays.push(
              <g key={`plumb-${areaIndex}-${roomIndex}`}>
                <rect
                  x={x}
                  y={y}
                  width={width}
                  height={height}
                  fill="#4caf50"
                  fillOpacity={0.2}
                  stroke="#4caf50"
                  strokeWidth={2}
                />
                <line
                  x1={x}
                  y1={y + height / 2}
                  x2={x + width}
                  y2={y + height / 2}
                  stroke="#4caf50"
                  strokeWidth={3}
                  strokeDasharray="10,5"
                />
                <text
                  x={x + width / 2}
                  y={y + 20}
                  textAnchor="middle"
                  fontSize={10}
                  fill="#2e7d32"
                  fontWeight="bold"
                >
                  WET WALL
                </text>
              </g>
            );
          }
        }
      });
    });
    
    return <g className="trade-overlays">{overlays}</g>;
  };
  
  // Render professional room
  const renderRoom = (room: Room, area: BuildingArea) => {
    const pos = transformPosition(room.position);
    const dim = transformDimensions(room.dimensions);
    
    const x = pos.x * SCALE;
    const y = pos.y * SCALE;
    const width = dim.width * SCALE;
    const height = dim.length * SCALE;
    
    // Room fill always white for professional look
    const fill = '#ffffff';
    
    return (
      <g key={room.id} className="room">
        {/* Room boundary */}
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={fill}
          stroke="none"
        />
        
        {/* Room walls */}
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill="none"
          {...getLineStyle('interior')}
        />
        
        {/* Add doors for certain room types */}
        {(room.type === 'office' || room.type === 'conference') && (
          <g transform={`translate(${x + width/2}, ${y + height})`}>
            <path d={DOOR_ARC} fill="none" stroke="#000000" strokeWidth={0.5} />
            <line x1={0} y1={0} x2={30} y2={0} stroke="#000000" strokeWidth={2} />
          </g>
        )}
        
        {/* Room label */}
        <text
          x={x + width / 2}
          y={y + height / 2 - 8}
          textAnchor="middle"
          fontSize={14}
          fill="#000000"
          fontFamily="Arial, sans-serif"
          fontWeight="bold"
        >
          {room.name.toUpperCase()}
        </text>
        
        {/* Room size */}
        <text
          x={x + width / 2}
          y={y + height / 2 + 8}
          textAnchor="middle"
          fontSize={12}
          fill="#333333"
          fontFamily="Arial, sans-serif"
        >
          {room.size} SF
        </text>
      </g>
    );
  };
  
  // Render equipment with architectural symbols
  const renderEquipment = (equipment: Equipment) => {
    if (equipment.location === 'roof') return null;
    
    // Only show equipment relevant to current view mode
    if (viewMode === 'architectural') return null;
    if (viewMode === 'mechanical' && equipment.type !== 'hvac') return null;
    if (viewMode === 'electrical' && equipment.type !== 'electrical') return null;
    if (viewMode === 'plumbing' && equipment.type !== 'plumbing') return null;
    
    const pos = transformPosition(equipment.location as Position);
    const x = pos.x * SCALE;
    const y = pos.y * SCALE;
    
    const symbol = EQUIPMENT_SYMBOLS[equipment.type] || EQUIPMENT_SYMBOLS.electrical;
    
    return (
      <g key={equipment.id} className="equipment" transform={`translate(${x}, ${y})`}>
        <path
          d={symbol}
          fill="none"
          stroke="#000000"
          strokeWidth={1}
        />
        <text
          x={0}
          y={-25}
          textAnchor="middle"
          fontSize={8}
          fill="#000000"
          fontFamily="Arial, sans-serif"
        >
          {equipment.name}
        </text>
      </g>
    );
  };
  
  // Render title block
  const renderTitleBlock = () => {
    const blockWidth = 200;
    const blockHeight = 100;
    const x = displayDimensions.width * SCALE - blockWidth - 20;
    const y = displayDimensions.height * SCALE - blockHeight - 20;
    
    return (
      <g className="title-block">
        <rect
          x={x}
          y={y}
          width={blockWidth}
          height={blockHeight}
          fill="#ffffff"
          stroke="#000000"
          strokeWidth={1}
        />
        
        {/* Title block content */}
        <text x={x + 10} y={y + 20} fontSize={12} fontWeight="bold" fontFamily="Arial, sans-serif">
          {projectName.toUpperCase()}
        </text>
        <text x={x + 10} y={y + 35} fontSize={10} fontFamily="Arial, sans-serif">
          FLOOR PLAN
        </text>
        <text x={x + 10} y={y + 50} fontSize={10} fontFamily="Arial, sans-serif" fontWeight="bold">
          SCALE: 1/8" = 1'-0"
        </text>
        <text x={x + 10} y={y + 65} fontSize={8} fontFamily="Arial, sans-serif">
          Date: {new Date().toLocaleDateString()}
        </text>
        <text x={x + 10} y={y + 80} fontSize={8} fontFamily="Arial, sans-serif">
          Drawing: A-101
        </text>
      </g>
    );
  };
  
  // Render north arrow (top right)
  const renderNorthArrow = () => {
    const size = 30;
    const x = displayDimensions.width * SCALE - 60;
    const y = 60;
    
    return (
      <g className="north-arrow" transform={`translate(${x}, ${y})`}>
        <circle cx={0} cy={0} r={size} fill="none" stroke="#000000" strokeWidth={1} />
        <path
          d="M 0,-20 L -8,10 L 0,5 L 8,10 Z"
          fill="#000000"
          stroke="none"
        />
        <text
          x={0}
          y={-25}
          textAnchor="middle"
          fontSize={14}
          fontWeight="bold"
          fontFamily="Arial, sans-serif"
        >
          N
        </text>
      </g>
    );
  };
  
  // Render scale bar
  const renderScaleBar = () => {
    const scaleLength = 50; // 50 feet
    const pixelLength = scaleLength * SCALE;
    const x = 50;
    const y = displayDimensions.height * SCALE - 50;
    
    return (
      <g className="scale-bar" transform={`translate(${x}, ${y})`}>
        <line x1={0} y1={0} x2={pixelLength} y2={0} stroke="#000000" strokeWidth={2} />
        <line x1={0} y1={-5} x2={0} y2={5} stroke="#000000" strokeWidth={2} />
        <line x1={pixelLength} y1={-5} x2={pixelLength} y2={5} stroke="#000000" strokeWidth={2} />
        
        {/* Scale divisions */}
        {[10, 20, 30, 40].map(ft => (
          <line
            key={ft}
            x1={ft * SCALE}
            y1={-3}
            x2={ft * SCALE}
            y2={3}
            stroke="#000000"
            strokeWidth={1}
          />
        ))}
        
        <text x={pixelLength / 2} y={-10} textAnchor="middle" fontSize={10} fontFamily="Arial, sans-serif">
          0      10      20      30      40      50 FT
        </text>
      </g>
    );
  };
  
  return (
    <div className="professional-floor-plan">
      <div className="floor-plan-toolbar">
        <div className="toolbar-group">
          <label>View Mode:</label>
          <select value={viewMode} onChange={(e) => setViewMode(e.target.value as any)}>
            <option value="architectural">Architectural</option>
            <option value="mechanical">Mechanical</option>
            <option value="electrical">Electrical</option>
            <option value="plumbing">Plumbing</option>
          </select>
        </div>
        
        <div className="toolbar-group">
          <label>
            <input
              type="checkbox"
              checked={showDimensions}
              onChange={(e) => setShowDimensions(e.target.checked)}
            />
            Show Dimensions
          </label>
          <label>
            <input
              type="checkbox"
              checked={showGrid}
              onChange={(e) => setShowGrid(e.target.checked)}
            />
            Show Grid
          </label>
          <label>
            <input
              type="checkbox"
              checked={autoRotate}
              onChange={(e) => setAutoRotate(e.target.checked)}
            />
            Auto-Rotate
          </label>
        </div>
        
        <div className="toolbar-group">
          <button onClick={() => window.print()} className="print-btn">
            Print
          </button>
          <button className="export-btn">Export PDF</button>
        </div>
      </div>
      
      <div className="floor-plan-container" ref={containerRef}>
        <svg
          ref={svgRef}
          width={displayDimensions.width * SCALE + 100}
          height={displayDimensions.height * SCALE + 100}
          viewBox={`-50 -50 ${displayDimensions.width * SCALE + 100} ${displayDimensions.height * SCALE + 100}`}
          style={{
            backgroundColor: '#ffffff',
            width: '100%',
            height: '100%',
          }}
        >
          {/* Grid layer */}
          {renderGrid()}
          
          {/* Building outline */}
          <rect
            x={0}
            y={0}
            width={displayDimensions.width * SCALE}
            height={displayDimensions.height * SCALE}
            fill="none"
            {...getLineStyle('exterior')}
          />
          
          {/* Areas and rooms */}
          {floorPlan.areas.map((area) =>
            area.rooms.map((room) => renderRoom(room, area))
          )}
          
          {/* Trade overlay zones */}
          {renderTradeOverlays()}
          
          {/* Equipment layer */}
          {floorPlan.equipment.map((eq) => renderEquipment(eq))}
          
          {/* Dimensions */}
          {showDimensions && (
            <g className="dimensions">
              {/* Overall building dimensions */}
              {renderDimension(
                0,
                0,
                displayDimensions.width * SCALE,
                0,
                `${displayDimensions.width}'-0"`,
                5
              )}
              {renderDimension(
                0,
                0,
                0,
                displayDimensions.height * SCALE,
                `${displayDimensions.height}'-0"`,
                5
              )}
              
              {/* Room dimensions for major rooms */}
              {floorPlan.areas.map((area) =>
                area.rooms
                  .filter(room => room.size > 200) // Only show dimensions for larger rooms
                  .map((room) => {
                    const pos = transformPosition(room.position);
                    const dim = transformDimensions(room.dimensions);
                    const x = pos.x * SCALE;
                    const y = pos.y * SCALE;
                    const width = dim.width * SCALE;
                    const height = dim.length * SCALE;
                    
                    return (
                      <g key={`dim-${room.id}`}>
                        {renderDimension(
                          x,
                          y + height,
                          x + width,
                          y + height,
                          `${Math.round(dim.width)}'-0"`,
                          1.5
                        )}
                        {renderDimension(
                          x + width,
                          y,
                          x + width,
                          y + height,
                          `${Math.round(dim.length)}'-0"`,
                          1.5
                        )}
                      </g>
                    );
                  })
              )}
            </g>
          )}
          
          {/* Drawing elements */}
          {renderNorthArrow()}
          {renderScaleBar()}
          {renderTitleBlock()}
        </svg>
      </div>
    </div>
  );
};

export default ProfessionalFloorPlan;