from typing import List, Optional

from bson import ObjectId

from app.classes.Publication import Publication
from app.db import db

COL = db["publications"]


def list_publications(filter_text: str = "") -> List[Publication]:
    query = {}
    if filter_text:
        query["$or"] = [
            {"title": {"$regex": filter_text, "$options": "i"}},
            {"code": {"$regex": filter_text, "$options": "i"}},
        ]
    docs = COL.find(query).sort([("code", 1), ("title", 1)])
    return [Publication.from_dict(d) for d in docs]


def get_publication(_id: str) -> Optional[Publication]:
    d = COL.find_one({"_id": ObjectId(_id)})
    return Publication.from_dict(d) if d else None


def create_publication(publication: Publication) -> str:
    res = COL.insert_one(publication.to_dict())
    return str(res.inserted_id)


def update_publication(_id: str, publication: Publication) -> int:
    return COL.update_one({"_id": ObjectId(_id)}, {"$set": publication.to_dict()}).modified_count


def delete_publication(_id: str) -> int:
    return COL.delete_one({"_id": ObjectId(_id)}).deleted_count


def update_publication_order(pub_id: str, order_number: str) -> None:
    """Прив’язує видання до замовлення"""
    COL.update_one({"_id": ObjectId(pub_id)}, {"$set": {"order_id": order_number}})


def clear_publication_order(pub_id: str) -> None:
    """Видаляє зв’язок видання із замовленням"""
    COL.update_one({"_id": ObjectId(pub_id)}, {"$unset": {"order_id": ""}})
