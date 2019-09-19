from unittest import TestCase, mock
from unittest.mock import Mock

from django.core.cache import cache
from django.test import override_settings

from drf_model_pusher.providers import PusherProvider


class TestPusherProvider(TestCase):
    def tearDown(self):
        cache.clear()

    @mock.patch("pusher.Pusher.trigger")
    def test_trigger_calls_pusher_trigger(self, trigger: Mock):
        provider = PusherProvider()
        provider.trigger(["my-channel"], "myevent", {"foo": "bar"})
        trigger.assert_called_once()

    @override_settings(DRF_MODEL_PUSHER_WEBHOOK_OPTIMISATION_ENABLED=True)
    @mock.patch("pusher.Pusher.trigger")
    def test_trigger_calls_pusher_trigger_when_channel_occupied(self, trigger: Mock):
        cache.set("drf-model-pusher:occupied:my-channel", True)

        provider = PusherProvider()
        provider.trigger(["my-channel"], "myevent", {"foo": "bar"})
        trigger.assert_called_once()

    @override_settings(DRF_MODEL_PUSHER_WEBHOOK_OPTIMISATION_ENABLED=True)
    @mock.patch("pusher.Pusher.trigger")
    def test_trigger_does_not_call_pusher_trigger_when_channel_vacated(self, trigger: Mock):
        cache.set("drf-model-pusher:occupied:my-channel", False)

        provider = PusherProvider()
        provider.trigger(["my-channel"], "myevent", {"foo": "bar"})
        trigger.assert_not_called()

    @override_settings(DRF_MODEL_PUSHER_WEBHOOK_OPTIMISATION_ENABLED=True)
    @mock.patch("pusher.Pusher.channels_info")
    @mock.patch("pusher.Pusher.trigger")
    def test_trigger_syncs_cache_if_channel_does_not_exist_in_cache(self, trigger: Mock, channels_info: Mock):
        channels_info.return_value = {"channels": {"my-channel": {}}}

        provider = PusherProvider()
        provider.trigger(["my-channel"], "myevent", {"foo": "bar"})

        self.assertTrue(cache.get("drf-model-pusher:occupied:my-channel"))
