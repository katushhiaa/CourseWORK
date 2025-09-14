from typing import List, Dict, Any

from bson import ObjectId
from app.db import db

COL = db['authors']

def list_authors(filter_text: str = "") -> List[Dict[str, Any]]:
    query = {"full_name": {"$regex": filter_text, "$options": "i"}} if filter_text else {}
    return list(COL.find(query).sort("full_name"))

def create_author(full_name: str, address: str, phone: str, extra_info: str = "") ->str:
    res = COL.insert_one({
        "full_name": full_name,
        "address": address,
        "phone": phone,
        "extra_info": extra_info,
    })
    return str(res.inserted_id)

def update_author(_id: str, full_name: str, address: str, phone: str, extra_info: str = "") ->int:
    return COL.update_one({
        "_id": ObjectId(_id)},
        {"$set": {
            "full_name": full_name,
            "address": address,
            "phone": phone,
            "extra_info": extra_info,
        }}).modified_count

def delete_author(_id: str) -> int:
    return COL.delete_one({
        "_id": ObjectId(_id)
    }).deleted_count