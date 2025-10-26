from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.db import db

ORDERS = db["orders"]
PUBLICATIONS = db["publications"]
CUSTOMERS = db["customers"]
PRINTERS = db["printers"]
AUTHORS = db["authors"]

def _mk_dt(dt: Optional[datetime | str]) -> Optional[datetime]:
    if not dt:
        return None
    if isinstance(dt, datetime):
        return dt
    if hasattr(dt, "year"):  # якщо це datetime.date
        return datetime(dt.year, dt.month, dt.day)
    return datetime.fromisoformat(str(dt))


# 1) Автори, чиї книги найчастіше друкуються — по кварталах
def author_top_by_quarter() -> List[Dict[str, Any]]:
    pipeline = [
        # 1️⃣ Беремо тільки замовлення, де є публікації
        {"$match": {"publication_ids": {"$exists": True, "$ne": []}}},

        # 2️⃣ Розпаковуємо масив publication_ids
        {"$unwind": "$publication_ids"},

        # 3️⃣ Конвертуємо рядкові ObjectId у справжні ObjectId
        {"$addFields": {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$publication_ids"}, "string"]},
                    "then": {"$toObjectId": "$publication_ids"},
                    "else": "$publication_ids"
                }
            }
        }},

        # 4️⃣ Підтягнемо самі публікації
        {"$lookup": {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {"$unwind": "$publication"},

        # 5️⃣ Конвертуємо publication.authors у ObjectId (бо це масив рядків)
        {"$addFields": {
            "author_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$publication.authors"}, "array"]},
                    "then": {
                        "$map": {
                            "input": "$publication.authors",
                            "as": "aid",
                            "in": {
                                "$cond": {
                                    "if": {"$eq": [{"$type": "$$aid"}, "string"]},
                                    "then": {"$toObjectId": "$$aid"},
                                    "else": "$$aid"
                                }
                            }
                        }
                    },
                    "else": []
                }
            }
        }},

        # 6️⃣ Розпаковуємо авторів
        {"$unwind": "$author_obj_id"},

        # 7️⃣ Підтягуємо дані про автора
        {"$lookup": {
            "from": "authors",
            "localField": "author_obj_id",
            "foreignField": "_id",
            "as": "auth"
        }},
        {"$unwind": "$auth"},

        # 8️⃣ Додаємо рік і квартал
        {"$addFields": {
            "year": {"$year": "$date_received"},
            "quarter": {"$ceil": {"$divide": [{"$month": "$date_received"}, 3]}}
        }},

        # 9️⃣ Групуємо: по автору, року, кварталу
        {"$group": {
            "_id": {
                "author_id": "$auth._id",
                "author": "$auth.full_name",
                "y": "$year",
                "q": "$quarter"
            },
            "orders_count": {"$sum": 1}
        }},

        # 🔟 Сортуємо по часу і кількості
        {"$sort": {"_id.y": 1, "_id.q": 1, "orders_count": -1}}
    ]

    return list(ORDERS.aggregate(pipeline))




# 2) Поточні замовлення (в роботі)
def current_orders() -> List[Dict[str, Any]]:
    q = {"is_completed": False}
    return list(ORDERS.find(q).sort("date_received", 1))


# 3) Загальний обсяг у друк. аркушах за квартали
def total_sheet_volume_by_quarter() -> List[Dict[str, Any]]:
    pipeline = [
        {"$match": {"publication_ids": {"$exists": True, "$ne": []}}},
        {"$unwind": "$publication_ids"},
        {"$addFields": {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$publication_ids"}, "string"]},
                    "then": {"$toObjectId": "$publication_ids"},
                    "else": "$publication_ids"
                }
            }
        }},
        {"$lookup": {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {"$unwind": "$publication"},
        {"$addFields": {
            "year": {"$year": "$date_received"},
            "quarter": {"$ceil": {"$divide": [{"$month": "$date_received"}, 3]}},
            "volume": {
                "$multiply": [
                    "$publication.sheet_volume",
                    "$publication.print_run"
                ]
            }
        }},
        {"$group": {
            "_id": {"y": "$year", "q": "$quarter"},
            "total_volume": {"$sum": "$volume"},
            "orders": {"$addToSet": "$order_number"}
        }},
        {"$sort": {"_id.y": 1, "_id.q": 1}}
    ]
    return list(ORDERS.aggregate(pipeline))


# 4) Найбільш завантажені друкарні по місяцях
def busiest_printers_by_month(
    dt_from: Optional[datetime] = None,
    dt_to: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    match_stage = {"printer_id": {"$ne": None}}
    if dt_from or dt_to:
        match_stage["date_received"] = {}
        if dt_from:
            match_stage["date_received"]["$gte"] = _mk_dt(dt_from)
        if dt_to:
            match_stage["date_received"]["$lte"] = _mk_dt(dt_to)

    pipeline = [
        {"$match": match_stage},

        # 1️⃣ Конвертуємо printer_id з рядка в ObjectId
        {"$addFields": {
            "printer_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$printer_id"}, "string"]},
                    "then": {"$toObjectId": "$printer_id"},
                    "else": "$printer_id"
                }
            },
            "y": {"$year": "$date_received"},
            "m": {"$month": "$date_received"}
        }},

        # 2️⃣ Групуємо по друкарні, році, місяцю
        {"$group": {
            "_id": {"printer_id": "$printer_obj_id", "y": "$y", "m": "$m"},
            "orders_count": {"$sum": 1}
        }},

        # 3️⃣ Підтягуємо дані друкарні
        {"$lookup": {
            "from": "printers",
            "localField": "_id.printer_id",
            "foreignField": "_id",
            "as": "printer"
        }},
        {"$unwind": {"path": "$printer", "preserveNullAndEmptyArrays": False}},

        # 4️⃣ Формуємо фінальний вигляд
        {"$project": {
            "printer": "$printer.name",
            "year": "$_id.y",
            "month": "$_id.m",
            "orders_count": 1,
            "_id": 0
        }},
        {"$sort": {"year": 1, "month": 1, "orders_count": -1}}
    ]

    return list(ORDERS.aggregate(pipeline))


