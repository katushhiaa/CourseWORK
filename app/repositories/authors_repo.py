from typing import List, Optional

from bson import ObjectId

from app.classes.Author import Author
from app.db import db

COL = db["authors"]


def list_authors(filter_text: str = "") -> List[Author]:
    query = {"full_name": {"$regex": filter_text, "$options": "i"}} if filter_text else {}
    docs = COL.find(query).sort("full_name")
    return [Author.from_dict(d) for d in docs]


def get_author_by_id(author_id: str) -> Optional[Author]:
    d = COL.find_one({"_id": ObjectId(author_id)})
    return Author.from_dict(d) if d else None


def create_author(author: Author) -> str:
    res = COL.insert_one(author.to_dict())
    return str(res.inserted_id)


def update_author(_id: str, author: Author) -> int:
    return COL.update_one({"_id": ObjectId(_id)}, {"$set": author.to_dict()}).modified_count


def delete_author(_id: str) -> int:
    return COL.delete_one({"_id": ObjectId(_id)}).deleted_count
