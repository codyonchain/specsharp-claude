# SpecSharp - Construction Cost & Investment Analysis Platform

SpecSharp provides instant, accurate construction cost estimates and investment analysis for commercial real estate projects. Input a project description and get detailed cost breakdowns, revenue projections, and ROI analysis in seconds.

## Architecture

### Single Source of Truth Design
- **master_config.py**: Contains ALL building data (costs, revenue, margins) for 57 building subtypes
- **unified_engine.py**: Single calculation engine for ALL metrics
- **No parallel systems**: One config, one engine, one data flow

### Key Features
- **13 Building Types**: Healthcare, Multifamily, Office, Retail, Restaurant, Industrial, Hospitality, Educational, Mixed Use, Specialty, Civic, Recreation, Parking
- **57 Subtypes**: From hospitals to cafes, each with specific cost and revenue models
- **Quality Adjustments**: Premium construction commands premium revenue
- **Regional Multipliers**: Adjusts for local market conditions
- **Complete Financial Analysis**: Construction costs, soft costs, revenue projections, NOI, ROI, payback period

## 🚀 Features

### Core Functionality
- **Natural Language Processing**: Describe your project in plain English and get instant cost estimates
- **Universal Revenue Calculation**: Building-specific revenue models for investment analysis
- **Quality Factor Adjustments**: Premium construction (>20% above base cost) gets premium rates
- **Mixed-Use Support**: Handle complex projects with multiple building types
- **Regional Cost Adjustments**: Automatic price adjustments based on project location

### Advanced Features
- **Trade Package Generation**: Create detailed PDF packages for electrical, mechanical, plumbing, structural, finishes, and general conditions trades
- **Project Comparison Tool**: Compare multiple scenarios side-by-side with visual analytics
- **Executive Summaries**: Generate professional reports with cost breakdowns and visualizations
- **Team Collaboration**: Share projects with team members (OAuth integration)
- **Export Options**: Download estimates as Excel spreadsheets or PDF reports
- **Markup & Margin Settings**: Customize overhead and profit percentages by trade
- **Real-time Cost Visualization**: Interactive charts showing cost distribution by trade

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (production)
- **Authentication**: JWT tokens with OAuth2 (Google)
- **API Documentation**: OpenAPI/Swagger (accessible at `/docs`)
- **PDF Generation**: ReportLab
- **Excel Export**: XlsxWriter with custom formatting

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for lightning-fast development
- **Styling**: CSS Modules + Tailwind CSS utilities
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **State Management**: React hooks and context

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/specsharp.git
   cd specsharp
   ```

2. **Set up environment variables**
   ```bash
   # Backend (.env in /backend)
   DATABASE_URL=sqlite:///./specsharp.db
   SECRET_KEY=your-secret-key-here-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   GOOGLE_CLIENT_ID=your-google-oauth-client-id
   GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
   ```

3. **Start the application**
   ```bash
   ./start-all.sh
   ```

   This will start:
   - Backend API on http://localhost:8001
   - Frontend on http://localhost:3000
   - API Documentation on http://localhost:8001/docs

4. **Test credentials** (for development)
   - Email: test2@example.com
   - Password: password123

## 📁 Project Structure

```
specsharp/
├── backend/
│   ├── app/
│   │   ├── v2/
│   │   │   ├── config/
│   │   │   │   └── master_config.py     # All building data
│   │   │   ├── engines/
│   │   │   │   └── unified_engine.py    # All calculations
│   │   │   └── api/
│   │   │       └── scope.py             # API endpoints
│   │   ├── api/          # Legacy V1 API endpoints
│   │   ├── core/         # Core business logic
│   │   ├── db/           # Database models & migrations
│   │   └── services/     # Business services
│   ├── tests/            # Backend tests
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client services
│   │   └── utils/        # Utility functions
│   ├── public/           # Static assets
│   └── package.json      # Node dependencies
├── scripts/              # Utility scripts
├── start-all.sh         # Start both services
├── start-backend.sh     # Start backend only
├── start-frontend.sh    # Start frontend only
└── CLAUDE.md            # AI assistant instructions
```

## Revenue Calculation System

### How It Works
1. User inputs project description (e.g., "4200 SF full service restaurant")
2. NLP detects building type and subtype
3. unified_engine calculates:
   - Construction costs from master_config base rates
   - Quality factor based on actual vs base cost
   - Revenue using building-specific metrics (per SF, per unit, per bed, etc.)
   - Operating margins (base or premium based on quality)
   - ROI metrics (NOI, cash-on-cash return, payback period)

### Revenue Metrics by Type
- **Healthcare**: Revenue per bed, visit, procedure, or scan
- **Multifamily**: Monthly rent per unit
- **Office/Retail**: Annual rent per SF
- **Restaurant**: Sales per SF
- **Hospitality**: Revenue per room
- **Educational**: Funding per student
- **Industrial**: Lease rate per SF
- **Parking**: Revenue per space

### Data Flow
```
master_config.py (data) 
    ↓
