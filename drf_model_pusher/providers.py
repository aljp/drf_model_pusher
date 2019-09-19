
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
            self._disabled = settings.DRF_MODEL_PUSHER_DISABLED

    def configure(self):
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
        if not isinstance(channels, list):
            raise TypeError("channels must be a list, received {0}".format(str(type(channels))))

        if self._disabled:
            return

        self.client.trigger(channels, event_name, data, socket_id)

    @property
    def client(self):
        if self._pusher is None:
            self.configure()

        return self._pusher


class AblyProvider(object):
    def __init__(self, *args, **kwargs):
        pass

    def configure(self):
        pass

    def trigger(self, channels, event_name, data):
        pass
