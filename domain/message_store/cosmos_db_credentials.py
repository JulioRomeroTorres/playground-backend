from pydantic import BaseModel
from typing import Optional

class CosmosDbCredentials(BaseModel):
    url: str
    database: str
    container: Optional[str] = None