from rest_framework import viewsets

from drf_model_pusher.views import ModelPusherViewMixin
from example.models import MyPublicModel, MyPrivateModel, MyPresenceModel
from example.serializers import MyPublicModelSerializer, MyPrivateModelSerializer, \
    MyPresenceModelSerializer


class MyPublicModelViewSet(ModelPusherViewMixin, viewsets.ModelViewSet):
    queryset = MyPublicModel.objects.all()
    serializer_class = MyPublicModelSerializer

    def get_pusher_channels(self):
        return ["channel"]


class MyPrivateModelViewSet(ModelPusherViewMixin, viewsets.ModelViewSet):
    queryset = MyPrivateModel.objects.all()
    serializer_class = MyPrivateModelSerializer

    def get_pusher_channels(self):
        return ["private-channel"]


class MyPresenceModelViewSet(ModelPusherViewMixin, viewsets.ModelViewSet):
    queryset = MyPresenceModel.objects.all()
    serializer_class = MyPresenceModelSerializer

    def get_pusher_channels(self):
        return ["presence-channel"]
