# CLAUDE.md

This file provides context and instructions for Claude when working in this repository.

---

## Project Overview

**Name:** DevOps AI Assistant — Claude POC  
**Purpose:** A Streamlit-based internal DevOps tool powered by Anthropic Claude for log analysis, pipeline debugging, and Kubernetes health checks.  
**Owner:** Narayana Reddy — Senior DevOps & Platform Engineer  
**Stack:** Python 3.11, Streamlit, Anthropic SDK, GCP/AWS

---

## Repository Structure

```
devops-claude-poc/
├── app.py                        # Home dashboard entry point
├── CLAUDE.md                     # This file
├── requirements.txt              # Python dependencies
├── README.md                     # Setup and usage guide
└── pages/
    ├── 1_AI_Chat.py              # Interactive DevOps Q&A
    ├── 2_Pipeline_Monitor.py     # CI/CD log root cause analysis
    ├── 3_Log_Analyzer.py         # Generic log file analyzer
    └── 4_K8s_Health.py           # Kubernetes cluster health advisor
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit >= 1.32 |
| AI Model | claude-sonnet-4-20250514 |
| AI SDK | anthropic >= 0.25 |
| Language | Python 3.11+ |
| Cloud | GCP (primary), AWS (secondary) |
| Container | Docker, Kubernetes (GKE / EKS) |
| IaC | Terraform |
| CI/CD | Jenkins, ArgoCD, Harness |
| Secrets | Environment variable `ANTHROPIC_API_KEY` |

---

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Run on custom port
streamlit run app.py --server.port 8502

# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Lint
flake8 . --max-line-length=120

# Format
black . --line-length 120
```

---

## Claude API Usage

### Model
Always use `claude-sonnet-4-20250514` in this project. Do not switch to Haiku or Opus unless explicitly asked.

### Max Tokens
Default to `max_tokens=2048` for all completions. Increase to `4096` only for long log analysis tasks.

### API Key
Loaded from environment variable only — never hardcoded:
```python
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
```

### Error Handling
All API calls must be wrapped in try/except and surface errors via `st.error()`.

---

## Coding Conventions

- All Python files use **snake_case** for variables and functions
- Streamlit pages follow the naming pattern: `{N}_{Page_Name}.py`
- System prompts are defined as module-level constants (`SYSTEM_PROMPT = ...`)
- Session state keys are lowercase snake_case: `st.session_state.messages`
- Max line length: 120 characters
- Use f-strings for string formatting (not `.format()` or `%`)
- No hardcoded credentials, URLs, or account IDs anywhere

---

## Pages Reference

### `app.py` — Home Dashboard
- Shows summary metrics (pipelines, pod health, alerts)
- Navigation cards to all feature pages
- No Claude API calls on this page

### `pages/1_AI_Chat.py` — AI Chat
- Multi-turn conversation with Claude
- System prompt tuned for DevOps/SRE/Platform Engineering
- Quick prompts sidebar for common scenarios
- Session state key: `messages` (list of role/content dicts)

### `pages/2_Pipeline_Monitor.py` — Pipeline Monitor
- Single-turn log analysis
- Supports Jenkins, GitHub Actions, ArgoCD, Terraform logs
- Analysis depth options: Quick Summary / Deep Dive / Fix + Prevention
- Sample logs built in for demo purposes

### `pages/3_Log_Analyzer.py` — Log Analyzer
- Accepts file upload (.log, .txt, .json) or paste
- Auto-detect or manual log type selection
- Focus area multi-select (errors, warnings, security, etc.)
- Line limit slider to prevent token overflow

### `pages/4_K8s_Health.py` — K8s Health Advisor
- Accepts kubectl output (get pods, get nodes, describe, events)
- Environment context (prod/staging/dev), K8s version, cloud provider
- Outputs health score 1–10 with prioritized fix commands

---

## Adding a New Page

1. Create `pages/{N}_{Name}.py`
2. Add `st.set_page_config(...)` at the top
3. Define a clear system prompt or analysis prompt as a constant
4. Wrap all Claude API calls in try/except
5. Add a download button for the AI response
6. Reference the page in `app.py` navigation card section

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude access |
| `STREAMLIT_SERVER_PORT` | No | Override default port 8501 |

---

## Deployment Notes

### Local (Mac)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

```bash
docker build -t devops-claude-poc .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY devops-claude-poc
```

### Kubernetes (GKE / EKS)
- Store `ANTHROPIC_API_KEY` in Kubernetes Secret or HashiCorp Vault
- Mount as environment variable — never bake into image
- Use Workload Identity (GKE) or IRSA (EKS) for cloud credentials

---

## Known Limitations

- No authentication on Streamlit UI — for internal/demo use only
- No streaming responses yet (Claude streams token-by-token — can be added)
- Log input is truncated to 200 lines by default to stay within token limits
- Session state is lost on page refresh (no persistence layer)

---

## Roadmap / Planned Features

- [ ] Security Scanner — Trivy/Snyk output analysis
- [ ] Terraform Plan Reviewer — paste `terraform plan` output for AI review
- [ ] Streaming responses with `st.write_stream()`
- [ ] GitHub Actions integration via MCP
- [ ] Slack alerting for critical issues
- [ ] Auth via Google OAuth (Streamlit-Authenticator)

---

## Contact

**Narayana Reddy**  
Senior DevOps & Platform Engineer  
Hyderabad, India  
Stack: GCP · AWS · K8s · Terraform · ArgoCD · MLOps
