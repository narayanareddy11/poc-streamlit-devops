"""
Test Case 1: Mock Data Generators
Tests that all four data generators return correct structure and valid values.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
from data.mock_data import (
    generate_pipeline_runs,
    generate_deployments,
    generate_incidents,
    generate_infra_metrics,
    SERVICES,
    ENVIRONMENTS,
)


class TestPipelineRuns:
    def test_returns_dataframe(self):
        df = generate_pipeline_runs(days=7)
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        df = generate_pipeline_runs(days=7)
        required = {"id", "service", "environment", "status", "duration_min", "triggered_at"}
        assert required.issubset(df.columns)

    def test_status_values_are_valid(self):
        df = generate_pipeline_runs(days=7)
        valid = {"success", "failed", "running", "cancelled"}
        assert set(df["status"].unique()).issubset(valid)

    def test_duration_is_positive(self):
        df = generate_pipeline_runs(days=7)
        assert (df["duration_min"] > 0).all()

    def test_services_are_valid(self):
        df = generate_pipeline_runs(days=7)
        assert set(df["service"].unique()).issubset(set(SERVICES))

    def test_row_count_scales_with_days(self):
        df_7 = generate_pipeline_runs(days=7)
        df_14 = generate_pipeline_runs(days=14)
        assert len(df_14) > len(df_7)


class TestDeployments:
    def test_returns_dataframe(self):
        df = generate_deployments(days=7)
        assert isinstance(df, pd.DataFrame)

    def test_status_only_success_or_failed(self):
        df = generate_deployments(days=7)
        assert set(df["status"].unique()).issubset({"success", "failed"})

    def test_environments_are_valid(self):
        df = generate_deployments(days=7)
        assert set(df["environment"].unique()).issubset(set(ENVIRONMENTS))

    def test_version_format(self):
        df = generate_deployments(days=7)
        assert df["version"].str.startswith("v").all()


class TestIncidents:
    def test_returns_dataframe(self):
        df = generate_incidents(days=7)
        assert isinstance(df, pd.DataFrame)

    def test_severity_values_are_valid(self):
        df = generate_incidents(days=7)
        assert set(df["severity"].unique()).issubset({"P1", "P2", "P3", "P4"})

    def test_resolved_is_boolean(self):
        df = generate_incidents(days=7)
        assert df["resolved"].dtype == bool

    def test_unresolved_incidents_have_no_duration(self):
        df = generate_incidents(days=30)
        unresolved = df[df["resolved"] == False]
        assert unresolved["duration_min"].isna().all()


class TestInfraMetrics:
    def test_returns_dataframe(self):
        df = generate_infra_metrics(days=1)
        assert isinstance(df, pd.DataFrame)

    def test_has_all_services(self):
        df = generate_infra_metrics(days=1)
        assert set(df["service"].unique()) == set(SERVICES)

    def test_cpu_pct_is_numeric(self):
        df = generate_infra_metrics(days=1)
        assert pd.api.types.is_float_dtype(df["cpu_pct"])

    def test_row_count_correct(self):
        # 1 day = 24 hours × 5 services = 120 rows
        df = generate_infra_metrics(days=1)
        assert len(df) == 24 * len(SERVICES)
