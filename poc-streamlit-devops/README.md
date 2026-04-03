# DevOps Operations Dashboard

A Streamlit-based DevOps monitoring dashboard POC with mock data visualizations for CI/CD pipelines, deployments, infrastructure metrics, and incidents.

## Features

- **Pipeline Runs** — trends over time, status breakdown (success/failed/running/cancelled)
- **Deployment Frequency** — per service and environment
- **Build Duration** — average build times across services
- **Infrastructure Metrics** — CPU, memory, error rate, and requests/sec (last 7 days)
- **Incidents Table** — severity-coded incident log with resolution status
- **Sidebar Filters** — date range, environment, and service selectors

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit 1.32 |
| Data | Pandas + Faker (mock data) |
| Charts | Plotly Express & Graph Objects |
| Language | Python 3.11+ |

## Project Structure

```
poc-streamlit-devops/
├── app.py              # Main dashboard
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── CLAUDE.md           # Claude Code instructions
└── data/
    └── mock_data.py    # Mock data generators
```

## Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

### Run on a custom port

```bash
streamlit run app.py --server.port 8502
```

## Mock Data

All data is randomly generated using `Faker` — no real infrastructure or credentials required. The sidebar **Refresh Data** button clears the cache and regenerates all data.

## Author

**Narayana Reddy** — Senior DevOps & Platform Engineer  
Hyderabad, India | GCP · AWS · K8s · Terraform · ArgoCD

<!-- yolo -->
