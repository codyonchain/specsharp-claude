from typing import List, Dict, Any, Optional, Tuple
import math
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

class WallType(str, Enum):
    EXTERIOR = "exterior"
    INTERIOR = "interior"
    PARTITION = "partition"

class DoorType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"
    OVERHEAD = "overhead"
    SLIDING = "sliding"

class FixtureType(str, Enum):
    TOILET = "toilet"
    SINK = "sink"
    URINAL = "urinal"
    WATER_FOUNTAIN = "water_fountain"

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Wall:
    id: str
    type: WallType
    start: Point
    end: Point
    thickness: float = 6.0  # inches

@dataclass
class Door:
    id: str
    type: DoorType
    position: Point
    width: float
    wall_id: str
    swing_direction: str = "in"  # in, out, both
    swing_side: str = "left"  # left, right

@dataclass
class Window:
    id: str
    position: Point
    width: float
    wall_id: str

@dataclass
class Fixture:
    id: str
    type: FixtureType
    position: Point
    rotation: float = 0.0

@dataclass
class DimensionLine:
    id: str
    start: Point
    end: Point
    offset: float
    text: str

@dataclass
class Space:
    id: str
    name: str
    type: str
    points: List[Point]  # Polygon vertices
    area: float
    height: float = 9.0

@dataclass
class TradeZone:
    id: str
    trade: str
    type: str  # coverage, circuit, wet_wall, etc.
    points: List[Point]
    equipment_id: Optional[str] = None
    description: Optional[str] = None

@dataclass
class ArchitecturalFloorPlan:
    building_width: float
    building_height: float
    walls: List[Wall]
    doors: List[Door]
    windows: List[Window]
    fixtures: List[Fixture]
    spaces: List[Space]
    dimensions: List[DimensionLine]
    trade_zones: List[TradeZone]
    scale: str = "1/8\" = 1'-0\""
    units: str = "feet"


