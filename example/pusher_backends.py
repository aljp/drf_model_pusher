from drf_model_pusher.backends import PusherBackend, PrivatePusherBackend
from example.serializers import MyModelSerializer


class MyModelPusherBackend(PusherBackend):
    serializer_class = MyModelSerializer


class MyModelPrivatePusherBackend(PrivatePusherBackend):
    serializer_class = MyModelSerializer
