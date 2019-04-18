"""The receiver methods attach to callbacks to signals"""
from drf_model_pusher.providers import PusherProvider


def send_pusher_event(
    signal,
    sender,
    instance,
    channels,
    event_name,
    data,
    socket_id=None,
    **kwargs
):
    """
    Sends an update using the provided provider class
    """

    push_provider_class = kwargs.get("provider_class", PusherProvider)
    push_provider = push_provider_class()
    push_provider.trigger(channels, event_name, data, socket_id)
