# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpecSharp is a construction cost estimation platform with a React/TypeScript frontend and FastAPI Python backend. The application provides deterministic pricing for construction projects with support for mixed-use buildings and regional cost variations.

### Current Known Issues
- **Login Regression**: Authentication is failing with "An error occurred" message. Test credentials: test2@example.com / password123
- **Port Mismatch**: Frontend API service configured for port 8000 but backend runs on port 8001

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
- **API Client**: `frontend/src/services/api.ts` (currently pointing to wrong port 8000)
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
- **API Base URL**: `frontend/src/services/api.ts:3` - Currently incorrect (port 8000 instead of 8001)
- **Backend Port**: `start-backend.sh:22` - Configured as 8001
- **Frontend Port**: `frontend/vite.config.ts:8` - Configured as 3000

## Testing Approach

- Backend: Uses pytest with test files in `backend/tests/`
- No frontend tests currently configured
- Manual testing via test credentials: test2@example.com / password123

## Cost Calculation Logic

The application uses deterministic pricing based on:
- Base costs per square foot for different systems (foundation, framing, HVAC, etc.)
- Regional multipliers for different cities
- Building type adjustments (warehouse costs 50% of office)
- Mixed-use weighted averages

See `backend/app/services/cost_service.py` for implementation details.