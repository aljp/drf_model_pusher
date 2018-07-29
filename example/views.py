from rest_framework import viewsets

from drf_model_pusher.views import ModelPusherViewMixin
from example.models import MyModel
from example.serializers import MyModelSerializer


class MyModelViewSet(ModelPusherViewMixin, viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer

    def get_pusher_channels(self):
        return ["channel"]
