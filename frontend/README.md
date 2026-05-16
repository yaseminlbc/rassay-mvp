# RASSAY Frontend

RASSAY is a B2B SaaS churn early-warning dashboard for Customer Success teams. The frontend currently runs with synthetic mock data and is prepared for a future FastAPI backend.

## Technology Stack

- React
- Vite
- Tailwind CSS
- React Router
- Recharts
- Lucide React

## Local Setup

```bash
cd frontend
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Environment Variables

Copy `.env.example` when configuring local environment values.

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=true
```

`VITE_API_BASE_URL` points to the future FastAPI backend. `VITE_USE_MOCK_DATA=true` keeps the frontend running with local synthetic data.

## Mock Mode

The frontend currently uses synthetic mock data from `src/data/mockData.js` through `src/services/api.js`. The mock shape is compatible with the planned RASSAY backend contract, including numeric `company_id` routing.

## FastAPI Integration

When the backend is ready, set:

```env
VITE_USE_MOCK_DATA=false
```

Make sure FastAPI is running at:

```text
http://localhost:8000
```

## Routes

- `/`
- `/customers/:company_id`
- `/integrations`

## Implemented Features

- Churn Risk Command Center
- Search and risk filtering
- CSV export
- Customer Detail & XAI Insights
- Data Integration Settings
