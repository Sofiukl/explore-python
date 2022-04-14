import datetime as dt
from marshmallow import Schema, fields


class Transaction():
    def __init__(self, group_id, title, amount, txn_date, category, brand, description, tags, type):
        self.group_id = group_id
        self.title = title
        self.amount = amount
        self.txn_date = txn_date
        self.type = str(type.value)
        self.category = category
        self.brand = brand
        self.description = description
        self.tags = tags
        self.created = dt.datetime.now()


    def __repr__(self):
        return '<Transaction(name={self.description!r})>'.format(self=self)



class TransactionSchema(Schema):
    group_id = fields.Str()
    title = fields.Str()
    amount = fields.Number()
    txn_date = fields.Date()
    type = fields.Str()
    category = fields.Str()
    brand = fields.Str()
    description = fields.Str()
    tags = fields.List(fields.Str())
    created = fields.Date()