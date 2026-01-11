from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager


class BaseApiClient(ABC):
    def __init__(
        self,
        base_url: str | None = None,
    ):
        """Base API client."""
        self._base_url = base_url
        self._client = self._create_client()

    @abstractmethod
    def _create_client(self) -> AbstractAsyncContextManager:
        """Initialize and return an API client instance.

        Client must implement __aenter__ and __aexit__ methods.
        """
        raise NotImplementedError()
