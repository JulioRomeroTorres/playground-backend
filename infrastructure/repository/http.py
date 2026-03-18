import aiohttp
import logging
from typing import Any
from collections.abc import Coroutine
from app.infrastructure.managers.http_manager import HttpRepositoryManager

class HttpRepository:
    def __init__(self, base_url: str) -> None:
        self.session = HttpRepositoryManager.get_session_for_baseurl(base_url)
        self.base_url = base_url
        self.logger = logging.getLogger(__name__ + ".HttpRepositoryClient")
        pass

    async def post(self, endpoint: str, data: dict) -> Coroutine[Any]:
        try:
            print("Ajaa",f"{self.base_url}{endpoint}")
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=data
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"HTTP error {e.status}: {e.message}")
            raise

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {e}")
            raise
            
        except aiohttp.ContentTypeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {await response.text()}") from e
    
    async def post_stream(self, endpoint: str, data: dict) -> Coroutine[Any]:
        try:
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=data
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"HTTP error {e.status}: {e.message}")
            raise

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {e}")
            raise
            
        except aiohttp.ContentTypeError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {await response.text()}") from e
