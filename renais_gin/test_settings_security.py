"""Isolated regression tests for the Renais Gin Django settings contract.

The suite stubs only Django's ImproperlyConfigured exception so configuration
rules can be tested without installing the application's large dependency set.
It is deliberately not a replacement for Django system, API, or deployment tests.
"""

import os
import secrets
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from unittest import TestCase
from unittest.mock import patch


class ImproperlyConfigured(Exception):
    """Minimal stand-in for Django's configuration exception."""


TEST_SECRET_KEY = secrets.token_urlsafe(64)


class SettingsSecurityContractTests(TestCase):
    settings_path = Path(__file__).resolve().parent / "renais_gin" / "settings.py"

    def load_settings(self, environment, *, test_database=True):
        test_database_environment = {
            "DJANGO_DB_ENGINE": "postgresql",
            "DJANGO_DB_NAME": "renais-test",
            "DJANGO_DB_USER": "renais-test",
            "DJANGO_DB_PASSWORD": "test-only-database-password",
            "DJANGO_DB_HOST": "db.example.test",
        } if test_database else {}
        environment = {**test_database_environment, **environment}

        django = ModuleType("django")
        django.__path__ = []
        django_core = ModuleType("django.core")
        django_core.__path__ = []
        exceptions = ModuleType("django.core.exceptions")
        exceptions.ImproperlyConfigured = ImproperlyConfigured
        django.core = django_core
        django_core.exceptions = exceptions

        fake_django_modules = {
            "django": django,
            "django.core": django_core,
            "django.core.exceptions": exceptions,
        }

        with patch.dict(os.environ, environment, clear=True):
            with patch.dict(sys.modules, fake_django_modules):
                spec = spec_from_file_location(
                    "_renais_settings_under_test", self.settings_path
                )
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                return module

    def test_secret_key_is_required_and_must_not_be_blank(self):
        for value in (None, "", "   "):
            with self.subTest(value=value):
                environment = {}
                if value is not None:
                    environment["DJANGO_SECRET_KEY"] = value
                environment["DJANGO_ALLOWED_HOSTS"] = "localhost"
                with self.assertRaises(ImproperlyConfigured):
                    self.load_settings(environment)

    def test_secret_key_requires_minimum_length_and_character_diversity(self):
        for value, expected in (
            ("x" * 49, "at least 50 characters"),
            ("x" * 80, "at least 5 distinct characters"),
        ):
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(ImproperlyConfigured, expected):
                    self.load_settings({
                        "DJANGO_SECRET_KEY": value,
                        "DJANGO_ALLOWED_HOSTS": "localhost",
                    })

    def test_debug_defaults_to_false_and_production_hosts_are_required(self):
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings({"DJANGO_SECRET_KEY": TEST_SECRET_KEY})

        settings = self.load_settings(
            {
                "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
                "DJANGO_ALLOWED_HOSTS": "app.example.test",
            }
        )
        self.assertFalse(settings.DEBUG)
        self.assertEqual(settings.ALLOWED_HOSTS, ["app.example.test"])

    def test_debug_mode_without_hosts_is_limited_to_loopback(self):
        settings = self.load_settings(
            {
                "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
                "DJANGO_DEBUG": "true",
            }
        )
        self.assertTrue(settings.DEBUG)
        self.assertEqual(settings.ALLOWED_HOSTS, ["localhost", "127.0.0.1", "[::1]"])

    def test_true_boolean_spellings_are_accepted(self):
        for value in ("1", "true", "TRUE", "yes", "on"):
            with self.subTest(value=value):
                settings = self.load_settings(
                    {
                        "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
                        "DJANGO_DEBUG": value,
                        "DJANGO_ALLOWED_HOSTS": "localhost",
                    }
                )
                self.assertTrue(settings.DEBUG)

    def test_false_boolean_spellings_are_accepted(self):
        for value in ("0", "false", "FALSE", "no", "off"):
            with self.subTest(value=value):
                settings = self.load_settings(
                    {
                        "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
                        "DJANGO_DEBUG": value,
                        "DJANGO_ALLOWED_HOSTS": "localhost",
                    }
                )
                self.assertFalse(settings.DEBUG)

    def test_invalid_boolean_is_rejected(self):
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings(
                {
                    "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
                    "DJANGO_DEBUG": "perhaps",
                    "DJANGO_ALLOWED_HOSTS": "localhost",
                }
            )

    def test_allowed_hosts_are_trimmed_and_empty_entries_removed(self):
        settings = self.load_settings(
            {
                "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
                "DJANGO_ALLOWED_HOSTS": " app.example.com, api.example.com ,, ",
            }
        )
        self.assertEqual(
            settings.ALLOWED_HOSTS, ["app.example.com", "api.example.com"]
        )


    def test_sqlite_is_debug_only_and_postgresql_requires_all_credentials(self):
        production_environment = {
            "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
            "DJANGO_ALLOWED_HOSTS": "localhost",
        }
        with self.assertRaisesRegex(
            ImproperlyConfigured,
            r"DJANGO_DB_ENGINE=postgresql \(or postgres\) is required when DJANGO_DEBUG is false",
        ):
            self.load_settings(production_environment, test_database=False)

        local = self.load_settings(
            {
                **production_environment,
                "DJANGO_DEBUG": "true",
                "DJANGO_DB_ENGINE": "sqlite",
            },
            test_database=False,
        )
        self.assertEqual(local.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3")

        blank_backend = self.load_settings(
            {
                **production_environment,
                "DJANGO_DEBUG": "true",
                "DJANGO_DB_ENGINE": "",
            },
            test_database=False,
        )
        self.assertEqual(
            blank_backend.DATABASES["default"]["ENGINE"],
            "django.db.backends.sqlite3",
        )

        with self.assertRaisesRegex(ImproperlyConfigured, "PostgreSQL requires"):
            self.load_settings(
                {
                    **production_environment,
                    "DJANGO_DB_ENGINE": "postgresql",
                    "DJANGO_DB_NAME": "renais",
                },
                test_database=False,
            )

        postgres = self.load_settings(
            {
                **production_environment,
                "DJANGO_DB_ENGINE": "postgresql",
                "DJANGO_DB_NAME": "renais",
                "DJANGO_DB_USER": "app",
                "DJANGO_DB_PASSWORD": "test-password",
                "DJANGO_DB_HOST": "db.example.test",
                "DJANGO_DB_PORT": "6432",
                "DJANGO_DB_SSLMODE": "verify-full",
                "DJANGO_DB_SSLROOTCERT": "/etc/ssl/certs/renais-ca.pem",
            },
            test_database=False,
        )
        self.assertEqual(
            postgres.DATABASES["default"]["ENGINE"],
            "django.db.backends.postgresql",
        )
        self.assertEqual(postgres.DATABASES["default"]["PORT"], "6432")
        self.assertEqual(
            postgres.DATABASES["default"]["OPTIONS"],
            {
                "sslmode": "verify-full",
                "sslrootcert": "/etc/ssl/certs/renais-ca.pem",
            },
        )
        self.assertTrue(postgres.DATABASES["default"]["CONN_HEALTH_CHECKS"])

        default_tls = self.load_settings(
            {
                **production_environment,
                "DJANGO_DB_ENGINE": "postgresql",
                "DJANGO_DB_NAME": "renais",
                "DJANGO_DB_USER": "app",
                "DJANGO_DB_PASSWORD": "test-password",
                "DJANGO_DB_HOST": "db.example.test",
            },
            test_database=False,
        )
        self.assertEqual(
            default_tls.DATABASES["default"]["OPTIONS"],
            {"sslmode": "verify-full"},
        )
        self.assertEqual(default_tls.DATABASES["default"]["CONN_MAX_AGE"], 60)

        with self.assertRaisesRegex(ImproperlyConfigured, "must be sqlite or postgresql"):
            self.load_settings(
                {
                    **production_environment,
                    "DJANGO_DB_ENGINE": "mysql",
                },
                test_database=False,
            )

    def test_postgresql_rejects_unverified_tls_and_invalid_connection_bounds(self):
        environment = {
            "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
            "DJANGO_ALLOWED_HOSTS": "localhost",
            "DJANGO_DB_ENGINE": "postgresql",
            "DJANGO_DB_NAME": "renais",
            "DJANGO_DB_USER": "app",
            "DJANGO_DB_PASSWORD": "test-password",
            "DJANGO_DB_HOST": "db.example.test",
        }
        invalid_settings = (
            {"DJANGO_DB_SSLMODE": "disable"},
            {"DJANGO_DB_SSLMODE": "prefer"},
            {"DJANGO_DB_SSLMODE": "require"},
            {"DJANGO_DB_PORT": "not-a-port"},
            {"DJANGO_DB_PORT": "70000"},
            {"DJANGO_DB_PORT": "0"},
            {"DJANGO_DB_CONN_MAX_AGE": "not-an-integer"},
            {"DJANGO_DB_CONN_MAX_AGE": "-1"},
            {"DJANGO_DB_CONN_MAX_AGE": "3601"},
        )
        for invalid in invalid_settings:
            with self.subTest(invalid=invalid), self.assertRaises(ImproperlyConfigured):
                self.load_settings(
                    {**environment, **invalid},
                    test_database=False,
                )

        verify_ca = self.load_settings(
            {**environment, "DJANGO_DB_SSLMODE": "verify-ca"},
            test_database=False,
        )
        self.assertEqual(
            verify_ca.DATABASES["default"]["OPTIONS"],
            {"sslmode": "verify-ca"},
        )

    def test_hsts_and_proxy_trust_are_opt_in_but_baseline_headers_are_enabled(self):
        settings = self.load_settings({
            "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
            "DJANGO_ALLOWED_HOSTS": "app.example.test",
        })
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 0)
        self.assertFalse(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertFalse(settings.SECURE_HSTS_PRELOAD)
        self.assertFalse(hasattr(settings, "SECURE_PROXY_SSL_HEADER"))
        self.assertTrue(settings.SECURE_SSL_REDIRECT)
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF)
        self.assertEqual(settings.X_FRAME_OPTIONS, "DENY")
        self.assertEqual(settings.SECURE_REFERRER_POLICY, "strict-origin-when-cross-origin")

        hardened = self.load_settings({
            "DJANGO_SECRET_KEY": TEST_SECRET_KEY,
            "DJANGO_ALLOWED_HOSTS": "app.example.test",
            "DJANGO_HSTS_SECONDS": "31536000",
            "DJANGO_HSTS_INCLUDE_SUBDOMAINS": "true",
            "DJANGO_HSTS_PRELOAD": "true",
            "DJANGO_TRUST_PROXY": "true",
        })
        self.assertEqual(hardened.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(hardened.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(hardened.SECURE_HSTS_PRELOAD)
        self.assertEqual(hardened.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))


if __name__ == "__main__":
    import unittest

    unittest.main()
