from marshmallow import post_load


from .transaction import Transaction, TransactionSchema
from .transaction_type import TransactionType


class Expence(Transaction):
    def __init__(self, group_id, title, amount, txn_date, category, brand, description, tags):
        super(Expence, self).__init__(group_id, title, amount, txn_date, category, brand, description, tags, TransactionType.EXPENCE)

    def __repr__(self):
        return '<Expence(name={self.description!r})>'.format(self=self)



class ExpenceSchema(TransactionSchema):
    @post_load
    def make_expence(self, data, **kwargs):
        return Expence(**data)