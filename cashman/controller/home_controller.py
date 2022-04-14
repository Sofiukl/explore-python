from flask import Flask, jsonify, request, render_template, send_file, after_this_request
from pymongo import MongoClient
from datetime import datetime
from json import dumps
from bson.objectid import ObjectId
import os
import datetime as dt
import calendar

from cashman.model.income import Income, IncomeSchema
from cashman.model.expence import Expence, ExpenceSchema
from cashman.model.transaction_type import TransactionType
from cashman.report import pdf_report_gen

UPLOAD_DIRECTORY = "temp_upload"


class HomeController:

    def __init__(self, db):
        self.db = db

    def home_page(self, group_id, group_name):
        data = []
        docs = self.db.transactions.find({"status": "Active", "group_id": group_id})
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            data.append(doc)

        # prep chart data
        now = datetime.now()
        month_view = self.prep_month_view(group_id, now)
        day_view = self.prep_day_view(group_id, now)

        result = self.get_statictics(group_id)
        statictic = result[0] if len(result) != 0 else {}
        return render_template(
            "home.html",
            title="cashman",
            data=data,
            statictic=statictic,
            group_name=group_name,
            group_id=group_id,
            xValues=month_view["xValues"],
            incomeValues=month_view["incomeValues"],
            expenceValues=month_view["expenceValues"],
            netValues=month_view["netValues"],
            day_view_x_values=day_view["day_view_x_values"],
            day_view_income_values=day_view["day_view_income_values"],
            day_view_expence_values=day_view["day_view_expence_values"],
            day_view_net_values=day_view["day_view_net_values"],
        )


    def gen_pdf(self, group_id, group_name):
        pdf_data = []
        pdf_data.append(['Title', 'Amount'])

        docs = self.db.transactions.find({"status": "Active", "group_id": group_id})
        for doc in docs:
            row = []
            if doc["type"] == "INCOME":
                amount = "+ " + str(doc["amount"])
            else:
                amount = "- " + str(doc["amount"])
            row.append(doc["title"])
            row.append(amount)
            pdf_data.append(row)
    
        filename = "txn_report_" + str(datetime.now().timestamp()) + ".pdf"
        filePath = os.path.join("cashman", UPLOAD_DIRECTORY, filename)
        pdf_report_gen.PdfReportGenerator(filePath).generate(pdf_data)

        @after_this_request
        def remove_file(response):
            try:
                os.remove(filePath)
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response
        return send_file(os.path.join(UPLOAD_DIRECTORY, filename), as_attachment=True)


    def get_txn(self):
        txn_type = request.args.get("type")
        if (
            txn_type != TransactionType.INCOME.value
            or txn_type != TransactionType.EXPENCE.value
        ):
            print("Please specify a valid transaction type")
            errResp = {"error": "Please specify a valid transaction type"}
            return jsonify(errResp), 400

        data = []
        docs = self.db.transactions.find({"type": txn_type, "status": "Active"})
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return jsonify(data)

    def del_txn(self, id):
        id = request.view_args["id"]
        print("Transaction delete request received for id {}".format(id))
        q = {"_id": ObjectId(id)}
        u = {"$set": {"status": "Inactive"}}
        self.update_txn(q, u)
        return "", 204

    def add_txn(self):
        body = request.get_json()
        print("POST /transactions with body {}".format(jsonify(body)))
        txn_type = body["type"]
        description = body["description"]

        if not description:
            print("Please specify a description")
            errResp = {"error": "Please specify a description"}
            return jsonify(errResp), 400

        if (
            txn_type != TransactionType.INCOME.value
            and txn_type != TransactionType.EXPENCE.value
        ):
            print("Please specify a valid transaction type")
            errResp = {"error": "Please specify a valid transaction type"}
            return jsonify(errResp), 400

        body.pop("type", None)
        txnObj = ""

        if txn_type == TransactionType.INCOME.value:
            txnObj = IncomeSchema().load(body)
        if txn_type == TransactionType.EXPENCE.value:
            txnObj = ExpenceSchema().load(body)

        args = txnObj.txn_date.timetuple()[:6]

        txnDbData = {
            "group_id": txnObj.group_id,
            "title": txnObj.title,
            "amount": txnObj.amount,
            "txn_date": datetime(*args),
            "type": txnObj.type,
            "category": txnObj.category,
            "brand": txnObj.brand,
            "description": txnObj.description,
            "tags": txnObj.tags,
            "created": txnObj.created,
            "status": "Active",
        }
        self.db.transactions.insert(txnDbData)
        return "", 204

    def get_statictics(self, group_id, first_day="", last_day=""):
        pipeline = []
        if first_day and last_day:
            date_filter = {"$match": {"txn_date": {"$gte": first_day, "$lte": last_day}}}
            pipeline.append(date_filter)
        elif first_day and not last_day:
            date_filter = {"$match": {"txn_date": {"$eq": first_day}}}
            pipeline.append(date_filter)

        pipeline += [
            {
                "$project": {
                    "_id": 0,
                    "ExpenceSentiment": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$type", "EXPENCE"]},
                                    {"$eq": ["$status", "Active"]},
                                    {"$eq": ["$group_id", group_id]},
                                ]
                            },
                            "$amount",
                            0,
                        ]
                    },
                    "IncomeSentiment": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$type", "INCOME"]},
                                    {"$eq": ["$status", "Active"]},
                                    {"$eq": ["$group_id", group_id]},
                                ]
                            },
                            "$amount",
                            0,
                        ]
                    },
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_expence": {"$sum": "$ExpenceSentiment"},
                    "total_income": {"$sum": "$IncomeSentiment"},
                }
            },
            {
                "$project": {
                    "total_income": "$total_income",
                    "total_expence": "$total_expence",
                    "net": {"$subtract": ["$total_income", "$total_expence"]},
                }
            },
        ]
        #print(pipeline)
        return self.agg_query("transactions", pipeline)

    def prep_day_view(self, group_id, now):
        day_view_x_values = []
        day_view_income_values = []
        day_view_expence_values = []
        day_view_net_values = []

        start_day = now + dt.timedelta(-9)
        index = 1
        for single_date in (start_day + dt.timedelta(n) for n in range(10)):
            day = datetime(single_date.year, single_date.month, single_date.day)
            # print(day)
            graph_result = self.get_statictics(group_id, day)
            graph_data = (
                graph_result[0]
                if len(graph_result) != 0
                else {"total_income": 0.0, "total_expence": 0.0, "net": 0.0}
            )
            day_view_x_values.append(int(day.strftime("%d")))
            day_view_income_values.append(graph_data["total_income"])
            day_view_expence_values.append(graph_data["total_expence"])
            day_view_net_values.append(graph_data["net"])
            index += 1

        x = {
                "day_view_x_values": day_view_x_values,
                "day_view_income_values": day_view_income_values,
                "day_view_expence_values": day_view_expence_values,
                "day_view_net_values": day_view_net_values,
            }
        return x

    def prep_month_view(self, group_id, now):
        currentYear = now.year
        xValues = []
        incomeValues = []
        expenceValues = []
        netValues = []

        for i in range(1, now.month + 1):
            _, num_days = calendar.monthrange(currentYear, i)
            first_day = datetime(currentYear, i, 1)
            last_day = datetime(currentYear, i, num_days)
            graph_result = self.get_statictics(group_id, first_day, last_day)
            graph_data = (
                graph_result[0]
                if len(graph_result) != 0
                else {"total_income": 0.0, "total_expence": 0.0, "net": 0.0}
            )
            # mname = calendar.month_name[i]
            xValues.append(i)
            incomeValues.append(graph_data["total_income"])
            expenceValues.append(graph_data["total_expence"])
            netValues.append(graph_data["net"])

        return {
            "xValues": xValues,
            "incomeValues": incomeValues,
            "expenceValues": expenceValues,
            "netValues": netValues
        }
    
    def update_txn(self, q, u):
        self.db["transactions"].update_one(q, u)

    def agg_query(self, base_coll, pipeline):
        cursor = self.db[base_coll].aggregate(pipeline)
        result = list(cursor)
        return result