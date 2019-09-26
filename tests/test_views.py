from unittest import TestCase, mock
from unittest.mock import Mock

from django.core.cache import cache
from pytest import mark
from rest_framework import status
from rest_framework.test import APIRequestFactory

from drf_model_pusher.views import ChannelExistenceWebhook
from example.models import MyPublicModel, MyPrivateModel, MyPresenceModel
from example.serializers import MyPublicModelSerializer, MyPrivateModelSerializer, MyPresenceModelSerializer
from example.views import MyPublicModelViewSet, MyPrivateModelViewSet, MyPresenceModelViewSet


@mark.django_db
class TestModelPusherViewMixinPublicChannels(TestCase):
    """Integration tests between models, serializers, pusher backends, and views."""

    @mock.patch("pusher.Pusher.trigger")
    def test_creations_are_pushed(self, trigger: Mock):

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/mymodels/", data={"name": "Henry"})

        view = MyPublicModelViewSet.as_view({"post": "create"})
        response = view(create_request)
        instance = MyPublicModel.objects.last()

        self.assertEqual(response.status_code, 201, response.data)

        trigger.assert_called_once_with(
            ["channel"], "mypublicmodel.create", MyPublicModelSerializer(instance=instance).data, None
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_updates_are_pushed(self, trigger: Mock):
        instance = MyPublicModel.objects.create(name="Julie")

        request_factory = APIRequestFactory()
        partial_update_request = request_factory.patch(
            path="/mymodels/123/", data={"name": "Michelle"}
        )

        view = MyPublicModelViewSet.as_view({"patch": "partial_update"})
        response = view(partial_update_request, pk=instance.pk)
        instance = MyPublicModel.objects.last()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(instance.name, "Michelle")

        trigger.assert_called_once_with(
            ["channel"], "mypublicmodel.update", MyPublicModelSerializer(instance=instance).data, None
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_deletions_are_pushed(self, trigger: Mock):
        instance = MyPublicModel.objects.create(name="Henry")

        request_factory = APIRequestFactory()
        delete_request = request_factory.delete(path="/mymodels/1/")

        view = MyPublicModelViewSet.as_view({"delete": "destroy"})
        response = view(delete_request, pk=instance.pk)

        self.assertEqual(response.status_code, 204, response.data)
        with self.assertRaises(MyPublicModel.DoesNotExist):
            instance = MyPublicModel.objects.get(pk=instance.pk)

        trigger.assert_called_once_with(
            ["channel"], "mypublicmodel.delete", MyPublicModelSerializer(instance=instance).data, None
        )


@mark.django_db
class TestModelPusherViewMixinPrivateChannels(TestCase):
    """Integration tests between models, serializers, pusher backends, and views."""

    @mock.patch("pusher.Pusher.trigger")
    def test_creations_are_pushed(self, trigger: Mock):

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/mymodels/", data={"name": "Henry"})

        view = MyPrivateModelViewSet.as_view({"post": "create"})
        response = view(create_request)
        instance = MyPrivateModel.objects.last()

        self.assertEqual(response.status_code, 201, response.data)

        trigger.assert_called_once_with(
            ["private-channel"], "myprivatemodel.create", MyPrivateModelSerializer(instance=instance).data, None
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_updates_are_pushed(self, trigger: Mock):
        instance = MyPrivateModel.objects.create(name="Julie")

        request_factory = APIRequestFactory()
        partial_update_request = request_factory.patch(
            path="/mymodels/123/", data={"name": "Michelle"}
        )

        view = MyPrivateModelViewSet.as_view({"patch": "partial_update"})
        response = view(partial_update_request, pk=instance.pk)
        instance = MyPrivateModel.objects.last()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(instance.name, "Michelle")

        trigger.assert_called_once_with(
            ["private-channel"], "myprivatemodel.update", MyPrivateModelSerializer(instance=instance).data, None
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_deletions_are_pushed(self, trigger: Mock):
        instance = MyPrivateModel.objects.create(name="Henry")

        request_factory = APIRequestFactory()
        delete_request = request_factory.delete(path="/mymodels/1/")

        view = MyPrivateModelViewSet.as_view({"delete": "destroy"})
        response = view(delete_request, pk=instance.pk)

        self.assertEqual(response.status_code, 204, response.data)
        with self.assertRaises(MyPrivateModel.DoesNotExist):
            instance = MyPrivateModel.objects.get(pk=instance.pk)

        trigger.assert_called_once_with(
            ["private-channel"], "myprivatemodel.delete", MyPrivateModelSerializer(instance=instance).data, None
        )


@mark.django_db
class TestModelPusherViewMixinPresenceChannels(TestCase):
    """Integration tests between models, serializers, pusher backends, and views."""

    @mock.patch("pusher.Pusher.trigger")
    def test_creations_are_pushed(self, trigger: Mock):

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/mymodels/", data={"name": "Henry"})

        view = MyPresenceModelViewSet.as_view({"post": "create"})
        response = view(create_request)
        instance = MyPresenceModel.objects.last()

        self.assertEqual(response.status_code, 201, response.data)

        trigger.assert_called_once_with(
            ["presence-channel"], "mypresencemodel.create", MyPresenceModelSerializer(instance=instance).data, None
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_updates_are_pushed(self, trigger: Mock):
        instance = MyPresenceModel.objects.create(name="Julie")

        request_factory = APIRequestFactory()
        partial_update_request = request_factory.patch(
            path="/mymodels/123/", data={"name": "Michelle"}
        )

        view = MyPresenceModelViewSet.as_view({"patch": "partial_update"})
        response = view(partial_update_request, pk=instance.pk)
        instance = MyPresenceModel.objects.last()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(instance.name, "Michelle")

        trigger.assert_called_once_with(
            ["presence-channel"], "mypresencemodel.update", MyPresenceModelSerializer(instance=instance).data, None
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_deletions_are_pushed(self, trigger: Mock):
        instance = MyPresenceModel.objects.create(name="Henry")

        request_factory = APIRequestFactory()
        delete_request = request_factory.delete(path="/mymodels/1/")

        view = MyPresenceModelViewSet.as_view({"delete": "destroy"})
        response = view(delete_request, pk=instance.pk)

        self.assertEqual(response.status_code, 204, response.data)
        with self.assertRaises(MyPresenceModel.DoesNotExist):
            instance = MyPresenceModel.objects.get(pk=instance.pk)

        trigger.assert_called_once_with(
            ["presence-channel"], "mypresencemodel.delete", MyPresenceModelSerializer(instance=instance).data, None
        )


@mark.django_db
class TestChannelExistenceWebhook(TestCase):
    """Test the ChannelExistenceWebhook"""
    def tearDown(self):
        cache.clear()

    @mock.patch("pusher.Pusher.validate_webhook")
    def test_auth_is_successful(self, validate_webhook: Mock):
        data = {
            "time_ms": 123456789,
            "events": [
                {"name": "channel_occupied", "channel": "my-channel"}
            ]
        }

        headers = dict(
            HTTP_X_PUSHER_KEY="123456789",
            HTTP_X_PUSHER_SIGNATURE="123456789"
        )

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/pusher/channel-existence/", data=data, **headers)
        view = ChannelExistenceWebhook().as_view()
        response = view(create_request)

        self.assertTrue(validate_webhook.called)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch("pusher.Pusher.validate_webhook")
    def test_occupied_channel_stored_in_cache(self, validate_webhook: Mock):
        data = {
            "time_ms": 123456789,
            "events": [
                {"name": "channel_occupied", "channel": "my-channel"}
            ]
        }

        headers = dict(
            HTTP_X_PUSHER_KEY="123456789",
            HTTP_X_PUSHER_SIGNATURE="123456789"
        )

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/pusher/channel-existence/", data=data, **headers)
        view = ChannelExistenceWebhook().as_view()
        response = view(create_request)

        self.assertTrue(validate_webhook.called)
        self.assertTrue(cache.get("drf-model-pusher:occupied:my-channel"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch("pusher.Pusher.validate_webhook")
    def test_multiple_occupied_channels_stored_in_cache(self, validate_webhook: Mock):
        data = {
            "time_ms": 123456789,
            "events": [
                {"name": "channel_occupied", "channel": "my-channel-1"},
                {"name": "channel_occupied", "channel": "my-channel-2"}
            ]
        }

        headers = dict(
            HTTP_X_PUSHER_KEY="123456789",
            HTTP_X_PUSHER_SIGNATURE="123456789"
        )

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/pusher/channel-existence/", data=data, **headers)
        view = ChannelExistenceWebhook().as_view()
        response = view(create_request)

        self.assertTrue(validate_webhook.called)
        self.assertTrue(cache.get("drf-model-pusher:occupied:my-channel-1"))
        self.assertTrue(cache.get("drf-model-pusher:occupied:my-channel-2"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch("pusher.Pusher.validate_webhook")
    def test_occupied_channel_vacated_in_cache(self, validate_webhook: Mock):
        data = {
            "time_ms": 123456789,
            "events": [
                {"name": "channel_occupied", "channel": "my-channel"}
            ]
        }

        headers = dict(
            HTTP_X_PUSHER_KEY="123456789",
            HTTP_X_PUSHER_SIGNATURE="123456789"
        )

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/pusher/channel-existence/", data=data, **headers)
        view = ChannelExistenceWebhook().as_view()
        response = view(create_request)

        self.assertTrue(validate_webhook.called)
        self.assertTrue(cache.get("drf-model-pusher:occupied:my-channel"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "time_ms": 123456789,
            "events": [
                {"name": "channel_vacated", "channel": "my-channel"}
            ]
        }

        create_request = request_factory.post(path="/pusher/channel-existence/", data=data, **headers)
        response = view(create_request)

        self.assertFalse(cache.get("drf-model-pusher:occupied:my-channel"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch("pusher.Pusher.validate_webhook")
    def test_vacate_channel_when_not_in_cache(self, validate_webhook: Mock):
        data = {
            "time_ms": 123456789,
            "events": [
                {"name": "channel_vacated", "channel": "my-channel"}
            ]
        }

        headers = dict(
            HTTP_X_PUSHER_KEY="123456789",
            HTTP_X_PUSHER_SIGNATURE="123456789"
        )

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/pusher/channel-existence/", data=data, **headers)
        view = ChannelExistenceWebhook().as_view()
        response = view(create_request)

        self.assertTrue(validate_webhook.called)
        self.assertFalse(cache.get("drf-model-pusher:occupied:my-channel"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
