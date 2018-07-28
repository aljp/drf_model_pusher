from django.apps import AppConfig

from drf_model_pusher.config import connect_pusher_views


class ExampleApp(AppConfig):
    name = "example"
