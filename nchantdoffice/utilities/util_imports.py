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

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules======================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from dill.pointers import parent
from kahndor.logma import Logma
from pyffice.notebooks.cherrytree import PyfficeCherryTree

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdImport(object):
    """"""

    def __init__(self, path, cfg=None):
        """"""
        logma.info(f"[util_imports] NchantdImport.__init__: path={path!r}")
        self.path = path
        try:
            self.config = kahndor.Instruct(pxcfg).select("NchantdImport").override(cfg)
            logma.debug(f"[util_imports] NchantdImport.__init__: config loaded, dikt_keys={list(self.config.dikt.keys())[:8]}")
        except Exception as e:
            logma.error(f"[util_imports] NchantdImport.__init__ failed: path={path!r} err={e}", exc_info=True)
            raise

    def run(self):
        """"""
        logma.info(f"[util_imports] NchantdImport.run: path={getattr(self, "path", None)!r}")
        # Base class is a no-op; subclasses override with actual conversion logic.
        return None


class NchantdCherrytreeImport(NchantdImport):
    """"""

    def __init__(self, path, cfg=None):
        """"""
        logma.info(f"[util_imports] NchantdCherrytreeImport.__init__: path={path!r}")
        try:
            super().__init__(path, cfg)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdCherrytreeImport").override(cfg))
            self.cherrytree = PyfficeCherryTree(path, self.config)
            logma.info(f"[util_imports] NchantdCherrytreeImport.__init__: PyfficeCherryTree built for path={path!r}")
        except Exception as e:
            logma.error(f"[util_imports] NchantdCherrytreeImport.__init__ failed: path={path!r} err={e}", exc_info=True)
            raise

    def run(self):
        """"""
        logma.info(f"[util_imports] NchantdCherrytreeImport.run: starting conversion of path={getattr(self, 'path', None)!r}")
        try:
            super().run()
            cherrytree = self.cherrytree.convert_to_yaml()
            logma.debug(f"[util_imports] cherrytree converted (yaml length={len(cherrytree) if hasattr(cherrytree, '__len__') else 'n/a'})")
            # TODO: resolve parent_node + app reference cleanly
            convert_yaml_to_nchantdoffice(cherrytree, self.app, parent_node)
            logma.info(f"[util_imports] NchantdCherrytreeImport.run: completed for path={getattr(self, 'path', None)!r}")
        except Exception as e:
            logma.error(f"[util_imports] NchantdCherrytreeImport.run failed: path={getattr(self, 'path', None)!r} err={e}", exc_info=True)
            raise


def convert_yaml_to_nchantdoffice(notebook, parent_node):
    """"""
    logma.info(f"[util_imports] convert_yaml_to_nchantdoffice: nodes={len(notebook) if hasattr(notebook, '__len__') else 'n/a'}")
    try:
        for node in notebook:
            for content in node.values():
                node = parent_node.add_child(
                    node,
                    "NchantdOfficeNode",
                    name=node.name,
                    description=node.description,
                    icon=node.icon,
                )
                logma.debug(f"[util_imports] convert_yaml_to_nchantdoffice: added child node name={node.name!r}")
                if content.get("text", None):
                    node.add_tab(node, "NchantdOfficeText")
                    logma.debug(f"[util_imports] convert_yaml_to_nchantdoffice: added text tab")
                if content.get("image", None):
                    for image in content.get("image", []):
                        node.add_tab(image, "NchantdOfficeImage")
                        logma.debug(f"[util_imports] convert_yaml_to_nchantdoffice: added image tab")
                # if content.get("table", None):
                #     for table.get("name", uuid(5)) in content.get("table", []):
                #         node.add_tab(table, "NchantdOfficeTable")
    except Exception as e:
        logma.error(f"[util_imports] convert_yaml_to_nchantdoffice failed: {e}", exc_info=True)
        raise


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
