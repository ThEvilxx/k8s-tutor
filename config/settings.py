"""课堂演示配置。公网运行必须显式设置密钥、主机名及 HTTPS 配置。"""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "local-development-only-never-use-in-production"
    else:
        raise ImproperlyConfigured("请设置 DJANGO_SECRET_KEY；本机演示可设置 DJANGO_DEBUG=True")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "practice",
]
MIDDLEWARE = [
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
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "practice.context_processors.release",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
DB_PATH = Path(os.getenv("DJANGO_DB_PATH", str(BASE_DIR / "data" / "db.sqlite3")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": DB_PATH,
                          "OPTIONS": {"timeout": 15}}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = Path(os.getenv("DJANGO_STATIC_ROOT", str(BASE_DIR / "staticfiles")))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "practice:home"
LOGOUT_REDIRECT_URL = "login"
APP_VERSION = os.getenv("APP_VERSION", "v1")
LLM_MODE = os.getenv("LLM_MODE", "mock")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "20"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "800"))
# 由 HTTPS 反向代理部署时按 docs/DEPLOYMENT.md 开启；不盲目信任代理头。
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = os.getenv("DJANGO_SECURE_COOKIES", "False").lower() == "true"
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
CSRF_TRUSTED_ORIGINS = [x for x in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if x]
