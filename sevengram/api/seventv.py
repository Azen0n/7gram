from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportError

from sevengram.api.base import BaseApiClient
from sevengram.exceptions import ApiError


class SevenTvApiClient(BaseApiClient):
    """7TV API client."""

    async def fetch_emote(self, external_id: str) -> dict:
        """Fetch a single 7TV emote."""
        transport = AIOHTTPTransport(
            url=self._base_url,
            headers={'User-Agent': 'sevengram/0.1.0'},
        )
        client = Client(transport=transport)
        query = gql(
            """
            query getEmote($id: ID!) {
              emotes {
                emote(id: $id) {
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

        async with client as session:
            try:
                result = await session.execute(query)
            except TransportError as e:
                session.close()
                raise ApiError('Failed to fetch an emote.') from e

        return result
