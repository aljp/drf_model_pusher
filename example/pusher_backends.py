from drf_model_pusher.backends import PusherBackend, PrivatePusherBackend, PresencePusherBackend
from example.serializers import MyPublicModelSerializer, MyPrivateModelSerializer, MyPresenceModelSerializer


class MyPublicModelPusherBackend(PusherBackend):
    serializer_class = MyPublicModelSerializer


class MyPrivateModelBackend(PrivatePusherBackend):
    serializer_class = MyPrivateModelSerializer


class MyPresenceModelBackend(PresencePusherBackend):
    serializer_class = MyPresenceModelSerializer
