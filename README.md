[![PyPI version](https://badge.fury.io/py/drf-model-pusher.svg)](https://badge.fury.io/py/drf-model-pusher)
[![Build Status](https://travis-ci.org/aljp/drf_model_pusher.svg?branch=master)](https://travis-ci.org/aljp/drf_model_pusher)

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
PUSHER_CLUSTER=""  
```

### Update Installed Apps

Add drf_model_pusher to your `INSTALLED_APPS`:

```python

INSTALLED_APPS = [
    "...",
    "drf_model_pusher",
]
``` 

### Implement Pusher Backends

Define some [PusherBackends]() for your models and serializers in a `pusher_backends.py` file.  The PusherBackend class just needs to define a `serializer_class` attribute which inherits from `ModelSerializer`.

```python
# example/pusher_backends.py

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

### Implement Views

Add the [ModelPusherViewMixin]() mixin class to your views and define a `get_pusher_channels` method which should return a list of strings to use as channels.

```python
# example/views.py

from rest_framework.viewsets import ModelViewSet
from drf_model_pusher.views import ModelPusherViewMixin
from example.serializers import MyModelSerializer

class MyModelViewSet(ModelPusherViewMixin, ModelViewSet):
    serializer_class = MyModelSerializer
    
    def get_pusher_channels(self):
        return ["<channel_id>"]
```

### Ignoring the current connection

If you want to ignore the current connection when sending messages you should set a `x-pusher-socket-id` header on your requests.  This may be useful if you're modifying resources and receiving the results in a response, you may not want the current connection to listen on these events to prevent duplicating content.

The PusherBackend.push_change method accepts an `ignore` boolean keyword argument which can toggle whether the pusher socket id is used, it defaults to `True`, so including the pusher socket id in the request will ignore the current connection for all pusher events sent by default.

### Settings

- `DRF_MODEL_PUSHER_BACKENDS_FILE` (default: `pusher_backends.py`) - The file in your applications to import PusherBackends.
- `DRF_MODEL_PUSHER_DISABLED` (default: `False`) - Determines whether or not to trigger Pusher events.

## Common Issues
### Unregistered Backends
If you have followed the above steps correctly and your backends are not registering, your app config may not be running it's `ready` method. To force this, in your apps `__init__.py` add the line `default_app_config = 'myapp.apps.MyAppConfig'`

### Pusher
Be aware of any pusher limits and consult their documentation at [https://pusher.com/docs](https://pusher.com/docs) for some common questions.  

[Pusher has a 10kb default size limit on messages, this can be increased to 256kb by contacting support.](https://support.pusher.com/hc/en-us/articles/202046553-What-is-the-message-size-limit-when-publishing-a-message-)

### Extending `PusherBackend`
If you want to extend `PusherBackend` or `PrivatePusherBackend` rather than declaring a new concrete backend, you need to make sure the class is abstract. For example your new base class would be similar to this:

```python
class MyPusherBackend(PusherBackend):
    class Meta:
        abstract = True

    # Override whatever methods here


class MyModelBackend(MyPusherBackend):
    class Meta:
        model = MyModel
```

## Contributions

It's early days, but if you'd like to report any issues or work on an improvement then please check for any similar existing issues before you report them.
