from typing import Optional

from app.classes.Entity import Entity


class Customer(Entity):
    def __init__(
        self,
        type_: str,
        name: str,  # ПІБ (для приватної особи) або назва організації"
        contact_person: str,  # "ПІБ контактної особи (для орг. або за потреби)",
        address: str,
        phone: str,
        fax: str,
        _id: Optional[str] = None,
    ):
        self._id = _id
        self.type = type_
        self.name = name
        self.contact_person = contact_person
        self.address = address
        self.phone = phone
        self.fax = fax

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        if value not in ("individual", "organization"):
            raise ValueError("Тип замовника має бути 'приватна особа' або 'організація'")
        self._type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        value = self.validate_required(value, "Назва/ПІБ")
        self._name = self.validate_length(value, "Назва/ПІБ", 2, 150)

    @property
    def contact_person(self) -> str:
        return self._contact_person

    @contact_person.setter
    def contact_person(self, value: str):
        self._contact_person = self.validate_length(value.strip(), "Контактна особа", 0, 100)

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = self.validate_length(value.strip(), "Адреса", 0, 200)

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        if value.strip():
            self._phone = self.validate_phone(value, "Телефон")
        else:
            self._phone = ""

    @property
    def fax(self) -> str:
        return self._fax

    @fax.setter
    def fax(self, value: str):
        if value.strip():
            self._fax = self.validate_phone(value, "Факс")
        else:
            self._fax = ""

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "contact_person": self.contact_person,
            "address": self.address,
            "phone": self.phone,
            "fax": self.fax,
        }

    @staticmethod
    def from_dict(data: dict) -> "Customer":
        return Customer(
            type_=data.get("type", "individual"),
            name=data.get("name", ""),
            contact_person=data.get("contact_person", ""),
            address=data.get("address", ""),
            phone=data.get("phone", ""),
            fax=data.get("fax", ""),
            _id=str(data.get("_id")) if data.get("_id") else None,
        )
