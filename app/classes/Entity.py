import re

class Entity:
    @staticmethod
    def trim(value: str | None) -> str:
        return (value or "").strip()

    @staticmethod
    def validate_required(value: str, field_name: str) -> str:
        v = Entity.trim(value)
        if not v:
            raise ValueError(f"{field_name} не може бути порожнім")
        return v

    @staticmethod
    def validate_length(value: str, field_name: str, min_len: int = 1, max_len: int = 255) -> str:
        v = Entity.trim(value)
        if not (min_len <= len(v) <= max_len):
            raise ValueError(f"{field_name} має містити від {min_len} до {max_len} символів")
        return v

    @staticmethod
    def validate_code(value: str, field_name: str = "Код") -> str:
        v = Entity.trim(value)
        if not re.fullmatch(r"[A-Za-z0-9\-]+", v):
            raise ValueError(f"{field_name} може містити лише латинські літери, цифри та '-'")
        return v

    @staticmethod
    def validate_positive_float(value: float | str, field_name: str) -> float:
        try:
            f = float(value)
        except Exception:
            raise ValueError(f"{field_name} має бути числом")
        if f <= 0:
            raise ValueError(f"{field_name} має бути додатнім числом")
        return f

    @staticmethod
    def validate_positive_int(value: int | str, field_name: str) -> int:
        try:
            i = int(value)
        except Exception:
            raise ValueError(f"{field_name} має бути цілим числом")
        if i <= 0:
            raise ValueError(f"{field_name} має бути додатним цілим числом")
        return i

    @staticmethod
    def validate_names_no_digits(value: str, field_name: str) -> str:
        v = Entity.validate_required(value, field_name)
        v = Entity.validate_length(v, field_name, 3, 100)
        if any(ch.isdigit() for ch in v):
            raise ValueError(f"{field_name} не повинен містити цифри")
        return v

    @staticmethod
    def validate_phone(
        value: str, field_name: str = "Телефон", min_len: int = 7, max_len: int = 15
    ) -> str:
        if not value:
            raise ValueError(f"{field_name} не може бути порожнім")
        cleaned = re.sub(r"[^\d]", "", value)
        if not (min_len <= len(cleaned) <= max_len):
            raise ValueError(f"{field_name} має містити від {min_len} до {max_len} цифр")

        return cleaned

    @staticmethod
    def validate_password_strength(password: str, field_name: str = "Пароль") -> str:
        v = Entity.trim(password)
        if len(v) < 8:
            raise ValueError(f"{field_name} має містити щонайменше 8 символів")
        if not re.search(r"[A-ZА-Я]", v):
            raise ValueError(f"{field_name} має містити принаймні одну велику літеру")
        if not re.search(r"[a-zа-я]", v):
            raise ValueError(f"{field_name} має містити принаймні одну малу літеру")
        if not re.search(r"\d", v):
            raise ValueError(f"{field_name} має містити принаймні одну цифру")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError(f"{field_name} має містити принаймні один спеціальний символ")
        return v