unified_engine.py (calculations)
    ↓
API response (multiple paths for compatibility)
    ↓
Frontend display (ExecutiveViewComplete.tsx)
```

## 🔧 Development

### Backend Development

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Run tests
pytest

# Code formatting
black .
flake8
mypy .
```

### Frontend Development

```bash
cd frontend
npm install

# Development server with hot-reload
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## 🎯 Usage Examples

### Natural Language Input Examples

1. **Office Building**
   ```
   50,000 sq ft office building in Austin, TX with standard finishes
   ```

2. **Mixed-Use Project**
   ```
   100,000 sq ft mixed use: 60% office, 40% retail in Seattle
   ```

3. **Restaurant**
   ```
   5,000 sq ft full service restaurant in New York with commercial kitchen
   ```

4. **Warehouse**
   ```
   75,000 sq ft warehouse with 10% office space in Phoenix
   ```

## Testing Revenue Calculations

### V2 API Testing
```bash
# Test restaurant
curl -X POST http://localhost:8001/api/v2/scope/generate \
  -d '{"description": "4200 sf full service restaurant"}'

# Expected: ~$2.1M revenue, 12% margin, $252K NOI

# Test multifamily  
curl -X POST http://localhost:8001/api/v2/scope/generate \
  -d '{"description": "100000 sf luxury apartments"}'

# Expected: ~$4.5M revenue, 35% margin, $1.6M NOI

# Test office
curl -X POST http://localhost:8001/api/v2/scope/generate \
  -d '{"description": "50000 sf class a office"}'

# Expected: ~$1.9M revenue, 65% margin, $1.3M NOI

# Test healthcare
curl -X POST http://localhost:8001/api/v2/scope/generate \
  -d '{"description": "25000 sf medical office building"}'

# Expected: ~$1.1M revenue, 65% margin, $703K NOI
```

### Using the Application

1. **Create Project**: Use natural language or the detailed form
2. **Review Estimate**: See cost breakdown by trade and system
3. **Generate Trade Packages**: Create PDF packages for subcontractors
4. **Compare Scenarios**: Evaluate different project configurations
5. **Export Results**: Download Excel or PDF reports

## 📊 Cost Calculation Logic

SpecSharp uses a deterministic pricing engine based on:

1. **Base Costs**: Per square foot rates for different building systems
   - Foundation: $12-20/SF (varies by type)
   - Structural: $18-35/SF (based on building type)
   - HVAC: $15-25/SF (climate zone adjusted)
   - Electrical: $10-20/SF (building use dependent)
   - Plumbing: $6-30/SF (restaurant vs office)
   - Finishes: $20-120/SF (quality level based)

2. **Building Type Multipliers**
   - Office: 1.0x (baseline)
   - Warehouse: 0.5x (reduced systems)
   - Restaurant: 1.5-2.0x (commercial kitchen requirements)
   - Mixed-Use: Weighted average calculation

3. **Regional Factors**
   - Tier 1 Cities (SF, NYC): 1.35-1.45x
   - Tier 2 Cities (Seattle, LA): 1.15-1.25x
   - Tier 3 Cities (Austin, Denver): 0.95-1.10x
   - Rural Areas: 0.85-0.95x

4. **Trade Breakdowns**: Detailed costs for 15+ construction trades

5. **Markups**: Configurable overhead (10%) and profit (10%) percentages

## 🔐 Security

- JWT-based authentication with secure token handling
- OAuth2 integration for Google sign-in
- Environment-based configuration for sensitive data
- CORS protection with configurable origins
- SQL injection protection via SQLAlchemy ORM
- Input validation using Pydantic models

## 🚀 Deployment

### Production Considerations
- Use PostgreSQL instead of SQLite
- Set secure SECRET_KEY (use `openssl rand -hex 32`)
- Configure proper CORS origins
- Enable HTTPS with SSL certificates
- Set up proper logging and monitoring
- Use Gunicorn with Uvicorn workers

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secure-random-key
GOOGLE_CLIENT_ID=your-oauth-client-id
GOOGLE_CLIENT_SECRET=your-oauth-client-secret
FRONTEND_URL=https://yourdomain.com
ENVIRONMENT=production
```

