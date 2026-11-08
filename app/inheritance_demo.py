# Базовий клас (Змінено сигнатуру — додано обов'язковий параметр timeout_sec)
class BaseRepository:
    def __init__(self, connection_string: str, timeout_sec: int):
        self.connection_string = connection_string
        self.timeout_sec = timeout_sec

    def execute_query(self, query: str) -> list:
        print(f"Executing with timeout {self.timeout_sec}s")
        return []

    def get_table_name(self) -> str:
        return "base_table"

# Зламаний проміжний клас (Помилка: не передано timeout_sec у super().__init__())
class AuditableRepository(BaseRepository):
    def __init__(self, connection_string: str, logger_name: str):
        super().__init__(connection_string) # TypeError: __init__() missing 1 required positional argument
        self.logger_name = logger_name

    def execute_query(self, query: str) -> list:
        return super().execute_query(query)

    def get_table_name(self) -> str:
        return "auditable_table"

# Глибокий нащадок
class MongoOrderRepository(AuditableRepository):
    def __init__(self, connection_string: str, logger_name: str, mongo_cluster: str):
        super().__init__(connection_string, logger_name)
        self.mongo_cluster = mongo_cluster

    def execute_query(self, query: str) -> list:
        return [{"order_id": 101}]

    def get_table_name(self) -> str:
        return "mongo_orders"