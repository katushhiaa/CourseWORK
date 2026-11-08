# Базовий клас (DIT = 1)
class BaseRepository:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def execute_query(self, query: str) -> list:
        print(f"Executing on {self.connection_string}: {query}")
        return []

    def get_table_name(self) -> str:
        return "base_table"

# Проміжний нащадок (DIT = 2) — масове перевизначення методів
class AuditableRepository(BaseRepository):
    def __init__(self, connection_string: str, logger_name: str):
        super().__init__(connection_string)
        self.logger_name = logger_name

    def execute_query(self, query: str) -> list:
        print(f"[{self.logger_name}] Auditing query execution...")
        return super().execute_query(query)

    def get_table_name(self) -> str:
        return "auditable_table"

# Глибокий нащадок (DIT = 3) — крихка ієрархія
class MongoOrderRepository(AuditableRepository):
    def __init__(self, connection_string: str, logger_name: str, mongo_cluster: str):
        super().__init__(connection_string, logger_name)
        self.mongo_cluster = mongo_cluster

    def execute_query(self, query: str) -> list:
        print(f"Routing to Mongo cluster {self.mongo_cluster}")
        return [{"order_id": 101, "status": "processed"}]

    def get_table_name(self) -> str:
        return "mongo_orders"