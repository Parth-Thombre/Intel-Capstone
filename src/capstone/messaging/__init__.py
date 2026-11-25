"""Message transport, validation and routing boundary.

Future clients validate wire envelopes and enqueue correlated internal events.
They must not change delivery state from network callbacks. Typed shared event
models belong in capstone.models; external-system translation belongs in
capstone.adapters.

MQTT clients, subscriptions and the event queue are not implemented here yet.
Importing this package opens no connection or background thread.
"""
