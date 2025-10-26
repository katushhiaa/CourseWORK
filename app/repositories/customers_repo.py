from typing import List, Optional

from bson import ObjectId

from app.classes.Customer import Customer
from app.db import db

# замовники
COL = db["customers"]


def list_customers(filter_text: str = "", type_filter: str | None = None) -> List[Customer]:
    query = {}
    if filter_text:
        query["$or"] = [
            {"name": {"$regex": filter_text, "$options": "i"}},
            {"contact_person": {"$regex": filter_text, "$options": "i"}},
            {"phone": {"$regex": filter_text, "$options": "i"}},
        ]
    if type_filter in ("individual", "organization"):
        query["type"] = type_filter
    docs = COL.find(query).sort([("type", 1), ("name", 1)])
    return [Customer.from_dict(d) for d in docs]


def get_customer(_id: str) -> Optional[Customer]:
    d = COL.find_one({"_id": ObjectId(_id)})
    return Customer.from_dict(d) if d else None


def create_customer(customer: Customer) -> str:
    res = COL.insert_one(customer.to_dict())
    return str(res.inserted_id)


def update_customer(_id: str, customer: Customer) -> int:
    return COL.update_one({"_id": ObjectId(_id)}, {"$set": customer.to_dict()}).modified_count


def delete_customer(_id: str) -> int:
    return COL.delete_one({"_id": ObjectId(_id)}).deleted_count
