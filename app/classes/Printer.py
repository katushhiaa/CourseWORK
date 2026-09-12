from typing import Optional

from app.classes.Entity import Entity

class Printer(Entity):
    def __init__(
        self,
        name: str,
        address: str,
        phone: str,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.name = name
        self.address = address
        self.phone = phone

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        value = self.validate_required(value, "Назва")
        self._name = self.validate_length(value, "Назва", 3, 100)

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str):
        value = self.validate_required(value, "Адреса")
        self._address = self.validate_length(value, "Адреса", 5, 200)

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        value = self.validate_required(value, "Телефон")
        self._phone = self.validate_phone(value, "Телефон", 7, 15)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
        }

    @staticmethod
    def from_dict(data: dict) -> "Printer":
        return Printer(
            name=data.get("name", ""),
            address=data.get("address", ""),
            phone=data.get("phone", ""),
            _id=str(data.get("_id")) if data.get("_id") else None,
        )
