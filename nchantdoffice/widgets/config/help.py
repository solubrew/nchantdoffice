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
from nchantrs.widgets.config.help import NchantdFAQs, NchantdHelpDocs, NchantdHelpChatDex
from nchantrs.widgets.trees import NchantdTree
from nchantdoffice.widgets.documents.media.pdfs import NchantdOfficePDF

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "help.yaml")


class NchantdOfficeFAQs(NchantdFAQs):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeFAQs").override(parent.config).override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeHelpDocs(NchantdHelpDocs):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeHelpDocs").override(cfg))
        self.index_tree = None
        self.reader = None

    def initModel(self, cfg=None):
        """Initialise the help-docs model.

        T-020: locates the bundled help PDF directory
        (or downloads the latest from the configured URL when an
        update is requested via ``update_help_docs``). The PDFs
        are listed in ``self.help_pdfs`` for the index tree to
        display. Falls back to an empty list when no PDFs are
        available locally.
        """
        super().initModel(cfg)
        self.help_pdfs = self._discover_help_pdfs()
        if not self.help_pdfs:
            logma.info("[help] no local help PDFs found; call update_help_docs to fetch")
        return self

    def initView(self, cfg=None):
        """Build the help-docs index + reader view.

        T-020: builds a two-pane layout with a ``NchantdTree``
        index on the left and a ``NchantdOfficePDF`` reader on the
        right. Selecting a node in the index opens the
        corresponding PDF in the reader.
        """
        cfg = cfg or {}
        cfg["layout"] = "horizontal"
        super().initView(cfg)

        # Index tree (left pane)
        try:
            cfg_tree = {"name": "Help Index"}
            self.index_tree = NchantdTree(self, cfg_tree).initWidget()
            for entry in self.help_pdfs:
                self.index_tree.addNode(
                    getattr(self.index_tree, "rootNode", None),
                    [entry.get("title", entry.get("path", "doc"))],
                )
            self.layout.addWidget(self.index_tree)
        except Exception as e:
            logma.error(f"[help] initView: tree build failed: {e}", exc_info=True)

        # PDF reader (right pane)
        try:
            self.reader = NchantdOfficePDF(self, {}).initWidget()
            self.layout.addWidget(self.reader)
        except Exception as e:
            logma.error(f"[help] initView: reader build failed: {e}", exc_info=True)
        return self

    def _discover_help_pdfs(self):
        """Walk the bundled help directory and return a list of PDF entries.

        Each entry is a dict ``{"path": ..., "title": ...}``. Returns
        an empty list when the directory is missing.
        """
        import os
        candidates = [
            self.config.dikt.get("help_pdf_dir") if hasattr(self, "config") else None,
            "/usr/share/nchantdoffice/docs",
            "/usr/local/share/nchantdoffice/docs",
            join(here, "_data_", "docs"),
        ]
        results = []
        for d in candidates:
            if not d or not os.path.isdir(d):
                continue
            try:
                for name in sorted(os.listdir(d)):
                    if name.lower().endswith(".pdf"):
                        results.append({
                            "path": os.path.join(d, name),
                            "title": os.path.splitext(name)[0].replace("_", " ").title(),
                        })
            except OSError:
                continue
        return results

    def update_help_docs(self, url=None, dest=None):
        """Download the latest help PDF bundle from ``url``.

        T-020: when network access is available, fetches the
        current help docs bundle and stores the PDFs in ``dest``
        (defaults to the bundled docs directory). Returns the list
        of downloaded file paths on success, an empty list on
        network / disk failure.

        ``url`` defaults to the value stored at
        ``config.dikt["help_docs_url"]``; ``dest`` defaults to the
        first existing help dir from ``_discover_help_pdfs``.
        """
        try:
            import os
            import requests  # type: ignore
            from kahndor.logma import Logma
            log = Logma(__name__)
            url = url or (self.config.dikt.get("help_docs_url") if hasattr(self, "config") else None)
            if not url:
                log.warning("[help] update_help_docs: no URL configured")
                return []
            dest = dest or (self.config.dikt.get("help_pdf_dir") if hasattr(self, "config") else None) or join(here, "_data_", "docs")
            os.makedirs(dest, exist_ok=True)
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "zip" in content_type:
                # Extract a zip of PDFs
                import zipfile, io
                with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                    zf.extractall(dest)
                log.info(f"[help] update_help_docs: extracted zip to {dest}")
            else:
                # Treat the response as a single PDF
                out = os.path.join(dest, os.path.basename(url) or "help.pdf")
                with open(out, "wb") as f:
                    f.write(response.content)
                log.info(f"[help] update_help_docs: wrote {out}")
            self.help_pdfs = self._discover_help_pdfs()
            return [e["path"] for e in self.help_pdfs]
        except Exception as e:
            logma.error(f"[help] update_help_docs failed: {e}", exc_info=True)
            return []

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeHelpChatDex(NchantdHelpChatDex):
    """"""

    def __init__(self, parent=None, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdHelpChatDex").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
