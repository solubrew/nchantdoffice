# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class FutureBalanceTimeLine(object):
    """"""

    def __init__(self, accounts, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("FutureBalanceTimeLine").override(cfg)
        self.accounts = (
            accounts  # Acocunts will be an object that has all accounts, expenses, revenues and relationships
        )

    def calculate_balance(self, balance, expenses, receipts):
        """"""
        balance += sum(expenses) - sum(receipts)
        return balance

    def calculate_balances(self, date=None):
        """"""
        if date is None:
            date = dt.datetime.now()
        for account in self.accounts.balance_accounts:
            current_balance = account.get_balance(date)
            expected_expenses = account.get_expected_expenses(date)
            expected_receipts = account.get_expected_receipts(date)
            balance = self.calculate_balance(current_balance, expected_expenses, expected_receipts)
            account.set_expected_balance(date, balance)
        return self

    def next_n_days(self, days=1):
        """"""
        today = dt.datetime.now()
        for n in range(days):
            self.calculate_balance(today + n)

    def next_n_weeks(self, weeks=1):
        """"""
        days = self.calculateDays(weeks * 7)
        self.next_n_days(days)

    def next_n_months(self, months=1):
        """"""
        days = self.calculateDays()
        self.next_n_days(days)

    def next_n_years(self, years=1):
        """"""
        days = self.calculateDays(years * 365)
        self.next_n_days(days)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
