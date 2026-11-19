# Review: `full` branch integration gates

**Review date:** 2026-11-19  
**Branch reviewed:** `full`  
**Branch head reviewed:** `161f76f9f5a87878bee81c03fb75b5cf9ab25d4f`

## Decision

Do not merge `full` directly into `master` yet. The branch contains a substantially larger Django application, but it diverges from the current default branch and its configuration is not safe to ship unchanged. This is an integration candidate, not a deployable release.

## Concrete blockers observed

1. **Insecure Django settings on the branch.** `renais_gin/renais_gin/settings.py` contains a hard-coded development `SECRET_KEY`, `DEBUG = True`, and `ALLOWED_HOSTS = ['*']`. The default branch has since been hardened to require `DJANGO_SECRET_KEY`, parse `DJANGO_DEBUG` strictly, and require explicit production hostnames. Preserve that security contract when integrating any feature code.
2. **Tracked coverage output.** The branch includes `renais_gin/.coverage`, a generated coverage artifact that does not belong in source control.
3. **No verified branch CI run.** No workflow run was returned for the reviewed `full` head SHA. The existing default-branch settings contract workflow does not prove that the larger branch's models, migrations, API endpoints, background tasks, templates, or dependencies work together.
4. **Major database and application changes.** The branch adds or changes substantial models, migrations, services, admin modules, templates, and asynchronous tasks. These need a disposable-database migration rehearsal and behavior tests before they can be trusted.
5. **Dependency baseline needs review.** The branch introduces a separate dependency set, including a Celery release-candidate pin. Establish a reproducible supported dependency set and verify compatibility before deployment.

## Required integration sequence

- Create a new integration branch from the current `master`; do not force-update `master` or overwrite the historical `full` branch.
- Port the larger application's source in reviewable slices while retaining the current hardened settings contract.
- Remove generated artifacts and ensure local environments, databases, and credentials remain untracked.
- Add isolated CI that installs the application dependencies, runs `pip check`, compiles Python source, runs Django system checks, checks migration consistency, and executes application tests.
- Run forward and reverse migration preservation tests against a disposable database seeded with representative synthetic records. Never use the tracked database for this rehearsal.
- Add tests for API permissions, authentication, input validation, rate limits, webhook/provider failure modes, and sensitive-data handling.
- Verify Docker, worker, Redis, and web-service configuration separately. A passing unit test suite does not establish a production deployment.
- Update the README's feature claims to match functions that are actually implemented and validated.

## Preserved scope

The branch is retained as historical work. This review does not delete files, rewrite Git history, rotate production credentials, or deploy the application. Any historical key exposed on the branch must be treated as compromised and rotated at the provider/deployment layer; changing source code alone does not revoke it.
