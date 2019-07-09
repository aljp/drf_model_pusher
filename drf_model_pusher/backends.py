"""
PusherBackend classes define how changes from a Model are serialized, and then which provider will send the message.
"""
from collections import defaultdict

from rest_framework.utils.encoders import JSONEncoder

from drf_model_pusher.providers import PusherProvider
from drf_model_pusher.signals import (
    pusher_backend_post_save,
    pusher_backend_pre_destroy,
)

pusher_backend_registry = defaultdict(list)

PUSH_CREATE = "create"
PUSH_UPDATE = "update"
PUSH_DELETE = "delete"
PUSH_PARTIAL_UPDATE = "partial_update"
PUSH_SYNC = "sync"
"""
These are the default events we have included, and they all mimic rest 
frameworks default view actions, except for the sync method. 

The update and partial_update events are intended to be implemented differently
on the client side.  An update event instructs the client to replace any 
existing object entirely, whilst partial update event instructs clients to only 
replace the provided attributes.

The sync method is intended to be used to instruct clients to request the 
object again, this may come in handy if your data may be too large to be sent
over web sockets.
"""


class PusherBackendMetaclass(type):
    """
    Register PusherBackend's with a registry for model lookups, supports
    "abstract" classes which are not registered but can extend functionality.
    """

    def __new__(mcs, cls, bases, dicts):
        if dicts.get("Meta") and hasattr(dicts.get("Meta"), "abstract"):
            dicts["__metaclass__"] = mcs
            return super().__new__(mcs, cls, bases, dicts)

        assert (
            dicts.get("serializer_class", None) is not None
        ), "PusherBackends require a serializer_class"
        dicts["__metaclass__"] = mcs

        final_cls = super().__new__(mcs, cls, bases, dicts)

        model_name = dicts["serializer_class"].Meta.model.__name__.lower()
        pusher_backend_registry[model_name].append(final_cls)
        return final_cls


class PusherBackend(metaclass=PusherBackendMetaclass):
    """
    PusherBackend is the base class for implementing serializers with Pusher
    """

    class Meta:
        abstract = True

    provider_class = PusherProvider
    serializer_class = None
    json_encoder = JSONEncoder

    def __init__(self, view=None, request=None):
        self.view = view
        self.request = request
        self.pusher_socket_id = self.get_pusher_socket()

    def get_pusher_socket(self):
        """Return the socket from the request header"""
        if self.view:
            return self.view.request.META.get("HTTP_X_PUSHER_SOCKET_ID", None)
        if self.request:
            return self.request.META.get("HTTP_X_PUSHER_SOCKET_ID", None)
        return None

    def use_pusher_socket(self):
        """Return True or False to ignore the current client

        The default implementation attempts to call the use_pusher_socket()
        method from the view, otherwise this will return False."""
        if self.view and hasattr(self.view, "use_pusher_socket"):
            return self.view.use_pusher_socket()
        return False

    def push_change(self, event, instance=None, pre_destroy=False, ignore=None):
        """Push changes for an instance

        A packet is initialised and sent via the 'pusher_backend_post_save()'
        and 'pusher_backend_pre_destroy()' signals.  A packet is a dictionary
        containing the channels, event name, and data to be sent.

        A Pusher Socket ID can be included with the signal to prevent this from
        sending the  update to the current client.  To send the Pusher Socket
        ID you can set the 'ignore' kwarg to True, or implement
        'use_pusher_socket()' on the view, or override the
        'use_pusher_socket()' method on the PusherBackend.
        """
        packet = self.get_packet(event, instance)

        channels = packet.get("channels", None)
        if not channels:
            raise ValueError("channels cannot be None")

        event_name = packet.get("event_name", None)
        if not event_name:
            raise ValueError("event_name cannot be None")

        data = packet.get("data", None)

        if ignore is None:
            ignore = self.use_pusher_socket()

        signal_kwargs = dict(
            sender=self.__class__,
            instance=self,
            channels=channels,
            event_name=event_name,
            data=data,
            socket_id=self.pusher_socket_id if ignore else None,
            provider_class=self.provider_class,
        )

        if pre_destroy:
            pusher_backend_pre_destroy.send(**signal_kwargs)
        else:
            pusher_backend_post_save.send(**signal_kwargs)

    def get_serializer_class(self):
        """Return the views serializer class

        The default implementation attempts to return the serializer_class
        attribute on the current instance, if that cannot be found then it
        will attempt to return the serializer class from the view.  Otherwise
        a ValueError is raised."""
        if self.serializer_class:
            return self.serializer_class

        if self.view and hasattr(self.view, "serializer_class"):
            return self.view.serializer_class

        raise ValueError(
            "{0} cannot find a Serializer class to use".format(self.__class__.__name__)
        )

    def get_serializer_context(self):
        """Return a dictionary that will be passed to the serializers context

        The serializer context from GenericAPIView.get_serializer_context()
        returns a dictionary containing the 'view' itself, the 'request', and
        a 'format' string.  The default implementation attempts to return the
        context from the view.  When the view does not have a
        'get_serializer_context()' method, we return a similar dictionary
        containing any view or request assigned to this PusherBackend instance.
        """
        context = {}
        if self.view:
            if hasattr(self.view, "get_serializer_context"):
                context = self.view.get_serializer_context()
            else:
                context = {"view": self.view, "request": self.view.request}

            if self.request:
                context["request"] = self.request

        elif self.request:
            context["request"] = self.request

        return context

    def get_serializer(self, *args, **kwargs):
        """Return the serializer with the context"""
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_channels(self, instance=None, serializer=None):
        """Return a list of channels from the view, serializer, and instance

        Channels are combined from the view, serializer, and instances 'get_pusher_channels' method."""
        channels = set()
        if self.view and hasattr(self.view, "get_pusher_channels"):
            channels.update(set(self.view.get_pusher_channels()))

        if serializer and hasattr(serializer, "get_pusher_channels"):
            channels.update(set(serializer.get_pusher_channels()))

        if instance and hasattr(instance, "get_pusher_channels"):
            channels.update(set(instance.get_pusher_channels()))

        if channels:
            return list(channels)

        raise ValueError(
            "{0}.get_channels() did not return any channels".format(
                self.__class__.__name__
            )
        )

    def get_event_name(self, event_type):
        """Return the model name and the event_type separated by a dot"""
        serializer_class = self.get_serializer_class()
        model_class_name = serializer_class.Meta.model.__name__.lower()
        return "{0}.{1}".format(model_class_name, event_type)

    def get_packet(self, event, instance):
        """Return all the kwargs to be sent with signal

        This implementation returns a dictionary containing the 'channels', 'event_name', and the serializers 'data'"""
        serializer = self.get_serializer(instance=instance)
        channels = self.get_channels(instance=instance, serializer=serializer)
        event_name = self.get_event_name(event)
        return {
            "channels": channels,
            "event_name": event_name,
            "data": JSONEncoder().encode(serializer.data),
        }


class PrivatePusherBackend(PusherBackend):
    """PrivatePusherBackend is the base class for implementing serializers
    with Pusher and prefixing the channel with `private-`."""

    class Meta:
        abstract = True

    def get_channels(self, instance=None, serializer=None):
        """Return the channels prefixed with `private-`"""
        channels = super().get_channels(instance=instance)
        private_channels = list(
            map(lambda channel: "private-{0}".format(channel), channels)
        )
        return private_channels


def get_models_pusher_backends(model):
    """Return the pusher backends registered for a model"""
    return pusher_backend_registry.get(model.__name__.lower(), [])
