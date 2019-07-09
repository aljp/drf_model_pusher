from drf_model_pusher.backends import get_models_pusher_backends, PUSH_UPDATE, PUSH_CREATE, PUSH_DELETE
from drf_model_pusher.exceptions import ModelPusherException
from drf_model_pusher.signals import pusher_backend_post_save


class ModelViewSetPusherMixin(object):
    """Enables views to push changes through pusher"""

    pusher_backend_classes = []

    push_creations = True
    push_updates = True
    push_deletions = True

    def __init__(
        self, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if kwargs.get("push_creations"):
            self.push_creations = bool(kwargs.get("push_creations"))
        if kwargs.get("push_updates"):
            self.push_updates = bool(kwargs.get("push_updates"))
        if kwargs.get("push_deletes"):
            self.push_deletes = bool(kwargs.get("push_deletes"))
        self.pusher_backend_classes = self.get_models_pusher_backend_classes()

    def get_models_pusher_backend_classes(self):
        """Return PusherBackend classes registered for the views model"""
        if hasattr(self, "queryset"):
            model = self.queryset.model
        elif hasattr(self, "get_queryset"):
            model = self.get_queryset().model
        else:
            raise ModelPusherException(
                "{0} must have a queryset attribute or get_queryset method defined".format(self.__class__.__name__)
            )
        return get_models_pusher_backends(model)

    def get_pusher_channels(self):
        """Return the channel from the view"""
        return []

    def use_pusher_socket(self):
        """Configure whether the PusherBackend should include the pusher socket id"""
        return False

    def get_pusher_backends(self):
        """Return all the pusher backends registered for this views model"""
        return [pusher_backend(view=self) for pusher_backend in self.pusher_backend_classes]

    def push_changes(self, event=PUSH_UPDATE, instance=None, pre_destroy=False):
        """Triggers the push_change method for all the pusher backends registered on this views model"""
        for pusher_backend in self.get_pusher_backends():
            pusher_backend.push_change(event, instance, pre_destroy=pre_destroy)

    def perform_update(self, serializer):
        """Update the object and then send the pusher event"""
        super().perform_update(serializer)
        if self.push_updates:
            self.push_changes(PUSH_UPDATE, serializer.instance)

    def perform_create(self, serializer):
        """Create the object and then send the pusher event"""
        super().perform_create(serializer)
        if self.push_creations:
            self.push_changes(PUSH_CREATE, serializer.instance)

    def perform_destroy(self, instance):
        """Sends the pusher event and then destroys the object

        This is done to ensure the serialization can occur"""
        if self.push_deletions:
            self.push_changes(PUSH_DELETE, instance, pre_destroy=True)
        super().perform_destroy(instance)

    def push(self, channels, event_name, data, socket_id=None):
        """Dispatch arbitrary data

        Intended to be invoked directly for custom purposes"""
        pusher_backend_post_save.send(
            instance=self,
            sender=self.__class__,
            channels=channels,
            event_name=event_name,
            data=data,
            socket_id=socket_id if socket_id else None
        )


ModelPusherViewMixin = ModelViewSetPusherMixin
