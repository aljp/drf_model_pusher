# DRF Model Pusher

Easy to use class mixins for [Django Rest Framework]() and [Pusher]() to keep your API realtime.

## Installation

Download from PyPI:

`pip install drf_model_pusher`

## Configuration

### Settings Config

In your settings set your Pusher App Id and credentials, the cluster is optional

```python
PUSHER_APP_ID=""  
PUSHER_KEY=""  
PUSHER_SECRET=""
PUSHER_CLUSTER_ID=""  
```

### Application Config

Edit your applications [AppConfig]() and import the `connect_pusher_views` method and run it in the AppConfig's ready method.

```python
from django.apps import AppConfig
from drf_model_pusher.receivers import connect_pusher_views

class MyAppConfig(AppConfig):
    def ready(self):
        connect_pusher_views()
        
``` 

### Implement Pusher Backends

Define some [PusherBackends]() for your models and serializers.  The PusherBackend class just needs to define a `serializer_class` attribute which inherits from `ModelSerializer`.

```python
from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from drf_model_pusher.backends import PusherBackend, PrivatePusherBackend

class MyModel(Model):
    pass

class MyModelSerializer(ModelSerializer):
    class Meta:
        model = MyModel

class MyModelPrivateSerializer(ModelSerializer):
    class Meta:
        model = MyModel

class MyModelPusherBackend(PusherBackend):
    serializer_class = MyModelSerializer
    
class MyModelPrivatePusherBackend(PrivatePusherBackend):
    serializer_class = MyModelPrivateSerializer
```

Then import your pusher backends in your AppConfig to register them.

> At some point I think it would be worth auto-loading from some predefined paths, such as scanning for a `pusher_backends.py` file in each app and importing them automatically.

```python
from django.apps import AppConfig
from drf_model_pusher.handlers import connect_pusher_views

class MyAppConfig(AppConfig):
    def ready(self):
        connect_pusher_views()
        #  The line below imports the backends which in turn register's them in the global registry.
        from example.pusher_backends import MyModelPusherBackend, MyModelPrivatePusherBackend
        
``` 

### Implement Views

Add the [PushModelChanges]() mixin class to your views.

```python
from rest_framework.viewsets import ModelViewSet
from drf_model_pusher.views import PushModelChanges

class MyModelViewSet(PushModelChanges, ModelViewSet):
    serializer_class = MyModelSerializer
    
    def get_channel_id(self):
        return "<channel_id>"
```

## Contributions

It's early days, but if you'd like to report any issues or work on an improvement then please check for any similar existing issues before you report them.