# Renais Gin

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![Django 5.2.19](https://img.shields.io/badge/django-5.2.19-green)](https://www.djangoproject.com/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue)](https://www.gnu.org/licenses/agpl-3.0.html)

Renais Gin is a Django prototype for registering bottle records, submitting sustainability pledges, reviewing pledges as a community, and viewing stored aggregate metrics. It is not a production verification or payments platform: submitted claims and product data are not independently verified, and the application does not call an AI model, write to a blockchain, or issue rebates.

## GitHub Pages demo

[Try the interactive browser demo](https://schillgc.github.io/Renais-Gin/). It demonstrates the bottle and pledge flow using static HTML, CSS, and JavaScript. It does not connect to Django, send form data to a server, create real accounts or reviews, or persist data; refreshing the page resets the demo.

The Django application still requires a Python host and database. GitHub Pages cannot run Django. See [Quick start](#quick-start) to run the application locally.

## What the prototype does

- **Bottle records:** Stores a bottle ID, batch, production date, and supplied terroir data. A QR image can be generated from those fields; it does not prove a bottle's authenticity or sourcing.
- **Pledges:** An authenticated user can submit one pledge per bottle registered to their account. A deterministic text heuristic may reject a submission; otherwise, it enters community review. The heuristic is not AI and does not approve claims.
- **Community review:** Authenticated accounts other than the pledge author may vote once per pledge. Three positive votes approve it; three negative votes reject it. Account uniqueness is not real-world identity verification.
- **Community circles:** Authenticated users can create, join, and leave circles. A circle leader cannot leave while they remain its leader.
- **PDFs and reports:** Users can upload PDFs and download their own files. Impact reports are generated from application records; neither uploads nor reported impacts are independently verified.
- **Movement metrics:** `GET /api/metrics/` returns the last stored snapshot without recalculating it. Run the `refresh_metrics` management command to update that snapshot.

The metrics are database aggregates, not independently audited impact results. In particular, the `total_rebates` field counts records marked as processed; it does not represent payments made by this prototype. The `impact_stories` field counts approved pledges, not verified stories.

## Quick start

The application and its domain tests use Python 3.12. The default local database is SQLite.

1. Create and activate a virtual environment:

   ```bash
   cd renais_gin
   python -m venv .venv
   # macOS/Linux
   source .venv/bin/activate
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

2. Install the small runtime used by the app's domain-test workflow:

   ```bash
   python -m pip install "Django==5.2.19" "Pillow==13.0.0" "qrcode==8.2"
   ```

   PDF report generation also requires `reportlab` (`python -m pip install "reportlab==4.4.4"`). The full `requirements.txt` includes additional, resource-intensive packages for integrations that are not active features of this prototype.

3. Configure local settings in the same shell:

   ```bash
   # macOS/Linux
   export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
   export DJANGO_DEBUG=true
   export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver
   ```

   In Windows PowerShell:

   ```powershell
   $env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   $env:DJANGO_DEBUG = "true"
   $env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1,testserver"
   ```

4. Apply migrations and start the development server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

   Open `http://127.0.0.1:8000/`. The dashboard requires an account; create one at `/signup/` or create an administrator with `python manage.py createsuperuser`.

The settings module reads environment variables directly; it does not load a `.env` file. Never use a development secret in production. PostgreSQL can be selected with the `DJANGO_DB_*` variables documented in [`.env.example`](.env.example); install the PostgreSQL driver from `requirements.txt` when using that database.

## Main routes

| Route | Access | Purpose |
|---|---|---|
| `/signup/` | Public | Create an account |
| `/accounts/login/` | Public | Sign in |
| `/` | Authenticated | View the user's bottles, pledges, and circles |
| `/register-bottle/` | Authenticated | Register an existing, unregistered bottle record |
| `/submit-pledge/<bottle_id>/` | Authenticated owner | Submit a pledge for a bottle registered to the account |
| `/validate-pledge/<pledge_id>/` | Authenticated reviewer | Review another account's pledge |
| `/circles/` | Authenticated | Browse community circles |
| `/api/metrics/` | Public, GET only | Read the stored metrics snapshot |

This is a Django server-rendered application, not a general REST API. There is no `/api/pledges/` endpoint.

## Tests and checks

Run the domain suite from `renais_gin/` using the isolated, in-memory test settings:

```bash
python manage.py test core --settings=renais_gin.test_settings --verbosity 2
python manage.py check --settings=renais_gin.test_settings
python manage.py makemigrations --check --dry-run --settings=renais_gin.test_settings
```

Run the standard-library security contract tests from the repository root:

```bash
python -m unittest discover -s renais_gin -p "test_settings_security.py" -v
python -m unittest discover -s renais_gin -p "test_api_security_contracts.py" -v
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for development workflow, database configuration, test-data cautions, and contribution guidance. See [SECURITY.md](SECURITY.md) for security boundaries and reporting guidance.

## Project layout

```text
.
├── renais_gin/
│   ├── core/                 # Models, forms, views, templates, migrations, commands
│   ├── renais_gin/           # Django settings and URL configuration
│   ├── manage.py
│   ├── test_api_security_contracts.py
│   └── test_settings_security.py
├── .github/workflows/        # Domain and security contract checks
├── docs/                     # Project review records
├── DEVELOPMENT.md
├── SECURITY.md
└── requirements.txt
```

## Status and license

This repository is an independently maintained demonstration. It does not establish product authenticity, environmental outcomes, financial rewards, or endorsement by a brand or supplier. See [LICENSE](LICENSE) for the GNU Affero General Public License version 3.
