from typing import List, Optional
from bson import ObjectId
from app.classes.Printer import Printer
from app.db import db

COL = db["printers"]

def list_printers(filter_text: str = "") -> List[Printer]:
    query = {}
    if filter_text:
        query["$or"] = [
            {"name": {"$regex": filter_text, "$options": "i"}},
            {"address": {"$regex": filter_text, "$options": "i"}},
            {"phone": {"$regex": filter_text, "$options": "i"}},
        ]
    docs = COL.find(query).sort([("name", 1)])
    return [Printer.from_dict(d) for d in docs]

def get_printer(_id: str) -> Optional[Printer]:
    d = COL.find_one({"_id": ObjectId(_id)})
    return Printer.from_dict(d) if d else None

def create_printer(printer: Printer) -> str:
    res = COL.insert_one(printer.to_dict())
    return str(res.inserted_id)

def update_printer(_id: str, printer: Printer) -> int:
    return COL.update_one({"_id": ObjectId(_id)}, {"$set": printer.to_dict()}).modified_count

def delete_printer(_id: str) -> int:
    return COL.delete_one({"_id": ObjectId(_id)}).deleted_count
