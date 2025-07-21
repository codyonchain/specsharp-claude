from typing import List, Dict, Any, Optional, Tuple
import math
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

class RoomType(str, Enum):
    OFFICE = "office"
    OPEN_OFFICE = "open_office"
    CONFERENCE = "conference"
    RESTROOM = "restroom"
    KITCHEN = "kitchen"
    STORAGE = "storage"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    LOBBY = "lobby"
    WAREHOUSE = "warehouse"
    LOADING_DOCK = "loading_dock"
    CORRIDOR = "corridor"

class EquipmentType(str, Enum):
    HVAC = "hvac"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FIRE = "fire"

@dataclass
class Position:
    x: float
    y: float

@dataclass
class Dimensions:
    width: float
    length: float

@dataclass
class Room:
    id: str
    name: str
    type: RoomType
    size: float  # square feet
    position: Position
    dimensions: Dimensions
    
@dataclass
class Equipment:
    id: str
    type: EquipmentType
    name: str
    location: Any  # Can be string like "roof" or Position

@dataclass
class BuildingArea:
    type: str
    dimensions: Dimensions
    position: Position
    features: List[str]
    rooms: List[Room]

@dataclass
class FloorPlan:
    building_dimensions: Dimensions
    areas: List[BuildingArea]
    equipment: List[Equipment]
    grid_size: float = 10.0  # 10ft grid


