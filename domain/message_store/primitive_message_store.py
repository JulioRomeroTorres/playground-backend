from pydantic import BaseModel

class PrimitiveMessageStore(BaseModel):
    thread_id: str
    max_messages: int | None = None