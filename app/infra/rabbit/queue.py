from faststream.rabbit import RabbitQueue

proxy_engine_queue = RabbitQueue(
    name="proxy_engine_queue",
    passive=True,
)
