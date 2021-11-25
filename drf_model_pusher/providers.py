
from django.conf import settings
from django.core.cache import cache
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

        valid_channels = channels

        # Only send events to channels that are occupied
        if getattr(settings, "DRF_MODEL_PUSHER_WEBHOOK_OPTIMISATION_ENABLED", False):
            valid_channels = []
            for channel in channels:
                cache_key = "drf-model-pusher:occupied:{}".format(channel)
                occupied = cache.get(cache_key)

                if occupied is None:
                    self._sync_cache()
                    occupied = cache.get(cache_key)

                if occupied is False:
                    continue

                if occupied is True:
                    valid_channels.append(channel)

        if valid_channels:
            self.client.trigger(valid_channels, event_name, data, socket_id)

    @property
    def client(self) -> Pusher:
        if self._pusher is None:
            self.configure()

        return self._pusher

    def _sync_cache(self):
        """
        Fetches channel existence state from Pusher and stores the results in the cache
        :return:
        """
        response = self.client.channels_info()
        occupied_channels = response.get("channels", {}).keys()

        cache.set_many(
            dict.fromkeys(occupied_channels, True)
        )


class AblyProvider(object):
    def __init__(self, *args, **kwargs):
        pass

    def configure(self):
        pass

    def trigger(self, channels, event_name, data):
        pass
