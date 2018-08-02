from django.conf import settings

from drf_model_pusher.proxies import PusherProxy


def send_pusher_event(
    signal, sender, instance, channels, event_name, data, socket_id=None, **kwargs
):
    """
    Send a pusher event from a signal
    """
    try:
        pusher_cluster = settings.PUSHER_CLUSTER
    except AttributeError:
        pusher_cluster = "mt1"

    pusher = PusherProxy(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=pusher_cluster,
    )
    pusher.trigger(channels, event_name, data)
