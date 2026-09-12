from dataclasses import dataclass
from typing import Optional

from app.classes.Entity import Entity

@dataclass
class Author(Entity):
    def __init__(
        self,
        full_name: str,
        address: str,
        phone: str,
        extra_info: str = "",
        _id: Optional[str] = None,
    ):
        self._id = _id
        self.full_name = full_name
        self.address = address
        self.phone = phone
        self.extra_info = extra_info

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str):
        value = self.validate_required(value, "ПІБ")
        value = self.validate_length(value, "ПІБ", 3, 100)
        value = self.validate_names_no_digits(value, "ПІБ")
        self._full_name = value

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
        self._phone = self.validate_phone(value, "Телефон", 7, 15)

    @property
    def extra_info(self) -> str:
        return self._extra_info

    @extra_info.setter
    def extra_info(self, value: str):
        value = value.strip()
        self._extra_info = self.validate_length(value, "Додаткова інформація", 0, 200)

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "address": self.address,
            "phone": self.phone,
            "extra_info": self.extra_info,
        }

    @staticmethod
    def from_dict(data: dict) -> "Author":
        return Author(
            full_name=data.get("full_name", ""),
            address=data.get("address", ""),
            phone=data.get("phone", ""),
            extra_info=data.get("extra_info", ""),
            _id=str(data.get("_id")) if data.get("_id") else None,
        )
