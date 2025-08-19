# SpecSharp V2 - Clean Architecture

## Overview
This is the clean architecture implementation of SpecSharp, running parallel to V1.

## Architecture Principles
1. **Single Source of Truth**: One master config for all building data
2. **Unified Engine**: One engine handles all calculations
3. **Clear Separation**: Config, engines, services, and API are clearly separated
4. **Type Safety**: Full type hints and validation
5. **Traceability**: Every calculation step is logged

## Directory Structure
```
v2/
├── config/          # All configuration files
│   └── master_config.py    # Single source of truth
├── engines/         # Calculation engines (pure business logic)
│   └── unified_engine.py   # One engine for all calculations
├── services/        # Business services (orchestration)
│   └── nlp_service.py      # Single NLP service
├── api/            # API endpoints (thin controllers)
│   └── endpoints.py        # V2 API endpoints
├── models/         # Data models and schemas
│   └── schemas.py          # Pydantic models
└── utils/          # Utility functions
    └── logging.py          # Structured logging
```

## Migration Status
- [ ] Directory structure created
- [ ] Master config implemented
- [ ] Unified engine built
- [ ] NLP service consolidated
- [ ] API endpoints created
- [ ] Frontend integration
- [ ] Parallel testing complete
- [ ] V1 deprecated

## Usage
Access V2 endpoints at `/api/v2/*`
Compare with V1 at `/api/v1/*` for validation