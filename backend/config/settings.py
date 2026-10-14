"""Django settings for the Open Word Bible API.

Configuration comes from the environment:
  DATABASE_URL          Postgres connection (default: local postgres on 5432)
  DJANGO_SECRET_KEY     required when DJANGO_DEBUG is off
  DJANGO_DEBUG          "1" for local development
  DJANGO_ALLOWED_HOSTS  comma-separated host names
  CSRF_TRUSTED_ORIGINS  comma-separated origins, e.g. https://api.openwordbible.org
  OWB_SITE_URL          the reader site, for sign-in links (default https://openwordbible.org)
  CORS_ALLOWED_ORIGINS  sites that may call the API (default: OWB_SITE_URL)
  OWB_SUPER_ADMIN_EMAILS  comma-separated emails that are super admins (set
                        in the Render dashboard, so they are not published)
  EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL
                        SMTP for sign-in emails; without EMAIL_HOST emails
                        are printed to the log instead of sent
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
                        "Continue with Google" (accounts/google.py); without
                        them the site hides the button
  DB_STATEMENT_TIMEOUT_MS  longest a database statement may run for the web
                        server, in ms (default 15000; 0 for no limit).
                        Management commands, tests included, have no limit.
  DJANGO_LOG_LEVEL      level for Django's own log messages (default WARNING)
  SENTRY_DSN            report errors to Sentry (config/sentry.py); without
                        it errors are only logged
"""
import os
import sys
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent
# The shared data code (owb/) lives at the repository root.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def env_list(name, default=""):
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


DEBUG = os.environ.get("DJANGO_DEBUG") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or (
    "dev-only-insecure-key" if DEBUG else None)
if not SECRET_KEY:
    raise RuntimeError("Set DJANGO_SECRET_KEY (or DJANGO_DEBUG=1 for local development)")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "texts",
    "translation",
    "api",
    "accounts",
]

MIDDLEWARE = [
    "accounts.cors.ApiCorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


def statement_timeout_ms(argv=sys.argv, environ=os.environ):
    """A search once ran for hours, so the web server gives up on a statement
    after 15 seconds. Management commands such as migrate, the imports and
    the tests (which rebuild the search tables) may run long, so they have
    no limit; runserver has the web server's."""
    if Path(argv[0]).name == "manage.py" and len(argv) > 1 and argv[1] != "runserver":
        return 0
    return int(environ.get("DB_STATEMENT_TIMEOUT_MS") or 15000)


def database_options(timeout_ms):
    return {"options": f"-c statement_timeout={timeout_ms}"}


DATABASES = {
    "default": dj_database_url.config(
        default="postgres://postgres@localhost:5432/owb", conn_max_age=600,
        conn_health_checks=True),
}
DATABASES["default"].setdefault("OPTIONS", {}).update(database_options(statement_timeout_ms()))

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Hashed, compressed files in production (built by collectstatic); plain
    # files in development and tests.
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if DEBUG
                    else "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["accounts.auth.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # Search (api/views.py): as Ochorus allows.
    "DEFAULT_THROTTLE_RATES": {"search": "120/min"},
}

# Accounts (backend/accounts/).
OWB_SITE_URL = os.environ.get("OWB_SITE_URL", "https://openwordbible.org").rstrip("/")
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", OWB_SITE_URL) + (
    ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:8080"] if DEBUG else [])
OWB_SUPER_ADMIN_EMAILS = [e.lower() for e in env_list("OWB_SUPER_ADMIN_EMAILS")]
SIGN_IN_LINK_MINUTES = 20
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_BACKEND = ("django.core.mail.backends.smtp.EmailBackend" if EMAIL_HOST
                 else "django.core.mail.backends.console.EmailBackend")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = EMAIL_PORT == 465
EMAIL_USE_TLS = not EMAIL_USE_SSL   # never send the SMTP password in the clear
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Open Word Bible <noreply@openwordbible.org>")

# Security headers (django.middleware.security.SecurityMiddleware). Django's
# defaults already send X-Frame-Options: DENY, Referrer-Policy: same-origin
# and Cross-Origin-Opener-Policy: same-origin.
SECURE_CONTENT_TYPE_NOSNIFF = True

# Cookies: the site signs in with an API token in the Authorization header
# (accounts/auth.py), never a cookie, so the cross-origin site -> API calls
# need no SameSite=None cookie. The only cookies are the admin's session and
# CSRF cookies, on the API host itself, and Google sign-in's short-lived
# state cookie (accounts/google.py, SameSite=Lax so it survives Google's
# top-level redirect back). Django's SameSite=Lax default suits them all.
SESSION_COOKIE_HTTPONLY = True

# Warnings and errors, with tracebacks, go to stdout, which Render keeps.
# Requests are logged by path only (Django leaves out the query string), so
# searches are never logged.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "stdout": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout",
                   "formatter": "plain"},
    },
    "root": {"handlers": ["stdout"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["stdout"], "level": os.environ.get("DJANGO_LOG_LEVEL", "WARNING"),
                   "propagate": False},
    },
}

if os.environ.get("SENTRY_DSN"):
    from config import sentry
    sentry.init(os.environ["SENTRY_DSN"], os.environ.get("RENDER_SERVICE_NAME", "local"))

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # A year of HTTPS-only, as the reader site sends (render.yaml); not
    # preloaded, so it can still be undone.
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False
    # check --deploy: Render redirects http to https at its edge (W008; a
    # redirect here could also turn away Render's health check of /healthz,
    # which may come over plain http), and preloading is left out on
    # purpose (W021).
    SILENCED_SYSTEM_CHECKS = ["security.W008", "security.W021"]
