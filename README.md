# SpecSharp - Construction Intelligence Tool

SpecSharp is a modern construction cost estimation platform that provides accurate, deterministic pricing for construction projects with support for mixed-use buildings and regional cost variations.

## 🚀 Key Features

- **Natural Language Input**: Describe your project in plain English (e.g., "150x300 warehouse (70%) + office(30%) with HVAC in California")
- **Mixed-Use Building Support**: Accurate calculations for buildings with multiple use types
- **Regional Pricing**: City and state-specific cost multipliers for accurate local pricing
- **Subcontractor View**: Filter costs by trade (Electrical, Plumbing, HVAC, etc.)
- **Deterministic Pricing**: Same inputs always produce the same cost estimates
- **Real-time Cost Breakdown**: Visual charts and detailed system-by-system pricing
- **Professional Scope Generation**: Export-ready construction scope documents

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy + SQLite/PostgreSQL
- Pydantic for data validation
- JWT authentication
- Matplotlib for floor plan generation

### Frontend
- React with TypeScript
- Vite for fast development
- Axios for API calls
- Recharts for data visualization
- React Router for navigation

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Option 1: Using startup scripts

1. Clone the repository:
```bash
git clone <repository-url>
cd specsharp
```

2. Start the backend:
```bash
./start-backend.sh
```

3. In a new terminal, start the frontend:
```bash
./start-frontend.sh
```

### Option 2: Manual setup

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## 🎯 Usage Examples

### Natural Language Input Examples

1. **Mixed-Use Building**:
   ```
   150x300 warehouse (70%) + office(30%) with HVAC and bathrooms in California
   ```

2. **Simple Office Building**:
   ```
   10000 SF office building in Seattle with 2 floors
   ```

3. **Warehouse Project**:
   ```
   25000 sqft warehouse with minimal HVAC in Austin, TX
   ```

### Using the Application

1. **Login**: Use test credentials (test@example.com / password123) or register
2. **Create Scope**: Toggle to natural language mode or use the form
3. **View Results**: See detailed cost breakdown by system
4. **Subcontractor Mode**: Toggle subcontractor view to filter by trade
5. **Export**: Download or share your scope document

## 📊 Cost Calculation Logic

### Base Costs (National Average per SF)
- Foundation: $12/SF
- Framing: $18/SF
- HVAC: $15/SF
- Electrical: $10/SF
- Plumbing: $6/SF
- Finishes: $20/SF

### Regional Multipliers
- San Francisco: 1.45x
- Los Angeles: 1.25x
- Seattle: 1.20x
- Austin: 0.95x
- Miami: 1.05x
- Denver: 1.10x

### Building Type Adjustments
- Warehouse: 50% of office costs
- Mixed-use: Weighted average based on percentages

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get access token

### Scope Management
- `POST /api/v1/scope/generate` - Generate new project scope
- `GET /api/v1/scope/projects` - List user's projects
- `GET /api/v1/scope/projects/{project_id}` - Get project details

### Cost Services
- `GET /api/v1/cost/regional-multipliers` - Get regional cost multipliers
- `GET /api/v1/cost/materials` - Get material costs
- `POST /api/v1/cost/calculate-breakdown` - Calculate cost breakdown

### Floor Plans
- `POST /api/v1/floor-plan/generate` - Generate floor plan
- `GET /api/v1/floor-plan/plans/{floor_plan_id}` - Get floor plan details

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./specsharp.db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-key-optional
ANTHROPIC_API_KEY=your-anthropic-key-optional
ENVIRONMENT=development
```

## Project Structure

```
specsharp/
├── backend/
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration and engine
│   │   ├── db/          # Database models and setup
│   │   ├── models/      # Pydantic models
│   │   └── services/    # Business logic services
│   ├── tests/           # Test files
│   └── requirements.txt # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API service layer
│   │   └── App.tsx      # Main application
│   └── package.json     # Node dependencies
└── README.md
```

## Development

### Adding New Features

1. **Backend**: Add new endpoints in `app/api/endpoints/`
2. **Frontend**: Create components in `src/components/`
3. **Services**: Add business logic in `app/services/`

### Testing

Run backend tests:
```bash
cd backend
pytest
```

### Code Style

- Backend: Follow PEP 8 guidelines
- Frontend: Use ESLint and Prettier for consistent formatting

## Deployment

For production deployment:

1. Update `.env` with production values
2. Use PostgreSQL instead of SQLite
3. Set up proper CORS origins
4. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
5. Build the React frontend for production: `npm run build`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.