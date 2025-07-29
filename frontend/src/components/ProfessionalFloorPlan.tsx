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

const ProfessionalFloorPlan: React.FC<ProfessionalFloorPlanProps> = ({ floorPlan, projectName }) => {
  if (!floorPlan) {
    return <div>No floor plan data available</div>;
  }
  
  // Create a simple, functional floor plan regardless of input data
  const buildingWidth = floorPlan?.building_dimensions?.width || 100;
  const buildingLength = floorPlan?.building_dimensions?.length || 80;
  const totalSF = buildingWidth * buildingLength;
  
  // Create rooms based on available data or defaults
  let rooms = [];
  if (floorPlan?.areas && Array.isArray(floorPlan.areas)) {
    // Use existing room data if available
    floorPlan.areas.forEach(area => {
      if (area.rooms && Array.isArray(area.rooms)) {
        rooms.push(...area.rooms);
      }
    });
  }
  
  // If no rooms, create default layout based on total square footage
  if (rooms.length === 0) {
    if (totalSF >= 8000) {
      // Large building - assume mixed use
      rooms = [
        { name: "WAREHOUSE", type: "warehouse", size: Math.floor(totalSF * 0.6), position: { x: 10, y: 10 }, dimensions: { width: buildingWidth - 20, length: (buildingLength - 30) * 0.6 } },
        { name: "OFFICE AREA", type: "office", size: Math.floor(totalSF * 0.25), position: { x: 10, y: 10 + (buildingLength - 30) * 0.6 + 10 }, dimensions: { width: (buildingWidth - 30) * 0.7, length: (buildingLength - 30) * 0.3 } },
        { name: "RESTROOMS", type: "restroom", size: Math.floor(totalSF * 0.05), position: { x: 10 + (buildingWidth - 30) * 0.7 + 10, y: 10 + (buildingLength - 30) * 0.6 + 10 }, dimensions: { width: (buildingWidth - 30) * 0.25, length: (buildingLength - 30) * 0.15 } },
        { name: "STORAGE", type: "storage", size: Math.floor(totalSF * 0.1), position: { x: 10 + (buildingWidth - 30) * 0.7 + 10, y: 10 + (buildingLength - 30) * 0.6 + 10 + (buildingLength - 30) * 0.15 + 5 }, dimensions: { width: (buildingWidth - 30) * 0.25, length: (buildingLength - 30) * 0.12 } }
      ];
    } else if (totalSF >= 3000) {
      // Medium building - office or restaurant
      rooms = [
        { name: "MAIN AREA", type: "office", size: Math.floor(totalSF * 0.7), position: { x: 10, y: 10 }, dimensions: { width: (buildingWidth - 30) * 0.75, length: buildingLength - 20 } },
        { name: "CONFERENCE", type: "conference", size: Math.floor(totalSF * 0.15), position: { x: 10 + (buildingWidth - 30) * 0.75 + 10, y: 10 }, dimensions: { width: (buildingWidth - 30) * 0.2, length: (buildingLength - 30) * 0.4 } },
        { name: "BREAK ROOM", type: "kitchen", size: Math.floor(totalSF * 0.1), position: { x: 10 + (buildingWidth - 30) * 0.75 + 10, y: 10 + (buildingLength - 30) * 0.4 + 10 }, dimensions: { width: (buildingWidth - 30) * 0.2, length: (buildingLength - 30) * 0.25 } },
        { name: "RESTROOM", type: "restroom", size: Math.floor(totalSF * 0.05), position: { x: 10 + (buildingWidth - 30) * 0.75 + 10, y: 10 + (buildingLength - 30) * 0.65 + 15 }, dimensions: { width: (buildingWidth - 30) * 0.2, length: (buildingLength - 30) * 0.2 } }
      ];
    } else {
      // Small building - simple layout
      rooms = [
        { name: "MAIN SPACE", type: "office", size: Math.floor(totalSF * 0.8), position: { x: 10, y: 10 }, dimensions: { width: buildingWidth - 20, length: (buildingLength - 30) * 0.8 } },
        { name: "SUPPORT", type: "storage", size: Math.floor(totalSF * 0.2), position: { x: 10, y: 10 + (buildingLength - 30) * 0.8 + 10 }, dimensions: { width: buildingWidth - 20, length: (buildingLength - 30) * 0.15 } }
      ];
    }
  }
  
  // Rooms are now properly configured
  
  const SCALE = 8; // Pixels per foot
  
  // Room type colors for easy identification - stronger colors for better visibility
  const roomColors = {
    warehouse: '#cfe2ff',    // Blue
    office: '#d4edda',       // Green  
    conference: '#f8d7da',   // Pink
    kitchen: '#fff3cd',      // Yellow
    restroom: '#cce5ff',     // Light blue
    storage: '#e2e3e5',      // Gray
    lobby: '#d1ecf1'         // Cyan
  };
  
  return (
    <div className="professional-floor-plan" style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <h3>{projectName} - Floor Plan</h3>
        <p>Building: {buildingWidth}' × {buildingLength}' ({totalSF.toLocaleString()} SF)</p>
      </div>
      
      <div style={{ border: '2px solid #333', backgroundColor: 'white', display: 'inline-block' }}>
        <svg 
          width={buildingWidth * SCALE + 100} 
          height={buildingLength * SCALE + 100}
          style={{ display: 'block' }}
        >
          {/* Building outline */}
          <rect 
            x={50} 
            y={50} 
            width={buildingWidth * SCALE} 
            height={buildingLength * SCALE}
            fill="white" 
            stroke="black" 
            strokeWidth="4"
          />
          
          {/* Grid lines every 10 feet */}
          {Array.from({ length: Math.floor(buildingWidth / 10) + 1 }, (_, i) => (
            <line 
              key={`v${i}`}
              x1={50 + i * 10 * SCALE} 
              y1={50} 
              x2={50 + i * 10 * SCALE} 
              y2={50 + buildingLength * SCALE}
              stroke="#ddd" 
              strokeWidth="0.5"
            />
          ))}
          {Array.from({ length: Math.floor(buildingLength / 10) + 1 }, (_, i) => (
            <line 
              key={`h${i}`}
              x1={50} 
              y1={50 + i * 10 * SCALE} 
              x2={50 + buildingWidth * SCALE} 
              y2={50 + i * 10 * SCALE}
              stroke="#ddd" 
              strokeWidth="0.5"
            />
          ))}
          
          {/* Rooms */}
          {rooms.map((room, index) => {
            const x = 50 + room.position.x * SCALE;
            const y = 50 + room.position.y * SCALE;
            const width = room.dimensions.width * SCALE;
            const height = room.dimensions.length * SCALE;
            const color = roomColors[room.type] || '#f9f9f9';
            
            return (
              <g key={index}>
                {/* Room fill */}
                <rect 
                  x={x} 
                  y={y} 
                  width={width} 
                  height={height}
                  fill={color} 
                  stroke="black" 
                  strokeWidth="2"
                />
                
                {/* Room label */}
                <text 
                  x={x + width/2} 
                  y={y + height/2 - 10} 
                  textAnchor="middle" 
                  fontSize="14" 
                  fontWeight="bold"
                  fill="black"
                >
                  {room.name}
                </text>
                
                {/* Room size */}
                <text 
                  x={x + width/2} 
                  y={y + height/2 + 10} 
                  textAnchor="middle" 
                  fontSize="12"
                  fill="black"
                >
                  {room.size.toLocaleString()} SF
                </text>
                
                {/* Room dimensions */}
                <text 
                  x={x + width/2} 
                  y={y + height/2 + 25} 
                  textAnchor="middle" 
                  fontSize="10"
                  fill="#666"
                >
                  {Math.round(room.dimensions.width)}' × {Math.round(room.dimensions.length)}'
                </text>
              </g>
            );
          })}
          
          {/* Building dimensions */}
          <text 
            x={50 + buildingWidth * SCALE / 2} 
            y={40} 
            textAnchor="middle" 
            fontSize="16" 
            fontWeight="bold"
          >
            {buildingWidth}'-0"
          </text>
          <text 
            x={30} 
            y={50 + buildingLength * SCALE / 2} 
            textAnchor="middle" 
            fontSize="16" 
            fontWeight="bold"
            transform={`rotate(-90, 30, ${50 + buildingLength * SCALE / 2})`}
          >
            {buildingLength}'-0"
          </text>
          
          {/* North arrow */}
          <g transform={`translate(${50 + buildingWidth * SCALE - 40}, 90)`}>
            <circle cx="0" cy="0" r="25" fill="white" stroke="black" strokeWidth="2"/>
            <path d="M 0,-18 L -6,8 L 0,4 L 6,8 Z" fill="black"/>
            <text x="0" y="-22" textAnchor="middle" fontSize="12" fontWeight="bold">N</text>
          </g>
          
          {/* Scale */}
          <g transform={`translate(70, ${50 + buildingLength * SCALE + 30})`}>
            <line x1="0" y1="0" x2={40 * SCALE} y2="0" stroke="black" strokeWidth="2"/>
            <line x1="0" y1="-5" x2="0" y2="5" stroke="black" strokeWidth="2"/>
            <line x1={40 * SCALE} y1="-5" x2={40 * SCALE} y2="5" stroke="black" strokeWidth="2"/>
            <text x={20 * SCALE} y="-10" textAnchor="middle" fontSize="12">40 FEET</text>
          </g>
          
          {/* Title block */}
          <g transform={`translate(${50 + buildingWidth * SCALE - 200}, ${50 + buildingLength * SCALE - 80})`}>
            <rect x="0" y="0" width="180" height="60" fill="white" stroke="black" strokeWidth="2"/>
            <text x="10" y="20" fontSize="14" fontWeight="bold">{projectName}</text>
            <text x="10" y="35" fontSize="10">FLOOR PLAN</text>
            <text x="10" y="50" fontSize="10">SCALE: 1/8" = 1'-0"</text>
          </g>
        </svg>
      </div>
    </div>
  );
};

export default ProfessionalFloorPlan;