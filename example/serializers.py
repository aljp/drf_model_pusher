from rest_framework import serializers

from example.models import MyModel


class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ("name",)
