# V2 API Documentation

## Base URL
```
http://localhost:8001/api/v2
```

## Endpoints

### 1. Health Check
**GET** `/health`

Check if V2 system is operational.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "building_types_loaded": 13,
  "subtypes_loaded": 48
}
```

### 2. Analyze Natural Language
**POST** `/analyze`

Parse natural language description into structured project data and calculate costs.

**Request:**
```json
{
  "text": "Build a 200,000 square foot hospital with emergency department in Nashville"
}
```

**Response:**
```json
{
  "parsed": {
    "building_type": "healthcare",
    "subtype": "hospital",
    "square_footage": 200000,
    "location": "Nashville",
    "project_class": "ground_up",
    "confidence": 0.95
  },
  "calculations": {
    "totals": {
      "total_project_cost": 150000000,
      "cost_per_sf": 750
    }
  }
}
```

### 3. Direct Calculation
**POST** `/calculate`

Calculate costs with explicit parameters.

**Request:**
```json
{
  "building_type": "multifamily",
  "subtype": "luxury_apartments",
  "square_footage": 100000,
  "location": "Nashville",
  "project_class": "ground_up",
  "floors": 5,
  "ownership_type": "for_profit",
  "special_features": ["rooftop_amenity", "pool"]
}
```

### 4. Compare Scenarios
**POST** `/compare`

Compare multiple project scenarios.

**Request:**
```json
{
  "scenarios": [
    {
      "name": "Option A",
      "building_type": "office",
      "subtype": "class_a",
      "square_footage": 50000,
      "location": "Nashville"
    },
    {
      "name": "Option B",
      "building_type": "office",
      "subtype": "class_b",
      "square_footage": 60000,
      "location": "Nashville"
    }
  ]
}
```

### 5. List Building Types
**GET** `/building-types`

Get all available building types and subtypes.

### 6. Get Building Details
**GET** `/building-details/{building_type}/{subtype}`

Get detailed configuration for a specific building type.

Example: `/building-details/healthcare/hospital`

### 7. Test NLP
**GET** `/test-nlp?text=...`

Test NLP parsing without calculations.

Example: `/test-nlp?text=luxury%20apartment%20complex`