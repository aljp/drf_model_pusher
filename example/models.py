from django.db import models


class MyPublicModel(models.Model):
    name = models.CharField(max_length=32)


class MyPrivateModel(models.Model):
    name = models.CharField(max_length=32)


class MyPresenceModel(models.Model):
    name = models.CharField(max_length=32)
