from distutils.util import strtobool

from django.conf import settings
from pusher import Pusher


class PusherProvider(object):
    """
    This class provides a wrapper to Pusher so that we can mock it or disable it easily
    """

    def __init__(self):
        self._pusher = None
        self._disabled = False

        if hasattr(settings, "DRF_MODEL_PUSHER_DISABLED"):
            self._disabled = bool(strtobool(settings.DRF_MODEL_PUSHER_DISABLED))

        self.configure()

    def configure(self):
        """Configure the Pusher client"""
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
        if self._disabled:
            return

        return self._pusher.trigger(channels, event_name, data, socket_id)


# TODO: Implement AblyProvider
class AblyProvider(object):
    def __init__(self, *args, **kwargs):
        pass

    def configure(self):
        pass

    def trigger(self, channels, event_name, data):
        pass
