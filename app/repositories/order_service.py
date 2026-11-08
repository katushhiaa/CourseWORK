from app.repositories.interfaces import IOrderService
from typing import Dict, Any

class OrderService(IOrderService):
    """Сервіс, що відповідає виключно за бізнес-логіку замовлень."""
    def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Processing order securely: {order_data}")
        return {"status": "order_processed", "data": order_data}