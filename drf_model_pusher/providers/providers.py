from distutils.util import strtobool

from django.conf import settings


class AbstractProvider(object):

    def __init__(self):
        self.disabled = False

        if hasattr(settings, "DRF_MODEL_PUSHER_DISABLED"):
            self.disabled = bool(strtobool(settings.DRF_MODEL_PUSHER_DISABLED))

    def trigger(self, *args, **kwargs):
        """Send a pusher event"""
        raise NotImplementedError()
