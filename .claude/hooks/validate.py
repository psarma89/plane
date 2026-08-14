#!/usr/bin/env python3

# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Run the pre-commit checks on every agent turn instead of only at commit time.

The JS checks here are the same two commands that .husky/pre-commit runs through
lint-staged, on the same globs. This hook adds no new policy. It moves the
existing policy earlier, so an agent fixes its own lint while it still holds the
context, instead of leaving the work for the commit.

Not included, on purpose:
  - check:types. Turbo declares it dependsOn ^build, so it needs sibling dist
    output and takes minutes. Too slow for a turn gate.
  - ruff format. Python formatting has never been enforced, so running it would
    rewrite large parts of any legacy file an agent touches.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_ROOT = Path(tempfile.gettempdir()) / "plane-turn-gate"

# Mirrors the lint-staged globs in package.json. Keep these two in sync.
FORMAT_SUFFIXES = {
    ".cjs", ".css", ".cts", ".js", ".json", ".jsx",
    ".md", ".mjs", ".mts", ".ts", ".tsx",
}
LINT_SUFFIXES = {".cjs", ".cts", ".js", ".jsx", ".mjs", ".mts", ".ts", ".tsx"}

PY_ROOT = REPO_ROOT / "apps" / "api"
BASE_REFS = ("origin/dev", "dev", "origin/preview", "preview")
OUTPUT_LIMIT = 8000

# Cap on failed stop attempts before the gate gives up and lets the turn end.
# The digest breaker below only catches an agent that changes nothing at all.
# An agent that keeps editing while trying to fix an inherited warning defeats
# it, so bound the cost of that case too.
MAX_ATTEMPTS = 2


def fail(message):
    print(message, file=sys.stderr)
    return 2


def read_event():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as error:
        raise RuntimeError(f"Could not read hook input: {error}") from error


def session_dir(event):
    session_id = str(event.get("session_id", "unknown"))
    return STATE_ROOT / hashlib.sha256(session_id.encode()).hexdigest()[:24]


def normalize_path(raw_path):
    path = Path(raw_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    try:
        path = path.resolve()
        path.relative_to(REPO_ROOT)
    except (OSError, ValueError):
        return None
    return path


def edited_paths(event):
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return [], False

    raw_paths = [
        value
        for key in ("file_path", "notebook_path")
        if isinstance(value := tool_input.get(key), str)
    ]

    paths = []
    for raw_path in raw_paths:
        path = normalize_path(raw_path)
        if path and path not in paths:
            paths.append(path)
    return paths, bool(raw_paths)


def record_paths(directory, paths):
    paths_dir = directory / "paths"
    paths_dir.mkdir(parents=True, exist_ok=True)
    for path in paths:
        relative_path = str(path.relative_to(REPO_ROOT))
        marker = hashlib.sha256(relative_path.encode()).hexdigest()
        (paths_dir / marker).write_text(relative_path)


def recorded_paths(directory):
    paths_dir = directory / "paths"
    if not paths_dir.exists():
        return []
    paths = []
    for marker in paths_dir.iterdir():
        path = normalize_path(marker.read_text())
        if path:
            paths.append(path)
    return paths


def git_paths(command):
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, check=False)
    if result.returncode != 0:
        return []
    paths = []
    for raw_path in result.stdout.split(b"\0"):
        if raw_path:
            path = normalize_path(raw_path.decode())
            if path and path not in paths:
                paths.append(path)
    return paths


