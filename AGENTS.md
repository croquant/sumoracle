# Mission
Fix or extend the codebase without breaking the axioms.

## Overview
- Django project (Python >=3.12)
- Async commands + HTTP client in `libs/sumoapi.py`
- Tests in `tests/`
- Formatting via Ruff and isort

## CLI First
Use shell tools (`ls`, `tree`, `rg`, `awk`, `curl`). Automate with `scripts/*.sh` when useful.

## Quick Explore (run before planning)
```bash
ls -1
tree -L 2 | head -n 40
rg -i "^(def main|class .*Config)" -g '*.py'
rg -i '(test_)\w+' tests/
```
Identify entry points (`manage.py`, `config/settings.py`), models and commands.

## Canonical Truth
Code beats docs. Update docs or open an issue if they diverge.

## Workflow
### Format & Lint
```bash
ruff check .
isort .
ruff --fix .
ruff format .
```
### Tests
```bash
coverage run manage.py test
coverage report -m
```
Must reach 95% coverage (`fail_under` in `pyproject.toml`).
### Pre-commit (if installed)
```bash
pre-commit install
pre-commit run --all-files
```
### Commit
Keep changes focused with clear messages.

## Loop
EXPLORE → PLAN → ACT → OBSERVE → REFLECT → COMMIT. Keep tests green.

## Style
- 80 char lines (`ruff.toml`)
- Prefer async/await

## Layout
- `app/models/` – Django models
- `app/management/commands/` – async commands
- `libs/sumoapi.py` – API client
- `tests/` – unit tests
