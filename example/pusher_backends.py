from drf_model_pusher.backends import PusherBackend
from example.serializers import MyModelSerializer


class MyModelPusherBackend(PusherBackend):
    serializer_class = MyModelSerializer
