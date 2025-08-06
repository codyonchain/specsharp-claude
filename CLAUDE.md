# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpecSharp is a construction cost estimation platform with a React/TypeScript frontend and FastAPI Python backend. The application provides deterministic pricing for construction projects with support for mixed-use buildings and regional cost variations.

### Recent Updates
- **Fixed**: Port configuration - Frontend now correctly points to backend port 8001
- **Fixed**: Cost per square foot calculation discrepancy 
- **Fixed**: Mobile responsiveness issues for Dashboard and ProjectDetail pages
- **Fixed**: Comparison page CSS and trade package downloads on mobile
- **Updated**: Who Uses SpecSharp icons and Vite port configuration
- **NEW FEATURE**: Project Classification (Ground-Up vs Addition vs Renovation)
  - Adds 15% premium for additions (tie-ins, protection, limited access)
  - Adds 35% premium for renovations (demolition, unknowns, phased work)
  - Automatic detection from natural language descriptions
  - Visual selector in project creation form

## Architecture

### Backend (FastAPI + Python)
- **Port**: 8001
- **Main Entry**: `backend/app/main.py`
- **API Structure**: RESTful API with `/api/v1` prefix
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT-based with python-jose
- **Key Services**:
  - `app/services/cost_service.py`: Cost calculation logic
  - `app/services/nlp_service.py`: Natural language parsing
  - `app/services/floor_plan_service.py`: Floor plan generation
  - `app/services/climate_service.py`: Climate zone handling

### Frontend (React + TypeScript + Vite)
- **Port**: 5173 (Vite dev server) or 3000 (configured in vite.config.ts)
- **Main Entry**: `frontend/src/main.tsx`
- **API Client**: `frontend/src/services/api.ts` (correctly configured for port 8001)
- **Key Components**:
  - `Login.tsx`: Authentication UI
  - `Dashboard.tsx`: Project list view
  - `ProjectDetail.tsx`: Cost breakdown display
  - `ScopeGenerator.tsx`: Project creation form
  - `FloorPlanViewer.tsx`: Floor plan visualization

## Common Development Commands

### Backend
```bash
# Start backend (from project root)
./start-backend.sh

# Manual backend start
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Run tests
cd backend
pytest

# Code formatting
black .
flake8
mypy .
```

### Frontend
```bash
# Start frontend (from project root)
./start-frontend.sh

# Manual frontend start
cd frontend
npm install
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Quick Start All Services
```bash
# Start both frontend and backend
./start-all.sh

# Test service health
./test-services.sh
```

## API Endpoints

- **Auth**: `/api/v1/auth/token` (POST) - Login endpoint expects form data with username/password
- **Projects**: `/api/v1/scope/projects` (GET) - List user projects
- **Scope Generation**: `/api/v1/scope/generate` (POST) - Create new project
- **Cost Calculation**: `/api/v1/cost/calculate-breakdown` (POST)
- **API Docs**: http://localhost:8001/docs

## Environment Configuration

Backend `.env` file required with:
```
DATABASE_URL=sqlite:///./specsharp.db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Critical File Locations

- **CORS Configuration**: `backend/app/core/config.py:18` - Allowed origins list
- **API Base URL**: `frontend/src/services/api.ts:3-5` - Correctly uses environment variable or defaults to port 8001
- **Backend Port**: `start-backend.sh:22` - Configured as 8001
- **Frontend Port**: `frontend/vite.config.ts:8` - Configured as 3000

## Testing Approach

- Backend: Uses pytest with test files in `backend/tests/`
- No frontend tests currently configured
- Manual testing credentials: test2@example.com / password123

## Cost Calculation Logic

The application uses deterministic pricing based on:
- Base costs per square foot for different systems (foundation, framing, HVAC, etc.)
- Regional multipliers for different cities (Based on RSMeans 2024 Q2 data)
- Building type adjustments (warehouse costs 50% of office)
- Mixed-use weighted averages
- **Project Classification Multipliers**:
  - Ground-Up: 1.0x (base cost)
  - Addition: 1.15x (includes tie-ins, protection, limited access)
  - Renovation: 1.35x (includes demolition, unknowns, phased work)

### Regional Cost Multipliers (2024 Q2)
- **Tennessee**:
  - Nashville: 1.02 (2% above national average)
  - Franklin: 1.03
  - Murfreesboro: 1.01
- **New Hampshire**:
  - Manchester: 0.99 (1% below national average)
  - Nashua: 0.98
  - Concord: 0.97
- **Massachusetts**:
  - Boston: 1.00 (at national average)
- **Major Markets**:
  - New York, NY: 1.25
  - San Francisco, CA: 1.22
  - Chicago, IL: 1.08
  - Dallas, TX: 0.95
  - Atlanta, GA: 0.94

### Base Construction Costs (per SF - National Average)
- **Restaurant Types**:
  - Quick Service: $300/SF
  - Casual Dining: $375/SF
  - Full-Service: $425/SF
  - Fine Dining: $550/SF
- **Commercial**:
  - Office: $250/SF
  - Retail: $200/SF
  - Medical: $350/SF
- **Industrial**:
  - Warehouse: $150/SF
  - Light Industrial: $175/SF

### Project Classification Details

**Ground-Up Construction**: New building on empty lot
- Standard pricing applies
- Full site work and utilities included
- No special protection or demolition costs

**Additions**: Expanding existing structures
- 15% cost premium applied
- Includes:
  - Structural tie-ins (2.5% of trade costs)
  - Weather protection at connections (1%)
  - Existing building protection (1.5%)
  - Limited access premium (1%)

**Renovations**: Remodeling existing spaces
- 35% cost premium applied
- Includes:
  - Selective demolition (4% of trade costs)
  - Dust protection & barriers (2%)
  - Hazardous material allowance (2.5%)
  - Phased construction premium (1.5%)

See `backend/app/services/cost_service.py` and `backend/app/core/engine.py` for implementation details.

### Cost Calculation Architecture

**Core Principle**: "Calculate once, store completely, display consistently"

#### How It Works:
1. **Costs are calculated ONCE at project creation** - All calculations happen in the backend when a project is generated
2. **All views display stored values from database** - Dashboard, detail view, and reports all use the same stored values
3. **Recalculation only happens when user explicitly updates project** - Manual refresh or project edit triggers recalculation
4. **Database values always override scope_data JSON if discrepancy exists** - Database is the single source of truth

#### Data Integrity:
- **Validation**: `validate_project_costs()` ensures mathematical consistency on save
- **Monitoring**: Cost discrepancies are automatically logged with warnings
- **Audit Trail**: All cost calculations are logged with full details
- **Migration**: `fix_cost_consistency.py` ensures existing projects are consistent

#### Database Fields:
- `subtotal` - Base construction cost before contingency
- `contingency_percentage` - Percentage for contingency (default 10%)
- `contingency_amount` - Calculated contingency amount
- `total_cost` - Final total (subtotal + contingency)
- `cost_per_sqft` - Total cost / square footage

#### Consistency Rules:
- The `/projects/{project_id}` endpoint ensures scope_data values match database values
- Dashboard and Detail views MUST display the SAME stored values
- If filtering by trade, use stored component values rather than recalculating
- Any detected discrepancy > $1 triggers a warning log

This architecture ensures absolute trust in displayed numbers across all views.