# Development guide

This guide covers the Django application on the default branch. The supported local path uses SQLite and does not require PostgreSQL, Redis, Node.js, Celery, or external service credentials.

## Prerequisites

- Python 3.12
- Git
- PowerShell on Windows, or a POSIX-compatible shell on macOS/Linux

## Set up a local environment

From the repository root:

```bash
git clone https://github.com/schillgc/Renais-Gin.git
cd Renais-Gin/renais_gin
python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Install the minimal runtime used by the domain-test workflow:

```bash
python -m pip install "Django==6.1.3" "Pillow==13.0.0" "qrcode==8.2"
```

The full repository `requirements.txt` includes additional packages for optional or inactive integrations, including large machine-learning libraries. They are not required for the core app or its domain tests. Install `reportlab==4.4.4` if you want to exercise PDF report generation. Install the pinned PostgreSQL driver from `requirements.txt` only when using PostgreSQL.

## Configure Django

Settings are read directly from environment variables; the project does not automatically load `.env` files. Generate a unique local key and configure the development host list in your current shell:

```bash
# macOS/Linux
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

```powershell
# Windows PowerShell
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1,testserver"
```

The local path uses SQLite only with `DJANGO_DEBUG=true` (as in the commands above). A non-debug process must set `DJANGO_DB_ENGINE=postgresql` and configure `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASSWORD`, and `DJANGO_DB_HOST`; the backend value is `postgresql` or `postgres`, not a Django engine import path. `DJANGO_DB_PORT` defaults to `5432`. Connections require certificate verification: `DJANGO_DB_SSLMODE` defaults to `verify-full` and also accepts `verify-ca`; use `DJANGO_DB_SSLROOTCERT` for a provider CA bundle. Unverified TLS modes are rejected. Never use production credentials in a development environment.

## Run the application

Run commands from `renais_gin/`:

```bash
python manage.py migrate
python manage.py runserver
```

Create an administrator account when needed:

```bash
python manage.py createsuperuser
```

The dashboard and community features require authentication. Sign-up is available at `/signup/`, and Django's login page is at `/accounts/login/`.

## Tests and checks

Run the Django domain tests against isolated in-memory SQLite settings:

```bash
python manage.py test core --settings=renais_gin.test_settings --verbosity 2
```

Run Django checks and ensure model changes have migrations:

```bash
python manage.py check --settings=renais_gin.test_settings
python manage.py makemigrations --check --dry-run --settings=renais_gin.test_settings
python -m compileall -q core renais_gin
```

The settings and API source-contract tests use only the Python standard library. Run them from the repository root:

```bash
python -m unittest discover -s renais_gin -p "test_settings_security.py" -v
python -m unittest discover -s renais_gin -p "test_api_security_contracts.py" -v
```

The GitHub Actions workflows run these test groups on changes to `master` and pull requests. The Django test settings use a disposable in-memory database; do not replace them with a real or shared database.

## Test data and management commands

- `python manage.py refresh_metrics` recalculates and stores the aggregate metrics snapshot. The public metrics endpoint only reads that snapshot.
- `python manage.py add_test_bottles --count 10` creates synthetic bottle records and a fixed `test_user` account. **Use this command only with a disposable local database.** Do not run it against shared, staging, or production data.
- `python manage.py initialize_ecosystem` also refreshes stored metrics; its legacy output mentions an AI ecosystem, but the command does not initialize or call an AI service.

## Database changes

Create and review migrations with:

```bash
python manage.py makemigrations
python manage.py showmigrations
python manage.py migrate
```

Commit migration files with the model changes that require them. Do not delete or rewrite applied migrations to resolve conflicts. For risky schema changes, test forward migration and data preservation on a disposable copy before deployment.

## Contribution workflow

1. Open or link an issue describing the behavior to change.
2. Make a focused change and add tests for new or corrected behavior.
3. Update documentation when routes, setup, configuration, or product claims change.
4. Run the checks above and inspect `git diff --check`.
5. Open a pull request describing the motivation, behavior change, migration impact, and validation performed.

Use imperative, specific commit subjects (for example, `fix: reject duplicate pledge votes`). Do not commit credentials, local databases, uploaded files, generated coverage output, or machine-specific settings.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the project contribution checklist and [SECURITY.md](SECURITY.md) for vulnerability reporting and security boundaries.
