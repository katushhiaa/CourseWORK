from typing import Optional
import bcrypt
from ..db import db

def _keys():
    return db["keys"]

def get_user(login: str) -> Optional[dict]:
    return _keys().find_one({"login": login})

def check_password(plain: str, user: dict) -> bool:
    ph = user.get("password_hash")
    if not ph:
        return False
    if isinstance(ph, str):
        ph = ph.encode()
    return bcrypt.checkpw(plain.encode(), ph)

def forgot_password(login: str) -> Optional[str]:
    doc = _keys().find_one({"login": login}, {"password_plain": 1})
    return (doc or {}).get("password_plain")

def create_user(login: str, password: str, access_right: str) -> None:
    if _keys().find_one({"login": login}):
        raise ValueError(f"Користувач '{login}' вже існує")

    salt = bcrypt.gensalt()
    _keys().insert_one(
        {
            "login": login,
            "password_hash": bcrypt.hashpw(password.encode(), salt),
            "password_plain": password,
            "access_right": access_right,
        }
    )

def request_access(login: str):
    reqs = db["requests"]
    existing = reqs.find_one({"login": login})
    if existing and existing.get("status") == "pending":
        raise ValueError("Ви вже подали заявку, очікуйте рішення адміністратора.")
    reqs.update_one(
        {"login": login},
        {
            "$set": {
                "login": login,
                "requested_role": "authorized",
                "status": "pending",
            }
        },
        upsert=True,
    )

def get_all_requests():
    return list(db["requests"].find({}))

def approve_request(login: str):
    user = db["keys"].find_one({"login": login})
    if not user:
        raise ValueError("Користувача не знайдено.")
    db["keys"].update_one({"login": login}, {"$set": {"access_right": "authorized"}})
    db["requests"].update_one({"login": login}, {"$set": {"status": "approved"}})

def reject_request(login: str):
    db["requests"].update_one({"login": login}, {"$set": {"status": "rejected"}})