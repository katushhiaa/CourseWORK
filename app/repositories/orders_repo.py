from datetime import datetime, date
from typing import List, Optional
from bson import ObjectId
from app.db import db
from app.classes.Order import Order
from app.repositories import publications_repo as PublicationsRepo

COL = db["orders"]

def list_orders(filter_text: str = "") -> List[Order]:
    query = {}
    if filter_text:
        query["$or"] = [
            {"order_number": {"$regex": filter_text, "$options": "i"}},
            {"product_type": {"$regex": filter_text, "$options": "i"}},
        ]
    docs = COL.find(query).sort([("order_number", 1)])
    return [Order.from_dict(d) for d in docs]

def get_order(_id: str) -> Optional[Order]:
    d = COL.find_one({"_id": ObjectId(_id)})
    return Order.from_dict(d) if d else None

def _convert_dates(data: dict) -> dict:
    for key in ("date_received", "date_completed"):
        if isinstance(data.get(key), date) and not isinstance(data[key], datetime):
            data[key] = datetime.combine(data[key], datetime.min.time())
    return data

def create_order(order: Order) -> str:
    data = _convert_dates(order.to_dict())
    res = COL.insert_one(data)
    order_id_str = str(res.inserted_id)
    for pub_id in order.publication_ids:
        PublicationsRepo.update_publication_order(pub_id, order.order_number)

    return order_id_str

def update_order(_id: str, order: Order) -> int:
    patch = _convert_dates(order.to_dict())
    result = COL.update_one({"_id": ObjectId(_id)}, {"$set": patch}).modified_count
    for pub_id in order.publication_ids:
        PublicationsRepo.update_publication_order(pub_id, order.order_number)

    return result

def cancel_order(order_id: str, reason: str):
    order = get_order(order_id)
    if not order:
        return 0
    result = COL.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {
            "cancel_reason": reason,
            "is_completed": False
        }},
    )
    for pub_id in order.publication_ids:
        PublicationsRepo.clear_publication_order(pub_id)

    return result.modified_count

def delete_order(_id: str) -> int:
    order = get_order(_id)
    if order:
        for pub_id in order.publication_ids:
            PublicationsRepo.clear_publication_order(pub_id)

    return COL.delete_one({"_id": ObjectId(_id)}).deleted_count

