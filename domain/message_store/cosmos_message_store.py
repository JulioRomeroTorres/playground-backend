from app.domain.message_store.primitive_message_store import PrimitiveMessageStore

class CosmosMessageStore(PrimitiveMessageStore):
    url: str
    database: str
    container: str