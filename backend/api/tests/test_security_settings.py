import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
PRODUCTION_ENV = {
    "DJANGO_DEBUG": "False",
    "DJANGO_SECRET_KEY": "s" * 64,
    "DJANGO_ALLOWED_HOSTS": "ricetta.test",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://ricetta.test",
    "POSTGRES_DB": "ricetta",
    "POSTGRES_USER": "ricetta",
    "POSTGRES_PASSWORD": "test-production-password",
    "POSTGRES_HOST": "db",
    "POSTGRES_PORT": "5432",
}
REQUIRED_PRODUCTION_SETTINGS = (
    "DJANGO_SECRET_KEY",
    "DJANGO_ALLOWED_HOSTS",
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
)


class ProductionSettingsTests(SimpleTestCase):
    def run_settings_import(self, overrides=None, removed=()):
        environment = os.environ.copy()
        environment.update(PRODUCTION_ENV)
        environment.update(overrides or {})
        for name in removed:
            environment.pop(name, None)
        return subprocess.run(
            [sys.executable, "-c", "import ricetta.settings"],
            cwd=BACKEND_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_production_rejects_each_missing_required_setting(self):
        for name in REQUIRED_PRODUCTION_SETTINGS:
            with self.subTest(name=name):
                result = self.run_settings_import(removed=(name,))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(name, result.stderr)

    def test_production_rejects_empty_and_placeholder_values(self):
        cases = {
            "DJANGO_SECRET_KEY": "replace-me-with-production-secret",
            "DJANGO_ALLOWED_HOSTS": "ricetta.example.com",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "http://ricetta.test",
            "POSTGRES_PASSWORD": "replace-me",
        }
        for name, value in cases.items():
            with self.subTest(name=name):
                result = self.run_settings_import(overrides={name: value})
                self.assertNotEqual(result.returncode, 0)

        empty_result = self.run_settings_import(overrides={"POSTGRES_DB": ""})
        self.assertNotEqual(empty_result.returncode, 0)

    def test_development_defaults_still_use_sqlite(self):
        environment = os.environ.copy()
        for name in (*REQUIRED_PRODUCTION_SETTINGS, "DJANGO_DEBUG"):
            environment.pop(name, None)
        command = (
            "import json; from ricetta import settings; "
            "print(json.dumps({'debug': settings.DEBUG, "
            "'engine': settings.DATABASES['default']['ENGINE']}))"
        )

        result = subprocess.run(
            [sys.executable, "-c", command],
            cwd=BACKEND_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(result.stdout)
        self.assertTrue(values["debug"])
        self.assertEqual(values["engine"], "django.db.backends.sqlite3")

    def test_production_enables_expected_https_settings(self):
        command = (
            "import json; from ricetta import settings; "
            "print(json.dumps({"
            "'session_secure': settings.SESSION_COOKIE_SECURE, "
            "'csrf_secure': settings.CSRF_COOKIE_SECURE, "
            "'ssl_redirect': settings.SECURE_SSL_REDIRECT, "
            "'proxy_header': settings.SECURE_PROXY_SSL_HEADER, "
            "'hsts_seconds': settings.SECURE_HSTS_SECONDS, "
            "'hsts_subdomains': settings.SECURE_HSTS_INCLUDE_SUBDOMAINS, "
            "'hsts_preload': settings.SECURE_HSTS_PRELOAD}))"
        )
        environment = os.environ.copy()
        environment.update(PRODUCTION_ENV)

        result = subprocess.run(
            [sys.executable, "-c", command],
            cwd=BACKEND_DIR,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(result.stdout)
        self.assertEqual(
            values,
            {
                "session_secure": True,
                "csrf_secure": True,
                "ssl_redirect": True,
                "proxy_header": ["HTTP_X_FORWARDED_PROTO", "https"],
                "hsts_seconds": 3600,
                "hsts_subdomains": False,
                "hsts_preload": False,
            },
        )

    def test_caddy_blocks_admin_and_preserves_backend_routes(self):
        caddyfile = (PROJECT_DIR / "Caddyfile").read_text()

        self.assertIn("@admin path /admin /admin/*", caddyfile)
        self.assertIn("handle @admin {\n\t\trespond 404\n\t}", caddyfile)
        self.assertNotIn("respond @admin 404", caddyfile)
        self.assertNotIn("handle /admin*", caddyfile)
        self.assertIn("handle /api/*", caddyfile)
        self.assertIn("handle /static/*", caddyfile)
        admin_handle = caddyfile.index("handle @admin {")
        self.assertLess(admin_handle, caddyfile.index("handle /api/*"))
        self.assertLess(admin_handle, caddyfile.index("handle /static/*"))
        self.assertLess(admin_handle, caddyfile.index("\n\thandle {"))
        self.assertNotIn("header_up X-Forwarded-Proto", caddyfile)

    def test_production_health_check_uses_first_allowed_host_and_https(self):
        compose = (PROJECT_DIR / "docker-compose.prod.yml").read_text()

        self.assertIn("os.environ['DJANGO_ALLOWED_HOSTS']", compose)
        self.assertIn(".split(',')[0].strip()", compose)
        self.assertIn("'Host': host", compose)
        self.assertIn("'X-Forwarded-Proto': 'https'", compose)
