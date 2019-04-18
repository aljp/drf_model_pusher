"""Methods for configuration drf_model_pusher"""
from drf_model_pusher.receivers import send_pusher_event
from drf_model_pusher.signals import pusher_backend_post_save, \
    pusher_backend_pre_destroy


def connect_pusher_views():
    """
    Register the send_pusher_event with the view_post_save and
    view_pre_destroy signals
    """
    pusher_backend_post_save.connect(send_pusher_event)
    pusher_backend_pre_destroy.connect(send_pusher_event)
