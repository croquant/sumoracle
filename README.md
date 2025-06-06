# sumoracle

This Django project interacts with the sumo-api.

## Development Setup

Install all requirements:

```bash
pip install -r requirements.txt
```

Install `pre-commit` and enable the hooks:

```bash
pre-commit install
```

## Linting and Formatting

Run ruff to check code style and `isort` to sort imports.

```bash
ruff .
isort .
```

To automatically fix issues with ruff, run:

```bash
ruff --fix .
```

You can also format the project using Ruff's formatter:

```bash
ruff format .
```

# Sumoracle

This project uses Django. Unit tests are located in the `tests` application.

## Running Tests

Make sure dependencies are installed from `requirements.txt`. Then run

```bash
python manage.py test
```

This command will use Django's built-in test runner to execute all tests.
