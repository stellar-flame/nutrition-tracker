
# Nutrition Tracker

A full-stack nutrition tracking application with AI-powered meal analysis. Log meals by entering a text description and get automatic nutritional breakdowns powered by OpenAI.

## Features

- **AI-Powered Nutrition Estimation** - Enter a meal description (e.g., "chicken salad with ranch dressing") and get automatic nutritional values
- **Daily Nutrition Dashboard** - View aggregated calories, protein, carbs, fat, fiber, sugar, and sodium
- **Meal Logging** - Add meals with automatic timestamps and itemized nutrition breakdowns
- **Real-time Updates** - React Query handles caching and automatic refetching

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite
- TanStack React Query
- Axios

### Backend
- Python 3.12 + FastAPI
- SQLModel + SQLAlchemy
- PostgreSQL
- OpenAI GPT-4o-mini
- Alembic (migrations)
### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/nutrition
export OPENAI_API_KEY=your-openai-api-key

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api to localhost:8000)
npm run dev
```

The app will be available at `http://localhost:5173`.

## Environment Variables

### Backend

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | OpenAI API key for nutrition estimation |

### Frontend

The Vite dev server proxies `/api` requests to `http://localhost:8000`.

## API Endpoints

### Nutrition

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/nutrition/summary?date=YYYY-MM-DD` | Daily nutrition summary |
| `GET` | `/nutrition/meals?date=YYYY-MM-DD` | List meals for a date |
| `POST` | `/nutrition/meals` | Create a meal (AI estimates nutrition) |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health/` | Basic health check |
| `GET` | `/health/db` | Database connectivity check |


## Deployment

I am currently studying for **AWS Certified Solutions Architect - Associate (SAA-C03)**
I am doing the folowing online course: https://learn.cantrill.io/p/aws-certified-solutions-architect-associate-saa-c03

I have been practicing the various deployments. In deployments folder I have documented what I have learnt and the various deployments I have done.


