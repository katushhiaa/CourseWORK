from datetime import date, datetime
from typing import List, Optional

from app.classes.Entity import Entity


class Order(Entity):
    def __init__(
        self,
        order_number: str,
        customer_id: str,
        product_type: str,
        publication_ids: Optional[List[str]] = None,
        printer_id: Optional[str] = None,
        date_received: Optional[date] = None,
        date_completed: Optional[date] = None,
        is_completed: bool = False,
        cancel_reason: Optional[str] = None,
        _id: Optional[str] = None,
    ):
        self._id = _id
        self.order_number = order_number
        self.customer_id = customer_id
        self.product_type = product_type
        self.publication_ids = publication_ids or []
        self.printer_id = printer_id
        self.date_received = date_received or date.today()
        self.date_completed = date_completed
        self.cancel_reason = cancel_reason
        self.is_completed = is_completed

    @property
    def order_number(self) -> str:
        return self._order_number

    @order_number.setter
    def order_number(self, value: str):
        self._order_number = self.validate_required(value, "Номер замовлення")

    @property
    def customer_id(self) -> str:
        return self._customer_id

    @customer_id.setter
    def customer_id(self, value: str):
        self._customer_id = self.validate_required(value, "ID замовника")

    @property
    def product_type(self) -> str:
        return self._product_type

    @product_type.setter
    def product_type(self, value: str):
        self._product_type = self.validate_required(value, "Вид продукції")

    @property
    def publication_ids(self) -> List[str]:
        return self._publication_ids

    @publication_ids.setter
    def publication_ids(self, value: List[str]):
        if not isinstance(value, list):
            raise ValueError("publication_ids має бути списком")
        self._publication_ids = [str(v) for v in value]

    @property
    def printer_id(self) -> Optional[str]:
        return self._printer_id

    @printer_id.setter
    def printer_id(self, value: Optional[str]):
        if value and not isinstance(value, str):
            raise ValueError("ID друкарні має бути рядком")
        self._printer_id = value

    @property
    def date_received(self) -> date:
        return self._date_received

    @date_received.setter
    def date_received(self, value: Optional[date]):
        if isinstance(value, datetime):
            value = value.date()
        if not isinstance(value, date):
            raise ValueError("date_received має бути об’єктом date")
        self._date_received = value

    @property
    def date_completed(self) -> Optional[date]:
        return self._date_completed

    @date_completed.setter
    def date_completed(self, value: Optional[date]):
        if isinstance(value, datetime):
            value = value.date()
        if value and not isinstance(value, (date, datetime)):
            raise ValueError("date_completed має бути датою або None")
        self._date_completed = value

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    @is_completed.setter
    def is_completed(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("is_completed має бути булевим значенням")
        self._is_completed = value

    def to_dict(self) -> dict:
        def fmt(d):
            return d.isoformat() if isinstance(d, datetime) else None

        return {
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "product_type": self.product_type,
            "publication_ids": self.publication_ids,
            "printer_id": self.printer_id,
            "date_received": self.date_received,
            "date_completed": self.date_completed if self.date_completed else None,
            "is_completed": self.is_completed,
            "cancel_reason": self.cancel_reason,
        }

    @staticmethod
    def from_dict(data: dict) -> "Order":
        def parse_date(val):
            if not val:
                return None
            if isinstance(val, (date, datetime)):
                return val if isinstance(val, date) else val.date()
            return datetime.fromisoformat(val).date()

        return Order(
            order_number=data.get("order_number", ""),
            customer_id=str(data.get("customer_id", "")),
            product_type=data.get("product_type", ""),
            publication_ids=[str(x) for x in data.get("publication_ids", [])],
            printer_id=str(data.get("printer_id")) if data.get("printer_id") else None,
            date_received=parse_date(data.get("date_received")),
            date_completed=parse_date(data.get("date_completed")),
            is_completed=bool(data.get("is_completed", False)),
            cancel_reason=data.get("cancel_reason"),
            _id=str(data.get("_id")) if data.get("_id") else None,
        )

