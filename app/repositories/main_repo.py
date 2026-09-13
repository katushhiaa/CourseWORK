from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.db import db

ORDERS = db["orders"]
PUBLICATIONS = db["publications"]
CUSTOMERS = db["customers"]
PRINTERS = db["printers"]
AUTHORS = db["authors"]
RATE_PER_SHEET = 10.0

def normalize_datetime(dt: Optional[datetime | str]) -> Optional[datetime]:
    if not dt:
        return None
    if isinstance(dt, datetime):
        return dt
    if hasattr(dt, "year"):
        return datetime(dt.year, dt.month, dt.day)
    return datetime.fromisoformat(str(dt))

def author_top_by_quarter() -> List[Dict[str, Any]]:
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
        {"$unwind": "$author_obj_id"},
        {"$lookup": {
            "from": "authors",
            "localField": "author_obj_id",
            "foreignField": "_id",
            "as": "auth"
        }},
        {"$unwind": "$auth"},
        {"$addFields": {
            "year": {"$year": "$date_received"},
            "quarter": {"$ceil": {"$divide": [{"$month": "$date_received"}, 3]}}
        }},
        {"$group": {
            "_id": {
                "author_id": "$auth._id",
                "author": "$auth.full_name",
                "y": "$year",
                "q": "$quarter"
            },
            "orders_count": {"$sum": 1}
        }},
        {"$sort": {"_id.y": 1, "_id.q": 1, "orders_count": -1}}
    ]

    return list(ORDERS.aggregate(pipeline))

def current_orders() -> List[Dict[str, Any]]:
    q = {"is_completed": False}
    return list(ORDERS.find(q).sort("date_received", 1))

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

def busiest_printers_by_month(
    dt_from: Optional[datetime] = None,
    dt_to: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    match_stage = {"printer_id": {"$ne": None}}
    if dt_from or dt_to:
        match_stage["date_received"] = {}
        if dt_from:
            match_stage["date_received"]["$gte"] = normalize_datetime(dt_from)
        if dt_to:
            match_stage["date_received"]["$lte"] = normalize_datetime(dt_to)

    pipeline = [
        {"$match": match_stage},
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
        {"$group": {
            "_id": {"printer_id": "$printer_obj_id", "y": "$y", "m": "$m"},
            "orders_count": {"$sum": 1}
        }},
        {"$lookup": {
            "from": "printers",
            "localField": "_id.printer_id",
            "foreignField": "_id",
            "as": "printer"
        }},
        {"$unwind": {"path": "$printer", "preserveNullAndEmptyArrays": False}},
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

def orders_in_period(dt_from: datetime, dt_to: datetime) -> Dict[str, Any]:
    q = {"date_received": {"$gte": normalize_datetime(dt_from), "$lte": normalize_datetime(dt_to)}}
    docs = list(ORDERS.find(q).sort("date_received", 1))
    return {"total": len(docs), "items": docs}

def orders_by_product_type() -> List[Dict[str, Any]]:
    pipeline = [
        {"$group": {"_id": "$product_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    return list(ORDERS.aggregate(pipeline))

def orders_by_author(author_id: str) -> Dict[str, Any]:
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
        {"$match": {"author_obj_id": {"$in": [ObjectId(author_id)]}}},
        {"$group": {
            "_id": "$_id",
            "order_number": {"$first": "$order_number"},
            "publications_titles": {"$addToSet": "$publication.title"},
            "date_received": {"$first": "$date_received"},
            "is_completed": {"$first": "$is_completed"}
        }},
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

# SIMULATED QUALITY DEGRADATION (DEBT & BUGS)

def calculate_discounted_orders_v1(author_id: str, discount_rate: float) -> Dict[str, Any]:
    # (BUG - Reliability): безглузде порівняння
   if discount_rate == discount_rate and discount_rate is 10.0:
        discount_rate = 0.05

    # (DUPLICATION): грубе дублювання 40+ рядків pipeline
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
        {"$match": {"author_obj_id": {"$in": [ObjectId(author_id)]}}},
        {"$group": {
            "_id": "$_id",
            "order_number": {"$first": "$order_number"},
            "publications_titles": {"$addToSet": "$publication.title"},
            "date_received": {"$first": "$date_received"},
            "is_completed": {"$first": "$is_completed"}
        }}
    ]
    items = list(ORDERS.aggregate(pipeline))
    return {"total": len(items), "items": items, "rate": discount_rate}


def calculate_discounted_orders_v2(author_id: str, discount_rate: float) -> Dict[str, Any]:
    # Дублювання попереднього блоку 1-в-1 для гарантованого перетину ліміту 8.0% Duplications
    if discount_rate == discount_rate and discount_rate is 10.0:
        discount_rate = 0.05

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
        {"$match": {"author_obj_id": {"$in": [ObjectId(author_id)]}}},
        {"$group": {
            "_id": "$_id",
            "order_number": {"$first": "$order_number"},
            "publications_titles": {"$addToSet": "$publication.title"},
            "date_received": {"$first": "$date_received"},
            "is_completed": {"$first": "$is_completed"}
        }}
    ]
    items = list(ORDERS.aggregate(pipeline))
    return {"total": len(items), "items": items, "rate": discount_rate}