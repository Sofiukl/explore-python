from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient

from cashman.controller.group_controller import GroupController
from cashman.controller.home_controller import HomeController


DB_URL = 'mongodb://mongo:27017'
DB_NAME = 'dev'

app = Flask(__name__)
app = Flask(__name__, static_url_path="/static")
client = MongoClient(DB_URL)
db = client[DB_NAME]
gc = GroupController(db)
hc = HomeController(db)

@app.route("/")
def dashboard():
    return gc.dashboard_page()

@app.route("/groups", methods=["POST"])
def add_txn_group():
    return gc.add_txn_group()

@app.route("/home/<group_id>/<group_name>")
def home(group_id, group_name):
    return hc.home_page(group_id, group_name)


@app.route("/transactions")
def get_incomes():
    return hc.get_txn()

@app.route("/transactions", methods=["POST"])
def add_txn():
    return hc.add_txn()

@app.route("/transactions/<id>", methods=["DELETE"])
def del_txn(id):
    return hc.del_txn(id)

@app.route("/pdf/<group_id>/<group_name>")
def gen_pdf(group_id, group_name):
    return hc.gen_pdf(group_id, group_name)

if __name__ == "__main__":
    app.run(debug=True)