### Docker Deployment (Coming Soon)
```bash
docker-compose up -d
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest -v
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### E2E Testing Flow
1. Create projects with various building types
2. Generate and verify trade packages
3. Test export functionality
4. Verify cost calculations
5. Test user authentication flow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style Guidelines
- Backend: Follow PEP 8, use Black formatter
- Frontend: ESLint + Prettier configuration
- Commit messages: Use conventional commits format

## 📝 API Documentation

### V2 API (Current)
- `POST /api/v2/scope/generate` - Generate new project estimate
- `GET /api/v2/scope/projects` - List all projects
- `GET /api/v2/scope/projects/{id}` - Get project details
- `GET /api/v2/scope/projects/{id}/owner-view` - Get investment analysis
- `POST /api/v2/analyze` - Analyze project description

### Legacy V1 Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login
- `GET /api/v1/oauth/login/google` - Google OAuth login

#### Projects
- `POST /api/v1/scope/generate` - Generate new project
- `GET /api/v1/scope/projects` - List projects
- `GET /api/v1/scope/projects/{id}` - Get project details
- `DELETE /api/v1/scope/projects/{id}` - Delete project

#### Trade Packages
- `GET /api/v1/trade-package/preview/{project_id}/{trade}` - Preview package
- `POST /api/v1/trade-package/generate/{project_id}/{trade}` - Generate package

#### Exports
- `POST /api/v1/excel/export/{project_id}` - Export to Excel
- `POST /api/v1/pdf/export/{project_id}` - Export to PDF

Full API documentation available at http://localhost:8001/docs when running locally.

## 🐛 Known Issues & Troubleshooting

### Common Issues
1. **Port Conflicts**: If ports 8001 or 3000 are in use, modify the start scripts
2. **Database Migrations**: Run `alembic upgrade head` if you see database errors
3. **CORS Errors**: Check that frontend URL is in backend CORS allowed origins

### Debug Mode
Enable debug logging:
```bash
# Backend
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Frontend
VITE_DEBUG=true npm run dev
```

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

- Email: support@specsharp.ai
- GitHub Issues: [Create an issue](https://github.com/yourusername/specsharp/issues)
- Documentation: [Wiki](https://github.com/yourusername/specsharp/wiki)

## 🙏 Acknowledgments

- Built with ❤️ by the SpecSharp team
- Special thanks to all contributors
- Powered by OpenAI for natural language processing

---

## Recent Changes (September 2025)

### Revenue System Refactor
- Unified all revenue calculations into master_config + unified_engine
- Removed parallel systems (owner_view_engine, owner_metrics_config)
- Added quality factors for premium construction
- Fixed frontend hardcoded values
- All 57 building subtypes now have complete revenue models

---

**Current Version**: 2.0.0  
**Last Updated**: September 2025