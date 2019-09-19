from django.core.cache import cache
from rest_framework import serializers


class PusherWebhookSerializer(serializers.Serializer):
    """
    Generic serializer to be used as the base of any Pusher webhook, represents the standard webhook format
    https://pusher.com/docs/channels/server_api/webhooks#webhook-format
    """
    time_ms = serializers.IntegerField()


class EventSerializer(serializers.Serializer):
    """
    Generic serializer to be used as the base of any Pusher webhook event
    """
    name = serializers.CharField()


class ChannelExistenceEventSerializer(EventSerializer):
    """
    Pusher webhook event serializer representing channel existence events
    https://pusher.com/docs/channels/server_api/webhooks#channel-existence-events
    """
    channel = serializers.CharField()


class ChannelExistenceSerializer(PusherWebhookSerializer):
    """
    Pusher webhook serializer representing a channel existence webhook
    https://pusher.com/docs/channels/server_api/webhooks#channel-existence-events
    """
    events = ChannelExistenceEventSerializer(many=True)

    def create(self, validated_data):
        for event in validated_data.get("events", []):
            # Channel is occupied, add it to the cache
            if event["name"] == "channel_occupied":
                cache_key = "drf-model-pusher:occupied:{}".format(event["channel"])
                cache.set(cache_key, True)

            # Channel has been vacated, remove it from the cache
            if event["name"] == "channel_vacated":
                cache_key = "drf-model-pusher:occupied:{}".format(event["channel"])
                cache.delete(cache_key)

        return validated_data
