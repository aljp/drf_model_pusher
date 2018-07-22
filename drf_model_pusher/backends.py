"""
Mixin Classes for Pusher integration with Views
"""
from collections import defaultdict

from drf_model_pusher.signals import view_pre_destroy, view_post_save

pusher_backend_registry = defaultdict(list)


class PusherBackendMetaclass(type):
    """
    Register PusherBackend's with a registry for model lookups, supports
    abstract classes
    """

    def __new__(mcs, cls, bases, dicts):
        if dicts.get('Meta') and hasattr(dicts.get('Meta'), 'abstract'):
            dicts['__metaclass__'] = mcs
            return super().__new__(mcs, cls, bases, dicts)

        assert (
            dicts.get('serializer_class', None) is not None,
            'PusherBackends require a serializer_class'
        )
        dicts['__metaclass__'] = mcs

        final_cls = super().__new__(mcs, cls, bases, dicts)

        model_name = dicts['serializer_class'].Meta.model.__name__.lower()
        pusher_backend_registry[model_name].append(final_cls)
        return final_cls


class PusherBackend(metaclass=PusherBackendMetaclass):
    """
    PusherBackend is the base class for implementing serializers with Pusher
    """

    class Meta:
        abstract = True

    def __init__(self, view):
        self.view = view
        self.pusher_socket_id = self.get_pusher_socket(view)

    def get_pusher_socket(self, view):
        pusher_socket = view.request.META.get("HTTP_X_PUSHER_SOCKET_ID", None)
        return pusher_socket

    def push_change(self, event, instance=None, pre_destroy=False, ignore=False):
        channel, event_name, data = self.get_packet(event, instance)
        if pre_destroy:
            view_pre_destroy.send(
                sender=self.__class__,
                instance=self,
                channel=channel,
                event_name=event_name,
                data=data,
                socket_id=self.pusher_socket_id if ignore else None,
            )
        else:
            view_post_save.send(
                sender=self.__class__,
                instance=self,
                channel=channel,
                event_name=event_name,
                data=data,
                socket_id=self.pusher_socket_id if ignore else None,
            )

    def get_event_name(self, event_type):
        """Return the model name and the event_type separated by a dot"""
        serializer_class = self.get_serializer_class()
        return f"{serializer_class.Meta.model.__name__.lower()}.{event_type}"

    def get_serializer_class(self):
        """Return the views serializer class"""
        return self.view.get_serializer_class()

    def get_serializer(self, view, *args, **kwargs):
        """Return the serializer initialized with the views serializer context"""
        serializer_class = self.get_serializer_class()
        kwargs["context"] = view.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_channel(self, instance=None):
        """Return the channel from the view or instance"""
        channel = self.view.get_pusher_channel()
        return channel

    def get_packet(self, event, instance):
        """Return a tuple consisting of the channel, event name, and the JSON serializable data."""
        channel = self.get_channel(instance=instance)
        event_name = self.get_event_name(event)
        data = self.get_serializer(self.view, instance=instance).data
        return channel, event_name, data


class PrivatePusherBackend(PusherBackend):
    """PrivatePusherBackend is the base class for implementing serializers
    with Pusher and prefixing the channel with `private-`."""

    class Meta:
        abstract = True

    def get_channel(self, instance=None):
        """Return the channel prefixed with `private-`"""
        channel = super().get_channel(instance=instance)
        return f"private-{channel}"


def get_models_pusher_backends(model):
    """Return the pusher backends registered for a model"""
    return pusher_backend_registry.get(model.__name__.lower(), [])
