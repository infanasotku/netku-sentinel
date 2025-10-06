from logging import Logger
import traceback
from typing import Callable

from app.infra.logging.logger import config, logger

__all__ = ["logger", "config"]


async def with_logging(func: Callable, logger: Logger = logger, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
