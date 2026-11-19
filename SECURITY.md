# Security

## Required deployment configuration

The Django application requires `DJANGO_SECRET_KEY` and fails during startup if it is missing. Generate a unique, high-entropy value for each environment and store it in the hosting platform's secret manager. Never commit the value to Git.

- `DJANGO_SECRET_KEY`: required secret; rotate it if it has ever been committed or exposed.
- `DJANGO_DEBUG`: defaults to `false`; accepted values are `true/false`, `yes/no`, `on/off`, and `1/0`.
- `DJANGO_ALLOWED_HOSTS`: comma-separated hostnames. Set the actual production hostnames explicitly.

## Existing key exposure

The historical default-branch settings file contained a hard-coded Django signing key. Treat that value as compromised: generate and deploy a new `DJANGO_SECRET_KEY` immediately. Removing a key from the current file does not erase it from Git history. If history is rewritten later, coordinate the rewrite with collaborators and rotate the key regardless.

## Local development

Set a fresh local-only `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=true`, and set `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1` in your shell before running Django commands. Do not reuse production credentials locally.
