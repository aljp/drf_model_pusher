"""The receiver methods attach to callbacks to signals"""
from typing import Any, Optional, Dict, List

from drf_model_pusher.providers import PusherProvider


def send_pusher_event(
    signal: Any,
    sender: Any,
    instance: Any,
    channels: List[str],
    event_name: str,
    data: Dict,
    socket_id: Optional[str] = None,
    **kwargs
):
    """
    Sends an update using the provided provider class
    """

    push_provider_class = kwargs.get("provider_class", PusherProvider)
    push_provider = push_provider_class()
    push_provider.configure()
    push_provider.trigger(channels, event_name, data, socket_id)
