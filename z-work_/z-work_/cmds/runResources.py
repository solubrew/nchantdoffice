# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid: <^(UUID)^>
        name:
        description: >
        expirary: <[expiration]>
        version: <[version]>
        path: <[LEXIvrs]>
        outline: <[outline]>
        authority: document|this
        security: sec|lvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import abspath, dirname, exists, join
from sys import argv
import datetime as dt

# ===============================================================================||
# from crow import  # Commented out crowLoad
crowLoad("NchantdTodo", "DELTA")

from nchantdtodo.resource import Resource_Human
from kahndor.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, "_data_", "models.yaml")


def runApplication(seq):
    """
    Method to run the application.

    :param seq: The sequence parameter.
    :type seq: any
    :return: None
    """
    name = "Joe"
    resource = Resource_Human(name)
    resource.build_routine()


if __name__ == "__main__":
    start = dt.datetime.now()
    print("Start", start)
    runApplication(argv)
    end = dt.datetime.now()
    print("End", end)
