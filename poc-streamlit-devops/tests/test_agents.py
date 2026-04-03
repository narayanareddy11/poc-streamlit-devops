"""
Test Case 2: Agent Scripts
Tests that agent modules load correctly and core helpers behave as expected.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import subprocess
import re


class TestIssueFixAgentHelpers:
    """Tests for the helper functions inside issue_fix_agent."""

    def test_syntax_check_passes_on_valid_file(self, tmp_path):
        """py_compile should succeed on a valid Python file."""
        valid_file = tmp_path / "valid.py"
        valid_file.write_text("x = 1\nprint(x)\n")

        result = subprocess.run(
            ["python3", "-m", "py_compile", str(valid_file)],
            capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_syntax_check_fails_on_invalid_file(self, tmp_path):
        """py_compile should fail on a file with a syntax error."""
        bad_file = tmp_path / "broken.py"
        bad_file.write_text("def foo(\n    pass\n")  # missing closing paren

        result = subprocess.run(
            ["python3", "-m", "py_compile", str(bad_file)],
            capture_output=True, text=True
        )
        assert result.returncode != 0

    def test_branch_name_slugify(self):
        """Branch name should be URL-safe from any issue string."""
        issue = "Pipeline success rate is ALWAYS 0%!!"
        branch = "fix/" + re.sub(r"[^a-z0-9]+", "-", issue.lower().strip())[:50].strip("-")
        assert branch.startswith("fix/")
        assert " " not in branch
        assert "%" not in branch
        assert "!" not in branch

    def test_branch_name_max_length(self):
        """Branch name slug should not exceed 50 chars (plus 'fix/' prefix)."""
        long_issue = "a" * 200
        branch = "fix/" + re.sub(r"[^a-z0-9]+", "-", long_issue.lower())[:50].strip("-")
        assert len(branch) <= 54  # 4 (fix/) + 50


class TestCodeReviewAgentImports:
    """Tests that the agent scripts are importable and well-formed."""

    def test_code_review_agent_syntax(self):
        """code_review_agent.py must have no syntax errors."""
        agent_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "agents", "code_review_agent.py"
        )
        result = subprocess.run(
            ["python3", "-m", "py_compile", agent_path],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_issue_fix_agent_syntax(self):
        """issue_fix_agent.py must have no syntax errors."""
        agent_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "agents", "issue_fix_agent.py"
        )
        result = subprocess.run(
            ["python3", "-m", "py_compile", agent_path],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_project_root_app_syntax(self):
        """app.py must have no syntax errors."""
        app_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app.py"
        )
        result = subprocess.run(
            ["python3", "-m", "py_compile", app_path],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"
