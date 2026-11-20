# Security policy

Renais Gin is a prototype, not a production-verified service. It does not independently verify bottle provenance, pledge outcomes, impact claims, or user identity. It does not process payments or interact with a live AI or blockchain provider.

## Reporting a vulnerability

Do not disclose exploitable details in a public issue. If GitHub private vulnerability reporting is enabled for this repository, use the repository's **Report a vulnerability** flow. Otherwise, contact the repository maintainers privately through GitHub and include:

- Affected commit, route, or component
- Preconditions and a concise reproduction
- Potential impact and any safe mitigation

Please avoid accessing or modifying data that is not yours. This project has no published response-time guarantee.

## Deployment secrets and settings

The Django application requires a non-empty `DJANGO_SECRET_KEY` and fails at startup if it is missing. Use a unique, high-entropy value for each environment, store it in a secrets manager, and never commit it.

| Variable | Requirement |
|---|---|
| `DJANGO_SECRET_KEY` | Required; generate a unique secret and rotate it if exposed. |
| `DJANGO_DEBUG` | Defaults to `false`; accepted values are `true`/`false`, `yes`/`no`, `on`/`off`, and `1`/`0`. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames; explicitly set production hosts. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Optional comma-separated trusted origins for deployments that need them. |
| `DJANGO_DB_*` | Optional database settings; SQLite is used when `DJANGO_DB_ENGINE` is omitted. |

With `DEBUG` disabled, the settings enable HTTPS redirection, secure session and CSRF cookies, and HSTS. A production deployment must still provide correct TLS termination, host configuration, trusted origins, database configuration, static/media storage, backups, monitoring, and operational review. The repository does not provide a complete production deployment.

The root `.env.example` contains placeholders, not usable secrets. The app reads environment variables directly and does not load a `.env` file automatically. Do not reuse production credentials in local development.

## Historical credential exposure

A historical default-branch settings file contained a hard-coded Django signing key. Treat it as compromised: rotate it in every environment where it may have been used. Removing a secret from the current tree—or rewriting Git history—does not revoke it. Repository history may still contain prior copies.

## Application and data boundaries

- Pledge text screening is a deterministic heuristic, not AI, fraud detection, or proof of authenticity. Community voting is account-based and cannot establish unique real-world voters.
- Bottle and terroir fields are stored as supplied. Generated QR codes encode record data but do not authenticate a product.
- Approval changes a pledge's status; it does not issue a rebate. Metric fields are database aggregates, not verified impact or payment records.
- PDF upload checks the 10 MiB size limit, file extension, and `%PDF-` header. These checks do not scan for malware or guarantee that a document is safe to open. Treat uploaded files as untrusted.
- Avoid entering sensitive personal information in pledge, circle, or product data. Use synthetic data for development and tests.

For local development, set a fresh local-only `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=true`, and allow only local/test hosts such as `localhost`, `127.0.0.1`, and `testserver`.
