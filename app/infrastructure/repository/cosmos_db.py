from azure.identity import DefaultAzureCredential   
from azure.cosmos import CosmosClient
from typing import Optional
from typing import Any, Dict, List
from app.domain.repository.not_sql_repository import INotSqlRepository

JsonType = Dict[str, Any]
JsonArrayType = List[JsonType]

class CosmosDbRepository(INotSqlRepository):
    def __init__(self, url: str, database: str, container: Optional[str] = None) -> None:
        credential = DefaultAzureCredential()
        self.client = CosmosClient(url=url, credential=credential)
        self.database = self.client.get_database_client(f"{database}")
        self.container = self._get_container(container) if container else None

    def _get_container(self, container_name: str):
        return self.database.get_container_client(f"{container_name}")

    def _create_container_reference(self, container_name: str):
        return self._get_container(container_name) if self.container is None else self.container

    def get_item(self, item_id: str, partition_key: str, container: Optional[str] = None):
        container = self._create_container_reference(container)
        return container.read_item(
            item=item_id,
            partition_key=partition_key,
        )

    def insert_item(self, raw_data: JsonType, container: Optional[str] = None) -> None:
        container = self._create_container_reference(container)
        return container.upsert_item(
            raw_data
        )

    def batch_insert(self, items: List[JsonType], partition_key: str, container: Optional[str] = None):
        batch_operations = []
        container = self._create_container_reference(container)

        for item in items:
            batch_operations.append(
                ("upsert", (item,), {})
            )

        container.execute_item_batch(
            batch_operations=batch_operations,
            partition_key=partition_key
        )

    def query_items(self, query: str, parameters: Optional[JsonArrayType] = None, 
                    enable_cross_partition_query: Optional[bool] = None,
                    container: Optional[str] = None):
        container = self._create_container_reference(container)
        return container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=enable_cross_partition_query,
        )

    def upsert_item(self, body: Dict[str, Any], container: Optional[str] = None) -> None:
        container = self._create_container_reference(container)
        container.upsert_item(body)

    def delete_item(self):
        pass