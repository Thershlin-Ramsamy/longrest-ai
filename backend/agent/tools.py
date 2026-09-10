"""
The agent's toolbox.

Every function here does exactly one thing to the sample repo, and nothing
else. Keeping the surface area this small is deliberate: it's much easier to
reason about what an autonomous agent *can* do when the list of actions is
short and each one is boring.
"""

import os
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_repo"))


def _safe_path(rel_path: str) -> str:
    """Resolve a path the agent gave us and refuse to leave the sample repo."""
    full = os.path.abspath(os.path.join(REPO_ROOT, rel_path))
    if not full.startswith(REPO_ROOT):
        raise ValueError(f"Refusing to touch a path outside the repo: {rel_path}")
    return full


def list_files(_input: dict) -> str:
    files = []
    for root, _, filenames in os.walk(REPO_ROOT):
        for name in filenames:
            rel = os.path.relpath(os.path.join(root, name), REPO_ROOT)
            files.append(rel)
    return "\n".join(sorted(files))


def read_file(input: dict) -> str:
    path = _safe_path(input["path"])
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(input: dict) -> str:
    path = _safe_path(input["path"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(input["content"])
    return f"Wrote {input['path']} ({len(input['content'])} chars)"


def run_tests(_input: dict) -> str:
    result = subprocess.run(
        ["python", "-m", "pytest", "-v"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return f"exit_code={result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"


TOOL_SCHEMAS = [
    {
        "name": "list_files",
        "description": "List every file in the repository, relative to its root.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "read_file",
        "description": "Read the full contents of one file in the repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relative to the repo root, e.g. calculator.py"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Overwrite a file in the repository with new content. Use this to apply your fix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string", "description": "The full new content of the file"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_tests",
        "description": "Run the test suite and return the output, including pass/fail status.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_tests": run_tests,
}
