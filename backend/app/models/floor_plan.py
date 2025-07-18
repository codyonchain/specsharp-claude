from pydantic import BaseModel, Field, validator
from typing import List, Optional, Tuple
from enum import Enum


class RoomType(str, Enum):
    OFFICE = "office"
    CONFERENCE = "conference"
    BATHROOM = "bathroom"
    KITCHEN = "kitchen"
    STORAGE = "storage"
    LOBBY = "lobby"
    CORRIDOR = "corridor"
    MECHANICAL = "mechanical"
    RETAIL = "retail"
    RESIDENTIAL = "residential"


class Room(BaseModel):
    id: str
    name: str
    type: RoomType
    dimensions: Tuple[float, float] = Field(..., description="Width x Height in feet")
    area: float = Field(gt=0)
    location: Tuple[float, float] = Field(..., description="X, Y coordinates")
    
    @validator('area', always=True)
    def calculate_area(cls, v, values):
        if 'dimensions' in values:
            return round(values['dimensions'][0] * values['dimensions'][1], 2)
        return v


class FloorPlanRequest(BaseModel):
    square_footage: float = Field(..., gt=0)
    shape: str = Field(default="rectangular", pattern="^(rectangular|L-shaped|square)$")
    num_rooms: Optional[int] = Field(None, ge=1, le=100)
    room_types: Optional[List[RoomType]] = None
    custom_requirements: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "square_footage": 5000,
                "shape": "rectangular",
                "num_rooms": 10,
                "room_types": ["office", "conference", "bathroom", "kitchen"],
                "custom_requirements": "Include corner offices and open workspace"
            }
        }


class FloorPlanResponse(BaseModel):
    id: str
    total_area: float
    rooms: List[Room]
    efficiency_ratio: float = Field(ge=0, le=1)
    image_url: Optional[str] = None
    svg_data: Optional[str] = None
    
    @validator('efficiency_ratio', always=True)
    def calculate_efficiency(cls, v, values):
        if 'rooms' in values and 'total_area' in values:
            usable_area = sum(room.area for room in values['rooms'])
            return round(usable_area / values['total_area'], 2)
        return v