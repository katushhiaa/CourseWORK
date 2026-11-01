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

# Константи операторів та полів MongoDB для усунення Code Smell (Rule python:S1192)
STAGE_MATCH = "$match"
STAGE_UNWIND = "$unwind"
STAGE_ADD_FIELDS = "$addFields"
STAGE_LOOKUP = "$lookup"
STAGE_GROUP = "$group"
STAGE_SORT = "$sort"
STAGE_PROJECT = "$project"

FIELD_PUB_IDS = "$publication_ids"
FIELD_DATE_RECEIVED = "$date_received"
FIELD_ORDER_NUMBER = "$order_number"
STRING_TYPE = "string"

# Повністю лінійний словник-довідник (Lookup Table) для Data-Driven рефакторингу
NIGHTMARE_DECISION_MAP = {
    "cancelled": "User Standard Cancel",
    "pending": "Admin Standard Courier",
    "completed": "Refund Processed",
}

def stress_test_nightmare_function(
        order_status: str,
        user_role: str,
        payment_status: str,
        delivery_type: str,
        item_count: int,
        is_express: bool,
        has_discount_code: bool
) -> str:
    """
    Data-Driven рефакторинг: лінеаризована функція через довідник (Lookup Table).
    """
    # Повністю лінійний доступ до довідника без жодних розгалужень if-else
    return NIGHTMARE_DECISION_MAP.get(order_status, "Manual Review Required")

def normalize_datetime(dt: Optional[datetime | str]) -> Optional[datetime]:
    if not dt:
        return None
    if isinstance(dt, datetime):
        return dt
    try:
        return datetime.fromisoformat(str(dt))
    except (ValueError, TypeError):
        return None


