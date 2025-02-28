"""
Django settings for siade25 project.

Generated by 'django-admin startproject' using Django 4.2.18.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
# ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')
ALLOWED_HOSTS = ['conferencedabidjan.com', 'www.conferencedabidjan.com', '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = [
    "https://conferencedabidjan.com",
    "https://www.conferencedabidjan.com",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.conferencedabidjan\.com$",  # Accepte tous les sous-domaines si besoin
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", ]
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'django_filters',
    'corsheaders',
    'simple_history',
    'django_celery_beat',
    'public',
    'administration',
    "compressor",
    'decouple',
    'django_user_agents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    'simple_history.middleware.HistoryRequestMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django_user_agents.middleware.UserAgentMiddleware',
    'public.middleware.VisitCounterMiddleware',
    'public.middleware.QRRedirectMiddleware',
    "public.middleware.DisableCSRFMiddleware",
]

ROOT_URLCONF = 'siade25.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "public.context_processors.open_graph_image",
            ],
        },
    },
]

WSGI_APPLICATION = 'siade25.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='cadb'),
        'PORT': config('DB_PORT', default=5433, cast=int),
    }
}

AUTH_USER_MODEL = 'public.User'
ACCOUNT_FORMS = {
    'signup': 'public.forms.CustomSignupForm',  # Modifier avec ton app
}
# Redis settings
CELERY_BROKER_URL = config('REDIS_URL')
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
# Active JWT avec Simple JWT
REST_USE_JWT = True  # Pour utiliser JWT avec dj-rest-auth
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  # Ajuste selon tes besoins
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # Permet de rafraîchir les tokens sans se reconnecter
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Configuration REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        'rest_framework.authentication.TokenAuthentication',
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Authentification JWT sécurisée
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # Toutes les requêtes nécessitent une authentification
    ],
}

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",

)

# GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH', '/opt/homebrew/opt/gdal/lib/libgdal.dylib')
# GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH', '/opt/homebrew/opt/geos/lib/libgeos_c.dylib')

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('Anglais')),
    # ('es', _('Espagnol')),
    # ('de', _('Allemand')),
    # ('hi', _('Hindi')),
]

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

USE_L10N = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',  # Dossier où seront stockés les fichiers de traduction
]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",  # 👈 Ajoutez cette ligne obligatoire
]

# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1
# USE_L10N = True
# REST Framework Configuration

# Configuration Allauth
# ACCOUNT_RATE_LIMITS = {
#     "login_failed": "5/5m",  # Max 5 tentatives toutes les 5 minutes
#     "email_login_failed": "5/5m",
#     "password_reset": "5/1h",  # Max 5 demandes de reset password par heure
#     "verify_email": "3/10m",  # Max 3 envois d'email de vérification toutes les 10 min
#     "signup": "10/h",  # Max 10 inscriptions par heure
# }

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"
# ACCOUNT_ADAPTER = "public.adapters.NoRedirectAccountAdapter"
ACCOUNT_ADAPTER = "public.adapters.NoUsernameAccountAdapter"


REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'administration.api.serializers.CustomRegisterSerializer',
}

ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "/"
SITE_URL = "https://www.conferencedabidjan.com"
# APPEND_SLASH = False
# LOGIN_REDIRECT_URL = "home"
# LOGOUT_REDIRECT_URL = "landing"
# ACCOUNT_LOGOUT_REDIRECT = "account_login"
# ACCOUNT_SIGNUP_REDIRECT_URL = "account_login"

# Configuration de Celery
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Configuration de l'e-mail via fichier .env
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
