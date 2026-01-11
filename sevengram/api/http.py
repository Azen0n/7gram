from httpx import AsyncClient

from sevengram.config import settings


def create_http_client() -> AsyncClient:
    return AsyncClient(
        headers={
            'User-Agent': settings.USER_AGENT,
        },
    )
