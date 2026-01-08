from typing import Protocol


class EmoteApiClient(Protocol):
    _base_url: str
    """Base external API URL."""

    """External emote API client protocol."""

    async def fetch_emote(self, external_id: int) -> dict:
        """Fetch a single emote."""
        ...
