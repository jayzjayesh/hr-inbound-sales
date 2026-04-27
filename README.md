# Inbound Carrier Sales — AI Agent Backend

API backend for the HappyRobot Inbound Carrier Sales agent. Automates inbound carrier calls with FMCSA verification, load search, rate negotiation, and provides a real-time analytics dashboard.

**Live URL**: [https://hr-inbound-sales.onrender.com](https://hr-inbound-sales.onrender.com)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     HappyRobot Platform                         │
│  Carrier Call → AI Agent → Prompt + Tools → Classify → Extract  │
└──────────────────────┬──────────────┬───────────────────────────┘
                       │              │
              verify_carrier    find_available_loads
                       │              │
                       ▼              ▼
            ┌──────────────────────────────────┐
            │     FastAPI Backend (Docker)      │
            │                                  │
            │  GET /api/v1/carrier?mc_number=  │──→ FMCSA QCMobile API
            │  GET /api/v1/loads?origin=...    │──→ In-Memory Load DB
            │  POST /api/v1/calls             │──→ SQLite (call records)
            │  GET /api/v1/metrics            │──→ Dashboard aggregation
            │  GET /dashboard                 │──→ Analytics UI
            └──────────────────────────────────┘
                    Deployed on Render (Docker)
```

## Features

### Objective 1 — Inbound Carrier Sales Agent
- **Carrier Verification**: FMCSA API integration for real-time MC number validation
- **Load Search**: Fuzzy matching on origin/destination with equipment filtering
- **Negotiation Logic**: 3-round negotiation with configurable 90% floor
- **18 Sample Loads**: Realistic freight data across multiple lanes and equipment types

### Objective 2 — Analytics Dashboard
- **Real-time dashboard** at `/dashboard` with auto-refresh every 30s
- **KPI Cards**: Total Calls, Success Rate, Avg Revenue, Negotiation Savings (with info tooltips)
- **Charts**: Call outcomes (donut), Carrier sentiment (donut), Volume over time (bar), Negotiation performance (grouped bar), Top lanes (horizontal bar)
- **Recent Calls Table**: Full call history with outcome/sentiment badges
- **Call Data API**: `POST /api/v1/calls` endpoint for ingesting post-call data

### Objective 3 — Containerization & Deployment
- **Dockerized**: Production-ready `Dockerfile` with Python 3.12 slim
- **Docker Compose**: Local development with `docker-compose.yml`
- **Render Blueprint**: `render.yaml` for one-click deployment
- **API Security**: X-API-Key header authentication on all data endpoints

---

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/jayzjayesh/hr-inbound-sales.git
cd hr-inbound-sales
cp .env.example .env
```

Edit `.env`:
```
FMCSA_API_KEY=your_fmcsa_web_key_here
API_KEY=a_secure_random_string
NEGOTIATION_FLOOR=0.90
```

### 2. Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Run with Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

- **Swagger docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8000/dashboard
- **Health check**: http://localhost:8000/health

---

## API Endpoints

### Carrier Verification

#### `GET /api/v1/carrier?mc_number={mc_number}`

Verify a carrier by MC number via FMCSA. Requires `X-API-Key` header.

```bash
curl -H "X-API-Key: your_key" "https://hr-inbound-sales.onrender.com/api/v1/carrier?mc_number=382280"
```

**Response:**
```json
{
  "mc_number": "382280",
  "legal_name": "L & LOPEZ TRUCKING",
  "dot_number": "871389",
  "operating_status": "AUTHORIZED",
  "is_eligible": true,
  "safety_rating": "S",
  "out_of_service": false,
  "message": "Carrier 'L & LOPEZ TRUCKING' (MC-382280) is authorized and eligible to haul loads."
}
```

### Load Search

#### `GET /api/v1/loads`

Search available loads with optional filters. Requires `X-API-Key` header.

| Parameter      | Type   | Description                          |
|---------------|--------|--------------------------------------|
| load_id       | string | Direct lookup by load ID (e.g., LD-1001) |
| origin        | string | Origin city/state (fuzzy match)      |
| destination   | string | Destination city/state (fuzzy match) |
| equipment_type| string | Van, Reefer, Flatbed                 |
| min_rate      | float  | Minimum rate in USD                  |
| max_rate      | float  | Maximum rate in USD                  |
| pickup_date   | string | Date filter (YYYY-MM-DD)             |

```bash
curl -H "X-API-Key: your_key" "https://hr-inbound-sales.onrender.com/api/v1/loads?origin=Dallas&equipment_type=Van"
```

#### `GET /api/v1/loads/{load_id}`

Get a specific load by ID. Requires `X-API-Key` header.

```bash
curl -H "X-API-Key: your_key" "https://hr-inbound-sales.onrender.com/api/v1/loads/LD-1001"
```

### Call Data & Metrics

#### `POST /api/v1/calls`

Record a completed call. Requires `X-API-Key` header.

```bash
curl -X POST "https://hr-inbound-sales.onrender.com/api/v1/calls" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{
    "mc_number": "382280",
    "carrier_name": "L & LOPEZ TRUCKING",
    "load_id": "LD-1001",
    "origin": "Dallas, TX",
    "destination": "Chicago, IL",
    "equipment_type": "Van",
    "loadboard_rate": 2850,
    "agreed_rate": 2700,
    "negotiation_rounds": 2,
    "call_outcome": "Success",
    "carrier_sentiment": "Positive",
    "call_summary": "Carrier booked Dallas to Chicago after negotiation.",
    "call_duration": 240
  }'
```

#### `GET /api/v1/metrics`

Aggregated metrics for the dashboard. No auth required.

#### `GET /dashboard`

Analytics dashboard UI. No auth required.

---

## Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → **Web Service**
3. Connect your repository
4. Settings:
   - **Runtime**: Docker
   - **Dockerfile Path**: `./Dockerfile`
5. Add environment variables:
   - `FMCSA_API_KEY` — your FMCSA WebKey
   - `API_KEY` — your API authentication key
   - `NEGOTIATION_FLOOR` — `0.90`
6. Deploy — accessible at `https://your-app.onrender.com`

---

## HappyRobot Configuration

See [`HAPPYROBOT_CONFIG.md`](HAPPYROBOT_CONFIG.md) for the complete agent prompt, tool schemas, classify/extract configurations, and webhook URLs.

---

## Project Structure

```
HR/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings from .env
│   ├── database.py          # SQLite database management
│   ├── auth/
│   │   └── api_key.py       # API key authentication
│   ├── routes/
│   │   ├── carrier.py       # GET /api/v1/carrier
│   │   ├── loads.py         # GET /api/v1/loads
│   │   └── calls.py         # POST /api/v1/calls, GET /api/v1/metrics
│   ├── services/
│   │   ├── fmcsa.py         # FMCSA API client
│   │   └── load_service.py  # Load search logic
│   ├── models/
│   │   ├── carrier.py       # Carrier Pydantic models
│   │   ├── load.py          # Load Pydantic models
│   │   └── call.py          # Call record Pydantic models
│   └── static/
│       ├── dashboard.html   # Analytics dashboard UI
│       ├── styles.css       # Dashboard styles (dark theme)
│       └── app.js           # Dashboard JavaScript (Chart.js)
├── data/
│   ├── loads.json           # 18 sample freight loads
│   └── seed_calls.json      # 18 sample call records for dashboard
├── Dockerfile
├── docker-compose.yml
├── render.yaml              # Render deployment blueprint
├── requirements.txt
└── .env.example
```

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn
- **Database**: SQLite (call records)
- **External API**: FMCSA QCMobile API
- **Frontend**: Vanilla HTML/CSS/JS, Chart.js
- **Deployment**: Docker, Render
