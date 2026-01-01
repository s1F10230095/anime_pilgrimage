"""
Django settings for anime_pilgrimage project.
"""

import os
import dj_database_url
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-key')

# Render環境かどうかを判定
DEBUG = 'RENDER' not in os.environ

if not DEBUG:
    # 🔴 本番環境 (Render)
    ALLOWED_HOSTS = []
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
else:
    # 🟢 開発環境 (PC / ngrok)
    ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    # ★重要: CloudinaryStorageは必ず django.contrib.staticfiles より前に記述
    'cloudinary_storage',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary',
    'django.contrib.staticfiles',
    'spots',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise は削除済み
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'anime_pilgrimage.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "accounts.context_processors.user_profile",
            ],
        },
    },
]

WSGI_APPLICATION = 'anime_pilgrimage.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Render上にいるときは、PostgreSQLを使う設定に上書きする
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('ja', _('Japanese')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

ASSETS_PATH = BASE_DIR / 'spots' / 'assets'
STATICFILES_DIRS = [
    ASSETS_PATH,
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Cloudinary Settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# ▼▼▼ ストレージ設定 ▼▼▼
if not DEBUG:
    # 🔴 本番環境 (Render)
    # 画像もCSSもすべてCloudinaryにアップロードして配信します
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "cloudinary_storage.storage.StaticHashedCloudinaryStorage",
        },
    }
    # ★重要: ライブラリのエラー回避のため、古い変数にも同じ値をセットします
    STATICFILES_STORAGE = "cloudinary_storage.storage.StaticHashedCloudinaryStorage"
else:
    # 🟢 開発環境 (ローカル)
    # 画像はCloudinary、CSSはローカルファイルを使用
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    # ★重要: ローカル用の設定も古い変数に合わせておきます
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok-free.dev',
    'https://*.onrender.com',
]