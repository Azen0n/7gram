from sqlalchemy import select

from sevengram.models import Emote, EmoteFormat, EmoteSource
from sevengram.repositories.base import BaseRepository


class EmoteRepository(BaseRepository):
    async def get_by_external_id(
        self,
        external_id: str,
        source: EmoteSource,
    ) -> Emote | None:
        """Return an existing Emote by external_id or None if not found."""
        stmt = select(Emote).where(
            Emote.external_id == external_id,
            Emote.source == source,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        file_id: str | None,
        source: EmoteSource,
        external_id: str,
        name: str,
        file_url: str,
        format: EmoteFormat,
    ) -> Emote:
        """Create a new Emote."""
        emote = Emote(
            file_id=file_id,
            source=source,
            external_id=external_id,
            name=name,
            file_url=file_url,
            format=format,
        )
        self._session.add(emote)
        await self._session.flush()
        return emote
