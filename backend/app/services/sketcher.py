import os

if os.getenv("DISABLE_FLOOR_PLAN_SKETCHER", "false").lower() == "true":
    HAS_MATPLOTLIB = False
    np = None
else:
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import Rectangle
        import numpy as np
        HAS_MATPLOTLIB = True
    except ImportError:
        HAS_MATPLOTLIB = False
        np = None
from typing import List, Tuple, Dict, Optional
import uuid
import io
import base64
import math
from app.models.floor_plan import FloorPlanRequest, FloorPlanResponse, Room, RoomType


class FloorPlanGenerator:
    def __init__(self):
        self.default_room_sizes = {
            RoomType.OFFICE: {"min": 100, "max": 200, "ratio": (1.0, 1.5)},
            RoomType.CONFERENCE: {"min": 200, "max": 400, "ratio": (1.0, 2.0)},
            RoomType.BATHROOM: {"min": 40, "max": 80, "ratio": (1.0, 1.5)},
            RoomType.KITCHEN: {"min": 100, "max": 300, "ratio": (1.0, 2.0)},
            RoomType.STORAGE: {"min": 50, "max": 150, "ratio": (1.0, 1.5)},
            RoomType.LOBBY: {"min": 200, "max": 500, "ratio": (1.0, 3.0)},
            RoomType.CORRIDOR: {"min": 50, "max": 200, "ratio": (0.2, 5.0)},
            RoomType.MECHANICAL: {"min": 100, "max": 200, "ratio": (1.0, 1.5)},
        }
    
    def generate(self, request: FloorPlanRequest) -> FloorPlanResponse:
        floor_plan_id = str(uuid.uuid4())[:8]
        
        building_dimensions = self._calculate_building_dimensions(
            request.square_footage, request.shape
        )
        
        rooms = self._generate_rooms(request, building_dimensions)
        
        svg_data = self._generate_svg(rooms, building_dimensions)
        
        return FloorPlanResponse(
            id=floor_plan_id,
            total_area=request.square_footage,
            rooms=rooms,
            svg_data=svg_data
        )
    
    def _calculate_building_dimensions(
        self, 
        square_footage: float, 
        shape: str
    ) -> Tuple[float, float]:
        if shape == "square":
            side = math.sqrt(square_footage)
            return (side, side)
        elif shape == "rectangular":
            ratio = 1.5
            width = math.sqrt(square_footage / ratio)
            height = width * ratio
            return (width, height)
        elif shape == "L-shaped":
            side = math.sqrt(square_footage * 0.75)
            return (side * 1.5, side * 1.5)
        else:
            ratio = 1.5
            width = math.sqrt(square_footage / ratio)
            height = width * ratio
            return (width, height)
    
    def _generate_rooms(
        self, 
        request: FloorPlanRequest,
        building_dimensions: Tuple[float, float]
    ) -> List[Room]:
        rooms = []
        
        if request.room_types:
            room_types = request.room_types
        else:
            room_types = self._determine_room_types(request)
        
        num_rooms = request.num_rooms or len(room_types)
        
        available_area = request.square_footage * 0.85
        
        positions = self._generate_room_positions(
            num_rooms, building_dimensions, request.shape
        )
        
        for i in range(min(num_rooms, len(positions))):
            room_type = room_types[i % len(room_types)]
            room_size = self._calculate_room_size(
                room_type, available_area / num_rooms
            )
            
            room = Room(
                id=f"room_{i+1}",
                name=f"{room_type.value.title()} {i+1}",
                type=room_type,
                dimensions=room_size,
                area=room_size[0] * room_size[1],
                location=positions[i]
            )
            rooms.append(room)
        
        corridor = self._add_corridor(rooms, building_dimensions)
        if corridor:
            rooms.append(corridor)
        
        return rooms
    
    def _determine_room_types(self, request: FloorPlanRequest) -> List[RoomType]:
        # Default to commercial for floor plans
        project_type = getattr(request, 'project_type', 'commercial')
        if project_type == "commercial":
            base_types = [
                RoomType.OFFICE, RoomType.OFFICE, RoomType.OFFICE,
                RoomType.CONFERENCE, RoomType.BATHROOM, RoomType.KITCHEN
            ]
        elif project_type == "residential":
            base_types = [
                RoomType.RESIDENTIAL, RoomType.RESIDENTIAL,
                RoomType.BATHROOM, RoomType.KITCHEN
            ]
        else:
            base_types = [
                RoomType.OFFICE, RoomType.CONFERENCE,
                RoomType.BATHROOM, RoomType.STORAGE
            ]
        
        if request.square_footage > 5000:
            base_types.extend([RoomType.LOBBY, RoomType.MECHANICAL])
        
        return base_types
    
    def _calculate_room_size(
        self, 
        room_type: RoomType, 
        target_area: float
    ) -> Tuple[float, float]:
        room_config = self.default_room_sizes.get(
            room_type, 
            {"min": 100, "max": 200, "ratio": (1.0, 1.5)}
        )
        
        area = max(room_config["min"], min(target_area, room_config["max"]))
        
        min_ratio, max_ratio = room_config["ratio"]
        ratio = min_ratio + (max_ratio - min_ratio) * 0.5
        
        width = math.sqrt(area / ratio)
        height = width * ratio
        
        return (round(width, 1), round(height, 1))
    
    def _generate_room_positions(
        self, 
        num_rooms: int,
        building_dimensions: Tuple[float, float],
        shape: str
    ) -> List[Tuple[float, float]]:
        positions = []
        width, height = building_dimensions
        
        if shape == "rectangular" or shape == "square":
            grid_cols = int(math.ceil(math.sqrt(num_rooms * width / height)))
            grid_rows = int(math.ceil(num_rooms / grid_cols))
            
            cell_width = width / grid_cols
            cell_height = height / grid_rows
            
            for i in range(num_rooms):
                row = i // grid_cols
                col = i % grid_cols
                x = col * cell_width + cell_width * 0.1
                y = row * cell_height + cell_height * 0.1
                positions.append((round(x, 1), round(y, 1)))
        
        elif shape == "L-shaped":
            main_rooms = int(num_rooms * 0.6)
            wing_rooms = num_rooms - main_rooms
            
            for i in range(main_rooms):
                x = (i % 3) * (width * 0.3) + width * 0.05
                y = (i // 3) * (height * 0.3) + height * 0.05
                positions.append((round(x, 1), round(y, 1)))
            
            for i in range(wing_rooms):
                x = width * 0.6 + (i % 2) * (width * 0.15)
                y = height * 0.6 + (i // 2) * (height * 0.15)
                positions.append((round(x, 1), round(y, 1)))
        
        return positions
    
    def _add_corridor(
        self, 
        rooms: List[Room], 
        building_dimensions: Tuple[float, float]
    ) -> Optional[Room]:
        if len(rooms) < 3:
            return None
        
        width, height = building_dimensions
        corridor_width = min(8.0, width * 0.1)
        
        return Room(
            id="corridor_main",
            name="Main Corridor",
            type=RoomType.CORRIDOR,
            dimensions=(corridor_width, height * 0.8),
            area=corridor_width * height * 0.8,
            location=(width / 2 - corridor_width / 2, height * 0.1)
        )
    
    def _generate_svg(
        self, 
        rooms: List[Room], 
        building_dimensions: Tuple[float, float]
    ) -> str:
        if not HAS_MATPLOTLIB:
            # Return a simple SVG without matplotlib
            return self._generate_simple_svg(rooms, building_dimensions)
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        width, height = building_dimensions
        building_rect = Rectangle((0, 0), width, height, 
                                linewidth=2, edgecolor='black', 
                                facecolor='white')
        ax.add_patch(building_rect)
        
        colors = {
            RoomType.OFFICE: '#E3F2FD',
            RoomType.CONFERENCE: '#F3E5F5',
            RoomType.BATHROOM: '#E0F2F1',
            RoomType.KITCHEN: '#FFF3E0',
            RoomType.STORAGE: '#F5F5F5',
            RoomType.LOBBY: '#E8F5E9',
            RoomType.CORRIDOR: '#EEEEEE',
            RoomType.MECHANICAL: '#FFEBEE',
            RoomType.RESIDENTIAL: '#E1F5FE',
        }
        
        for room in rooms:
            x, y = room.location
            w, h = room.dimensions
            color = colors.get(room.type, '#FFFFFF')
            
            room_rect = Rectangle((x, y), w, h,
                                linewidth=1, edgecolor='gray',
                                facecolor=color, alpha=0.7)
            ax.add_patch(room_rect)
            
            ax.text(x + w/2, y + h/2, f"{room.name}\n{room.area:.0f} sqft",
                   ha='center', va='center', fontsize=8, wrap=True)
        
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_aspect('equal')
        ax.set_xlabel('Width (feet)')
        ax.set_ylabel('Height (feet)')
        ax.set_title(f'Floor Plan - Total Area: {sum(r.area for r in rooms):.0f} sqft')
        
        ax.grid(True, alpha=0.3)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='svg', bbox_inches='tight')
        buffer.seek(0)
        svg_data = buffer.getvalue().decode('utf-8')
        
        plt.close()
        
        return svg_data
    
    def _generate_simple_svg(
        self,
        rooms: List[Room],
        building_dimensions: Tuple[float, float]
    ) -> str:
        width, height = building_dimensions
        scale = 2  # pixels per foot
        
        svg = f'''<svg width="{width * scale}" height="{height * scale}" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="{width * scale}" height="{height * scale}" 
              fill="white" stroke="black" stroke-width="2"/>'''
        
        colors = {
            RoomType.OFFICE: '#E3F2FD',
            RoomType.CONFERENCE: '#F3E5F5',
            RoomType.BATHROOM: '#E0F2F1',
            RoomType.KITCHEN: '#FFF3E0',
            RoomType.STORAGE: '#F5F5F5',
            RoomType.LOBBY: '#E8F5E9',
            RoomType.CORRIDOR: '#EEEEEE',
            RoomType.MECHANICAL: '#FFEBEE',
            RoomType.RESIDENTIAL: '#E1F5FE',
        }
        
        for room in rooms:
            x, y = room.location
            w, h = room.dimensions
            color = colors.get(room.type, '#FFFFFF')
            
            svg += f'''
        <rect x="{x * scale}" y="{y * scale}" width="{w * scale}" height="{h * scale}"
              fill="{color}" stroke="gray" stroke-width="1" opacity="0.7"/>
        <text x="{(x + w/2) * scale}" y="{(y + h/2) * scale}" 
              text-anchor="middle" font-size="12">{room.name}</text>'''
        
        svg += '</svg>'
        return svg


floor_plan_generator = FloorPlanGenerator()
