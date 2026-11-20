# Contributing

Thanks for helping improve Renais Gin. This repository is a Django prototype; keep implementation, tests, and documentation aligned with the behavior that actually exists.

## Before you start

- Search existing issues and pull requests for related work.
- For a substantial change, open an issue first to agree on scope.
- Do not publish security-sensitive details in a public issue; follow [SECURITY.md](SECURITY.md).
- Keep changes focused. Avoid adding paid services or claiming external integrations without a working implementation and tests.

## Local checks

Follow [DEVELOPMENT.md](DEVELOPMENT.md) to create the Python 3.12 environment. Before opening a pull request, run the domain tests and checks from `renais_gin/`:

```bash
python manage.py test core --settings=renais_gin.test_settings --verbosity 2
python manage.py check --settings=renais_gin.test_settings
python manage.py makemigrations --check --dry-run --settings=renais_gin.test_settings
python -m compileall -q core renais_gin
```

From the repository root, also run the standard-library security contract tests:

```bash
python -m unittest discover -s renais_gin -p "test_settings_security.py" -v
python -m unittest discover -s renais_gin -p "test_api_security_contracts.py" -v
```

## Pull request expectations

A pull request should:

- Explain the problem and the intended behavior.
- Include focused tests for behavior added or corrected.
- Include migrations when models change; never rewrite applied migrations to avoid a migration conflict.
- Update relevant documentation and remove claims that no longer match the implementation.
- State the commands run and any checks that could not be completed.
- Avoid secrets, real personal data, generated databases, uploaded media, and machine-specific files.

Use a specific imperative commit subject, preferably in Conventional Commit form, such as `fix: reject duplicate pledge votes` or `docs: clarify metrics snapshot behavior`. Keep the subject concise; use a body for motivation, important implementation details, or compatibility notes.

## Project boundaries

Pledge approval is community review, not verification of real-world impact. Metric values are stored aggregates, not audited outcomes. The current prototype does not make payments, call an AI model, or submit blockchain transactions. Changes must preserve these boundaries unless a separately reviewed, tested integration is actually implemented.
