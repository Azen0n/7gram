from sevengram.config import settings

from .http import create_http_client
from .seventv import SevenTvApiClient

seventv_client = SevenTvApiClient(settings.SEVENTV_API_URL.encoded_string())
http_client = create_http_client()
