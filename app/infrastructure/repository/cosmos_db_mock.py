from typing import Optional
from typing import Any, Dict, List
from app.domain.repository.not_sql_repository import INotSqlRepository
from app.infrastructure.contants import DISPATCHER_MOCK_SETTINGS

JsonType = Dict[str, Any]
JsonArrayType = List[JsonType]

class CosmosDbRepositoryMock(INotSqlRepository):
    def __init__(self, url: str, database: str, container: Optional[str] = None) -> None:
        pass
    def _get_container(self, container_name: str):
        return ""

    def _create_container(self, container_name: str):
        return None

    def get_item(self, item_id: str, partition_key: str, container: Optional[str] = None):
        return DISPATCHER_MOCK_SETTINGS

    def insert_item(self, raw_data: JsonType, container: Optional[str] = None) -> None:
        return None

    def query_items(self, query: str, parameters: Optional[JsonArrayType] = None, 
                    enable_cross_partition_query: Optional[bool] = None,
                    container: Optional[str] = None):

        return []

    def delete_item(self):
        pass