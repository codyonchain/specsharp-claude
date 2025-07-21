import React, { useState, useRef, useEffect } from 'react';
import './FloorPlanViewer.css';

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

interface FloorPlanViewerProps {
  floorPlan: FloorPlanData;
  projectName: string;
}

const FloorPlanViewer: React.FC<FloorPlanViewerProps> = ({ floorPlan, projectName }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Constants - increased for better visibility
  const PIXELS_PER_FOOT = 30; // Much larger for better readability
  const EXTERIOR_WALL_WIDTH = 6;
  const INTERIOR_WALL_WIDTH = 3;
  const MIN_FONT_SIZE = 24; // Larger font size
  const LABEL_FONT_SIZE = 20;
  const EQUIPMENT_SIZE = 60; // Larger equipment icons
  
  // State
  const [scale, setScale] = useState(1);
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [hoveredRoom, setHoveredRoom] = useState<Room | null>(null);
  const [hoveredEquipment, setHoveredEquipment] = useState<Equipment | null>(null);
  const [showLegend, setShowLegend] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Layer visibility
  const [layers, setLayers] = useState({
    rooms: true,
    equipment: true,
    grid: false,
    labels: true,
    dimensions: false,
  });
  
  // Colors for different room types
  const roomColors: Record<string, string> = {
    warehouse: '#f0f0f0',
    office: '#e8f4f8',
    open_office: '#e8f4f8',
    conference: '#f3e5f5',
    restroom: '#e0f2f1',
    kitchen: '#fff3e0',
    storage: '#f5f5f5',
    mechanical: '#ffebee',
    electrical: '#fff9c4',
    lobby: '#e8f5e9',
    loading_dock: '#ffe082',
    corridor: '#fafafa',
  };
  
  const equipmentColors: Record<string, string> = {
    hvac: '#2196f3',
    electrical: '#ffc107',
    plumbing: '#4caf50',
    fire: '#f44336',
  };
  
  // Calculate scale to fit building in viewport at 90% width
  useEffect(() => {
    if (containerRef.current && floorPlan) {
      const container = containerRef.current.getBoundingClientRect();
      const targetWidthRatio = 0.9; // Fill 90% of container width
      const targetHeightRatio = 0.85; // Fill 85% of container height
      
      const buildingWidth = floorPlan.building_dimensions.width * PIXELS_PER_FOOT;
      const buildingLength = floorPlan.building_dimensions.length * PIXELS_PER_FOOT;
      
      // Account for padding
      const availableWidth = container.width - 80; // 40px padding on each side
      const availableHeight = container.height - 80;
      
      // Calculate scale to fit
      const scaleX = (availableWidth * targetWidthRatio) / buildingWidth;
      const scaleY = (availableHeight * targetHeightRatio) / buildingLength;
      const optimalScale = Math.min(scaleX, scaleY, 1.5); // Cap at 1.5x to prevent over-scaling
      
      setScale(optimalScale);
    }
  }, [floorPlan, PIXELS_PER_FOOT]);
  
  // Zoom handlers only (no panning)
  const handleZoomIn = () => {
    setScale(s => Math.min(s * 1.2, 3));
  };
  
  const handleZoomOut = () => {
    setScale(s => Math.max(s * 0.8, 0.5));
  };
  
  // Layer toggle
  const toggleLayer = (layer: keyof typeof layers) => {
    setLayers(prev => ({ ...prev, [layer]: !prev[layer] }));
  };
  
  // Reset view to optimal scale
  const resetView = () => {
    if (containerRef.current && floorPlan) {
      const container = containerRef.current.getBoundingClientRect();
      const targetWidthRatio = 0.9;
      const targetHeightRatio = 0.85;
      const buildingWidth = floorPlan.building_dimensions.width * PIXELS_PER_FOOT;
      const buildingLength = floorPlan.building_dimensions.length * PIXELS_PER_FOOT;
      const availableWidth = container.width - 80;
      const availableHeight = container.height - 80;
      const scaleX = (availableWidth * targetWidthRatio) / buildingWidth;
      const scaleY = (availableHeight * targetHeightRatio) / buildingLength;
      setScale(Math.min(scaleX, scaleY, 1.5));
    }
  };
  
  // Export to PDF (placeholder)
  const exportToPDF = () => {
    alert('PDF export would be implemented here');
  };
  
  // Render grid
  const renderGrid = () => {
    if (!layers.grid) return null;
    
    const gridSize = floorPlan.grid_size * PIXELS_PER_FOOT;
    const width = floorPlan.building_dimensions.width * PIXELS_PER_FOOT;
    const length = floorPlan.building_dimensions.length * PIXELS_PER_FOOT;
    const lines = [];
    
    // Vertical lines
    for (let x = 0; x <= width; x += gridSize) {
      lines.push(
        <line
          key={`v-${x}`}
          x1={x}
          y1={0}
          x2={x}
          y2={length}
          stroke="#e0e0e0"
          strokeWidth={0.5}
        />
      );
    }
    
    // Horizontal lines
    for (let y = 0; y <= length; y += gridSize) {
      lines.push(
        <line
          key={`h-${y}`}
          x1={0}
          y1={y}
          x2={width}
          y2={y}
          stroke="#e0e0e0"
          strokeWidth={0.5}
        />
      );
    }
    
    return <g className="grid-layer">{lines}</g>;
  };
  
  // Render room
  const renderRoom = (room: Room) => {
    const color = roomColors[room.type] || '#ffffff';
    const isHovered = hoveredRoom?.id === room.id;
    const isSelected = selectedRoom?.id === room.id;
    
    // Scale room dimensions
    const x = room.position.x * PIXELS_PER_FOOT;
    const y = room.position.y * PIXELS_PER_FOOT;
    const width = room.dimensions.width * PIXELS_PER_FOOT;
    const height = room.dimensions.length * PIXELS_PER_FOOT;
    
    return (
      <g key={room.id} className="room-group">
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={color}
          stroke={isSelected ? '#1976d2' : '#333'}
          strokeWidth={isSelected ? EXTERIOR_WALL_WIDTH : INTERIOR_WALL_WIDTH}
          opacity={isHovered ? 0.8 : 0.9}
          style={{ cursor: 'pointer' }}
          onMouseEnter={() => setHoveredRoom(room)}
          onMouseLeave={() => setHoveredRoom(null)}
          onClick={() => setSelectedRoom(room)}
        />
        
        {layers.labels && (
          <g>
            <rect
              x={x + width / 2 - 60}
              y={y + height / 2 - 12}
              width={120}
              height={24}
              fill="white"
              opacity="0.9"
              rx="2"
            />
            <text
              x={x + width / 2}
              y={y + height / 2}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={MIN_FONT_SIZE}
              fill="#333"
              fontWeight="600"
              style={{ pointerEvents: 'none' }}
            >
              {room.name}
            </text>
            {room.size > 150 && (
              <text
                x={x + width / 2}
                y={y + height / 2 + 25}
                textAnchor="middle"
                fontSize={LABEL_FONT_SIZE}
                fill="#666"
                style={{ pointerEvents: 'none' }}
              >
                {room.size} SF
              </text>
            )}
          </g>
        )}
      </g>
    );
  };
  
  // Render equipment
  const renderEquipment = (equipment: Equipment) => {
    if (!layers.equipment) return null;
    
    const color = equipmentColors[equipment.type] || '#999';
    const isHovered = hoveredEquipment?.id === equipment.id;
    
    // Handle roof-mounted equipment
    if (equipment.location === 'roof') {
      return null; // Will be shown in equipment list
    }
    
    const pos = equipment.location as Position;
    const x = pos.x * PIXELS_PER_FOOT - EQUIPMENT_SIZE / 2;
    const y = pos.y * PIXELS_PER_FOOT - EQUIPMENT_SIZE / 2;
    
    return (
      <g key={equipment.id} className="equipment-group">
        <rect
          x={x}
          y={y}
          width={EQUIPMENT_SIZE}
          height={EQUIPMENT_SIZE}
          fill={color}
          stroke="#333"
          strokeWidth={3}
          opacity={isHovered ? 1 : 0.8}
          rx="6"
          style={{ cursor: 'pointer' }}
          onMouseEnter={() => setHoveredEquipment(equipment)}
          onMouseLeave={() => setHoveredEquipment(null)}
        />
        <text
          x={x + EQUIPMENT_SIZE / 2}
          y={y + EQUIPMENT_SIZE / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="32"
          fill="white"
          fontWeight="bold"
          style={{ pointerEvents: 'none' }}
        >
          {equipment.type.charAt(0).toUpperCase()}
        </text>
        {layers.labels && (
          <g>
            <rect
              x={x}
              y={y - 35}
              width={EQUIPMENT_SIZE}
              height={28}
              fill="white"
              opacity="0.9"
              rx="4"
            />
            <text
              x={x + EQUIPMENT_SIZE / 2}
              y={y - 21}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="16"
              fill="#333"
              fontWeight="600"
            >
              {equipment.name}
            </text>
          </g>
        )}
      </g>
    );
  };
  
  // Render area outline
  const renderArea = (area: BuildingArea) => {
    const x = area.position.x * PIXELS_PER_FOOT;
    const y = area.position.y * PIXELS_PER_FOOT;
    const width = area.dimensions.width * PIXELS_PER_FOOT;
    const height = area.dimensions.length * PIXELS_PER_FOOT;
    
    return (
      <g key={area.type} className="area-group">
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill="none"
          stroke="#666"
          strokeWidth={3}
          strokeDasharray={area.type === 'warehouse' ? '10,10' : 'none'}
        />
        
        {layers.labels && (
          <g>
            <rect
              x={x + width / 2 - 80}
              y={y + 10}
              width={160}
              height={30}
              fill="white"
              opacity="0.9"
              rx="4"
            />
            <text
              x={x + width / 2}
              y={y + 30}
              textAnchor="middle"
              fontSize="28"
              fontWeight="bold"
              fill="#333"
              style={{ textTransform: 'uppercase' }}
            >
              {area.type}
            </text>
          </g>
        )}
        
        {area.rooms.map(room => renderRoom(room))}
      </g>
    );
  };
  
  // Render scale indicator
  const renderScale = () => {
    const scaleLength = 50 * PIXELS_PER_FOOT; // 50 feet in pixels
    const y = floorPlan.building_dimensions.length * PIXELS_PER_FOOT - 60;
    
    return (
      <g className="scale-indicator" transform={`translate(60, ${y})`}>
        <rect x={-15} y={-30} width={scaleLength + 30} height={50} fill="white" opacity="0.9" rx="6" />
        <line x1={0} y1={0} x2={scaleLength} y2={0} stroke="#333" strokeWidth={4} />
        <line x1={0} y1={-10} x2={0} y2={10} stroke="#333" strokeWidth={4} />
        <line x1={scaleLength} y1={-10} x2={scaleLength} y2={10} stroke="#333" strokeWidth={4} />
        <text x={scaleLength / 2} y={-15} textAnchor="middle" fontSize="20" fontWeight="600" fill="#333">
          50 ft
        </text>
      </g>
    );
  };
  
  // Render north arrow
  const renderNorthArrow = () => {
    const x = floorPlan.building_dimensions.width * PIXELS_PER_FOOT - 80;
    const y = 80;
    
    return (
      <g className="north-arrow" transform={`translate(${x}, ${y})`}>
        <circle cx={0} cy={0} r={45} fill="white" opacity="0.9" stroke="#333" strokeWidth={2} />
        <path
          d="M 0,-30 L -12,12 L 0,0 L 12,12 Z"
          fill="#333"
          stroke="#333"
          strokeWidth={3}
        />
        <text x={0} y={-38} textAnchor="middle" fontSize="24" fontWeight="bold" fill="#333">
          N
        </text>
      </g>
    );
  };
  
  return (
    <div className="floor-plan-viewer">
      <div className="floor-plan-header">
        <h2>{projectName} - Floor Plan</h2>
      </div>
      
      <div className="floor-plan-content">
        <div className="floor-plan-controls">
          <button onClick={handleZoomIn}>+</button>
          <button onClick={handleZoomOut}>−</button>
          <button onClick={resetView}>Fit</button>
          <button onClick={exportToPDF} className="export-btn">PDF</button>
        </div>
        
        <button 
          className={`sidebar-toggle ${sidebarCollapsed ? 'collapsed' : ''}`}
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        >
          {sidebarCollapsed ? '◀' : '▶'}
        </button>
        
        <div 
          className="floor-plan-canvas"
          ref={containerRef}
        >
          <svg
            ref={svgRef}
            viewBox={`0 0 ${floorPlan.building_dimensions.width * PIXELS_PER_FOOT} ${floorPlan.building_dimensions.length * PIXELS_PER_FOOT}`}
            preserveAspectRatio="xMidYMid meet"
            style={{
              width: `${floorPlan.building_dimensions.width * PIXELS_PER_FOOT * scale}px`,
              height: `${floorPlan.building_dimensions.length * PIXELS_PER_FOOT * scale}px`,
              maxWidth: '100%',
              maxHeight: '100%',
            }}
          >
            {renderGrid()}
            
            {/* Building outline */}
            <rect
              x={0}
              y={0}
              width={floorPlan.building_dimensions.width * PIXELS_PER_FOOT}
              height={floorPlan.building_dimensions.length * PIXELS_PER_FOOT}
              fill="white"
              stroke="#333"
              strokeWidth={EXTERIOR_WALL_WIDTH * 2}
            />
            
            {/* Areas and rooms */}
            {layers.rooms && floorPlan.areas.map(area => renderArea(area))}
            
            {/* Equipment */}
            {layers.equipment && floorPlan.equipment
              .filter(eq => eq.location !== 'roof')
              .map(eq => renderEquipment(eq))}
            
            {/* Scale and north arrow */}
            {renderScale()}
            {renderNorthArrow()}
          </svg>
          
          {/* Hover tooltip */}
          {(hoveredRoom || hoveredEquipment) && (
            <div className="floor-plan-tooltip">
              {hoveredRoom && (
                <>
                  <div>{hoveredRoom.name}</div>
                  <div>{hoveredRoom.size} SF</div>
                  <div>{hoveredRoom.type.replace('_', ' ')}</div>
                </>
              )}
              {hoveredEquipment && (
                <>
                  <div>{hoveredEquipment.name}</div>
                  <div>{hoveredEquipment.type.toUpperCase()}</div>
                </>
              )}
            </div>
          )}
        </div>
        
        <div className={`floor-plan-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          {/* Room details */}
          {selectedRoom && (
            <div className="room-details">
              <h3>Room Details</h3>
              <div className="detail-item">
                <label>Name:</label>
                <span>{selectedRoom.name}</span>
              </div>
              <div className="detail-item">
                <label>Type:</label>
                <span>{selectedRoom.type.replace('_', ' ')}</span>
              </div>
              <div className="detail-item">
                <label>Size:</label>
                <span>{selectedRoom.size} SF</span>
              </div>
              <div className="detail-item">
                <label>Dimensions:</label>
                <span>{selectedRoom.dimensions.width.toFixed(0)}' × {selectedRoom.dimensions.length.toFixed(0)}'</span>
              </div>
            </div>
          )}
          
          {/* Layers */}
          <div className="layer-controls">
            <h3>Layers</h3>
            {Object.entries(layers).map(([key, value]) => (
              <label key={key} className="layer-toggle">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={() => toggleLayer(key as keyof typeof layers)}
                />
                <span>{key.charAt(0).toUpperCase() + key.slice(1)}</span>
              </label>
            ))}
          </div>
          
          {/* Legend */}
          <div className="legend">
            <h3>Legend</h3>
            
            <h4>Room Types</h4>
            {Object.entries(roomColors).map(([type, color]) => (
              <div key={type} className="legend-item">
                <div className="legend-color" style={{ backgroundColor: color }} />
                <span>{type.replace('_', ' ')}</span>
              </div>
            ))}
            
            <h4>Equipment</h4>
            {Object.entries(equipmentColors).map(([type, color]) => (
              <div key={type} className="legend-item">
                <div className="legend-color" style={{ backgroundColor: color }} />
                <span>{type.toUpperCase()}</span>
              </div>
            ))}
          </div>
          
          {/* Roof equipment list */}
          {floorPlan.equipment.some(eq => eq.location === 'roof') && (
            <div className="roof-equipment">
              <h3>Roof Equipment</h3>
              {floorPlan.equipment
                .filter(eq => eq.location === 'roof')
                .map(eq => (
                  <div key={eq.id} className="equipment-item">
                    <span className="equipment-icon" style={{ color: equipmentColors[eq.type] }}>■</span>
                    <span>{eq.name}</span>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FloorPlanViewer;