"""
PusherBackend classes define how changes from a Model are serialized, and then which provider will send the message.
"""
from collections import defaultdict
from typing import List, Dict

from drf_model_pusher.providers import PusherProvider
from drf_model_pusher.signals import view_pre_destroy, view_post_save

pusher_backend_registry = defaultdict(list)


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


class PacketAdapter(object):
    """Adapt data from the (event, channels, data) to a potentially different format."""

    def parse_packet(self, channels: List[str], event_name: str, data: Dict):
        return channels, event_name, data


class PusherBackend(metaclass=PusherBackendMetaclass):
    """
    PusherBackend is the base class for implementing serializers with Pusher
    """

    class Meta:
        abstract = True

    packet_adapter_class = PacketAdapter
    provider_class = PusherProvider

    def __init__(self, view):
        self.view = view
        self.pusher_socket_id = self.get_pusher_socket(view)
        self.packet_adapter = PacketAdapter()

    def get_pusher_socket(self, view):
        """Return the socket from the request header."""
        pusher_socket = view.request.META.get("HTTP_X_PUSHER_SOCKET_ID", None)
        return pusher_socket

    def push_change(self, event, instance=None, pre_destroy=False, ignore=True):
        """Send a signal to push the update"""
        channels, event_name, data = self.get_packet(event, instance)
        if pre_destroy:
            view_pre_destroy.send(
                sender=self.__class__,
                instance=self,
                channels=channels,
                event_name=event_name,
                data=data,
                socket_id=self.pusher_socket_id if ignore else None,
                provider_class=self.provider_class,
            )
        else:
            view_post_save.send(
                sender=self.__class__,
                instance=self,
                channels=channels,
                event_name=event_name,
                data=data,
                socket_id=self.pusher_socket_id if ignore else None,
                provider_class=self.provider_class,
            )

    def get_event_name(self, event_type):
        """Return the model name and the event_type separated by a dot"""
        serializer_class = self.get_serializer_class()
        model_class_name = serializer_class.Meta.model.__name__.lower()
        return "{0}.{1}".format(model_class_name, event_type)

    def get_serializer_class(self):
        """Return the views serializer class"""
        return self.view.get_serializer_class()

    def get_serializer(self, view, *args, **kwargs):
        """Return the serializer initialized with the views serializer context"""
        serializer_class = self.get_serializer_class()
        kwargs["context"] = view.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_channels(self, instance=None):
        """Return the channel from the view or instance"""
        channels = self.view.get_pusher_channels()
        return channels

    def get_packet(self, event, instance):
        """Return a tuple consisting of the channel, event name, and the JSON serializable data."""
        channels = self.get_channels(instance=instance)
        event_name = self.get_event_name(event)
        data = self.get_serializer(self.view, instance=instance).data
        channels, event_name, data = self.packet_adapter.parse_packet(channels, event_name, data)
        return channels, event_name, data


class PrivatePusherBackend(PusherBackend):
    """PrivatePusherBackend is the base class for implementing serializers
    with Pusher and prefixing the channel with `private-`."""

    class Meta:
        abstract = True

    def get_channel(self, instance=None):
        """Return the channel prefixed with `private-`"""
        channel = super().get_channel(instance=instance)
        return "private-{channel}".format(channel=channel)


def get_models_pusher_backends(model):
    """Return the pusher backends registered for a model"""
    return pusher_backend_registry.get(model.__name__.lower(), [])
