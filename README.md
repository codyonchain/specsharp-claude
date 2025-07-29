# SpecSharp - AI-Powered Construction Cost Estimation Platform

SpecSharp is a modern web application that provides instant, deterministic construction cost estimates using AI-powered natural language processing. Built for general contractors, developers, and construction professionals, SpecSharp transforms project descriptions into detailed cost breakdowns in seconds.

## 🚀 Features

### Core Functionality
- **Natural Language Processing**: Describe your project in plain English and get instant cost estimates
- **Deterministic Pricing**: Consistent, rule-based pricing engine for reliable estimates
- **Mixed-Use Support**: Handle complex projects with multiple building types (office, warehouse, restaurant, etc.)
- **Regional Cost Adjustments**: Automatic price adjustments based on project location
- **Professional Floor Plans**: AI-generated architectural floor plans with proper room layouts

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
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core business logic & pricing engine
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

### Core Endpoints

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

**Current Version**: 1.0.0  
**Last Updated**: July 2025