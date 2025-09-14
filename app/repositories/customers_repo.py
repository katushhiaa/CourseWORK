from typing import List, Dict, Any
from bson import ObjectId
from app.db import db

#замовники
COL = db["customers"]

def list_customers(filter_text: str = "", type_filter: str | None = None) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if filter_text:
        q["$or"] = [
            {"name": {"$regex": filter_text, "$options": "i"}},
            {"contact_person": {"$regex": filter_text, "$options": "i"}},
            {"phone": {"$regex": filter_text, "$options": "i"}},
        ]
    if type_filter in ("individual", "organization"):
        q["type"] = type_filter
    return list(COL.find(q).sort([("type", 1), ("name", 1)]))

def create_customer(doc: Dict[str, Any]) -> str:
    return str(COL.insert_one(doc).inserted_id)

def update_customer(_id: str, patch: Dict[str, Any]) -> int:
    return COL.update_one({"_id": ObjectId(_id)}, {"$set": patch}).modified_count

def delete_customer(_id: str) -> int:
    return COL.delete_one({"_id": ObjectId(_id)}).deleted_count