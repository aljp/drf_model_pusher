"""
PusherBackend classes define how changes from a Model are serialized, and then which provider will send the message.
"""
from collections import defaultdict

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
        """Send a signal to push the update"""
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

        if pre_destroy:
            pusher_backend_pre_destroy.send(
                sender=self.__class__,
                instance=self,
                channels=channels,
                event_name=event_name,
                data=data,
                socket_id=self.pusher_socket_id if ignore else None,
                provider_class=self.provider_class,
            )
        else:
            pusher_backend_post_save.send(
                sender=self.__class__,
                instance=self,
                channels=channels,
                event_name=event_name,
                data=data,
                socket_id=self.pusher_socket_id if ignore else None,
                provider_class=self.provider_class,
            )

    def get_serializer_class(self):
        """Return the views serializer class

        The default implementation attempts to return the serializer_class
        attribute on the current instance, if that cannot be found then it
        will attempt to return the serializer class from the view.  Otherwise
        a NotImplementedError is raised."""
        if self.serializer_class:
            return self.serializer_class

        if self.view and hasattr(self.view, "serializer_class"):
            return self.view.serializer_class

        raise NotImplementedError(
            "{0} cannot find a 'serializer_class' attribute".format(
                self.__class__.__name__
            )
        )

    def get_serializer_context(self):
        """Return a dictionary that will be passed to the serializers context

        The default implementation attempts to return the context from the
        views 'get_serializer_context()' method, if the view has no
        'get_serializer_context()' method then one is """
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
        """Return the serializer initialized with the views serializer context"""
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_channels(self, instance=None, serializer=None):
        """Return a list of channels from the view, serializer, and instance"""
        channels = set()
        if self.view and hasattr(self.view, "get_pusher_channels"):
            channels.update(set(self.view.get_pusher_channels()))

        if serializer and hasattr(serializer, "get_pusher_channels"):
            channels.update(set(self.view.get_pusher_channels()))

        if instance and hasattr(instance, "get_pusher_channels"):
            channels.update(set(self.view.get_pusher_channels()))

        if channels:
            return list(channels)

        raise NotImplementedError(
            "{0} cannot find a get_pusher_channels() method on the view, serializer, or instance".format(
                self.__class__.__name__
            )
        )

    def get_event_name(self, event_type):
        """Return the model name and the event_type separated by a dot"""
        serializer_class = self.get_serializer_class()
        model_class_name = serializer_class.Meta.model.__name__.lower()
        return "{0}.{1}".format(model_class_name, event_type)

    def get_packet(self, event, instance):
        """Return a dictionary containing of the 'channel', 'event_name', and the serializers 'data'"""
        serializer = self.get_serializer(instance=instance)
        channels = self.get_channels(instance=instance, serializer=serializer)
        event_name = self.get_event_name(event)
        return {"channels": channels, "event_name": event_name, "data": serializer.data}


class PrivatePusherBackend(PusherBackend):
    """PrivatePusherBackend is the base class for implementing serializers
    with Pusher and prefixing the channel with `private-`."""

    class Meta:
        abstract = True

    def get_channel(self, instance=None):
        """Return the channel prefixed with `private-`"""
        channels = super().get_channels(instance=instance)
        private_channels = list(
            map(lambda channel: "private-{0}".format(channels), channels)
        )
        return private_channels


def get_models_pusher_backends(model):
    """Return the pusher backends registered for a model"""
    return pusher_backend_registry.get(model.__name__.lower(), [])
