from faststream.rabbit import RabbitRouter

from app.infra.rabbit.queue import proxy_engine_queue

router = RabbitRouter()


@router.subscriber(proxy_engine_queue)
async def handle_engine_events(event):
    pass
