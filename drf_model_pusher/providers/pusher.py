from django.conf import settings
from pusher import Pusher

from drf_model_pusher.providers.providers import AbstractProvider


class PusherProvider(AbstractProvider):
    """
    This class provides a wrapper to Pusher so that we can mock it or disable it easily
    """

    def __init__(self):
        super().__init__()
        try:
            pusher_cluster = settings.PUSHER_CLUSTER
        except AttributeError:
            pusher_cluster = "mt1"

        self._pusher = Pusher(
            app_id=settings.PUSHER_APP_ID,
            key=settings.PUSHER_KEY,
            secret=settings.PUSHER_SECRET,
            cluster=pusher_cluster,
        )

    def trigger(self, channels, event_name, data, socket_id=None):
        """Send a pusher event"""
        if self.disabled:
            return

        return self._pusher.trigger(channels, event_name, data, socket_id)
