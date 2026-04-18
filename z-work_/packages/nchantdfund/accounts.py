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
pxcfg = join(here, "_data_", "accounts.yaml")


class Account(object):
    """"""

    def __init__(self, name, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("").override(cfg)
        self.name = name
        self.recurrence = {}
        self.expected_balance = {}
        self.expected_receipts = {}
        self.expected_expenses = {}
        self.historical_balance = {}
        self.current_balance = None
        self.max_date = None

    def add_expected_expense(self, date, value):
        """"""
        if date not in self.expected_expenses:
            self.expected_expenses[date] = []
        self.expected_expenses[date].append(value)
        return self

    def add_expected_receipt(self, date, value):
        """"""
        if date not in self.expected_receipts:
            self.expected_receipts[date] = []
        self.expected_receipts[date].append(value)
        return self

    def get_balance(self, date):
        """"""
        if date in self.historical_balance:
            return self.historical_balance[date]
        if date in self.expected_balance:
            return self.expected_balance[date]
        while date not in self.expected_balance:
            date = date - 1
            if date in self.historical_balance:
                self.set_expected_balance(date, self.historical_balance[date])

    def get_expected_expenses(self, date):
        """"""

    def get_expected_receipts(self, date):
        """"""

    def refresh_expected_balances(self):
        """"""
        for date in self.expected_balance:
            if date < dt.datetime.now():
                del self.expected_balance[date]
            else:
                self.expected_balance[date] = self.current_balance
        return self

    def set_expected_balance(self, date, balance):
        """"""
        self.expected_balance[date] = balance
        return self

    def set_historical_balance(self, date, balance):
        """"""
        if date < dt.datetime.now():
            raise Exception(f"Date has not passed yet {date}")
        self.historical_balance[date] = balance
        return self

    def set_recurrence(self, start_dttm, window="daily", end_dttm=None, name="prime"):
        """"""
        self.recurrence[name] = {start_dttm: window}
        return self


class DebitAccount(Account):
    """"""

    def __init__(self, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("Account").override(cfg)


class CreditAccount(Account):
    """A class representing an Account or AccountLike Expense that primarily requests funds from the user"""

    def __init__(self, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("").override(cfg)


class IncomeAccount(Account):
    """A class representing an Account or AccountLike Source that primarily sends funds to the user"""

    def __init__(self, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("").override(cfg)


class AccountsManager(object):
    """"""

    def __init__(self, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("Accounts").override(cfg)


class HealthCareSavingsAccount(DebitAccount):
    """"""

    def __init__(self, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("").override(cfg)


class CreditCardAccount(CreditAccount):
    """"""

    def __init__(self, cfg=None):
        """"""
        self.config = kahndor.instruct(pxcfg).select("").override(cfg)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
