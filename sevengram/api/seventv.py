from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportError

from sevengram.api.base import BaseApiClient
from sevengram.config import settings
from sevengram.exceptions import ApiError


class SevenTvApiClient(BaseApiClient):
    """7TV API client."""

    def _create_client(self) -> Client:
        transport = AIOHTTPTransport(
            url=self._base_url,
            headers={
                'User-Agent': settings.USER_AGENT,
            },
        )
        return Client(transport=transport)

    async def fetch_emote(self, external_id: str) -> dict:
        """Fetch a single 7TV emote."""
        query = gql(
            """
            query getEmote($id: ID!) {
              emotes {
                emote(id: $id) {
                  id,
                  defaultName,
                  flags {
                    animated,
                  },
                  images {
                    url,
                    mime,
                    size,
                  },
                }
              }
            }
            """,
        )
        query.variable_values = {'id': external_id}

        async with self._client as session:
            try:
                result = await session.execute(query)
                emote_data = result['emotes']['emote']
            except TransportError as e:
                raise ApiError('Failed to fetch an emote.') from e

        return emote_data
