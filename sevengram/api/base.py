class BaseApiClient:
    def __init__(
        self,
        base_url: str,
    ):
        """Base API client."""
        self._base_url = base_url
