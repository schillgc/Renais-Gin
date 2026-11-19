#!/usr/bin/env python
"""Prepare a local Renais Gin checkout without creating migrations or demo credentials."""

from pathlib import Path
import subprocess
import sys


def run(*args):
    print("\\n> " + " ".join(args), flush=True)
    subprocess.run(args, check=True)


def main():
    project_dir = Path(__file__).resolve().parent
    manage_py = project_dir / "manage.py"
    if not manage_py.is_file():
        raise SystemExit("manage.py was not found beside this setup script.")

    for relative in (
        "media/qr_codes",
        "media/pdfs/user_uploads",
        "media/pdfs/generated_reports",
        "staticfiles",
        "logs",
    ):
        (project_dir / relative).mkdir(parents=True, exist_ok=True)

    # Migrations must be authored and reviewed separately; setup only applies
    # migrations already committed to the repository.
    run(sys.executable, str(manage_py), "migrate", "--noinput")
    run(sys.executable, str(manage_py), "collectstatic", "--noinput")

    print(
        "\\nSetup complete. Create an administrator interactively with "
        "'python manage.py createsuperuser', then run 'python manage.py runserver'."
    )


if __name__ == "__main__":
    main()
