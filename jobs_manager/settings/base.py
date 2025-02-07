import os
from pathlib import Path

from concurrent_log_handler import ConcurrentRotatingFileHandler
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent


AUTH_USER_MODEL = "workflow.Staff"

# Application definition

INSTALLED_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "django_node_assets",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_tables2",
    "workflow",
    "simple_history",
]

CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "workflow.middleware.LoginRequiredMiddleware",
]

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login/"
LOGIN_EXEMPT_URLS = ["logout"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "sql_file": {
            "level": "DEBUG",
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/debug_sql.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "xero_file": {
            "level": "DEBUG",
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/xero_integration.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["sql_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "xero": {
            "handlers": ["xero_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "xero_python": {
            "handlers": ["xero_file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}


INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = "jobs_manager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "workflow/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "jobs_manager.wsgi.application"
load_dotenv(BASE_DIR / ".env")

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "msm_workflow"),
        "USER": os.getenv("MSM_DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", "password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", 3306),
        "TEST": {
            "NAME": "test_msm_workflow",
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-nz"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_DIRS = [
    # Bootstrap CSS and JS
    ("bootstrap", "node_modules/bootstrap/dist"),
    # Bootstrap Icons CSS
    ("bootstrap-icons", "node_modules/bootstrap-icons/font"),
    # ag-Grid Community (CSS/JS)
    ("ag-grid-community", "node_modules/ag-grid-community/dist"),
    ("ag-grid-styles", "node_modules/@ag-grid-community/styles"),
    # Highcharts (JS)
    ("highcharts", "node_modules/highcharts"),
    # jQuery (JS)
    ("jquery", "node_modules/jquery/dist"),
    # JSONEditor (CSS/JS)
    ("jsoneditor", "node_modules/jsoneditor/dist"),
    # jsPDF (JS)
    ("jspdf", "node_modules/jspdf/dist"),
    # jsPDF-AutoTable (JS)
    ("jspdf-autotable", "node_modules/jspdf-autotable/dist"),
    # PDFMake (JS)
    ("pdfmake", "node_modules/pdfmake/build/"),
    # Moment.js (JS)
    ("moment", "node_modules/moment"),
    # SortableJS (JS)
    ("sortablejs", "node_modules/sortablejs"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECRET_KEY = os.getenv("SECRET_KEY")

# ===========================
# CUSTOM SETTINGS
# ===========================

XERO_CLIENT_ID = os.getenv("XERO_CLIENT_ID", "")
XERO_CLIENT_SECRET = os.getenv("XERO_CLIENT_SECRET", "")
XERO_REDIRECT_URI = os.getenv("XERO_REDIRECT_URI", "")

DROPBOX_WORKFLOW_FOLDER = os.path.join(os.path.expanduser("~"), "Dropbox/MSM Workflow")
