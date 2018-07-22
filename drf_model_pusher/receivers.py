from django.conf import settings
from pusher import Pusher


def send_pusher_event(
    signal,
    sender,
    instance,
    channel,
    event_name,
    data,
    socket_id=None,
):
    """
    Send a pusher event from a signal
    """
    try:
        pusher_cluster = settings.PUSHER_CLUSTER
    except AttributeError:
        pusher_cluster = 'mt1'

    pusher = Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=pusher_cluster,
    )
    pusher.trigger(
        [channel],
        event_name,
        data,
    )
