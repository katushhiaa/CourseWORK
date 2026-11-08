# Базовий сервіс з'єднання (незалежний компонент)
class ConnectionService:
    def __init__(self, connection_string: str, timeout_sec: int = 5):
        self.connection_string = connection_string
        self.timeout_sec = timeout_sec

    def execute(self, query: str) -> list:
        print(f"Executing on {self.connection_string} with timeout {self.timeout_sec}s")
        return []

# Сервіс аудиту (делегує роботу через композицію)
class AuditLogger:
    def __init__(self, logger_name: str):
        self.logger_name = logger_name

    def log_action(self, query: str):
        print(f"[{self.logger_name}] Auditing query...")

# Плоский клас репозиторію — успадкування замінено на композицію (DIT = 1)
class MongoOrderRepository:
    def __init__(self, connection_service: ConnectionService, audit_logger: AuditLogger, mongo_cluster: str):
        self.connection_service = connection_service  # Композиція (DI)
        self.audit_logger = audit_logger              # Композиція (DI)
        self.mongo_cluster = mongo_cluster

    def execute_query(self, query: str) -> list:
        self.audit_logger.log_action(query)
        print(f"Routing directly to Mongo cluster {self.mongo_cluster}")
        return self.connection_service.execute(query)

    def get_table_name(self) -> str:
        return "mongo_orders"