import pandas as pd
import random
from datetime import datetime, timedelta

SERVICES = ["auth-service", "api-gateway", "payment-service", "user-service", "notification-service"]
ENVIRONMENTS = ["dev", "staging", "production"]
STATUSES = ["success", "failed", "running", "cancelled"]
INCIDENT_SEVERITY = ["P1", "P2", "P3", "P4"]


def generate_pipeline_runs(days=30) -> pd.DataFrame:
    records = []
    base = datetime.now()
    for i in range(days * 8):
        ts = base - timedelta(hours=random.randint(0, days * 24))
        status = random.choices(STATUSES, weights=[70, 15, 8, 7])[0]
        records.append({
            "id": f"run-{i+1:04d}",
            "service": random.choice(SERVICES),
            "environment": random.choice(ENVIRONMENTS),
            "status": status,
            "duration_min": round(random.uniform(1.5, 18.0), 2),
            "triggered_at": ts,
            "branch": random.choice(["main", "develop", f"feature/task-{random.randint(100,999)}"]),
        })
    df = pd.DataFrame(records).sort_values("triggered_at", ascending=False).reset_index(drop=True)
    return df


def generate_deployments(days=30) -> pd.DataFrame:
    records = []
    base = datetime.now()
    for i in range(days * 3):
        ts = base - timedelta(hours=random.randint(0, days * 24))
        success = random.random() > 0.1
        records.append({
            "id": f"deploy-{i+1:04d}",
            "service": random.choice(SERVICES),
            "environment": random.choice(ENVIRONMENTS),
            "version": f"v1.{random.randint(0,9)}.{random.randint(0,99)}",
            "status": "success" if success else "failed",
            "deployed_at": ts,
            "deploy_duration_min": round(random.uniform(2, 12), 2),
        })
    df = pd.DataFrame(records).sort_values("deployed_at", ascending=False).reset_index(drop=True)
    return df


def generate_incidents(days=30) -> pd.DataFrame:
    records = []
    base = datetime.now()
    for i in range(random.randint(15, 30)):
        start = base - timedelta(hours=random.randint(0, days * 24))
        duration = random.randint(5, 480)
        resolved = random.random() > 0.15
        records.append({
            "id": f"INC-{1000+i}",
            "service": random.choice(SERVICES),
            "severity": random.choices(INCIDENT_SEVERITY, weights=[5, 20, 45, 30])[0],
            "title": random.choice([
                "High latency on API endpoint",
                "Deployment rollback triggered",
                "Database connection pool exhausted",
                "Memory leak detected",
                "SSL certificate expiry warning",
                "Disk usage above 90%",
                "Auth service 5xx spike",
            ]),
            "started_at": start,
            "duration_min": duration if resolved else None,
            "resolved": resolved,
            "environment": random.choice(ENVIRONMENTS),
        })
    df = pd.DataFrame(records).sort_values("started_at", ascending=False).reset_index(drop=True)
    return df


def generate_infra_metrics(days=7) -> pd.DataFrame:
    records = []
    base = datetime.now()
    for h in range(days * 24):
        ts = base - timedelta(hours=h)
        for svc in SERVICES:
            records.append({
                "timestamp": ts,
                "service": svc,
                "cpu_pct": round(random.gauss(45, 15), 1),
                "memory_pct": round(random.gauss(60, 10), 1),
                "error_rate_pct": round(max(0, random.gauss(1.5, 1.2)), 2),
                "req_per_sec": round(max(0, random.gauss(200, 80)), 0),
            })
    return pd.DataFrame(records)
