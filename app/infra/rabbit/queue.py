from faststream.rabbit import RabbitQueue

proxy_engine_queue = RabbitQueue(
    name="proxy_engine_queue",
    passive=True,
)

sentinel_dead_letter_queue = RabbitQueue(
    name="sentinel_dead_letters",
    durable=True,
    routing_key="sentinel_dead_letters",
)

MAX_RETRY = 2