class FloorPlanService:
    """Service for generating professional floor plans"""
    
    def __init__(self):
        self.grid_size = 5.0  # 5ft grid for more precision
        self.min_corridor_width = 8.0  # Generous corridors
        
        # Standard room sizes (min, max in sqft)
        self.room_sizes = {
            RoomType.OFFICE: (120, 200),
            RoomType.CONFERENCE: (300, 500),
            RoomType.RESTROOM: (50, 150),
            RoomType.KITCHEN: (150, 300),
            RoomType.STORAGE: (50, 200),
            RoomType.MECHANICAL: (200, 400),
            RoomType.ELECTRICAL: (100, 200),
            RoomType.LOBBY: (200, 600),
        }
    
    def generate_floor_plan(
        self, 
        square_footage: float,
        project_type: str,
        building_mix: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Generate a professional floor plan based on project parameters"""
        
        if project_type == "mixed_use" and building_mix:
            return self._generate_mixed_use_plan(square_footage, building_mix)
        elif project_type == "commercial":
            return self._generate_commercial_plan(square_footage)
        elif project_type == "industrial":
            return self._generate_industrial_plan(square_footage)
        else:
            return self._generate_generic_plan(square_footage)
    
    def _generate_mixed_use_plan(
        self, 
        total_sqft: float, 
        building_mix: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate a mixed-use building floor plan"""
        
        # Calculate dimensions assuming rectangular building
        aspect_ratio = 2.0  # Length to width ratio
        width = math.sqrt(total_sqft / aspect_ratio)
        length = width * aspect_ratio
        
        # Round to grid
        width = self._round_to_grid(width)
        length = self._round_to_grid(length)
        
        areas = []
        equipment = []
        
        # Calculate area sizes
        warehouse_pct = building_mix.get('warehouse', 0.7)
        office_pct = building_mix.get('office', 0.3)
        
        warehouse_length = length * warehouse_pct
        office_length = length * office_pct
        
        # Create warehouse area
        if warehouse_pct > 0:
            warehouse_area = self._create_warehouse_area(
                width, warehouse_length, Position(0, 0)
            )
            areas.append(warehouse_area)
            
            # Add warehouse equipment
            equipment.extend(self._place_warehouse_equipment(
                warehouse_area.dimensions, warehouse_area.position
            ))
        
        # Create office area
        if office_pct > 0:
            office_area = self._create_office_area(
                width, office_length, Position(0, warehouse_length)
            )
            areas.append(office_area)
            
            # Add office equipment
            equipment.extend(self._place_office_equipment(
                office_area.dimensions, office_area.position
            ))
        
        # Add rooftop equipment
        equipment.extend(self._place_rooftop_equipment(width, length))
        
        floor_plan = FloorPlan(
            building_dimensions=Dimensions(width, length),
            areas=areas,
            equipment=equipment
        )
        
        return self._floor_plan_to_dict(floor_plan)
    
    def _create_warehouse_area(
        self, 
        width: float, 
        length: float, 
        position: Position
    ) -> BuildingArea:
        """Create warehouse area with loading docks"""
        
        rooms = []
        
        # Main warehouse space
        warehouse_room = Room(
            id=str(uuid.uuid4())[:8],
            name="Warehouse Floor",
            type=RoomType.WAREHOUSE,
            size=width * length * 0.85,  # 85% of area
            position=Position(position.x + 10, position.y + 10),
            dimensions=Dimensions(width - 20, length - 40)
        )
        rooms.append(warehouse_room)
        
        # Loading docks along one side
        dock_width = 14  # Standard dock door width
        num_docks = int(length / 50)  # One dock per 50ft
        
        for i in range(min(num_docks, 4)):  # Max 4 docks
            dock = Room(
                id=str(uuid.uuid4())[:8],
                name=f"Loading Dock {i+1}",
                type=RoomType.LOADING_DOCK,
                size=dock_width * 20,
                position=Position(
                    position.x + width - 20,
                    position.y + 30 + (i * 50)
                ),
                dimensions=Dimensions(20, dock_width)
            )
            rooms.append(dock)
        
        # Small office for shipping/receiving
        shipping_office = Room(
            id=str(uuid.uuid4())[:8],
            name="Shipping Office",
            type=RoomType.OFFICE,
            size=200,
            position=Position(position.x + width - 30, position.y + 10),
            dimensions=Dimensions(20, 10)
        )
        rooms.append(shipping_office)
        
        # Restrooms
        restroom_m = Room(
            id=str(uuid.uuid4())[:8],
            name="Men's Restroom",
            type=RoomType.RESTROOM,
            size=100,
            position=Position(position.x + 10, position.y + length - 20),
            dimensions=Dimensions(10, 10)
        )
        rooms.append(restroom_m)
        
        restroom_w = Room(
            id=str(uuid.uuid4())[:8],
            name="Women's Restroom",
            type=RoomType.RESTROOM,
            size=100,
            position=Position(position.x + 20, position.y + length - 20),
            dimensions=Dimensions(10, 10)
        )
        rooms.append(restroom_w)
        
        return BuildingArea(
            type="warehouse",
            dimensions=Dimensions(width, length),
            position=position,
            features=["loading_docks", "column_grid", "high_bay"],
            rooms=rooms
        )
    
    def _create_office_area(
        self, 
        width: float, 
        length: float, 
        position: Position
    ) -> BuildingArea:
        """Create office area with logical room layout"""
        
        rooms = []
        
        # Entry lobby
        lobby = Room(
            id=str(uuid.uuid4())[:8],
            name="Reception/Lobby",
            type=RoomType.LOBBY,
            size=400,
            position=Position(position.x + width/2 - 20, position.y + 10),
            dimensions=Dimensions(40, 10)
        )
        rooms.append(lobby)
        
        # Open office area
        open_office = Room(
            id=str(uuid.uuid4())[:8],
            name="Open Office",
            type=RoomType.OPEN_OFFICE,
            size=width * length * 0.4,  # 40% of office area
            position=Position(position.x + 20, position.y + 30),
            dimensions=Dimensions(width - 40, length * 0.5)
        )
        rooms.append(open_office)
        
        # Private offices along perimeter
        office_size = 150
        num_offices = int((width - 40) / 15)  # 15ft wide offices
        
        for i in range(min(num_offices, 6)):
            office = Room(
                id=str(uuid.uuid4())[:8],
                name=f"Office {i+1}",
                type=RoomType.OFFICE,
                size=office_size,
                position=Position(
                    position.x + 10 + (i * 15),
                    position.y + length - 20
                ),
                dimensions=Dimensions(15, 10)
            )
            rooms.append(office)
        
        # Conference rooms
        conference1 = Room(
            id=str(uuid.uuid4())[:8],
            name="Large Conference",
            type=RoomType.CONFERENCE,
            size=400,
            position=Position(position.x + width - 40, position.y + 30),
            dimensions=Dimensions(20, 20)
        )
        rooms.append(conference1)
        
        conference2 = Room(
            id=str(uuid.uuid4())[:8],
            name="Small Conference",
            type=RoomType.CONFERENCE,
            size=200,
            position=Position(position.x + width - 40, position.y + 50),
            dimensions=Dimensions(20, 10)
        )
        rooms.append(conference2)
        
        # Kitchen/Break room
        kitchen = Room(
            id=str(uuid.uuid4())[:8],
            name="Break Room",
            type=RoomType.KITCHEN,
            size=300,
            position=Position(position.x + width - 40, position.y + 70),
            dimensions=Dimensions(20, 15)
        )
        rooms.append(kitchen)
        
        # Restrooms
        restroom_m = Room(
            id=str(uuid.uuid4())[:8],
            name="Men's Restroom",
            type=RoomType.RESTROOM,
            size=100,
            position=Position(position.x + 10, position.y + 10),
            dimensions=Dimensions(10, 10)
        )
        rooms.append(restroom_m)
        
        restroom_w = Room(
            id=str(uuid.uuid4())[:8],
            name="Women's Restroom",
            type=RoomType.RESTROOM,
            size=100,
            position=Position(position.x + 20, position.y + 10),
            dimensions=Dimensions(10, 10)
        )
        rooms.append(restroom_w)
        
        # IT/Server room
        it_room = Room(
            id=str(uuid.uuid4())[:8],
            name="IT Room",
            type=RoomType.ELECTRICAL,
            size=150,
            position=Position(position.x + width - 20, position.y + 10),
            dimensions=Dimensions(10, 15)
        )
        rooms.append(it_room)
        
        return BuildingArea(
            type="office",
            dimensions=Dimensions(width, length),
            position=position,
            features=["suspended_ceiling", "vav_boxes", "perimeter_offices"],
            rooms=rooms
        )
    
    def _place_warehouse_equipment(
        self, 
        dimensions: Dimensions, 
        position: Position
    ) -> List[Equipment]:
        """Place equipment in warehouse area"""
        
        equipment = []
        
        # Main electrical panel
        equipment.append(Equipment(
            id=str(uuid.uuid4())[:8],
            type=EquipmentType.ELECTRICAL,
            name="Main Distribution Panel",
            location=Position(position.x + 10, position.y + 10)
        ))
        
        # Fire sprinkler riser
        equipment.append(Equipment(
            id=str(uuid.uuid4())[:8],
            type=EquipmentType.FIRE,
            name="Sprinkler Riser",
            location=Position(position.x + dimensions.width - 10, position.y + 10)
        ))
        
        return equipment
    
    def _place_office_equipment(
        self, 
        dimensions: Dimensions, 
        position: Position
    ) -> List[Equipment]:
        """Place equipment in office area"""
        
        equipment = []
        
        # Electrical sub-panel
        equipment.append(Equipment(
            id=str(uuid.uuid4())[:8],
            type=EquipmentType.ELECTRICAL,
            name="Office Panel",
            location=Position(position.x + dimensions.width - 10, position.y + 10)
        ))
        
        # Water heater
        equipment.append(Equipment(
            id=str(uuid.uuid4())[:8],
            type=EquipmentType.PLUMBING,
            name="Water Heater",
            location=Position(position.x + 30, position.y + 10)
        ))
        
        return equipment
    
    def _place_rooftop_equipment(self, width: float, length: float) -> List[Equipment]:
        """Place HVAC equipment on roof"""
        
        equipment = []
        
        # Calculate number of RTUs based on square footage
        total_sqft = width * length
        tons_required = total_sqft / 400  # Rule of thumb: 400 sqft per ton
        units_needed = math.ceil(tons_required / 30)  # 30-ton units
        
        for i in range(units_needed):
            equipment.append(Equipment(
                id=str(uuid.uuid4())[:8],
                type=EquipmentType.HVAC,
                name=f"RTU-{i+1}",
                location="roof"
            ))
        
        return equipment
    
    def _generate_commercial_plan(self, square_footage: float) -> Dict[str, Any]:
        """Generate a standard commercial building plan"""
        # Simplified implementation
        building_mix = {"office": 1.0}
        return self._generate_mixed_use_plan(square_footage, building_mix)
    
    def _generate_industrial_plan(self, square_footage: float) -> Dict[str, Any]:
        """Generate an industrial building plan"""
        # Simplified implementation
        building_mix = {"warehouse": 1.0}
        return self._generate_mixed_use_plan(square_footage, building_mix)
    
    def _generate_generic_plan(self, square_footage: float) -> Dict[str, Any]:
        """Generate a generic building plan"""
        # Default to office
        return self._generate_commercial_plan(square_footage)
    
    def _round_to_grid(self, value: float) -> float:
        """Round value to nearest grid size"""
        return round(value / self.grid_size) * self.grid_size
    
    def _floor_plan_to_dict(self, floor_plan: FloorPlan) -> Dict[str, Any]:
        """Convert FloorPlan dataclass to dictionary"""
        return {
            "building_dimensions": {
                "width": floor_plan.building_dimensions.width,
                "length": floor_plan.building_dimensions.length
            },
            "areas": [
                {
                    "type": area.type,
                    "dimensions": {
                        "width": area.dimensions.width,
                        "length": area.dimensions.length
                    },
                    "position": {"x": area.position.x, "y": area.position.y},
                    "features": area.features,
                    "rooms": [
                        {
                            "id": room.id,
                            "name": room.name,
                            "type": room.type,
                            "size": room.size,
                            "position": {"x": room.position.x, "y": room.position.y},
                            "dimensions": {
                                "width": room.dimensions.width,
                                "length": room.dimensions.length
                            }
                        }
                        for room in area.rooms
                    ]
                }
                for area in floor_plan.areas
            ],
            "equipment": [
                {
                    "id": eq.id,
                    "type": eq.type,
                    "name": eq.name,
                    "location": eq.location if isinstance(eq.location, str) 
                               else {"x": eq.location.x, "y": eq.location.y}
                }
                for eq in floor_plan.equipment
            ],
            "grid_size": floor_plan.grid_size
        }


# Create singleton instance
floor_plan_service = FloorPlanService()