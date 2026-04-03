"""
Issue Fix Agent
---------------
Takes an issue description, fixes the code, runs tests, and raises a GitHub PR.

Usage:
    python agents/issue_fix_agent.py "Pipeline success rate metric is always showing 0%"
    python agents/issue_fix_agent.py "Add a dark mode toggle to the sidebar"
"""

import sys
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock
import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYSTEM_PROMPT = """You are a senior DevOps & Python engineer working on a Streamlit DevOps dashboard.

Your workflow for fixing an issue:
1. **Understand** — Read relevant files to understand the codebase
2. **Diagnose** — Identify the root cause of the issue
3. **Fix** — Make the minimal, correct code change
4. **Verify** — Run basic checks (syntax, imports) using Bash
5. **Report** — Summarize what you changed and why

Rules:
- Only change what is necessary to fix the issue
- Do not add unrelated improvements
- Prefer editing existing files over creating new ones
- After fixing, always run: python3 -m py_compile <changed_file> to verify syntax
- Always show a diff-style summary of your changes
"""


def run_tests(project_root: str) -> tuple[bool, str]:
    """Run syntax checks on all Python files."""
    results = []
    passed = True

    py_files = ["app.py", "data/mock_data.py"]
    for f in py_files:
        path = os.path.join(project_root, f)
        if not os.path.exists(path):
            continue
        result = subprocess.run(
            ["python3", "-m", "py_compile", path],
            capture_output=True, text=True
        )
        status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
        if result.returncode != 0:
            passed = False
            results.append(f"{status} {f}\n  {result.stderr.strip()}")
        else:
            results.append(f"{status} {f}")

    return passed, "\n".join(results)


def create_pr(issue: str, project_root: str) -> str:
    """Create a git branch, commit changes, and open a PR."""
    import re

    # Create branch name from issue
    branch = "fix/" + re.sub(r"[^a-z0-9]+", "-", issue.lower().strip())[:50].strip("-")

    try:
        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=project_root
        )
        if not status.stdout.strip():
            return "No changes detected — nothing to commit."

        # Create and switch to new branch
        subprocess.run(["git", "checkout", "-b", branch], cwd=project_root, check=True)

        # Stage all modified tracked files
        subprocess.run(["git", "add", "-u"], cwd=project_root, check=True)

        # Commit
        commit_msg = f"fix: {issue[:72]}\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=project_root, check=True)

        # Push branch
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            cwd=project_root, check=True
        )

        # Create PR via gh CLI
        pr_result = subprocess.run(
            [
                "gh", "pr", "create",
                "--title", f"fix: {issue[:70]}",
                "--body", f"## Summary\n- Fixes: {issue}\n\n## Changes\nAutomatically fixed by Issue Fix Agent.\n\n🤖 Generated with Claude Opus 4.6",
                "--base", "main",
                "--head", branch,
            ],
            capture_output=True, text=True, cwd=project_root
        )
        if pr_result.returncode == 0:
            return f"PR created: {pr_result.stdout.strip()}"
        else:
            return f"Push succeeded but PR creation failed: {pr_result.stderr.strip()}\nBranch: {branch}"

    except subprocess.CalledProcessError as e:
        return f"Git/PR step failed: {e}"


async def run_issue_fix(issue: str):
    print(f"\n{'='*60}")
    print("  ISSUE FIX AGENT")
    print(f"{'='*60}")
    print(f"  Issue: {issue}")
    print(f"{'='*60}\n")

    print("🔍 Analyzing and fixing issue...\n")

    async for message in query(
        prompt=f"Fix this issue: {issue}",
        options=ClaudeAgentOptions(
            cwd=PROJECT_ROOT,
            allowed_tools=["Read", "Glob", "Grep", "Edit", "Write", "Bash"],
            system_prompt=SYSTEM_PROMPT,
            model="claude-opus-4-6",
            permission_mode="acceptEdits",
            max_turns=30,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\n{'='*60}")
            print("  Fix complete. Running tests...")
            print(f"{'='*60}\n")

            # Run tests
            passed, test_output = run_tests(PROJECT_ROOT)
            print(test_output)

            if passed:
                print(f"\n✅ All tests passed!\n")
                print("🚀 Creating PR...\n")
                pr_result = create_pr(issue, PROJECT_ROOT)
                print(pr_result)
            else:
                print(f"\n❌ Tests failed — PR not created. Please review the errors above.")

            print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agents/issue_fix_agent.py \"<issue description>\"")
        sys.exit(1)

    issue = " ".join(sys.argv[1:])
    anyio.run(run_issue_fix, issue)
