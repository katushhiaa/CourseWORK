from typing import List, Optional
from app.classes.Entity import Entity

class Publication(Entity):
    def __init__(
        self,
        code: str,
        title: str,
        authors: List[str],
        sheet_volume: float,
        print_run: int,
        order_id: Optional[str] = None,
        _id: Optional[str] = None,
    ):
        self._id = _id
        self.code = code
        self.title = title
        self.authors = authors
        self.sheet_volume = sheet_volume
        self.print_run = print_run
        self.order_id = order_id

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str):
        value = self.validate_required(value, "Код")
        value = self.validate_length(value, "Код", 1, 20)
        value = self.validate_code(value)
        self._code = value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        value = self.validate_required(value, "Назва")
        value = self.validate_length(value, "Назва", 3, 200)
        self._title = value

    @property
    def authors(self) -> List[str]:
        return self._authors

    @authors.setter
    def authors(self, value: List[str]):
        if not isinstance(value, list) or not all(isinstance(a, str) for a in value):
            raise ValueError("Список авторів повинен містити лише рядки")
        self._authors = value

    @property
    def sheet_volume(self) -> float:
        return self._sheet_volume

    @sheet_volume.setter
    def sheet_volume(self, value: float):
        value = self.validate_positive_float(value, "Кількість сторінок")
        self._sheet_volume = float(value)

    @property
    def print_run(self) -> int:
        return self._print_run

    @print_run.setter
    def print_run(self, value: int):
        value = self.validate_positive_int(value, "Тираж видання")
        self._print_run = int(value)

    @property
    def order_id(self) -> Optional[str]:
        return self._order_id

    @order_id.setter
    def order_id(self, value: Optional[str]):
        if value and not isinstance(value, str):
            raise ValueError("ID замовлення має бути рядком")
        self._order_id = value

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "title": self.title,
            "authors": self.authors,
            "sheet_volume": self.sheet_volume,
            "print_run": self.print_run,
            "order_id": self.order_id,
        }

    @staticmethod
    def from_dict(data: dict) -> "Publication":
        return Publication(
            code=data.get("code", ""),
            title=data.get("title", ""),
            authors=[str(a) for a in data.get("authors", [])],
            sheet_volume=float(data.get("sheet_volume", 0)),
            print_run=int(data.get("print_run", 0)),
            order_id=str(data.get("order_id")) if data.get("order_id") else None,
            _id=str(data.get("_id")) if data.get("_id") else None,
        )
