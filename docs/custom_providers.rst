.. DRF Model Pusher documentation for implementing custom providers

Implementing Custom Providers
============================================

DRF Model Pusher provides functionality to allow you to implement your own custom providers if none of the included providers suit your needs.

To implement a custom provider you need to implement a few methods expected by the `drf_model_pusher.providers.BaseProvider` class. These methods are::

    from drf_model_pusher.providers import BaseProvider

    class MyCustomProvider(BaseProvider):
        def configure(self):
            """
            This method can be used to setup a connection with the provider or implement other one-time initial configuration.
            """
            pass

        def parse_packet(self, backend, channels, event_name, data, socket_id=None):
            """
            This method is available to be implemented as a hook before the event is sent. This could be useful
            for logging or sanitizing any data before transit.
            """
            return channels, event_name, data

        def trigger(self, channels, event_name, data, socket_id=None):
            """
            This method is where the event should be sent to the provider.
            """
            pass

.. code-block:: python