class ArchitecturalFloorPlanService:
    """Service for generating professional architectural floor plans"""
    
    def __init__(self):
        self.grid_size = 2.0  # 2ft grid for precision
        self.wall_thickness = {
            WallType.EXTERIOR: 8.0,  # inches
            WallType.INTERIOR: 6.0,
            WallType.PARTITION: 4.0
        }
        
    def generate_architectural_plan(
        self, 
        square_footage: float,
        project_type: str,
        building_mix: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Generate a professional architectural floor plan"""
        
        # Calculate optimal dimensions
        dimensions = self._calculate_optimal_dimensions(square_footage)
        width, height = dimensions
        
        # Generate based on project type
        if project_type == "mixed_use" and building_mix:
            plan = self._generate_mixed_use_architectural(width, height, building_mix)
        elif project_type == "commercial":
            plan = self._generate_commercial_architectural(width, height)
        elif project_type == "industrial":
            plan = self._generate_industrial_architectural(width, height)
        else:
            plan = self._generate_office_architectural(width, height)
            
        # Add trade zones
        plan.trade_zones = self._generate_trade_zones(plan)
        
        # Convert to dict and ensure proper orientation
        plan_dict = self._floor_plan_to_dict(plan)
        return self._ensure_landscape_orientation(plan_dict)
    
    def _calculate_optimal_dimensions(self, square_footage: float) -> Tuple[float, float]:
        """Calculate building dimensions for optimal aspect ratio"""
        # Target aspect ratio between 1.5:1 and 2:1
        aspect_ratio = 1.618  # Golden ratio
        
        # Calculate dimensions
        width = math.sqrt(square_footage * aspect_ratio)
        height = square_footage / width
        
        # Round to grid
        width = self._round_to_grid(width, 5.0)
        height = self._round_to_grid(height, 5.0)
        
        return (width, height)
    
    def _generate_mixed_use_architectural(
        self, 
        width: float, 
        height: float, 
        building_mix: Dict[str, float]
    ) -> ArchitecturalFloorPlan:
        """Generate mixed-use architectural plan"""
        
        walls = []
        spaces = []
        doors = []
        windows = []
        fixtures = []
        dimensions = []
        
        # Exterior walls
        exterior_walls = self._create_exterior_walls(width, height)
        walls.extend(exterior_walls)
        
        # Calculate zone sizes
        if building_mix:
            warehouse_pct = building_mix.get('warehouse', 0.7)
            office_pct = building_mix.get('office', 0.3)
        else:
            warehouse_pct = 0.7
            office_pct = 0.3
        
        warehouse_height = height * warehouse_pct
        office_height = height * office_pct
        
        # Warehouse section
        if warehouse_pct > 0:
            warehouse_elements = self._create_warehouse_section(
                width, warehouse_height, Point(0, 0)
            )
            walls.extend(warehouse_elements['walls'])
            spaces.extend(warehouse_elements['spaces'])
            doors.extend(warehouse_elements['doors'])
            
        # Separation wall
        if warehouse_pct > 0 and office_pct > 0:
            separation_wall = Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=Point(0, warehouse_height),
                end=Point(width, warehouse_height),
                thickness=8.0  # Fire-rated wall
            )
            walls.append(separation_wall)
        
        # Office section
        if office_pct > 0:
            office_elements = self._create_office_section(
                width, office_height, Point(0, warehouse_height)
            )
            walls.extend(office_elements['walls'])
            spaces.extend(office_elements['spaces'])
            doors.extend(office_elements['doors'])
            windows.extend(office_elements['windows'])
            fixtures.extend(office_elements['fixtures'])
        
        # Add dimension lines
        dimensions = self._create_dimension_lines(width, height)
        
        return ArchitecturalFloorPlan(
            building_width=width,
            building_height=height,
            walls=walls,
            doors=doors,
            windows=windows,
            fixtures=fixtures,
            spaces=spaces,
            dimensions=dimensions,
            trade_zones=[]
        )
    
    def _create_exterior_walls(self, width: float, height: float) -> List[Wall]:
        """Create exterior walls with proper corners"""
        walls = []
        
        # Bottom wall
        walls.append(Wall(
            id=str(uuid.uuid4())[:8],
            type=WallType.EXTERIOR,
            start=Point(0, 0),
            end=Point(width, 0),
            thickness=self.wall_thickness[WallType.EXTERIOR]
        ))
        
        # Right wall
        walls.append(Wall(
            id=str(uuid.uuid4())[:8],
            type=WallType.EXTERIOR,
            start=Point(width, 0),
            end=Point(width, height),
            thickness=self.wall_thickness[WallType.EXTERIOR]
        ))
        
        # Top wall
        walls.append(Wall(
            id=str(uuid.uuid4())[:8],
            type=WallType.EXTERIOR,
            start=Point(width, height),
            end=Point(0, height),
            thickness=self.wall_thickness[WallType.EXTERIOR]
        ))
        
        # Left wall
        walls.append(Wall(
            id=str(uuid.uuid4())[:8],
            type=WallType.EXTERIOR,
            start=Point(0, height),
            end=Point(0, 0),
            thickness=self.wall_thickness[WallType.EXTERIOR]
        ))
        
        return walls
    
    def _create_warehouse_section(
        self, 
        width: float, 
        height: float, 
        origin: Point
    ) -> Dict[str, List]:
        """Create warehouse section with proper architectural elements"""
        
        walls = []
        spaces = []
        doors = []
        
        # Main warehouse space
        warehouse_space = Space(
            id=str(uuid.uuid4())[:8],
            name="Warehouse",
            type="warehouse",
            points=[
                Point(origin.x + 20, origin.y + 20),
                Point(origin.x + width - 20, origin.y + 20),
                Point(origin.x + width - 20, origin.y + height - 20),
                Point(origin.x + 20, origin.y + height - 20)
            ],
            area=(width - 40) * (height - 40),
            height=24.0  # High bay
        )
        spaces.append(warehouse_space)
        
        # Loading dock doors
        dock_spacing = 20.0  # 20ft between dock doors
        dock_width = 10.0   # 10ft wide dock doors
        num_docks = min(4, int((height - 40) / dock_spacing))
        
        right_wall_id = str(uuid.uuid4())[:8]
        for i in range(num_docks):
            dock_y = origin.y + 30 + (i * dock_spacing)
            door = Door(
                id=str(uuid.uuid4())[:8],
                type=DoorType.OVERHEAD,
                position=Point(origin.x + width - 5, dock_y),
                width=dock_width,
                wall_id=right_wall_id,
                swing_direction="up"
            )
            doors.append(door)
            
            # Add small office next to first dock
            if i == 0:
                office_walls = [
                    Wall(
                        id=str(uuid.uuid4())[:8],
                        type=WallType.INTERIOR,
                        start=Point(origin.x + width - 30, dock_y - 5),
                        end=Point(origin.x + width - 30, dock_y + 15)
                    ),
                    Wall(
                        id=str(uuid.uuid4())[:8],
                        type=WallType.INTERIOR,
                        start=Point(origin.x + width - 30, dock_y + 15),
                        end=Point(origin.x + width - 10, dock_y + 15)
                    )
                ]
                walls.extend(office_walls)
                
                office_space = Space(
                    id=str(uuid.uuid4())[:8],
                    name="Dock Office",
                    type="office",
                    points=[
                        Point(origin.x + width - 30, dock_y - 5),
                        Point(origin.x + width - 10, dock_y - 5),
                        Point(origin.x + width - 10, dock_y + 15),
                        Point(origin.x + width - 30, dock_y + 15)
                    ],
                    area=20 * 20
                )
                spaces.append(office_space)
        
        # Restrooms in corner
        restroom_walls = self._create_restroom_walls(
            Point(origin.x + 10, origin.y + height - 30),
            20, 20
        )
        walls.extend(restroom_walls)
        
        return {
            'walls': walls,
            'spaces': spaces,
            'doors': doors
        }
    
    def _create_office_section(
        self, 
        width: float, 
        height: float, 
        origin: Point
    ) -> Dict[str, List]:
        """Create office section with proper architectural elements"""
        
        walls = []
        spaces = []
        doors = []
        windows = []
        fixtures = []
        
        # Main entry
        entry_door = Door(
            id=str(uuid.uuid4())[:8],
            type=DoorType.DOUBLE,
            position=Point(origin.x + width/2, origin.y),
            width=6.0,
            wall_id="front",
            swing_direction="in"
        )
        doors.append(entry_door)
        
        # Lobby
        lobby_width = 30
        lobby = Space(
            id=str(uuid.uuid4())[:8],
            name="Lobby",
            type="lobby",
            points=[
                Point(origin.x + width/2 - lobby_width/2, origin.y + 5),
                Point(origin.x + width/2 + lobby_width/2, origin.y + 5),
                Point(origin.x + width/2 + lobby_width/2, origin.y + 25),
                Point(origin.x + width/2 - lobby_width/2, origin.y + 25)
            ],
            area=lobby_width * 20
        )
        spaces.append(lobby)
        
        # Corridor
        corridor_wall_left = Wall(
            id=str(uuid.uuid4())[:8],
            type=WallType.INTERIOR,
            start=Point(origin.x + width/2 - 4, origin.y + 25),
            end=Point(origin.x + width/2 - 4, origin.y + height - 10)
        )
        corridor_wall_right = Wall(
            id=str(uuid.uuid4())[:8],
            type=WallType.INTERIOR,
            start=Point(origin.x + width/2 + 4, origin.y + 25),
            end=Point(origin.x + width/2 + 4, origin.y + height - 10)
        )
        walls.extend([corridor_wall_left, corridor_wall_right])
        
        # Private offices along left side
        office_width = 15
        office_depth = 12
        num_offices = int((height - 35) / office_width)
        
        for i in range(num_offices):
            office_y = origin.y + 25 + (i * office_width)
            
            # Office walls
            office_wall = Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=Point(origin.x + 10, office_y),
                end=Point(origin.x + 10 + office_depth, office_y)
            )
            walls.append(office_wall)
            
            # Office door
            door = Door(
                id=str(uuid.uuid4())[:8],
                type=DoorType.SINGLE,
                position=Point(origin.x + 10 + office_depth, office_y + 2),
                width=3.0,
                wall_id=corridor_wall_left.id,
                swing_direction="in",
                swing_side="left"
            )
            doors.append(door)
            
            # Office window
            window = Window(
                id=str(uuid.uuid4())[:8],
                position=Point(origin.x + 5, office_y + office_width/2),
                width=8.0,
                wall_id="exterior_left"
            )
            windows.append(window)
            
            # Office space
            office = Space(
                id=str(uuid.uuid4())[:8],
                name=f"Office {i+1}",
                type="office",
                points=[
                    Point(origin.x + 10, office_y),
                    Point(origin.x + 10 + office_depth, office_y),
                    Point(origin.x + 10 + office_depth, office_y + office_width - 1),
                    Point(origin.x + 10, office_y + office_width - 1)
                ],
                area=office_depth * (office_width - 1)
            )
            spaces.append(office)
        
        # Conference rooms on right side
        conf_room = self._create_conference_room(
            Point(origin.x + width - 35, origin.y + 25),
            25, 20
        )
        walls.extend(conf_room['walls'])
        spaces.extend(conf_room['spaces'])
        doors.extend(conf_room['doors'])
        windows.extend(conf_room['windows'])
        
        # Restrooms
        restroom_elements = self._create_restrooms(
            Point(origin.x + width - 35, origin.y + 50),
            25, 15
        )
        walls.extend(restroom_elements['walls'])
        spaces.extend(restroom_elements['spaces'])
        doors.extend(restroom_elements['doors'])
        fixtures.extend(restroom_elements['fixtures'])
        
        return {
            'walls': walls,
            'spaces': spaces,
            'doors': doors,
            'windows': windows,
            'fixtures': fixtures
        }
    
    def _create_restrooms(
        self, 
        origin: Point, 
        width: float, 
        height: float
    ) -> Dict[str, List]:
        """Create restroom layout with fixtures"""
        
        walls = []
        spaces = []
        doors = []
        fixtures = []
        
        # Dividing wall
        divider = Wall(
            id=str(uuid.uuid4())[:8],
            type=WallType.INTERIOR,
            start=Point(origin.x + width/2, origin.y),
            end=Point(origin.x + width/2, origin.y + height)
        )
        walls.append(divider)
        
        # Men's restroom
        mens_space = Space(
            id=str(uuid.uuid4())[:8],
            name="Men's Restroom",
            type="restroom",
            points=[
                Point(origin.x, origin.y),
                Point(origin.x + width/2 - 0.5, origin.y),
                Point(origin.x + width/2 - 0.5, origin.y + height),
                Point(origin.x, origin.y + height)
            ],
            area=(width/2 - 0.5) * height
        )
        spaces.append(mens_space)
        
        # Men's door
        mens_door = Door(
            id=str(uuid.uuid4())[:8],
            type=DoorType.SINGLE,
            position=Point(origin.x + 2, origin.y),
            width=3.0,
            wall_id="corridor",
            swing_direction="in"
        )
        doors.append(mens_door)
        
        # Men's fixtures
        fixtures.extend([
            Fixture(
                id=str(uuid.uuid4())[:8],
                type=FixtureType.TOILET,
                position=Point(origin.x + 2, origin.y + height - 3),
                rotation=0
            ),
            Fixture(
                id=str(uuid.uuid4())[:8],
                type=FixtureType.URINAL,
                position=Point(origin.x + 5, origin.y + height - 3),
                rotation=0
            ),
            Fixture(
                id=str(uuid.uuid4())[:8],
                type=FixtureType.SINK,
                position=Point(origin.x + width/4, origin.y + 2),
                rotation=180
            )
        ])
        
        # Women's restroom
        womens_space = Space(
            id=str(uuid.uuid4())[:8],
            name="Women's Restroom",
            type="restroom",
            points=[
                Point(origin.x + width/2 + 0.5, origin.y),
                Point(origin.x + width, origin.y),
                Point(origin.x + width, origin.y + height),
                Point(origin.x + width/2 + 0.5, origin.y + height)
            ],
            area=(width/2 - 0.5) * height
        )
        spaces.append(womens_space)
        
        # Women's door
        womens_door = Door(
            id=str(uuid.uuid4())[:8],
            type=DoorType.SINGLE,
            position=Point(origin.x + width - 5, origin.y),
            width=3.0,
            wall_id="corridor",
            swing_direction="in"
        )
        doors.append(womens_door)
        
        # Women's fixtures
        fixtures.extend([
            Fixture(
                id=str(uuid.uuid4())[:8],
                type=FixtureType.TOILET,
                position=Point(origin.x + width/2 + 2, origin.y + height - 3),
                rotation=0
            ),
            Fixture(
                id=str(uuid.uuid4())[:8],
                type=FixtureType.TOILET,
                position=Point(origin.x + width/2 + 5, origin.y + height - 3),
                rotation=0
            ),
            Fixture(
                id=str(uuid.uuid4())[:8],
                type=FixtureType.SINK,
                position=Point(origin.x + 3*width/4, origin.y + 2),
                rotation=180
            )
        ])
        
        return {
            'walls': walls,
            'spaces': spaces,
            'doors': doors,
            'fixtures': fixtures
        }
    
    def _create_conference_room(
        self, 
        origin: Point, 
        width: float, 
        height: float
    ) -> Dict[str, List]:
        """Create conference room"""
        
        walls = []
        spaces = []
        doors = []
        windows = []
        
        # Conference room walls
        walls.extend([
            Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=origin,
                end=Point(origin.x + width, origin.y)
            ),
            Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=Point(origin.x, origin.y),
                end=Point(origin.x, origin.y + height)
            ),
            Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=Point(origin.x, origin.y + height),
                end=Point(origin.x + width, origin.y + height)
            )
        ])
        
        # Conference room space
        conf_space = Space(
            id=str(uuid.uuid4())[:8],
            name="Conference Room",
            type="conference",
            points=[
                origin,
                Point(origin.x + width, origin.y),
                Point(origin.x + width, origin.y + height),
                Point(origin.x, origin.y + height)
            ],
            area=width * height
        )
        spaces.append(conf_space)
        
        # Door
        door = Door(
            id=str(uuid.uuid4())[:8],
            type=DoorType.SINGLE,
            position=Point(origin.x, origin.y + height/2),
            width=3.0,
            wall_id="corridor",
            swing_direction="in"
        )
        doors.append(door)
        
        # Windows
        for i in range(2):
            window = Window(
                id=str(uuid.uuid4())[:8],
                position=Point(origin.x + width + 5, origin.y + 5 + (i * 10)),
                width=8.0,
                wall_id="exterior_right"
            )
            windows.append(window)
        
        return {
            'walls': walls,
            'spaces': spaces,
            'doors': doors,
            'windows': windows
        }
    
    def _create_dimension_lines(self, width: float, height: float) -> List[DimensionLine]:
        """Create dimension lines for the building"""
        dimensions = []
        
        # Overall width dimension
        dimensions.append(DimensionLine(
            id=str(uuid.uuid4())[:8],
            start=Point(0, -15),
            end=Point(width, -15),
            offset=15,
            text=f"{width}'-0\""
        ))
        
        # Overall height dimension
        dimensions.append(DimensionLine(
            id=str(uuid.uuid4())[:8],
            start=Point(-15, 0),
            end=Point(-15, height),
            offset=15,
            text=f"{height}'-0\""
        ))
        
        return dimensions
    
    def _generate_trade_zones(self, plan: ArchitecturalFloorPlan) -> List[TradeZone]:
        """Generate trade overlay zones"""
        zones = []
        
        # HVAC zones (based on spaces)
        for space in plan.spaces:
            if space.area > 1000:  # Large spaces get their own zone
                zone = TradeZone(
                    id=str(uuid.uuid4())[:8],
                    trade="hvac",
                    type="coverage",
                    points=space.points,
                    description=f"RTU Zone - {space.name}"
                )
                zones.append(zone)
        
        # Electrical zones
        # Main panel location
        panel_zone = TradeZone(
            id=str(uuid.uuid4())[:8],
            trade="electrical",
            type="panel",
            points=[
                Point(10, 10),
                Point(15, 10),
                Point(15, 15),
                Point(10, 15)
            ],
            description="Main Distribution Panel"
        )
        zones.append(panel_zone)
        
        # Plumbing zones (wet walls)
        for space in plan.spaces:
            if space.type == "restroom":
                # Create wet wall zone
                wet_wall = TradeZone(
                    id=str(uuid.uuid4())[:8],
                    trade="plumbing",
                    type="wet_wall",
                    points=self._expand_polygon(space.points, 2),
                    description=f"Wet Wall - {space.name}"
                )
                zones.append(wet_wall)
        
        return zones
    
    def _expand_polygon(self, points: List[Point], distance: float) -> List[Point]:
        """Expand a polygon by a given distance"""
        # Simple expansion - in practice would use proper polygon offset algorithm
        center_x = sum(p.x for p in points) / len(points)
        center_y = sum(p.y for p in points) / len(points)
        
        expanded = []
        for point in points:
            dx = point.x - center_x
            dy = point.y - center_y
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx = dx / length * distance
                dy = dy / length * distance
            expanded.append(Point(point.x + dx, point.y + dy))
        
        return expanded
    
    def _create_restroom_walls(
        self, 
        origin: Point, 
        width: float, 
        height: float
    ) -> List[Wall]:
        """Create basic restroom walls"""
        return [
            Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=origin,
                end=Point(origin.x + width, origin.y)
            ),
            Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=Point(origin.x + width, origin.y),
                end=Point(origin.x + width, origin.y + height)
            ),
            Wall(
                id=str(uuid.uuid4())[:8],
                type=WallType.INTERIOR,
                start=Point(origin.x, origin.y + height),
                end=Point(origin.x + width, origin.y + height)
            )
        ]
    
    def _round_to_grid(self, value: float, grid: float) -> float:
        """Round value to nearest grid size"""
        return round(value / grid) * grid
    
    def _floor_plan_to_dict(self, plan: ArchitecturalFloorPlan) -> Dict[str, Any]:
        """Convert floor plan to dictionary"""
        return {
            "building_width": plan.building_width,
            "building_height": plan.building_height,
            "walls": [
                {
                    "id": wall.id,
                    "type": wall.type,
                    "start": {"x": wall.start.x, "y": wall.start.y},
                    "end": {"x": wall.end.x, "y": wall.end.y},
                    "thickness": wall.thickness
                }
                for wall in plan.walls
            ],
            "doors": [
                {
                    "id": door.id,
                    "type": door.type,
                    "position": {"x": door.position.x, "y": door.position.y},
                    "width": door.width,
                    "wall_id": door.wall_id,
                    "swing_direction": door.swing_direction,
                    "swing_side": door.swing_side
                }
                for door in plan.doors
            ],
            "windows": [
                {
                    "id": window.id,
                    "position": {"x": window.position.x, "y": window.position.y},
                    "width": window.width,
                    "wall_id": window.wall_id
                }
                for window in plan.windows
            ],
            "fixtures": [
                {
                    "id": fixture.id,
                    "type": fixture.type,
                    "position": {"x": fixture.position.x, "y": fixture.position.y},
                    "rotation": fixture.rotation
                }
                for fixture in plan.fixtures
            ],
            "spaces": [
                {
                    "id": space.id,
                    "name": space.name,
                    "type": space.type,
                    "points": [{"x": p.x, "y": p.y} for p in space.points],
                    "area": space.area,
                    "height": space.height
                }
                for space in plan.spaces
            ],
            "dimensions": [
                {
                    "id": dim.id,
                    "start": {"x": dim.start.x, "y": dim.start.y},
                    "end": {"x": dim.end.x, "y": dim.end.y},
                    "offset": dim.offset,
                    "text": dim.text
                }
                for dim in plan.dimensions
            ],
            "trade_zones": [
                {
                    "id": zone.id,
                    "trade": zone.trade,
                    "type": zone.type,
                    "points": [{"x": p.x, "y": p.y} for p in zone.points],
                    "equipment_id": zone.equipment_id,
                    "description": zone.description
                }
                for zone in plan.trade_zones
            ],
            "scale": plan.scale,
            "units": plan.units
        }
    
    def _ensure_landscape_orientation(self, plan_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the plan is in landscape orientation"""
        if plan_dict["building_height"] > plan_dict["building_width"]:
            # Rotate 90 degrees
            plan_dict["rotated"] = True
            
            # Swap dimensions
            plan_dict["building_width"], plan_dict["building_height"] = \
                plan_dict["building_height"], plan_dict["building_width"]
            
            # Rotate all points
            for wall in plan_dict["walls"]:
                wall["start"]["x"], wall["start"]["y"] = \
                    wall["start"]["y"], plan_dict["building_width"] - wall["start"]["x"]
                wall["end"]["x"], wall["end"]["y"] = \
                    wall["end"]["y"], plan_dict["building_width"] - wall["end"]["x"]
            
            for door in plan_dict["doors"]:
                door["position"]["x"], door["position"]["y"] = \
                    door["position"]["y"], plan_dict["building_width"] - door["position"]["x"]
            
            for window in plan_dict["windows"]:
                window["position"]["x"], window["position"]["y"] = \
                    window["position"]["y"], plan_dict["building_width"] - window["position"]["x"]
            
            for fixture in plan_dict["fixtures"]:
                fixture["position"]["x"], fixture["position"]["y"] = \
                    fixture["position"]["y"], plan_dict["building_width"] - fixture["position"]["x"]
                fixture["rotation"] = (fixture["rotation"] + 90) % 360
            
            for space in plan_dict["spaces"]:
                for point in space["points"]:
                    point["x"], point["y"] = \
                        point["y"], plan_dict["building_width"] - point["x"]
            
            for dim in plan_dict["dimensions"]:
                dim["start"]["x"], dim["start"]["y"] = \
                    dim["start"]["y"], plan_dict["building_width"] - dim["start"]["x"]
                dim["end"]["x"], dim["end"]["y"] = \
                    dim["end"]["y"], plan_dict["building_width"] - dim["end"]["x"]
            
            for zone in plan_dict["trade_zones"]:
                for point in zone["points"]:
                    point["x"], point["y"] = \
                        point["y"], plan_dict["building_width"] - point["x"]
        else:
            plan_dict["rotated"] = False
        
        return plan_dict
    
    def _generate_commercial_architectural(self, width: float, height: float) -> ArchitecturalFloorPlan:
        """Generate commercial building plan"""
        # For now, reuse office logic
        return self._generate_office_architectural(width, height)
    
    def _generate_industrial_architectural(self, width: float, height: float) -> ArchitecturalFloorPlan:
        """Generate industrial building plan"""
        # Create a simple warehouse layout
        building_mix = {"warehouse": 1.0}
        return self._generate_mixed_use_architectural(width, height, building_mix)
    
    def _generate_office_architectural(self, width: float, height: float) -> ArchitecturalFloorPlan:
        """Generate office building plan"""
        building_mix = {"office": 1.0}
        return self._generate_mixed_use_architectural(width, height, building_mix)


# Create singleton instance
architectural_floor_plan_service = ArchitecturalFloorPlanService()