from django.dispatch import Signal


view_post_save = Signal(
    providing_args=["instance", "channels", "event_name", "data", "socket_id"]
)
pusher_backend_post_save = view_post_save

view_pre_destroy = Signal(
    providing_args=["instance", "channels", "event_name", "data", "socket_id"]
)
pusher_backend_pre_destroy = view_pre_destroy
