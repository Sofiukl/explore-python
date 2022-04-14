from marshmallow import post_load
import datetime as dt
from marshmallow import Schema, fields


class TransactionGroup():
    def __init__(self, name, is_default=False, description=""):
        self.name = name
        self.description = description
        self.is_default = is_default
        self.created = dt.datetime.now()


    def __repr__(self):
        return '<TransactionGroup(name={self.description!r})>'.format(self=self)



class TransactionGroupSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    is_default = fields.Boolean()
    created = fields.Date()

    @post_load
    def make_txn_group(self, data, **kwargs):
        return TransactionGroup(**data)