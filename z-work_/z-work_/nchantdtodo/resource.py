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
import datetime as dt

# ===============================================================================||
from kahndor.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, "_data_", "models.yaml")


class Resource:
    """"""

    def __init__(self, name, fungibility):
        """
        Initializes an instance of the class.

        :param name: The name of the object to be initialized.
        :type name: str
        :param fungibility: The fungibility of the object to be initialized.
        :type fungibility: bool
        """
        self.name = name
        self.schedule = {}
        self.fungibility = fungibility

    def build_schedule(self, inc=15):
        """
        self.schedule can contain

        a status of ONTRACK, OVERLOADED, UNTRACKED
        the state can be PAST, CURRENT, FUTURE

        :param inc:
        :return:

        """
        for t in range(0, 24 * 60, inc):
            t = dt.timedelta(minutes=t)
            logma.info(str(t)[: str(t).rfind(":")])
            self.schedule[str(t)[: str(t).rfind(":")]] = {
                "events": [],
                "tasks": [],
                "status": "ONTRACK",
                "state": "FUTURE",
            }
        return self


class Resource_Human(Resource):
    """
    Resource_Human

    This class represents a human resource. It inherits from the Resource class.

    Methods:
        __init__(self, name, fungibility=0.7)
            Initializes a new instance of the Resource_Human class.

        default_routine(self, window='daily')
            Sets the default routine for the human resource based on the specified window.

    Attributes:
        name (str)
            The name of the human resource.

        fungibility (float)
            The fungibility of the human resource.

    Example usage:
        # Create a new human resource
        human = Resource_Human("John Doe", 0.8)

        # Set the default routine for the human resource
        human.default_routine("daily")

        # Set the default routine for the human resource using the default window ('daily')
        human.default_routine()

    """

    def __init__(self, name, fungibility=0.7):
        """"""
        Resource.__init__(self, name, fungibility)

    def default_routine(self, window="daily"):
        """
        This method is used to define the default routine based on the given window parameter.

        :param window: Optional parameter to specify the window type (default is 'daily')
        :return: The object itself

        Example usage:
            obj = ClassName()
            obj.default_routine('daily')
        """
        if window == "daily":
            sleep_start_tm = ""
            sleep_end_tm = ""
            sleep_tms = {"main": 480}

            eat_tms = {"breakfast": 30, "lunch": 30, "dinner": 30}
        elif window == "weekly":
            # standard weekly work 40 hours
            # 2 day weekend
            pass
        elif window == "monthly":
            # standard pill payments
            pass
        elif window == "yearly":
            #
            pass
        elif window == "life":
            #
            pass
        return self


class Resource_Machine(Resource):
    """
    This class represents a Resource Machine, which is a specific type of Resource.

    Attributes:
        name (str): The name of the Resource Machine.
        fungibility (float): The fungibility factor of the Resource Machine.

    Methods:
        __init__(name, fungibility=0.9): Initializes the Resource Machine with the given name and fungibility factor.

    """

    def __init__(self, name, fungibility=0.9):
        """"""
        Resource.__init__(self, name, fungibility)


class Resource_Consumable(Resource):
    """
    Class: Resource_Consumable

    This class represents a consumable resource. It inherits from the base class Resource.

    Attributes:
    - name: The name of the consumable resource.
    - price: The price of the consumable resource.

    Methods:
    - __init__(name): Initializes the Resource_Consumable object with the given name and a default price of 0.99.

    Example usage:
    resource = Resource_Consumable("Water Bottle")
    """

    def __init__(self, name):
        """"""
        Resource.__init__(self, name, 0.99)
