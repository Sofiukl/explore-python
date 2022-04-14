from marshmallow import post_load
from .transaction import Transaction, TransactionSchema
from .transaction_type import TransactionType


class Income(Transaction):
    def __init__(self, group_id, title, amount, txn_date, category, brand, description, tags):
        super(Income, self).__init__(group_id, title, amount, txn_date, category, brand, description, tags, TransactionType.INCOME)

    def __repr__(self):
        return '<Income(name={self.description!r})>'.format(self=self)



class IncomeSchema(TransactionSchema):

    @post_load
    def make_income(self, data, **kwargs):
        return Income(**data)