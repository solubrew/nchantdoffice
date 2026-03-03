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
from condor import condor
from dill.pointers import parent
from ogma.logma import Logma
from pyffice.notebooks.cherrytree import PyfficeCherryTree

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")

pxcfg = {}


class NchantdImport(object):
    """"""

    def __init__(self, path, cfg=None):
        """"""
        self.path = path
        self.config = condor.Instruct(pxcfg).select("NchantdImport")
        self.config.override(cfg)

    def run(self):
        """"""
        pass


class NchantdCherrytreeImport(NchantdImport):
    """"""

    def __init__(self, path, cfg=None):
        """"""
        self.config = condor.Instruct(pxcfg).select("NchantdCherrytreeImport")
        super().__init__(path, self.config)
        self.config.override(cfg)
        self.cherrytree = PyfficeCherryTree(path, self.config)

    def run(self):
        """"""
        super().run()
        cherrytree = self.cherrytree.convert_to_yaml()
        convert_yaml_to_nchantdoffice(cherrytree, self.app, parent_node)


def convert_yaml_to_nchantdoffice(notebook, parent_node):
    """"""
    for node in notebook:
        for content in node.values():
            node = parent_node.add_child(
                node,
                "NchantdOfficeNode",
                name=node.name,
                description=node.description,
                icon=node.icon,
            )
            if content.get("text", None):
                node.add_tab(node, "NchantdOfficeText")
            if content.get("image", None):
                for image in content.get("image", []):
                    node.add_tab(image, "NchantdOfficeImage")
            # if content.get("table", None):
            #     for table.get("name", uuid(5)) in content.get("table", []):
            #         node.add_tab(table, "NchantdOfficeTable")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
