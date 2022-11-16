import db
import re
from pydantic import BaseModel
from fastapi import FastAPI
from typing import Union
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

db = db.get_client()


class Search(BaseModel):
    name: str = None
    state: str = None
    age: str = None
    father: str = None
    voter_id: str = None
    gender: str = None
    house: str = None
    ac: str = None
    pc: str = None


class Generate(BaseModel):
    name: str
    state: str
    age: str
    father: str

    ac: str = None
    pc: str = None
    voter_id: str = None
    gender: str = None


def get_mongo_regex(t):
    return {"$regex": f"^{t}.*", "$options": 'i'}


def get_mongo_regex_case_insensitive(t):
    return {"$regex": f"{t}", "$options": 'i'}


@app.post("/search")
def read_root(body: Search):
    find_q = {}

    if body.name:
        find_q['name'] = get_mongo_regex(body.name)

    if body.state:
        find_q['state'] = get_mongo_regex(body.state)

    if body.age:
        find_q['age'] = body.age

    if body.father:
        find_q['relation'] = {"type": "father",
                              "name": get_mongo_regex(body.state)}
    if body.voter_id:
        find_q['epic_no'] = get_mongo_regex(body.voter_id)

    if body.gender:
        find_q['gender'] = get_mongo_regex_case_insensitive(body.gender)

    if body.state:
        find_q['house'] = get_mongo_regex(body.house)

    if body.ac:
        find_q['ac'] = get_mongo_regex_case_insensitive(body.ac)

    if body.pc:
        find_q['pc'] = get_mongo_regex_case_insensitive(body.pc)

    pipeline = [
        {"$match": find_q},
        {"$set": {"links": {"$concatArrays": [["$relation"], "$links"]}}},
        {"$unwind": {"path": "$links", "preserveNullAndEmptyArrays": False}},
        {"$lookup": {
            "from": "dump_data",
            "localField": "links.id",
            "foreignField": "_id",
            "as": "links.info"
        }},
        {"$unwind": {"path": "$links.info", "preserveNullAndEmptyArrays": False}},
        {"$set": {
            "link": {
                "relation": "$links.type",
                "name": "$links.info.name",
                "voter_id": "$links.info.epic_number",
                "house": "$links.info.house"
            }
        }},
        {
            "$group": {
                "_id": "$_id",
                "name": {"$first": "$name"},
                "relation": {"$first": "self"},
                "voter_id": {"$first": "$epic_number"},
                "house": {"$first": "$house"},
                "links": {"$push": "$link"}
            }
        },
        {"$set": {
            "link_count": {"$size": "$links"}
        }},
        {"$sort": {
            "link_count": -1
        }},
        {"$limit": 50},
        {"$project": {
            "_id": 0
        }}
    ]

    res = db['dump_data'].aggregate(pipeline)
    return list(res)


@app.post("/generate")
def gen(body: Generate):
    di = body.dict(exclude_none=True)
    di['type'] = 'user'
    di['scraped'] = False
    db['scrape_req'].insert_one(di)

    return {
        "status": "added to waitlist"
    }
