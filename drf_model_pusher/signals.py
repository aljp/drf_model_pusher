from django.dispatch import Signal


view_post_save = Signal(
    providing_args=['instance', 'channel', 'event_name', 'data', 'socket_id']
)

view_pre_destroy = Signal(
    providing_args=['instance', 'channel', 'event_name', 'data', 'socket_id']
)
