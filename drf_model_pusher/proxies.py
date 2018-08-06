from django.conf import settings
from pusher import Pusher


class PusherProxy(object):
    """
    This class provides a wrapper to Pusher so that we can mock it or disable it easily
    """
    def __init__(self, *args, **kwargs):
        self._pusher = Pusher(*args, **kwargs)
        self._disabled = False

        if hasattr(settings, "DRF_MODEL_PUSHER_DISABLED"):
            self._disabled = settings.DRF_MODEL_PUSHER_DISABLED

    def trigger(self, channels, event_name, data):
        if self._disabled:
            return

        self._pusher.trigger(channels, event_name, data)