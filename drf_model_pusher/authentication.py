from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from drf_model_pusher.providers import PusherProvider


class PusherWebhookAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Makes sure to validate auth headers with Pusher
        https://pusher.com/docs/channels/server_api/webhooks#authentication
        :param request:
        :return:
        """
        validated_data = PusherProvider().client.validate_webhook(
            key=request.META.get("HTTP_X_PUSHER_KEY"),
            signature=request.META.get("HTTP_X_PUSHER_SIGNATURE"),
            body=request.data
        )

        if validated_data is None:
            raise AuthenticationFailed()

        return (None, None,)
