# Sumoracle

Sumoracle is a Django 5.2 project that imports sumo data from
[sumo-api.com](https://sumo-api.com/).  It exposes HTML pages, a small
REST API and several management commands for gathering and analysing
basho results.

## Features

- Async `SumoApiClient` for talking to the public API
- Models for divisions, rikishi, basho, bouts and historic rankings
- Pages rendered with Django templates
- Ninja API routes under `/api/`
- Async management commands: `populate`, `history`, `bouts`, `glicko`,
  `dataset` and `importance` (neural network)

## Quick start

1. Use **Python 3.12** and install the requirements
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy the example environment file and edit the values
   ```bash
   cp .env.example .env
   ```
3. Run the migrations
   ```bash
   python manage.py migrate
   ```
4. Optionally load data from the API
   ```bash
   python manage.py populate  # rikishi and divisions
   python manage.py history   # rankings and measurements
   python manage.py bouts     # individual matches
   python manage.py glicko    # compute ratings
   python manage.py dataset   # export CSV dataset
   python manage.py importance <file>  # neural network feature analysis
   ```
5. Start the development server
   ```bash
   python manage.py runserver
   ```

## Docker

A `Dockerfile` and `docker-compose.yml` are provided.  The stack runs the
web server and a Postgres container.

```bash
docker compose up
```

The entrypoint waits for the database and applies migrations before
starting Gunicorn.

## Management commands

All custom commands derive from an asynchronous base class.  A snippet
from `AsyncBaseCommand` shows the structure:
```python
class AsyncBaseCommand(BaseCommand):
    """Base class for async management commands."""

    async def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement run()")

    def handle(self, *args, **kwargs):
        try:
            asyncio.run(self.run(*args, **kwargs))
        except SumoApiError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
```

See `app/management/commands/` for the concrete implementations.

## API

The Ninja API lives at `/api/` with routers for rikishi, divisions and
basho.  Requests return JSON schemas defined in `app/schemas`.

## Tests and formatting

- Lint with Ruff and isort
  ```bash
  ruff check .
  isort .
  ruff --fix .
  ruff format .
  ```
- Run the test suite with coverage
  ```bash
  coverage run manage.py test
  coverage report -m
  ```
  Coverage must stay above 95%.

## Project layout

- `app/` – Django app with models, views and commands
- `libs/sumoapi.py` – async HTTP client
- `tests/` – unit tests ensuring >95% coverage

Sumoracle is released under the license found in `LICENSE.md`.
