
from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from datetime import datetime
import datetime as dt
from json import dumps

from cashman.model.transaction_group import TransactionGroup, TransactionGroupSchema

class GroupController:

    def __init__(self, db):
        print("GroupController")
        self.db = db
    
    def dashboard_page(self):
        data = self.get_all_groups()
        dashboard = self.get_dashboard()

        for group in data:
            isExist = False
            for d in dashboard:
                if group.get("name") == d.get("group"):
                    isExist = True
            if not isExist:
                dashboard.append(
                    {
                        "_id": group["_id"],
                        "group": group["name"],
                        "count": 0,
                        "description": group["description"],
                    }
                )

        return render_template("dashboard.html", title="cashman", dashboard=dashboard)

    def add_txn_group(self):
        body = request.get_json()
        print("POST /group with body {}".format(jsonify(body)))
        name = body["name"]

        if not name:
            print("Please specify a name")
            errResp = {"error": "Please specify a name"}
            return jsonify(errResp), 400

        groupObj = TransactionGroupSchema().load(body)

        groupDbData = {
            "name": groupObj.name,
            "description": groupObj.description,
            "is_default": groupObj.is_default,
            "created": groupObj.created,
            "status": "Active",
        }
        self.db.transactions_group.insert(groupDbData)
        return "", 204

    def get_groups():
        data = get_all_groups()
        return jsonify(data)

    def get_all_groups(self):
        data = []
        docs = self.db.transactions_group.find({"status": "Active"})
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return data
    
    def get_dashboard(self):
        pipeline = [
            {
                "$lookup": {
                    "let": {"groupObjId": {"$toObjectId": "$group_id"}},
                    "from": "transactions_group",
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$_id", "$$groupObjId"]},
                                        {"$eq": ["$status", "Active"]},
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "group",
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": [{"$arrayElemAt": ["$group", 0]}, "$$ROOT"]
                    }
                }
            },
            {"$match": {"status": "Active"}},
            {"$project": {"group": 0, "status": 0, "created": 0}},
            {
                "$group": {
                    "_id": "$group_id",
                    "group": {"$first": "$name"},
                    "count": {"$sum": 1},
                }
            },
        ]
        return self.agg_query("transactions", pipeline)

    def agg_query(self, base_coll, pipeline):
        cursor = self.db[base_coll].aggregate(pipeline)
        result = list(cursor)
        return result