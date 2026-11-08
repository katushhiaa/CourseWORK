from abc import ABC, abstractmethod
from typing import Dict, Any

class IOrderService(ABC):
    """Абстрактний контракт для обробки замовлень."""
    @abstractmethod
    def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class IPrinterService(ABC):
    """Абстрактний контракт для взаємодії з принтерами."""
    @abstractmethod
    def send_to_printer(self, printer_id: str, payload: dict) -> bool:
        pass