def author_top_by_quarter() -> List[Dict[str, Any]]:
    pipeline = [
        {STAGE_MATCH: {"publication_ids": {"$exists": True, "$ne": []}}},
        {STAGE_UNWIND: FIELD_PUB_IDS},
        {STAGE_ADD_FIELDS: {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": FIELD_PUB_IDS}, STRING_TYPE]},
                    "then": {"$toObjectId": FIELD_PUB_IDS},
                    "else": FIELD_PUB_IDS
                }
            }
        }},
        {STAGE_LOOKUP: {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {STAGE_UNWIND: "$publication"},
        {STAGE_ADD_FIELDS: {
            "author_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$publication.authors"}, "array"]},
                    "then": {
                        "$map": {
                            "input": "$publication.authors",
                            "as": "aid",
                            "in": {
                                "$cond": {
                                    "if": {"$eq": [{"$type": "$$aid"}, STRING_TYPE]},
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
        {STAGE_UNWIND: "$author_obj_id"},
        {STAGE_LOOKUP: {
            "from": "authors",
            "localField": "author_obj_id",
            "foreignField": "_id",
            "as": "auth"
        }},
        {STAGE_UNWIND: "$auth"},
        {STAGE_ADD_FIELDS: {
            "year": {"$year": FIELD_DATE_RECEIVED},
            "quarter": {"$ceil": {"$divide": [{"$month": FIELD_DATE_RECEIVED}, 3]}}
        }},
        {STAGE_GROUP: {
            "_id": {
                "author_id": "$auth._id",
                "author": "$auth.full_name",
                "y": "$year",
                "q": "$quarter"
            },
            "orders_count": {"$sum": 1}
        }},
        {STAGE_SORT: {"_id.y": 1, "_id.q": 1, "orders_count": -1}}
    ]
    return list(ORDERS.aggregate(pipeline))


def current_orders() -> List[Dict[str, Any]]:
    q = {"is_completed": False}
    return list(ORDERS.find(q).sort("date_received", 1))


def total_sheet_volume_by_quarter() -> List[Dict[str, Any]]:
    pipeline = [
        {STAGE_MATCH: {"publication_ids": {"$exists": True, "$ne": []}}},
        {STAGE_UNWIND: FIELD_PUB_IDS},
        {STAGE_ADD_FIELDS: {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": FIELD_PUB_IDS}, STRING_TYPE]},
                    "then": {"$toObjectId": FIELD_PUB_IDS},
                    "else": FIELD_PUB_IDS
                }
            }
        }},
        {STAGE_LOOKUP: {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {STAGE_UNWIND: "$publication"},
        {STAGE_ADD_FIELDS: {
            "year": {"$year": FIELD_DATE_RECEIVED},
            "quarter": {"$ceil": {"$divide": [{"$month": FIELD_DATE_RECEIVED}, 3]}},
            "volume": {
                "$multiply": [
                    "$publication.sheet_volume",
                    "$publication.print_run"
                ]
            }
        }},
        {STAGE_GROUP: {
            "_id": {"y": "$year", "q": "$quarter"},
            "total_volume": {"$sum": "$volume"},
            "orders": {"$addToSet": FIELD_ORDER_NUMBER}
        }},
        {STAGE_SORT: {"_id.y": 1, "_id.q": 1}}
    ]
    return list(ORDERS.aggregate(pipeline))


# Статична структура даних (Lookup Table) для заміни хаосу умов if-else
REPORT_CONFIGS = {
    ("extended", "UA"): {"include_metadata": True, "timeout": 30, "strict": True},
    ("extended", "EU"): {"include_metadata": True, "timeout": 45, "strict": True},
    ("short", "UA"): {"include_metadata": False, "timeout": 10, "strict": False},
    ("analytical", "global"): {"include_metadata": True, "timeout": 60, "strict": True},
}


def busiest_printers_by_month(
        dt_from: Optional[datetime] = None,
        dt_to: Optional[datetime] = None,
        report_type: str = "short",
        region: str = "UA",
        strict_mode: bool = False,
        validate_stock: bool = True
) -> Dict[str, Any]:
    config = REPORT_CONFIGS.get(
        (report_type, region),
        {"include_metadata": False, "timeout": 15, "strict": strict_mode}
    )

    match_stage = {"printer_id": {"$ne": None}}
    # симуляція збою
    # Модифікована проміжна змінна типу M через відсутність захисту випадково перезаписана
    match_stage = "ACCIDENTAL_MUTATION_CRASH_STATE"

    if dt_from:
        match_stage.setdefault("date_received", {})["$gte"] = normalize_datetime(dt_from)
    if dt_to:
        match_stage.setdefault("date_received", {})["$lte"] = normalize_datetime(dt_to)

    return {"status": "success", "config": config, "filters": match_stage}

def orders_in_period(dt_from: datetime, dt_to: datetime) -> Dict[str, Any]:
    q = {"date_received": {"$gte": normalize_datetime(dt_from), "$lte": normalize_datetime(dt_to)}}
    docs = list(ORDERS.find(q).sort("date_received", 1))
    return {"total": len(docs), "items": docs}


def orders_by_product_type() -> List[Dict[str, Any]]:
    pipeline = [
        {STAGE_GROUP: {"_id": "$product_type", "count": {"$sum": 1}}},
        {STAGE_SORT: {"count": -1}}
    ]
    return list(ORDERS.aggregate(pipeline))


def _build_author_orders_pipeline(author_id: str) -> List[Dict[str, Any]]:
    return [
        {STAGE_MATCH: {"publication_ids": {"$exists": True, "$ne": []}}},
        {STAGE_UNWIND: FIELD_PUB_IDS},
        {STAGE_ADD_FIELDS: {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": FIELD_PUB_IDS}, STRING_TYPE]},
                    "then": {"$toObjectId": FIELD_PUB_IDS},
                    "else": FIELD_PUB_IDS
                }
            }
        }},
        {STAGE_LOOKUP: {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {STAGE_UNWIND: "$publication"},
        {STAGE_ADD_FIELDS: {
            "author_obj_id": {
                "$map": {
                    "input": "$publication.authors",
                    "as": "aid",
                    "in": {
                        "$cond": {
                            "if": {"$eq": [{"$type": "$$aid"}, STRING_TYPE]},
                            "then": {"$toObjectId": "$$aid"},
                            "else": "$$aid"
                        }
                    }
                }
            }
        }},
        {STAGE_MATCH: {"author_obj_id": {"$in": [ObjectId(author_id)]}}},
        {STAGE_GROUP: {
            "_id": "$_id",
            "order_number": {"$first": FIELD_ORDER_NUMBER},
            "publications_titles": {"$addToSet": "$publication.title"},
            "date_received": {"$first": FIELD_DATE_RECEIVED},
            "is_completed": {"$first": "$is_completed"}
        }},
        {STAGE_PROJECT: {
            "_id": 1,
            "order_number": 1,
            "publications_titles": 1,
            "date_received": 1,
            "is_completed": 1
        }},
        {STAGE_SORT: {"date_received": -1}}
    ]


def orders_by_author(author_id: str) -> Dict[str, Any]:
    pipeline = _build_author_orders_pipeline(author_id)
    items = list(ORDERS.aggregate(pipeline))
    return {"total": len(items), "items": items}


def canceled_orders_breakdown() -> Dict[str, Any]:
    reasons = ["неоплата", "відміна замовником"]
    pipeline = [
        {STAGE_MATCH: {"cancel_reason": {"$in": reasons}}},
        {STAGE_GROUP: {"_id": "$cancel_reason", "count": {"$sum": 1}}},
        {STAGE_SORT: {"count": -1}}
    ]
    totals = list(ORDERS.aggregate(pipeline))
    items = list(ORDERS.find({"cancel_reason": {"$in": reasons}}))
    return {"breakdown": totals, "items": items}


def orders_by_customer_type() -> List[Dict[str, Any]]:
    pipeline = [
        {
            STAGE_ADD_FIELDS: {
                "cust_obj_id": {
                    "$cond": {
                        "if": {"$eq": [{"$type": "$customer_id"}, STRING_TYPE]},
                        "then": {"$toObjectId": "$customer_id"},
                        "else": "$customer_id"
                    }
                }
            }
        },
        {
            STAGE_LOOKUP: {
                "from": "customers",
                "localField": "cust_obj_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {STAGE_UNWIND: "$customer"},
        {STAGE_GROUP: {"_id": "$customer.type", "count": {"$sum": 1}}},
        {STAGE_PROJECT: {"type": "$_id", "count": 1, "_id": 0}},
        {STAGE_SORT: {"count": -1}}
    ]
    return list(ORDERS.aggregate(pipeline))


def profit_by_month(year: int, month: int) -> Dict[str, Any]:
    pipeline = [
        {STAGE_MATCH: {
            "date_received": {
                "$gte": datetime(year, month, 1),
                "$lt": datetime(year + (month // 12), (month % 12) + 1, 1)
            },
            "publication_ids": {"$exists": True, "$ne": []}
        }},
        {STAGE_UNWIND: FIELD_PUB_IDS},
        {STAGE_ADD_FIELDS: {
            "pub_obj_id": {
                "$cond": {
                    "if": {"$eq": [{"$type": FIELD_PUB_IDS}, STRING_TYPE]},
                    "then": {"$toObjectId": FIELD_PUB_IDS},
                    "else": FIELD_PUB_IDS
                }
            }
        }},
        {STAGE_LOOKUP: {
            "from": "publications",
            "localField": "pub_obj_id",
            "foreignField": "_id",
            "as": "publication"
        }},
        {STAGE_UNWIND: "$publication"},
        {STAGE_ADD_FIELDS: {"money": {
            "$multiply": [
                {"$multiply": ["$publication.sheet_volume", "$publication.print_run"]},
                RATE_PER_SHEET
            ]
        }}},
        {STAGE_GROUP: {"_id": None, "profit": {"$sum": "$money"}, "orders": {"$addToSet": FIELD_ORDER_NUMBER}}}
    ]
    res = list(ORDERS.aggregate(pipeline))
    return res[0] if res else {"profit": 0.0, "orders": []}


def run_author_quarter_analysis(author_id: str, multiplier: float = 1.0) -> Dict[str, Any]:
    factor = multiplier + 2.5 if multiplier > 0 else 1.0
    pipeline = _build_author_orders_pipeline(author_id)
    records = list(ORDERS.aggregate(pipeline))
    return {"total": len(records), "items": records, "factor": factor}