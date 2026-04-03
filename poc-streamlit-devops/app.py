import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from data.mock_data import (
    generate_pipeline_runs,
    generate_deployments,
    generate_incidents,
    generate_infra_metrics,
)

st.set_page_config(
    page_title="DevOps Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("🚀 DevOps Dashboard")
st.sidebar.markdown("POC — Streamlit + Mock DevOps Data")

days = st.sidebar.slider("Date range (days)", 7, 60, 30)
selected_env = st.sidebar.multiselect(
    "Environment",
    ["dev", "staging", "production"],
    default=["dev", "staging", "production"],
)
selected_service = st.sidebar.multiselect(
    "Service",
    ["auth-service", "api-gateway", "payment-service", "user-service", "notification-service"],
    default=["auth-service", "api-gateway", "payment-service", "user-service", "notification-service"],
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data(days):
    return (
        generate_pipeline_runs(days),
        generate_deployments(days),
        generate_incidents(days),
        generate_infra_metrics(min(days, 7)),
    )

pipelines, deployments, incidents, metrics = load_data(days)

cutoff = datetime.now() - timedelta(days=days)
pipelines = pipelines[pipelines["triggered_at"] >= cutoff]
deployments = deployments[deployments["deployed_at"] >= cutoff]
incidents = incidents[incidents["started_at"] >= cutoff]

# Apply filters
if selected_env:
    pipelines = pipelines[pipelines["environment"].isin(selected_env)]
    deployments = deployments[deployments["environment"].isin(selected_env)]
    incidents = incidents[incidents["environment"].isin(selected_env)]
    metrics = metrics[metrics["service"].isin(selected_service)]

if selected_service:
    pipelines = pipelines[pipelines["service"].isin(selected_service)]
    deployments = deployments[deployments["service"].isin(selected_service)]
    incidents = incidents[incidents["service"].isin(selected_service)]

# ── Page title ────────────────────────────────────────────────────────────────
st.title("🚀 MCP-DevOps Operations Dashboard")
st.caption(f"Last {days} days · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

# ── KPI cards ─────────────────────────────────────────────────────────────────
total_runs = len(pipelines)
success_rate = (pipelines["status"] == "success").mean() * 100 if total_runs else 0
total_deploys = len(deployments)
deploy_success = (deployments["status"] == "success").mean() * 100 if total_deploys else 0
open_incidents = incidents[~incidents["resolved"]].shape[0]
p1_incidents = incidents[(incidents["severity"] == "P1") & (~incidents["resolved"])].shape[0]
avg_build_min = pipelines["duration_min"].mean() if total_runs else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Pipeline Runs", total_runs)
k2.metric("Pipeline Success Rate", f"{success_rate:.1f}%",
          delta=f"{success_rate - 85:.1f}% vs target",
          delta_color="normal")
k3.metric("Deployments", total_deploys)
k4.metric("Deploy Success Rate", f"{deploy_success:.1f}%")
k5.metric("Open Incidents", open_incidents,
          delta=f"P1: {p1_incidents}",
          delta_color="inverse")

st.markdown("---")

# ── Row 1: Pipeline trends + Status breakdown ─────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Pipeline Runs Over Time")
    df_daily = (
        pipelines.assign(date=pipelines["triggered_at"].dt.date)
        .groupby(["date", "status"])
        .size()
        .reset_index(name="count")
    )
    fig = px.bar(
        df_daily, x="date", y="count", color="status",
        color_discrete_map={"success": "#2ecc71", "failed": "#e74c3c",
                            "running": "#3498db", "cancelled": "#95a5a6"},
        labels={"count": "Runs", "date": "Date"},
        height=300,
    )
    fig.update_layout(margin=dict(t=10, b=10), legend_title="Status")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Status Breakdown")
    status_counts = pipelines["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig2 = px.pie(
        status_counts, names="status", values="count",
        color="status",
        color_discrete_map={"success": "#2ecc71", "failed": "#e74c3c",
                            "running": "#3498db", "cancelled": "#95a5a6"},
        height=300,
    )
    fig2.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Deployment frequency + Build duration ──────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Deployment Frequency by Service")
    deploy_svc = (
        deployments.groupby(["service", "status"])
        .size()
        .reset_index(name="count")
    )
    fig3 = px.bar(
        deploy_svc, x="service", y="count", color="status",
        color_discrete_map={"success": "#2ecc71", "failed": "#e74c3c"},
        barmode="group", height=300,
        labels={"count": "Deployments", "service": "Service"},
    )
    fig3.update_layout(margin=dict(t=10, b=10), xaxis_tickangle=-20)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Avg Build Duration by Service (min)")
    build_dur = pipelines.groupby("service")["duration_min"].mean().reset_index()
    build_dur.columns = ["service", "avg_duration"]
    fig4 = px.bar(
        build_dur.sort_values("avg_duration", ascending=True),
        x="avg_duration", y="service", orientation="h",
        color="avg_duration", color_continuous_scale="Blues",
        height=300, labels={"avg_duration": "Avg Duration (min)", "service": ""},
    )
    fig4.update_layout(margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Infra metrics ──────────────────────────────────────────────────────
st.subheader("Infrastructure Metrics (Last 7 days)")

svc_pick = st.selectbox("Select service", options=metrics["service"].unique())
svc_metrics = metrics[metrics["service"] == svc_pick].sort_values("timestamp")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Avg CPU %", f"{svc_metrics['cpu_pct'].mean():.1f}%")
m2.metric("Avg Memory %", f"{svc_metrics['memory_pct'].mean():.1f}%")
m3.metric("Avg Error Rate %", f"{svc_metrics['error_rate_pct'].mean():.2f}%")
m4.metric("Avg Req/s", f"{svc_metrics['req_per_sec'].mean():.0f}")

fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=svc_metrics["timestamp"], y=svc_metrics["cpu_pct"],
                           name="CPU %", line=dict(color="#3498db")))
fig5.add_trace(go.Scatter(x=svc_metrics["timestamp"], y=svc_metrics["memory_pct"],
                           name="Memory %", line=dict(color="#e67e22")))
fig5.add_trace(go.Scatter(x=svc_metrics["timestamp"], y=svc_metrics["error_rate_pct"],
                           name="Error Rate %", line=dict(color="#e74c3c"),
                           yaxis="y2"))
fig5.update_layout(
    height=300,
    margin=dict(t=10, b=10),
    yaxis=dict(title="CPU / Memory %", range=[0, 100]),
    yaxis2=dict(title="Error Rate %", overlaying="y", side="right", range=[0, 10]),
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig5, use_container_width=True)

# ── Row 4: Incidents table ────────────────────────────────────────────────────
st.subheader("Recent Incidents")
severity_colors = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "P4": "🟢"}
display_inc = incidents.copy()
display_inc["sev"] = display_inc["severity"].map(severity_colors) + " " + display_inc["severity"]
display_inc["resolved_label"] = display_inc["resolved"].map({True: "✅ Resolved", False: "🔥 Open"})
display_inc["duration"] = display_inc["duration_min"].apply(
    lambda x: f"{int(x)} min" if pd.notna(x) else "ongoing"
)

st.dataframe(
    display_inc[["id", "sev", "title", "service", "environment",
                 "started_at", "duration", "resolved_label"]]
    .rename(columns={
        "id": "ID", "sev": "Severity", "title": "Title",
        "service": "Service", "environment": "Env",
        "started_at": "Started", "duration": "Duration",
        "resolved_label": "Status",
    }),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")
st.caption("POC · Built with Streamlit · Mock data only")