def repository_changed_paths():
    """Catch edits the tool matcher missed: shell heredocs, subagents, codemods."""
    merge_base = None
    for base_ref in BASE_REFS:
        result = subprocess.run(
            ["git", "merge-base", "HEAD", base_ref],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        if result.returncode == 0:
            merge_base = result.stdout.strip()
            break

    paths = git_paths(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", "-z", merge_base or "HEAD"]
    )
    for path in git_paths(["git", "ls-files", "--others", "--exclude-standard", "-z"]):
        if path not in paths:
            paths.append(path)
    return paths


def run_command(label, command, timeout):
    try:
        result = subprocess.run(
            command, cwd=REPO_ROOT, capture_output=True,
            text=True, timeout=timeout, check=False,
        )
    except FileNotFoundError:
        return f"{label} could not run because {command[0]} was not found."
    except subprocess.TimeoutExpired:
        return f"{label} did not finish in {timeout} seconds."

    if result.returncode == 0:
        return None

    output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    output = output[-OUTPUT_LIMIT:]
    return f"{label} failed.\n{output}" if output else f"{label} failed."


def relative(paths, suffixes, under=None):
    return [
        str(path.relative_to(REPO_ROOT))
        for path in paths
        if path.exists() and path.suffix in suffixes and (under is None or under in path.parents)
    ]


def format_paths(paths):
    targets = relative(paths, FORMAT_SUFFIXES)
    if not targets:
        return None
    return run_command(
        "Formatting", ["pnpm", "exec", "oxfmt", "--no-error-on-unmatched-pattern", *targets], 60
    )


def state_digest(paths):
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(REPO_ROOT)).encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def validate_paths(paths):
    targets = relative(paths, LINT_SUFFIXES)
    if targets:
        error = run_command(
            "Lint", ["pnpm", "exec", "oxlint", "--fix", "--deny-warnings", *targets], 120
        )
        if error:
            return error

    python_targets = relative(paths, {".py"}, under=PY_ROOT)
    if python_targets and shutil.which("ruff"):
        return run_command("Python lint", ["ruff", "check", *python_targets], 60)
    return None


def handle_edit(event):
    directory = session_dir(event)
    paths, identified = edited_paths(event)

    if not identified:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "unknown-edit").touch()
        return fail(
            "The turn gate could not identify the edited file, so no scoped check ran. "
            "The full changed-file set is checked when the turn ends."
        )

    if not paths:
        return 0

    record_paths(directory, paths)
    error = format_paths(paths)
    return fail(error) if error else 0


def handle_stop(event):
    directory = session_dir(event)
    paths = recorded_paths(directory) if directory.exists() else []
    for path in repository_changed_paths():
        if path not in paths:
            paths.append(path)

    if not paths:
        shutil.rmtree(directory, ignore_errors=True)
        return 0

    directory.mkdir(parents=True, exist_ok=True)
    record_paths(directory, paths)

    digest_before = state_digest(paths)
    error = format_paths(paths)
    if error:
        return fail(error)

    # The formatter changing anything here proves an edit reached disk without
    # passing through the per-edit hook. Block so the agent reviews the result.
    if state_digest(paths) != digest_before:
        return fail(
            "The formatter changed files that were missed during editing. "
            "Review the changes, then finish again."
        )

    if (directory / "unknown-edit").exists():
        return fail(
            "The turn gate could not identify every edited file, so it fell back to "
            "the full changed-file set."
        )

    # Identical bytes since the last failure means the agent cannot satisfy this
    # gate. Let the turn end rather than loop.
    last_attempt = directory / "last-attempt"
    if last_attempt.exists() and last_attempt.read_text() == state_digest(paths):
        return 0

    attempts_file = directory / "attempts"
    attempts = 0
    if attempts_file.exists():
        try:
            attempts = int(attempts_file.read_text())
        except ValueError:
            attempts = 0

    if attempts >= MAX_ATTEMPTS:
        print(
            f"The turn gate failed {attempts} times and is standing down. "
            "The remaining errors are reported above. Leave them for review, "
            "or fix them in a later turn.",
            file=sys.stderr,
        )
        return 0

    error = validate_paths(paths)
    if error:
        # Record the digest AFTER oxlint --fix, not before. The fix pass rewrites
        # bytes, so a digest taken earlier never matches the next stop and costs
        # the agent a second wasted turn.
        last_attempt.write_text(state_digest(paths))
        attempts_file.write_text(str(attempts + 1))
        return fail(f"{error}\nFix the reported error. The gate runs again after the next edit.")

    shutil.rmtree(directory, ignore_errors=True)
    return 0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"edit", "stop"}:
        return fail("Usage: validate.py edit|stop")

    if not (REPO_ROOT / "node_modules").exists():
        print("The turn gate did not run: node_modules is missing. Run pnpm install.", file=sys.stderr)
        return 0

    try:
        event = read_event()
        return handle_edit(event) if sys.argv[1] == "edit" else handle_stop(event)
    except RuntimeError as error:
        return fail(str(error))


if __name__ == "__main__":
    sys.exit(main())
