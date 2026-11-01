"""
Django settings for WMS Control project.
Warehouse Management System Configuration.
"""

import os
from pathlib import Path
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
# DEBUG = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность и окружение
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-s+qy(2%im18dd9_%(s6hih^(!p(qc*2zwan1%8itk7wfgbyht6')

# В продакшене переключается через переменную окружения DEBUG=False
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'MAbylmazhitov.pythonanywhere.com', 
    '*'
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

# Установленные приложения WMS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Сторонние библиотеки
    'django_cleanup.apps.CleanupConfig',
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'cloudinary_storage',
    'cloudinary',
    
    # Локальные приложения WMS
    'accounts',    # Профили сотрудников, роли (Admin, Manager, Storekeeper)
    'inventory',   # Номенклатура, категории, остатки, ячейки склада
    'orders',      # Накладные, приходы, списания, перемещения
]

# Промежуточное ПО (Middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Статика для Render/Production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',   # Многоязычность (EN/RU)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Шаблонизатор и маршрутизация WMS
ROOT_URLCONF = 'warehouse.urls'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'warehouse.wsgi.application'

# Конфигурация базы данных
DATABASES = {
    'default': {        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

    # 'default': {
       # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
       # 'NAME': 'warehouse',
       # 'USER' : 'customer',
       # 'PASSWORD' : 'customer',
       # 'HOST' : '127.0.0.1',
       # 'PORT' : '5432',
    # }
    
}

# Подключение базы из переменной окружения (Render / PostgreSQL)
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Валидация паролей
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

# Интернационализация и локализация (EN / RU)
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Aqtobe'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Русский'),
)

# Статические файлы (CSS, JS, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Медиафайлы
MEDIA_ROOT = os.path.join(BASE_DIR, 'media').replace('\\', '/')
MEDIA_URL = '/media/'

# Редиректы авторизации WMS
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Параметры почтового сервера (Email notifications)
EMAIL_TIMEOUT = 300
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'shop260222@mail.ru')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'Nn27t2PMDiJ7rSqWeFuw')
EMAIL_PORT = 25
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER