from rest_framework import serializers

from example.models import MyPublicModel, MyPrivateModel, MyPresenceModel


class MyPublicModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPublicModel
        fields = ("name",)


class MyPrivateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPrivateModel
        fields = ("name",)


class MyPresenceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPresenceModel
        fields = ("name",)
