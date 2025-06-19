# Sumoracle

**Sumoracle** is a Django application that consumes data from the
[Sumo API](https://sumo-api.com/).
It provides models, views and management commands for working with rikishi,
basho and other sumo related objects.

## Project setup

This project requires **Python 3.12** or later.

1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install the Python requirements (includes `django-ninja`):
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and adjust the values:
   ```bash
   cp .env.example .env
   ```
   Do not commit the `.env` file to version control.
4. Apply the initial database migrations:
   ```bash
   python manage.py migrate
   ```
5. (Optional) populate the database using these commands:
   ```bash
   python manage.py populate  # fetch rikishi data
   python manage.py history   # import ranking, shikona and measurements history
   ```

## Running the development server

Start Django's built‑in server:
```bash
python manage.py runserver
```
This uses the settings from `config/settings.py` and an SQLite database.

## Docker quickstart

The project includes a `Dockerfile` and `docker-compose.yml` for running
the application in containers.

Build the image:
```bash
docker build -t sumoracle .
```

Start the stack (web + Postgres):
```bash
docker compose up
```

Run management commands inside the container:
```bash
docker compose run web python manage.py migrate
```

Environment variables are read from `.env`. See `.env.example` for the
available keys.

## Linting and formatting

The project relies on [ruff](https://docs.astral.sh/ruff/) and
[isort](https://pycqa.github.io/isort/). You can run them directly:
```bash
ruff check .
isort .
```
To automatically fix issues run:
```bash
ruff --fix .
ruff format .
```

## Running tests

Execute the Django test suite with:
```bash
python manage.py test
```
All tests live inside the `tests` application.

## Coverage reports

The `coverage` package is used to measure test coverage.

To run the test suite with coverage enabled and print a summary:
```bash
coverage run manage.py test
coverage report -m
```
Coverage must be at least 95%.
Open `htmlcov/index.html` in a browser to inspect the report.

## Contributing

We use [pre‑commit](https://pre-commit.com/) to enforce formatting and linting.
Install the hooks after cloning:
```bash
pre-commit install
```
Run all hooks locally before submitting a pull request:
```bash
pre-commit run --all-files
```
Continuous Integration on GitHub Actions runs `ruff check` and the Django test
suite for every pull request.
You can see the configuration in `.github/workflows/ci.yml`.

## Repository layout

- `app/` – main Django application with models, views and management commands.
- `libs/sumoapi.py` – asynchronous client for the public Sumo API.
- `tests/` – Django app with unit tests.

An excerpt from the Sumo API client shows the asynchronous design:
```python
class SumoApiClient:
    """Async client for the public Sumo API."""
    def __init__(self, **client_kwargs):
        ...
```

