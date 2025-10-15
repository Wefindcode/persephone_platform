from __future__ import annotations

import logging
import sys
import uuid
from typing import Any, Callable

from fastapi import Request
from pythonjsonlogger import jsonlogger

REQUEST_ID_HEADER = "X-Request-ID"


def setup_logging() -> None:
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter("%(levelname)s %(name)s %(message)s")
    log_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [log_handler]


async def request_id_middleware(request: Request, call_next: Callable[..., Any]) -> Any:
    request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response
