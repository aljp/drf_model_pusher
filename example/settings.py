import os

SECRET_KEY = os.environ.get("SECRET_KEY")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "example.ExampleApp",
    "drf_model_pusher",
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "example"}}

REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

PUSHER_APP_ID = "123456"
PUSHER_KEY = "ok"
PUSHER_SECRET = "ok"
