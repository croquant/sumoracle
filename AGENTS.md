# Mission

Autonomously fix or extend the codebase without violating the axioms.

## Repository Overview

- Django application. Async commands and HTTP client in `libs/sumoapi.py`.
- Tests live in `tests/`.
- Ruff and isort handle linting and formatting.
- Requires Python 3.12 or later.

## CLI First

Work from the shell using tools like `ls`, `tree`, `grep`/`rg`, `awk`, and
`curl`. Automate recurring checks in `scripts/*.sh` when possible.

## Explore & Map (run before planning)

```bash
ls -1
tree -L 2 | head -n 40
rg -i "^(def main|class .*Config)" -g '*.py'
rg -i '(test_)\w+' tests/
```

Identify entry points (`manage.py`, `config/settings.py`), core models and
management commands.

## Canonical Truth

Code overrides docs. Update documentation or open an issue if anything is out
of sync.

## Workflow

1. **Format and lint**
   ```bash
   ruff check .
   isort .
   ruff --fix .
   ruff format .
   ```
2. **Run tests with coverage**
   ```bash
   coverage run manage.py test
   coverage report -m
   ```
3. **Run pre-commit hooks** (if installed)
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```
4. **Commit** focused changes with a descriptive message.

## Workflow Loop

EXPLORE → PLAN → ACT → OBSERVE → REFLECT → COMMIT. Keep commits small and
ensure tests remain green.

## Coding Style

- Line length is 80 characters (`ruff.toml`).
- Prefer async/await where appropriate.

## Repository Layout

- `app/models/` – Django models.
- `app/management/commands/` – asynchronous commands.
- `libs/sumoapi.py` – async client for the Sumo API.
- `tests/` – unit tests.
