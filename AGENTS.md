# Sumoracle Contributor Guide

Welcome to the Sumoracle codebase. This is a Django 5.2 project that uses
Python 3.12 and relies heavily on asynchronous management commands and an
async HTTP client.

## Project Overview
- `app/` – Django app with models, views and Ninja API routes
- `app/management/commands/` – async commands run via `manage.py`
- `libs/` – helper libraries including `sumoapi.py` (async client)
- `tests/` – unit tests covering the API, models and commands
- Docker files are provided for local development

## Quick Explore
Run these commands before planning any changes:
```bash
ls -1
find . -maxdepth 2 | head -n 40
rg -i "^(def main|class .*Config)" -g '*.py'
rg -i '(test_)\w+' tests/
```
Identify entry points such as `manage.py` and `config/settings.py` as well
as key models and commands.

## Development Workflow
1. **Format & Lint**
   ```bash
   ruff check .
   isort .
   ruff --fix .
   ruff format .
   ```
2. **Run Tests** (coverage must remain above 95%)
   ```bash
   coverage run manage.py test
   coverage report -m
   ```
3. *(Optional)* **Pre‑commit**
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```
4. **Commit** – keep commits focused and descriptive.

Follow the loop: EXPLORE → PLAN → ACT → OBSERVE → REFLECT → COMMIT. Code is
authoritative; update documentation when behaviour changes.

## Style Guidelines
- Maximum line length is 80 characters
- Prefer `async`/`await` for new code

## Pull Request
- Title format: `[sumoracle] <Title>`
- Ensure tests and linting pass before opening the PR

