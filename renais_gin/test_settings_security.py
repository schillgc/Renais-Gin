"""Isolated regression tests for the Renais Gin Django settings contract.

The suite stubs only Django's ImproperlyConfigured exception so configuration
rules can be tested without installing the application's large dependency set.
It is deliberately not a replacement for Django system, API, or deployment tests.
"""

import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from unittest import TestCase
from unittest.mock import patch


class ImproperlyConfigured(Exception):
    """Minimal stand-in for Django's configuration exception."""


class SettingsSecurityContractTests(TestCase):
    settings_path = Path(__file__).resolve().parent / "renais_gin" / "settings.py"

    def load_settings(self, environment):
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

    def test_debug_defaults_to_false_and_production_hosts_are_required(self):
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings({"DJANGO_SECRET_KEY": "test-only-secret"})

        settings = self.load_settings(
            {
                "DJANGO_SECRET_KEY": "test-only-secret",
                "DJANGO_ALLOWED_HOSTS": "app.example.test",
            }
        )
        self.assertFalse(settings.DEBUG)
        self.assertEqual(settings.ALLOWED_HOSTS, ["app.example.test"])

    def test_debug_mode_without_hosts_is_limited_to_loopback(self):
        settings = self.load_settings(
            {
                "DJANGO_SECRET_KEY": "test-only-secret",
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
                        "DJANGO_SECRET_KEY": "test-only-secret",
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
                        "DJANGO_SECRET_KEY": "test-only-secret",
                        "DJANGO_DEBUG": value,
                        "DJANGO_ALLOWED_HOSTS": "localhost",
                    }
                )
                self.assertFalse(settings.DEBUG)

    def test_invalid_boolean_is_rejected(self):
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings(
                {
                    "DJANGO_SECRET_KEY": "test-only-secret",
                    "DJANGO_DEBUG": "perhaps",
                    "DJANGO_ALLOWED_HOSTS": "localhost",
                }
            )

    def test_allowed_hosts_are_trimmed_and_empty_entries_removed(self):
        settings = self.load_settings(
            {
                "DJANGO_SECRET_KEY": "test-only-secret",
                "DJANGO_ALLOWED_HOSTS": " app.example.com, api.example.com ,, ",
            }
        )
        self.assertEqual(
            settings.ALLOWED_HOSTS, ["app.example.com", "api.example.com"]
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
