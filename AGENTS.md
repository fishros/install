# AGENTS.md

Guidance for coding agents working in this repository.

## 1) Repository Overview

- Project: `fishros/install` one-click installer framework (mainly Python scripts + shell bootstrap).
- Entry points:
- `install` (shell bootstrap script users fetch and run).
- `install.py` (interactive installer and tool dispatcher).
- `tools/` (actual install/config tool implementations).
- `tests/test_runner.py` + `tests/fish_install_test.yaml` (automation harness driven by scripted menu choices).
- CI: `.github/workflows/test-install.yml` runs tests in Docker across Ubuntu `18.04/20.04/22.04/24.04`.

## 2) Environment and Dependencies

- Python target: system `python3` on Ubuntu-like environments.
- Runtime deps used by code/CI:
- `pyyaml`
- `distro`
- System tools commonly required: `wget`, `apt`, `sudo`, `lsb_release`, `curl`, `tar`.
- Typical local setup:
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install --upgrade pip pyyaml distro`

## 3) Build / Lint / Test Commands

There is no compile step and no dedicated lint config in repo.

### 3.1 Build / Package

- No package build pipeline (`setup.py`, `pyproject.toml`, `Makefile`) exists.
- Optional sanity check command:
- `python3 -m py_compile install.py tests/test_runner.py tools/*.py`

### 3.2 Lint / Static Checks

- No enforced linter in CI today.
- If you need lightweight style checks before PR, use optional commands:
- `python3 -m pip install ruff`
- `ruff check install.py tests tools`
- Only auto-fix when explicitly requested by user/reviewer.

### 3.3 Test Commands (Primary)

- Run all tests for auto-detected host Ubuntu codename:
- `cd tests && python3 test_runner.py`
- Run tests for one Ubuntu codename bucket:
- `cd tests && python3 test_runner.py --target-os-version focal`
- Common codenames in repo config:
- `bionic`, `focal`, `jammy`, `noble`

### 3.4 Running a Single Test Case (Important)

`test_runner.py` currently filters by OS codename, not by test name.

- Practical single-case approach:
- Temporarily keep only one case in `tests/fish_install_test.yaml`, run:
- `cd tests && python3 test_runner.py --target-os-version <codename>`
- Or create a temporary YAML containing one case and point runner after a small local patch.
- If adding support, recommended enhancement is a new CLI arg:
- `--test-name <exact_name>` with filtering in `main()`.

### 3.5 CI-Equivalent Test Run

- CI uses Docker Ubuntu images and runs:
- `PYTHONIOENCODING=utf-8 python3 -u test_runner.py`
- It uploads:
- `tests/test_report.json`
- `tests/test_report.html`

## 4) Codebase Structure and Conventions

- `install.py` stores menu metadata in `tools` dict keyed by numeric option IDs.
- Each tool module under `tools/` exports a `Tool` class inheriting `BaseTool`.
- Convention:
- Installation modules: `tools/tool_install_*.py`
- Configuration modules: `tools/tool_config_*.py`
- Tool metadata generally set in `Tool.__init__`:
- `self.name`
- `self.type` (`BaseTool.TYPE_INSTALL` / `TYPE_CONFIG`)
- `self.author`
- Main behavior is usually in helper methods and invoked by `run()`.

## 5) Style Guidelines for Agent Changes

Follow existing project style first; avoid broad refactors unless asked.

### 5.1 Imports

- Use standard library imports first, then local imports.
- Existing code often uses multiple explicit local imports from `.base`; keep that pattern in touched files.
- Do not introduce unused imports.
- Prefer explicit imports over wildcard imports.

### 5.2 Formatting

- Preserve UTF-8 file header where already present:
- `# -*- coding: utf-8 -*-`
- Keep line style consistent with surrounding file (many files use compact spacing patterns).
- Avoid reformatting entire legacy files for style-only reasons.
- Keep functions focused and relatively short when adding new logic.

### 5.3 Types and Function Signatures

- Repo is mostly untyped; do not enforce project-wide typing retrofits.
- You may add targeted type hints for new helper functions if it improves clarity and remains lightweight.
- Keep external behavior backward compatible with Python 3 environments used in CI.

### 5.4 Naming Conventions

- Modules: snake_case with role prefix (`tool_install_`, `tool_config_`).
- Classes: `CamelCase` (`Tool`, utility classes in `base.py`).
- Functions and variables: `snake_case`.
- Constants: upper snake case when truly constant.
- Menu/tool IDs in `install.py` are stable interface points; avoid renumbering existing IDs.

### 5.5 Error Handling and Logging

- Follow existing behavior pattern:
- Use `PrintUtils.print_info/print_warn/print_error/print_success` for user-visible status.
- For command execution, use `CmdTask(...).run()` and inspect return code where failure matters.
- Return explicit status (`True/False` or numeric code) consistently with surrounding file.
- In top-level runners, keep broad exception handling that preserves diagnostics (see `install.py`, `tests/test_runner.py`).
- Do not swallow exceptions silently unless existing flow explicitly tolerates it and cleanup is guaranteed.

### 5.6 Shell and System Command Safety

- Many tools execute privileged commands; minimize risk when editing:
- Avoid changing `sudo` behavior unless necessary.
- Keep noninteractive apt flags for automation where applicable.
- Prefer idempotent operations (`mkdir -p`, safe overwrite logic, backup/restore patterns).
- Be careful with paths under `/tmp` because test harness depends on them.

### 5.7 Test Harness Expectations

- `tests/test_runner.py` creates temporary config and sets `FISH_INSTALL_CONFIG`.
- `install.py` has branches for CI/non-interactive contexts (`GITHUB_ACTIONS`, `FISH_INSTALL_CONFIG`).
- Preserve these checks when modifying startup or post-run behavior.

## 6) Contribution Workflow for Agents

- When adding a new tool:
- Create module in `tools/` using naming conventions above.
- Implement `Tool(BaseTool)` and `run()`.
- Register it in `install.py` `tools` dict with proper `tip`, `type`, path, and dependencies.
- Add or update tests in `tests/fish_install_test.yaml` if behavior should be CI-covered.
- Run relevant test command(s) from section 3 before finishing.

## 7) Cursor / Copilot Rules Status

Checked locations requested by user:

- `.cursorrules`: not present
- `.cursor/rules/`: not present
- `.github/copilot-instructions.md`: not present

If these files are added later, treat them as higher-priority agent instructions and update this document.

## 8) PR/Change Quality Checklist

- Commands in docs still work exactly as written.
- No accidental breaking changes to menu IDs or tool paths.
- New commands handle both interactive and CI/non-interactive contexts.
- Tests executed and outcome captured in final report to user.
- Keep edits focused; avoid unrelated cleanup in legacy files.