# 5) Замовлення за період
def orders_in_period(dt_from: datetime, dt_to: datetime) -> Dict[str, Any]:
    q = {"date_received": {"$gte": _mk_dt(dt_from), "$lte": _mk_dt(dt_to)}}
    docs = list(ORDERS.find(q).sort("date_received", 1))
    return {"total": len(docs), "items": docs}


# 6) Замовлення за видами продукції
def orders_by_product_type() -> List[Dict[str, Any]]:
    pipeline = [
        {"$group": {"_id": "$product_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return list(ORDERS.aggregate(pipeline))


# 7) Замовлення за участю певного автора
def orders_by_author(author_id: str) -> Dict[str, Any]:
    pipeline = [
        # 1️⃣ Беремо тільки ті, де є публікації
        {"$match": {"publication_ids": {"$exists": True, "$ne": []}}},
        {"$unwind": "$publication_ids"},

        # 2️⃣ Конвертуємо publication_ids у ObjectId
        {"$addFields": {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$publication_ids"}, "string"]},
                    "then": {"$toObjectId": "$publication_ids"},
                    "else": "$publication_ids"
                }
            }
        }},

        # 3️⃣ Підтягуємо публікації
        {"$lookup": {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {"$unwind": "$publication"},

        # 4️⃣ Конвертуємо authors у ObjectId (бо це масив рядків)
        {"$addFields": {
            "author_obj_id": {
                "$map": {
                    "input": "$publication.authors",
                    "as": "aid",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$type": "$$aid"}, "string"]},
                            "then": {"$toObjectId": "$$aid"},
                            "else": "$$aid"
                        }
                    }
                }
            }
        }},

        # 5️⃣ Фільтруємо тільки ті публікації, де є наш автор
        {"$match": {"author_obj_id": {"$in": [ObjectId(author_id)]}}},

        # 6️⃣ Групуємо по замовленню, збираємо всі назви видань
        {"$group": {
            "_id": "$_id",
            "order_number": {"$first": "$order_number"},
            "publications_titles": {"$addToSet": "$publication.title"},
            "date_received": {"$first": "$date_received"},
            "is_completed": {"$first": "$is_completed"}
        }},

        # 7️⃣ Форматуємо в зручний вигляд
        {"$project": {
            "_id": 1,
            "order_number": 1,
            "publications_titles": 1,
            "date_received": 1,
            "is_completed": 1
        }},
        {"$sort": {"date_received": -1}}
    ]

    items = list(ORDERS.aggregate(pipeline))
    return {"total": len(items), "items": items}



# 8) Скасовані замовлення
def canceled_orders_breakdown() -> Dict[str, Any]:
    reasons = ["неоплата", "відміна замовником"]
    pipeline = [
        {"$match": {"cancel_reason": {"$in": reasons}}},
        {"$group": {"_id": "$cancel_reason", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    totals = list(ORDERS.aggregate(pipeline))
    items = list(ORDERS.find({"cancel_reason": {"$in": reasons}}))
    return {"breakdown": totals, "items": items}


# 9) Кількість замовлень від приватних осіб та організацій
def orders_by_customer_type() -> List[Dict[str, Any]]:
    pipeline = [
        {
            "$addFields": {
                "cust_obj_id": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$customer_id"}, "string"]},
                        "then": {"$toObjectId": "$customer_id"},
                        "else": "$customer_id"
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "customers",
                "localField": "cust_obj_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {"$unwind": "$customer"},
        {"$group": {"_id": "$customer.type", "count": {"$sum": 1}}},
        {"$project": {"type": "$_id", "count": 1, "_id": 0}},
        {"$sort": {"count": -1}}
    ]

    return list(ORDERS.aggregate(pipeline))


# 10) Прибуток за місяць
RATE_PER_SHEET = 10.0

def profit_by_month(year: int, month: int) -> Dict[str, Any]:
    pipeline = [
        {"$match": {
            "date_received": {
                "$gte": datetime(year, month, 1),
                "$lt": datetime(year + (month // 12), (month % 12) + 1, 1)
            },
            "publication_ids": {"$exists": True, "$ne": []}
        }},
        {"$unwind": "$publication_ids"},
        {"$addFields": {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$publication_ids"}, "string"]},
                    "then": {"$toObjectId": "$publication_ids"},
                    "else": "$publication_ids"
                }
            }
        }},
        {"$lookup": {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {"$unwind": "$publication"},
        {"$addFields": {"money": {
            "$multiply": [
                {"$multiply": ["$publication.sheet_volume", "$publication.print_run"]},
                RATE_PER_SHEET
            ]
        }}},
        {"$group": {"_id": None, "profit": {"$sum": "$money"}, "orders": {"$addToSet": "$order_number"}}}
    ]
    res = list(ORDERS.aggregate(pipeline))
    return res[0] if res else {"profit": 0.0, "orders": []}
