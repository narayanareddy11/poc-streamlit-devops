"""
Code Review Agent
-----------------
Reviews Python source files for code quality, security, and best practices.

Usage:
    python agents/code_review_agent.py app.py
    python agents/code_review_agent.py data/mock_data.py
    python agents/code_review_agent.py          # reviews all .py files
"""

import sys
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYSTEM_PROMPT = """You are a senior DevOps & Python code reviewer.

When reviewing code, always check for:
1. **Code Quality** — readability, naming conventions, dead code, complexity
2. **Security** — hardcoded secrets, injection risks, unsafe inputs
3. **Performance** — unnecessary computation, memory leaks, inefficient queries
4. **Streamlit best practices** — caching, session state, layout
5. **Error handling** — missing try/except, unhandled edge cases
6. **Style** — PEP 8 compliance, line length, imports

Format your review as:
## Code Review: <filename>
### Summary
<1-2 sentence overall assessment>

### Issues Found
| Severity | Line | Issue | Suggestion |
|----------|------|-------|------------|
...

### Positives
- ...

### Overall Score: X/10
"""


async def run_code_review(target: str | None = None):
    if target:
        prompt = f"Review the file: {target}. Give a detailed code review."
    else:
        prompt = (
            "Review all Python files in this project (app.py and data/mock_data.py). "
            "Give a detailed code review for each file, then a summary."
        )

    print(f"\n{'='*60}")
    print("  CODE REVIEW AGENT")
    print(f"{'='*60}")
    print(f"  Target: {target or 'all Python files'}")
    print(f"{'='*60}\n")

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=PROJECT_ROOT,
            allowed_tools=["Read", "Glob", "Grep"],
            system_prompt=SYSTEM_PROMPT,
            model="claude-opus-4-6",
            max_turns=20,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\n{'='*60}")
            print("  Review complete.")
            print(f"{'='*60}\n")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    anyio.run(run_code_review, target)
