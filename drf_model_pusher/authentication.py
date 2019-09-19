import json

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from drf_model_pusher.providers import PusherProvider


class PusherWebhookAuthentication(BaseAuthentication):
    def authenticate(self, request: Request):
        """
        Makes sure to validate auth headers with Pusher
        https://pusher.com/docs/channels/server_api/webhooks#authentication
        :param request:
        :return:
        """
        validated_data = PusherProvider().client.validate_webhook(
            key=request.META.get("HTTP_X_PUSHER_KEY"),
            signature=request.META.get("HTTP_X_PUSHER_SIGNATURE"),
            body=json.dumps(request.data, separators=(',', ':'))
        )

        if validated_data is None:
            raise AuthenticationFailed()

        return (None, None,)
