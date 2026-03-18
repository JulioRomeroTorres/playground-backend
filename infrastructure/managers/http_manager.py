import aiohttp
from typing import Dict, Optional

class HttpRepositoryManager:
    _sessions: Dict[str, aiohttp.ClientSession] = {}
    @classmethod
    def get_session_for_baseurl(cls, base_url: str, time_out: Optional[int] = 30) -> aiohttp.ClientSession:

        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        key = f"{parsed.hostname}:{parsed.port or (443 if parsed.scheme == 'https' else 80)}"
        
        if key not in cls._sessions or cls._sessions[key].closed:            
            cls._sessions[key] = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=time_out)
            )
        
        return cls._sessions[key]
    
    @classmethod 
    async def close_all_sessions(cls):
        for _, session in cls._sessions.items():
            if not session.closed:
                await session.close()
        cls._sessions.clear()
