from unittest import TestCase, mock
from unittest.mock import Mock, call

from pytest import mark
from rest_framework.test import APIRequestFactory

from example.models import MyModel
from example.serializers import MyModelSerializer
from example.views import MyModelViewSet


@mark.django_db
class TestModelPusherViewMixin(TestCase):
    """Integration tests between models, serializers, pusher backends, and views."""

    @mock.patch("pusher.Pusher.trigger")
    def test_creations_are_pushed(self, trigger):

        request_factory = APIRequestFactory()
        create_request = request_factory.post(path="/mymodels/", data={"name": "Henry"})

        view = MyModelViewSet.as_view({"post": "create"})
        response = view(create_request)
        instance = MyModel.objects.last()

        self.assertEqual(response.status_code, 201, response.data)
        trigger.assert_has_calls(
            [
                call(
                    ["channel"],
                    "mymodel.create",
                    MyModelSerializer(instance=instance).data,
                    None,
                ),
                call(
                    ["private-channel"],
                    "mymodel.create",
                    MyModelSerializer(instance=instance).data,
                    None,
                ),
            ]
        )

    @mock.patch("example.views.MyModelViewSet.use_pusher_socket")
    @mock.patch("pusher.Pusher.trigger")
    def test_use_pusher_socket(self, trigger, use_pusher_socket):
        use_pusher_socket.return_value = True
        pusher_socket_id = 0.987654321

        request_factory = APIRequestFactory()
        create_request = request_factory.post(
            path="/mymodels/",
            data={"name": "Henry"},
            HTTP_X_PUSHER_SOCKET_ID=pusher_socket_id,
        )
        view = MyModelViewSet.as_view({"post": "create"})
        response = view(create_request)
        instance = MyModel.objects.last()

        self.assertEqual(response.status_code, 201, response.data)
        trigger.assert_has_calls(
            [
                call(
                    ["channel"],
                    "mymodel.create",
                    MyModelSerializer(instance=instance).data,
                    pusher_socket_id,
                ),
                call(
                    ["private-channel"],
                    "mymodel.create",
                    MyModelSerializer(instance=instance).data,
                    pusher_socket_id,
                ),
            ]
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_updates_are_pushed(self, trigger):
        instance = MyModel.objects.create(name="Julie")

        request_factory = APIRequestFactory()
        partial_update_request = request_factory.patch(
            path="/mymodels/123/", data={"name": "Michelle"}
        )

        view = MyModelViewSet.as_view({"patch": "partial_update"})
        response = view(partial_update_request, pk=instance.pk)
        instance = MyModel.objects.last()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(instance.name, "Michelle")

        trigger.assert_has_calls(
            [
                call(
                    ["channel"],
                    "mymodel.update",
                    MyModelSerializer(instance=instance).data,
                    None,
                ),
                call(
                    ["private-channel"],
                    "mymodel.update",
                    MyModelSerializer(instance=instance).data,
                    None,
                ),
            ]
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_deletions_are_pushed(self, trigger):
        instance = MyModel.objects.create(name="Henry")

        request_factory = APIRequestFactory()
        delete_request = request_factory.delete(path="/mymodels/1/")

        view = MyModelViewSet.as_view({"delete": "destroy"})
        response = view(delete_request, pk=instance.pk)

        self.assertEqual(response.status_code, 204, response.data)
        with self.assertRaises(MyModel.DoesNotExist):
            instance = MyModel.objects.get(pk=instance.pk)

        trigger.assert_has_calls(
            [
                call(
                    ["channel"],
                    "mymodel.delete",
                    MyModelSerializer(instance=instance).data,
                    None,
                ),
                call(
                    ["private-channel"],
                    "mymodel.delete",
                    MyModelSerializer(instance=instance).data,
                    None,
                ),
            ]
        )

    @mock.patch("pusher.Pusher.trigger")
    def test_push(self, trigger):

        view = MyModelViewSet()
        view.push(["channel"], "custom.event", {"ok": "cool"})

        trigger.assert_called_once_with(
            ["channel"],
            "custom.event",
            {"ok": "cool"},
            None
        )

