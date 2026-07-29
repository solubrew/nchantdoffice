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
from os.path import dirname, join, exists
import os
import subprocess
import threading

# ======================================3rd Party Library Modules=====================================================||
from pygments import highlight
from pygments.lexers import PythonLexer, JavaLexer, JavascriptLexer, CLexer
from pygments.lexers import JsonLexer, YamlLexer, CssLexer, IniLexer
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers.dotnet import CSharpLexer
from pygments.lexers.ruby import RubyLexer
from pygments.formatters import HtmlFormatter
from numpy import isnan, nan
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxWidget
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.libraries.pyqt import QTimer
from nchantrs.libraries import pyqt
from pycurity.pysan import Sanitized
from nchantdoffice.widgets.panes.sources import NchantdSourceEditPane, NchantdSourcesListPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = False
logma = Logma(__name__)
if not log:
    logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "notebooks.yaml")


def _preexec_die_with_parent():
    """Child preexec (Linux): request SIGTERM when the parent process dies.

    Ensures the Jupyter subprocess is reaped even if the app crashes or is killed
    without a clean shutdown — the leftover-server problem. No-op off Linux.
    """
    try:
        import ctypes
        import signal

        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        PR_SET_PDEATHSIG = 1
        libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)
    except Exception:
        pass


class NchantdOfficeNotebook(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        icfg = {}
        super().__init__("Nchantd Notebook", parent, icfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNotebook").override(cfg))
        self.jupyter_process = None
        self.server_port = 8888
        self.server_url = f"http://localhost:{self.server_port}"
        self.server_running = False

        # Kernel management
        self.kernel_manager = None
        self.kernel_client = None
        self.kernel_name = "python3"
        self.kernel_running = False
        self.current_notebook_path = None

        # Cell & notebook data-model (consolidated from pyffice.notebooks.notebooks)
        self.cells = []
        self.notebook = None

        # Navigation self-heal state. The embedded viewer defers its initial
        # about:blank load until it has an on-screen surface; that load can then
        # commit *after* our real navigation and clobber it back to about:blank.
        # We remember the intended URL and re-issue it from loadFinished.
        self._target_url = None
        self._nav_retries = 0
        self.pinned = False

    def initModel(self):
        """Load the notebook document and resolve its file_path.

        T-NEW-006 (T-NEW-005 followup): the previously-saved notebook
        location lives at ``document.content["content"]["file_path"]``
        after Sprint 1's persistence fix; the Pyffice document's
        ``self.file_path`` is still the initial ``/default.ipynb`` until
        ``open_file`` runs. We therefore prefer the saved content
        location, then the cfg, then ``document.file_path``.
        """
        super().initModel()
        self.document = self.app.model.codex.init_notebook({"document": self.config.dikt.get("document", {})})
        self.document.load_document()
        saved_content = self.document.content or {}
        nested_content = saved_content.get("content", {}) if isinstance(saved_content, dict) else {}
        self.file_path = (
            nested_content.get("file_path")
            or saved_content.get("file_path")
            or self.config.dikt.get("file_path")
            or self.document.file_path
        )
        self.context_menu.get_menu("context.document.notebook")
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        if "buttons" not in cfg:
            cfg["buttons"] = {}
        # cfg["buttons"][10] = {"action": "start_server", "handler": self.cmd_start_server}
        # cfg["buttons"][11] = {"action": "restart_server", "handler": self.cmd_restart_server}
        # cfg["buttons"][12] = {"action": "stop_server", "handler": self.cmd_stop_server}
        # cfg["buttons"][13] = {"action": "new_notebook", "handler": self.cmd_new_notebook}
        # cfg["buttons"][14] = {
        #     "action": "start_kernel",
        #     "handler": self.cmd_start_kernel,
        # cfg["buttons"][15] = {"action": "interrupt_kernel", "handler": self.cmd_interrupt_kernel}
        cfg["buttons"][14] = {
            "name": "select_url",
            "label": "URL",
            "layout": "horizontal",
            "size": [30, 30],
            "combobox": {"size": [500, 30], "options": self.get_url_history()},
            "type": "dropdown",
            "handler": self.cmd_goto_page,
            "value": self.get_current_url(),
        }
        self.url_select_entry = NchantdDropDown(self, cfg["buttons"][14])
        cfg["buttons"][14]["widget"] = self.url_select_entry
        cfg["buttons"][17] = {"action": "web_page_pin", "handler": self.cmd_pin_page, "value": self.cmd_check_is_pinned}
        cfg["buttons"][49] = "_insert_stretch"
        cfg["fill"] = True
        super().initView(cfg)
        # Start the embedded viewer on a blank page. Loading the Jupyter URL
        # before the server is up yields an ERR_CONNECTION_REFUSED error page
        # that can persist even after a later reload; we navigate explicitly once
        # the server is confirmed reachable (see start_jupyter_server).
        # links_in_place: new-window/target=_blank requests (how Jupyter opens a
        # notebook when a .ipynb is double-clicked in the tree) load in THIS view
        # instead of being dropped. See NchantdWebEnginePage.createWindow.
        cfg = {"url": "about:blank", "is_app": True, "links_in_place": True}
        logma.info(f"[notebook] initView: creating web viewer (blank until ready; target={self.server_url})")
        # initWidget (not initView) so the viewer's initModel runs too: it honours
        # is_app/url from cfg and seeds the model-side url state before first show.
        self.browser = NchantdWebViewer(self, cfg).initWidget()
        self._wire_browser_load_logging()
        self.layout.addWidget(self.browser)
        # Auto-start Jupyter server when tab opens (defaults True).
        # QTimer.singleShot defers the start until the event loop is idle so
        # the UI renders first; start_jupyter_server() spawns the subprocess
        # and loads the URL into self.browser once it's up.
        autostart = True
        if self.config and isinstance(getattr(self.config, "dikt", None), dict):
            autostart = self.config.dikt.get("autostart_server", True)
        logma.info(
            f"[notebook] initView: autostart={autostart} | server_running={self.server_running} | "
            f"target server_url={self.server_url}"
        )
        if autostart and not self.server_running:
            logma.info("[notebook] initView: scheduling start_jupyter_server in 500ms (QTimer.singleShot)")
            QTimer.singleShot(500, self.start_jupyter_server)

        # T-044: re-load the previously-open .ipynb file when one
        # is configured. Looks for the path on
        # ``config.dikt["last_notebook_path"]`` first, then falls
        # back to ``self.current_notebook_path``. The actual
        # reload is deferred 1 second so it runs after the
        # Jupyter server is up.
        last_path = None
        if hasattr(self, "config"):
            last_path = self.config.dikt.get("last_notebook_path")
        if not last_path:
            last_path = getattr(self, "current_notebook_path", None)
        if last_path and self._looks_like_ipynb_path(last_path):
            logma.info(f"[notebook] initView: scheduling reload of {last_path}")
            QTimer.singleShot(1000, self._make_reload_handler(last_path))
        return self

    def _make_reload_handler(self, last_path):
        """Return a QTimer singleShot slot that reloads ``last_path``.

        Replaces the previous ``lambda p=last_path:`` form with a
        named factory; satisfies the lambda-antipattern auditor and
        makes the slot testable in isolation.
        """
        def _handler(_p=last_path):
            self.open_notebook(_p)
        return _handler

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_url_history(self):
        """Return the list of URLs the notebook has visited.

        Combines the static default URL (the local Jupyter server) with
        any URLs the user has navigated to since the notebook was
        opened. Returns a list of URL strings, most recent first.
        """
        history = []
        if getattr(self, "server_url", None):
            history.append(self.server_url)
        seen = set(history)
        for url in getattr(self, "_url_history", []) or []:
            if url and url not in seen:
                history.append(url)
                seen.add(url)
        return history



    def _looks_like_ipynb_path(self, path):
        """Return True if ``path`` is a string ending in ``.ipynb``."""
        return bool(path) and isinstance(path, str) and path.lower().endswith(".ipynb")

    def open_notebook(self, path):
        """Open a local .ipynb file in the embedded webview.

        T-044 helper - resolves to an absolute path, validates the
        file exists, then issues a webview.setUrl() to the Jupyter
        server's ``/notebooks/<name>`` endpoint. Returns ``self``.
        """
        if not self._looks_like_ipynb_path(path):
            logma.warning(f"[notebook] open_notebook: not a .ipynb path: {path}")
            return self
        import os
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            logma.warning(f"[notebook] open_notebook: file missing: {path}")
            return self
        try:
            import urllib.parse
            self.current_notebook_path = path
            if hasattr(self, "config"):
                self.config.dikt["last_notebook_path"] = path
            target = f"{self.server_url}/notebooks/{urllib.parse.quote(os.path.basename(path))}"
            if hasattr(self, "browser") and self.browser is not None and hasattr(self.browser, "setUrl"):
                from PySide6 import QtCore
                self.browser.setUrl(QtCore.QUrl(target))
            logma.info(f"[notebook] open_notebook: navigated to {target}")
        except Exception as e:
            logma.error(f"[notebook] open_notebook failed: {e}", exc_info=True)
        return self

    def get_current_url(self):
        """Return the URL the notebook is currently displaying.

        Falls back to the local Jupyter server URL when no explicit
        navigation has happened yet.
        """
        current = getattr(self, "_target_url", None)
        if current:
            return current
        return getattr(self, "server_url", None) or ""

    def cmd_goto_page(self, url=None, *args, **kwargs):
        """Navigate the embedded browser to the given URL.

        Validates that the URL is non-empty and remembers it for the
        next ``get_current_url`` call. Returns ``self`` for chainable
        call sites.
        """
        if not url:
            return self
        self._target_url = url
        history = list(getattr(self, "_url_history", []) or [])
        if url in history:
            history.remove(url)
        history.insert(0, url)
        # Cap history at 50 entries to keep the dropdown manageable
        self._url_history = history[:50]
        if hasattr(self, "web_view") and self.web_view is not None:
            try:
                self.web_view.setUrl(pyqt.QUrl(url))
            except Exception as e:
                logma.error(f"[notebooks] cmd_goto_page failed: {e}", exc_info=True)
        return self

    def add_cell(self, cell):
        """Append a cell to the notebook.

        Args:
            cell: Cell dict (must contain 'cell_type' and 'source' keys)
        """
        if self.cells is None:
            self.cells = []
        self.cells.append(cell)
        logma.info(f"Cell added; total: {len(self.cells)}")
        return self

    def check_kernel_alive(self):
        """Check if kernel is alive and responsive"""
        if self.kernel_client:
            return self.kernel_client.is_alive()
        return False

    def clear_cell(self, dex):
        """Clear outputs of cell at given index.

        Args:
            dex: Zero-based cell index
        """
        if self.cells is None or not (0 <= dex < len(self.cells)):
            logma.error(f"Invalid cell index: {dex}")
            return self
        self.cells[dex]["outputs"] = []
        logma.info(f"Cell {dex} outputs cleared")
        return self

    def clear_cells(self):
        """Clear outputs of all cells."""
        if self.cells:
            for cell in self.cells:
                cell["outputs"] = []
            logma.info(f"Cleared outputs of {len(self.cells)} cells")
        return self

    def cmd_check_is_pinned(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_pin_page(self, event, *args, **kwargs):
        """"""
        self.pin_page()
        return self

    def cmd_unpin_page(self, event, *args, **kwargs):
        """"""
        super().unpin_page()
        self.document.unpin_page()
        return self

    # ========== Command Handlers ==========

    def cmd_start_server(self, event=None, *args, **kwargs):
        """Start Jupyter notebook server"""
        if not self.server_running:
            self.start_jupyter_server()
        else:
            logma.info("Jupyter server is already running")
        return self

    def cmd_restart_server(self, event=None, *args, **kwargs):
        """Restart Jupyter notebook server"""
        self.stop_jupyter_server()
        import time

        time.sleep(1)  # Wait for server to fully stop
        self.start_jupyter_server()
        return self

    def cmd_stop_server(self, event=None, *args, **kwargs):
        """Stop Jupyter notebook server"""
        self.stop_jupyter_server()
        return self

    def cmd_new_notebook(self, event=None, *args, **kwargs):
        """Create a new notebook"""
        self.create_new_notebook()
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """Open a local notebook file"""
        super().cmd_open_local_file(event, *args, **kwargs)
        if self.local_file and exists(self.local_file):
            self.load_notebook_file(self.local_file)
        return self

    def cmd_set_server_port(self, event=None, *args, **kwargs):
        """Set server port number"""
        if hasattr(self, "port_spin"):
            new_port = self.port_spin.value()
            if new_port != self.server_port:
                self.server_port = new_port
                self.server_url = f"http://localhost:{self.server_port}"
                logma.info(f"Server port changed to: {self.server_port}")
                # Restart server if running
                if self.server_running:
                    logma.info("Restarting server with new port...")
                    self.cmd_restart_server()
        return self

    def cmd_select_kernel(self, event=None, *args, **kwargs):
        """Select Jupyter kernel"""
        if hasattr(self, "kernel_select"):
            kernel = self.kernel_select.currentText()
            logma.info(f"Selected kernel: {kernel}")
            self.kernel_name = kernel
            # Restart kernel if running
            if self.kernel_running:
                logma.info("Restarting kernel with new kernel type...")
                self.restart_kernel()
        return self

    def cmd_start_kernel(self, event=None, *args, **kwargs):
        """Start the Jupyter kernel"""
        if not self.kernel_running:
            self.start_kernel()
        else:
            logma.info("Kernel is already running")
        return self

    def cmd_interrupt_kernel(self, event=None, *args, **kwargs):
        """Interrupt the running kernel"""
        self.interrupt_kernel()
        return self

    def cmd_toggle_autostart(self, event=None, *args, **kwargs):
        """Toggle auto-start server setting"""
        if hasattr(self, "autostart_checkbox"):
            autostart = self.autostart_checkbox.isChecked()
            logma.info(f"Auto-start server: {autostart}")
            # Save to config
            if self.config:
                self.config.dikt["autostart_server"] = autostart
        return self

    def create_new_notebook(self, notebook_name=None):
        """Create a new Jupyter notebook"""
        try:
            import nbformat
            from nbformat.v4 import new_notebook, new_code_cell

            # Create a new notebook
            nb = new_notebook()

            # Add a welcome cell
            nb.cells.append(new_code_cell("# New Notebook\nprint('Hello, World!')"))

            # Save the notebook
            if notebook_name is None:
                notebook_name = "Untitled.ipynb"

            save_path = join(dirname(self.file_path) if self.file_path else ".", notebook_name)

            with open(save_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)

            logma.info(f"Created new notebook: {save_path}")
            self.current_notebook_path = save_path

            # Open the new notebook in browser
            if self.browser and self.server_running:
                notebook_url = f"{self.server_url}/notebooks/{notebook_name}"
                logma.info(f"[notebook] opening new notebook at exact url={notebook_url}")
                self._navigate_browser(notebook_url)
            else:
                logma.warning(
                    f"[notebook] new notebook created but not opened "
                    f"(browser={bool(self.browser)}, server_running={self.server_running})"
                )

        except Exception as e:
            logma.error(f"Error creating new notebook: {e}", exc_info=True)

        return self

    def del_cell(self, dex):
        """Delete cell at given index.

        Args:
            dex: Zero-based cell index
        """
        if self.cells is None:
            logma.warning("No cells to delete")
            return self
        if 0 <= dex < len(self.cells):
            self.cells.pop(dex)
            logma.info(f"Cell {dex} deleted; remaining: {len(self.cells)}")
        else:
            logma.error(f"Cell index {dex} out of range (size={len(self.cells)})")
        return self

    def execute_cell(self, cell_code, timeout=60):
        """Execute a specific cell code in the kernel

        Args:
            cell_code: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            dict with 'output', 'error', 'status' keys
        """
        if not self.kernel_running or not self.kernel_client:
            logma.error("Kernel not running. Start kernel first.")
            return {"output": "", "error": "Kernel not running", "status": "error"}

        try:
            # Execute the code
            msg_id = self.kernel_client.execute(cell_code)

            # Collect output
            output = []
            error = None
            status = "ok"

            import time

            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    logma.error(f"Cell execution timeout after {timeout}s")
                    return {"output": "\n".join(output), "error": "Execution timeout", "status": "timeout"}

                try:
                    msg = self.kernel_client.get_iopub_msg(timeout=1)

                    if msg["parent_header"].get("msg_id") == msg_id:
                        msg_type = msg["header"]["msg_type"]
                        content = msg["content"]

                        if msg_type == "stream":
                            output.append(content["text"])
                        elif msg_type == "execute_result":
                            output.append(str(content["data"]))
                        elif msg_type == "display_data":
                            output.append(str(content["data"]))
                        elif msg_type == "error":
                            error = "\n".join(content["traceback"])
                            status = "error"
                        elif msg_type == "status" and content["execution_state"] == "idle":
                            break

                except Exception as e:
                    # Check if execution is complete
                    if self.kernel_client.is_alive():
                        continue
                    else:
                        break

            result = {"output": "\n".join(output), "error": error, "status": status}

            logma.info(f"Cell executed with status: {status}")
            return result

        except Exception as e:
            logma.error(f"Error executing cell: {e}")
            return {"output": "", "error": str(e), "status": "error"}

    def execute_code_interactive(self, code):
        """Execute code and return output for interactive use

        Args:
            code: Python code to execute

        Returns:
            Formatted output string
        """
        result = self.execute_cell(code)

        output_parts = []
        if result["output"]:
            output_parts.append(result["output"])
        if result["error"]:
            output_parts.append(f"ERROR:\n{result['error']}")

        return "\n".join(output_parts) if output_parts else "Execution completed (no output)"

    def execute_all_cells(self, notebook_path=None):
        """Execute all cells in the notebook

        Args:
            notebook_path: Path to .ipynb file, or uses current_notebook_path
        """
        if notebook_path is None:
            notebook_path = self.current_notebook_path

        if not notebook_path or not exists(notebook_path):
            logma.error("No notebook file specified or file not found")
            return self

        try:
            import nbformat

            # Read the notebook
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            # Start kernel if not running
            if not self.kernel_running:
                self.start_kernel()

            # Execute each code cell
            results = []
            for idx, cell in enumerate(nb.cells):
                if cell.cell_type == "code":
                    logma.info(f"Executing cell {idx + 1}/{len(nb.cells)}")
                    result = self.execute_cell(cell.source)
                    results.append(result)

                    # Update cell outputs
                    if result["status"] == "ok":
                        cell.outputs = [{"output_type": "stream", "name": "stdout", "text": result["output"]}]
                    elif result["error"]:
                        cell.outputs = [
                            {
                                "output_type": "error",
                                "ename": "Error",
                                "evalue": result["error"],
                                "traceback": [result["error"]],
                            }
                        ]

            # Save notebook with outputs
            with open(notebook_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)

            logma.info(f"Executed {len(results)} cells")

        except Exception as e:
            logma.error(f"Error executing all cells: {e}")

        return self

    def get_available_kernels(self):
        """Get list of available Jupyter kernels"""
        try:
            import subprocess
            import json

            result = subprocess.run(
                ["jupyter", "kernelspec", "list", "--json"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                kernel_data = json.loads(result.stdout)
                kernels = list(kernel_data.get("kernelspecs", {}).keys())
                return kernels if kernels else ["python3"]
            else:
                return ["python3"]

        except Exception as e:
            logma.error(f"Error getting kernels: {e}")
            return ["python3"]

    def get_kernel_info(self):
        """Get information about the running kernel"""
        if not self.kernel_running or not self.kernel_client:
            return None

        try:
            # Request kernel info
            msg_id = self.kernel_client.kernel_info()

            # Wait for response
            import time

            timeout = 5
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    msg = self.kernel_client.get_shell_msg(timeout=1)
                    if msg["parent_header"].get("msg_id") == msg_id:
                        return msg["content"]
                except (KeyError, TypeError) as e:
                    logma.debug(f"[notebooks] kernel-info header lookup: {e}")
                    continue

            logma.warning("Timeout waiting for kernel info")
            return None

        except Exception as e:
            logma.error(f"Error getting kernel info: {e}")
            return None

    def get_kernel(self):
        """Return the stored value of get_kernel."""
        return getattr(self, 'kernel_name', 'python3') or 'python3'
    def get_server_port(self):
        """Return the stored value of get_server_port."""
        return getattr(self, 'server_port', 8888) or 8888
    def get_config_autostart_server(self):
        """Return the auto-start-server flag from the config.

        Reads ``config.dikt["autostart_server"]`` and returns it as a
        boolean. Defaults to ``False`` when not set.
        """
        return bool(self.config.dikt.get("autostart_server", False))
    def cmd_cell_type_change(self, event=None, *args, **kwargs):
        """Update the active cell's cell_type based on the dropdown.

        Reads the current selection from ``self.cell_type_select`` and
        writes it into the currently selected cell's ``cell_type``
        field. No-op if no cell is selected or the dropdown is empty.
        """
        if not hasattr(self, "cell_type_select") or self.cell_type_select is None:
            return self
        new_type = None
        getter = getattr(self.cell_type_select, "currentText", None) or getattr(self.cell_type_select, "get_value", None)
        if callable(getter):
            new_type = getter()
        if not new_type:
            return self
        # Find active cell
        active_cell = None
        if hasattr(self, "table") and self.table is not None:
            try:
                active_cell = self.table.currentItem()
            except Exception:
                active_cell = None
        if active_cell is not None:
            row = active_cell.row()
            try:
                if 0 <= row < len(self.cells):
                    self.cells[row]["cell_type"] = new_type
            except (TypeError, KeyError):
                pass
        self.config.dikt["cell_type"] = new_type
        return self
    def get_cell_type(self):
        """Return the cell type of the currently active cell.

        Reads the active cell's ``cell_type`` (defaults to ``"code"``
        for Jupyter notebooks). Returns ``"code"`` if no cell is
        selected.
        """
        if hasattr(self, "cells") and self.cells:
            if hasattr(self, "table") and self.table is not None:
                try:
                    item = self.table.currentItem()
                    if item is not None:
                        idx = item.row()
                        if 0 <= idx < len(self.cells):
                            return self.cells[idx].get("cell_type", "code")
                except Exception:
                    pass
        return self.config.dikt.get("cell_type", "code")
    def get_completions(self, code, cursor_pos):
        """Get code completions at cursor position

        Args:
            code: Code string
            cursor_pos: Cursor position in code

        Returns:
            List of completion matches
        """
        if not self.kernel_running or not self.kernel_client:
            return []

        try:
            msg_id = self.kernel_client.complete(code, cursor_pos)

            import time

            timeout = 3
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    msg = self.kernel_client.get_shell_msg(timeout=1)
                    if msg["parent_header"].get("msg_id") == msg_id:
                        content = msg["content"]
                        return content.get("matches", [])
                except (KeyError, TypeError) as e:
                    logma.debug(f"[notebooks] completion-match lookup: {e}")
                    continue

            return []

        except Exception as e:
            logma.error(f"Error getting completions: {e}")
            return []

    def get_binary(self):
        """Serialize the notebook to the standard .ipynb JSON format.

        Builds the notebook dict from the in-memory cells and returns
        the UTF-8 encoded JSON bytes. Returns empty bytes if the
        notebook has no cells yet.
        """
        try:
            import json
            nb = {
                "cells": self.cells or [],
                "metadata": {
                    "kernelspec": {"name": getattr(self, "kernel_name", "python3"),
                                   "display_name": "Python 3"},
                },
                "nbformat": 4,
                "nbformat_minor": 5,
            }
            return json.dumps(nb, indent=1, default=str).encode("utf-8")
        except Exception as e:
            logma.error(f"[notebooks] get_binary failed: {e}", exc_info=True)
            return b""

    def get_content(self):
        """Return notebook location and serialized notebook as one payload."""
        return {
            "content": {
                "file_path": self.file_path,
                "notebook_bytes": self.get_binary(),
            }
        }

    def inspect_object(self, code, cursor_pos, detail_level=0):
        """Get object inspection/documentation

        Args:
            code: Code string
            cursor_pos: Cursor position
            detail_level: 0 for brief, 1 for detailed

        Returns:
            Inspection data dict
        """
        if not self.kernel_running or not self.kernel_client:
            return None

        try:
            msg_id = self.kernel_client.inspect(code, cursor_pos, detail_level=detail_level)

            import time

            timeout = 3
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    msg = self.kernel_client.get_shell_msg(timeout=1)
                    if msg["parent_header"].get("msg_id") == msg_id:
                        return msg["content"]
                except (KeyError, TypeError) as e:
                    logma.debug(f"[notebooks] message-header lookup: {e}")
                    continue

            return None

        except Exception as e:
            logma.error(f"Error inspecting object: {e}")
            return None

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Server Port: ",
            "layout": "horizontal",
            "range": [8000, 9999],
            "default": self.server_port,
            "handler": self.cmd_set_server_port,
            "value": self.get_server_port(),
        }
        self.port_spin = NchantdLabeledSpinBox(self, cfg)
        items[cnt]["widget"] = self.port_spin
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Kernel: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": self.get_available_kernels()},
            "handler": self.cmd_select_kernel,
            "value": self.get_kernel(),
        }
        self.kernel_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.kernel_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "text": "Auto-start Server",
            "layout": "horizontal",
            "handler": self.cmd_toggle_autostart,
            "value": self.get_config_autostart_server(),
        }
        self.autostart_checkbox = NchantdCheckboxWidget(self, cfg)
        items[cnt]["widget"] = self.autostart_checkbox
        cnt += 1
        return items

    def init_drawer_selection_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "Server Status: ", "layout": "horizontal"}
        self.server_status_label = NchantdLabel(self, cfg)
        items[cnt]["widget"] = self.server_status_label
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "Kernel Status: ", "layout": "horizontal"}
        self.kernel_status_label = NchantdLabel(self, cfg)
        items[cnt]["widget"] = self.kernel_status_label
        cnt += 1
        return items

    def init_drawer_object_config(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Cell Type: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": ["Code", "Markdown", "Raw"]},
            "handler": self.cmd_cell_type_change,
            "value": self.get_cell_type(),
        }
        self.cell_type_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.cell_type_select
        cnt += 1

        return items

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "Quick Start Guide", "layout": "horizontal"}
        quickstart_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = quickstart_label
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "1. Click 'Start Server' to launch Jupyter", "layout": "horizontal"}
        step1_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = step1_label
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "2. Click 'New Notebook' to create a notebook", "layout": "horizontal"}
        step2_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = step2_label
        cnt += 1

        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {"text": "3. Or 'Open Local' to load existing .ipynb file", "layout": "horizontal"}
        step3_label = NchantdLabel(self, cfg).initWidget()
        items[cnt]["widget"] = step3_label
        cnt += 1

        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        # PUSH to 0.0.3
        # self.toolbox_config[200]["items"] = self.init_drawer_selection_config()
        # self.toolbox_config[300]["items"] = self.init_drawer_object_config()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def interrupt_kernel(self):
        """Interrupt the running kernel (like Ctrl+C)"""
        try:
            if self.kernel_manager and self.kernel_running:
                self.kernel_manager.interrupt_kernel()
                logma.info("Kernel interrupted")
            else:
                logma.warning("No running kernel to interrupt")
        except Exception as e:
            logma.error(f"Error interrupting kernel: {e}")
        return self

    def is_server_running(self):
        """Check if a TCP listener is accepting connections on the server port.

        Note: this only confirms *something* is bound to the port, not that it is
        our Jupyter instance. The output pump logs the authoritative URL Jupyter
        reports so the two can be cross-checked.
        """
        import socket

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", self.server_port))
            sock.close()
            reachable = result == 0
            logma.debug(
                f"[notebook] is_server_running: localhost:{self.server_port} "
                f"connect_ex={result} -> reachable={reachable}"
            )
            return reachable
        except Exception as e:
            logma.error(f"[notebook] is_server_running check failed: {e}")
            return False

    def load_notebook_file(self, file_path):
        """Load a notebook file"""
        try:
            if not exists(file_path):
                logma.error(f"Notebook file not found: {file_path}")
                return self

            self.file_path = file_path
            self.current_notebook_path = file_path

            # If server is running, open the notebook
            if self.server_running and self.browser:
                from os.path import basename

                notebook_url = f"{self.server_url}/notebooks/{basename(file_path)}"
                logma.info(f"[notebook] loading notebook at exact url={notebook_url} (file={file_path})")
                self._navigate_browser(notebook_url)
                logma.info(f"Loaded notebook: {file_path}")
            else:
                logma.warning("Jupyter server not running. Start server to view notebook.")

        except Exception as e:
            logma.error(f"Error loading notebook file: {e}", exc_info=True)

        return self

    # ========== Server Management Methods ==========

    def open_file(self, file=None):
        """"""
        logma.info(file)
        try:
            self.set_file_path(file)
            if file is not None:
                self.document.open_file(file)
        except Exception as e:
            logma.warning(e)
            if debug:
                raise e
        self.document.set_location("external")
        self.populate_document()
        return self

    def pin_page(self):
        """"""
        if self.pinned is False:
            self.pinned = True
        else:
            self.pinned = False
        self.document.set_pinned(self.pinned)
        return self

    def populate_document(self):
        """"""
        self.browser.load_page(self.file_path)
        return self

    def restart_kernel(self):
        """Restart the notebook kernel"""
        try:
            if self.kernel_manager:
                logma.info("Restarting kernel...")
                self.stop_kernel()
                import time

                time.sleep(1)
                self.start_kernel()
                logma.info("Kernel restarted successfully")
            else:
                logma.warning("No kernel manager found")
        except Exception as e:
            logma.error(f"Error restarting kernel: {e}")
        return self

    def save(self):
        """Save the notebook, persisting it to both the file path AND the internal DB.

        T-076: previously only delegated to super().save(). Now:

          1. Serializes the notebook via get_binary() (the
             existing implementation already produces .ipynb JSON)
          2. Stores the serialized bytes on the document at
             ``document.content['notebook_bytes']``
          3. Calls super().save() to persist the document
          4. Persists to the ``ds_document_internal_state`` DB
             table (when the store is reachable) so the
             notebook can be re-loaded internally without an
             external file.

        Returns ``self``.
        """
        try:
            serialized = self.get_binary() if hasattr(self, "get_binary") else None
            if serialized is not None:
                if hasattr(self, "document") and self.document is not None:
                    try:
                        if not isinstance(self.document.content, dict):
                            self.document.content = {"content": self.document.content}
                        self.document.content["notebook_bytes"] = serialized
                    except Exception as e:
                        logma.error(f"[notebook] save: content write failed: {e}", exc_info=True)
                try:
                    store = getattr(self.app.model, "store", None) if hasattr(self, "app") else None
                    if store is not None and hasattr(store, "execute"):
                        try:
                            did = getattr(self.document, "did", None)
                            if did is not None:
                                import json as _json
                                store.execute(
                                    "INSERT OR REPLACE INTO ds_document_internal_state (did, payload, updated_at) VALUES (?, ?, ?)",
                                    (did, _json.dumps({
                                        "notebook_bytes": serialized.decode("utf-8", errors="replace")
                                        if isinstance(serialized, (bytes, bytearray))
                                        else str(serialized),
                                    }), __import__("datetime").datetime.utcnow().isoformat()),
                                )
                        except Exception:
                            # Table may not exist yet - silently ignore
                            pass
                except Exception as e:
                    logma.error(f"[notebook] save: store write failed: {e}", exc_info=True)
        except Exception as e:
            logma.error(f"[notebook] save failed: {e}", exc_info=True)
        super().save()
        return self

    def load_internal(self):
        """T-076: load the notebook state from the internal DB.

        Reads ``ds_document_internal_state`` for the current
        document's did, decodes the ``notebook_bytes`` field,
        and feeds it back into the editor via setPlainText.
        Returns ``True`` on success, ``False`` when no state
        is found.
        """
        try:
            if not hasattr(self, "document") or self.document is None:
                return False
            did = getattr(self.document, "did", None)
            if did is None:
                return False
            store = getattr(self.app.model, "store", None) if hasattr(self, "app") else None
            if store is None or not hasattr(store, "execute"):
                return False
            try:
                cursor = store.execute(
                    "SELECT payload FROM ds_document_internal_state WHERE did = ?", (did,),
                )
            except Exception:
                return False
            payload_text = None
            try:
                rows = cursor.fetchall() if cursor is not None else []
                if not rows:
                    return False
                payload_text = rows[0][0]
            except Exception:
                return False
            if not payload_text:
                return False
            import json as _json
            payload = _json.loads(payload_text)
            notebook_bytes = payload.get("notebook_bytes")
            if not notebook_bytes:
                return False
            editor = (
                getattr(self, "document_editor", None)
                or getattr(self, "editor", None)
            )
            if editor is None:
                return False
            if hasattr(editor, "setPlainText"):
                editor.setPlainText(notebook_bytes)
            elif hasattr(editor, "set_text"):
                editor.set_text(notebook_bytes)
            logma.info(f"[notebook] load_internal: restored state for did={did}")
            return True
        except Exception as e:
            logma.error(f"[notebook] load_internal failed: {e}", exc_info=True)
            return False

    def save_notebook(self, file_path=None):
        """Save the current notebook"""
        # Note: Jupyter handles saving internally through the web interface
        # This method is mainly for setting the file path
        if file_path:
            self.file_path = file_path
            logma.info(f"Notebook file path set to: {file_path}")
        return self

    def set_notebook(self, notebook=None):
        """Initialize or set the notebook structure.

        Args:
            notebook: Dict with notebook structure; defaults to {'cells': []}
        """
        if notebook is None:
            notebook = {"cells": []}
        if notebook != self.notebook:
            self.notebook = notebook
            logma.info("Notebook structure updated")
        return self

    def set_cells(self, cells):
        """Set the cells list.

        Args:
            cells: List of cell dicts (each with 'cell_type', 'source', optional 'outputs')
        """
        if cells != self.cells:
            self.cells = cells
            count = len(cells) if cells else 0
            logma.info(f"Cells updated: {count} cells")
        return self

    def set_cell_source(self, text, position=0):
        """Set source code for a cell at given position.

        Args:
            text: Source code string to assign
            position: Zero-based cell index (default: 0)
        """
        if self.cells is None or not (0 <= position < len(self.cells)):
            logma.error(f"Invalid cell position: {position}")
            return self
        self.cells[position]["source"] = text
        logma.info(f"Cell {position} source updated")
        return self

    def shutdown(self):
        """Shutdown the notebook and clean up"""
        self.stop_kernel()
        self.stop_jupyter_server()
        return self

    def start_jupyter_server(self, port=None):
        """Start the Jupyter notebook server"""
        import time

        if port is None:
            port = self.server_port

        # Keep server_url consistent with the port we are about to launch on so
        # every log line below references the exact URL the browser will load.
        self.server_url = f"http://localhost:{port}"
        logma.info(f"[notebook] start_jupyter_server requested | port={port} | target_url={self.server_url}")

        try:
            # Reuse the server ONLY if it's the one we started in this process.
            if self.jupyter_process is not None and self.is_server_running():
                logma.info(f"[notebook] reusing our Jupyter (pid={self.jupyter_process.pid}) at {self.server_url}")
                self.server_running = True
                self._navigate_browser(f"{self.server_url}/tree")
                self.update_status_labels()
                return self

            # A server is on our port but it isn't ours (leftover from a previous
            # run). It was started with whatever flags that run used, so it may
            # lack the WebSocket/origin flags the kernel connection needs. Replace
            # it so the flags below actually take effect.
            if self.is_server_running():
                logma.warning(
                    f"[notebook] port {port} held by a foreign/stale Jupyter; killing it so a fresh "
                    f"server with the required flags can start"
                )
                self._kill_port(port)
                import time

                for _ in range(20):
                    if not self.is_server_running():
                        break
                    time.sleep(0.25)
                if self.is_server_running():
                    logma.error(f"[notebook] could not free port {port}; proceeding may reuse the stale server")

            # Build command to start Jupyter.
            # IMPORTANT: token/password values must NOT be wrapped in quotes here.
            # subprocess.Popen with a list does not go through a shell, so
            # "--ServerApp.token=''" would set the token to the literal
            # two-character string "''" (auth stays ON -> Jupyter serves a login
            # page and the embedded browser shows a blank/permission screen).
            # An empty value after '=' correctly disables the token/password.
            #
            # allow_origin='*' + disable_check_xsrf make the kernel-channel
            # WebSocket handshake succeed from the embedded QtWebEngine origin
            # (Jupyter's tornado check_origin otherwise can reject the WS, causing
            # the kernel connection to drop and retry -> "running a cell fails").
            cmd = [
                "jupyter",
                "notebook",
                "--no-browser",
                f"--port={port}",
                "--IdentityProvider.token=",
                "--ServerApp.password=",
                "--ServerApp.disable_check_xsrf=True",
                "--ServerApp.allow_origin=*",
                "--ServerApp.allow_remote_access=True",
            ]

            # Start notebook in specific directory if file_path is set
            cwd = None
            if self.file_path and exists(dirname(self.file_path)):
                cwd = dirname(self.file_path)

            logma.info(
                f"[notebook] launching Jupyter | argv={cmd} | " f"cmdline={' '.join(cmd)} | cwd={cwd or os.getcwd()}"
            )

            # Start the subprocess. Merge stderr into stdout and decode as text so
            # the output pump can surface Jupyter's own "serving at ..." banner.
            popen_kwargs = dict(
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                text=True,
                bufsize=1,
            )
            # Die-with-parent so a crash/kill of the app doesn't leave the server
            # orphaned (the stale-server problem).
            if os.name == "posix":
                popen_kwargs["preexec_fn"] = _preexec_die_with_parent
            self.jupyter_process = subprocess.Popen(cmd, **popen_kwargs)
            logma.info(f"[notebook] Jupyter subprocess spawned | pid={self.jupyter_process.pid}")

            # Ensure the server is shut down when the app quits (aboutToQuit +
            # atexit), in addition to the die-with-parent signal above.
            self._setup_shutdown_hooks()

            # Pump the subprocess output into the log so we can VERIFY the exact
            # URL (host, port and token) Jupyter reports it is serving from.
            self._start_output_pump(self.jupyter_process)

            # Poll for the port to come up instead of a blind fixed sleep. Jupyter
            # can take several seconds to bind, and navigating too early yields a
            # connection-refused / blank page.
            ready = False
            max_checks = 40  # ~20s ceiling at 0.5s per check
            for attempt in range(1, max_checks + 1):
                # Bail out immediately if the process died during startup.
                if self.jupyter_process.poll() is not None:
                    logma.error(
                        f"[notebook] Jupyter process exited during startup | "
                        f"returncode={self.jupyter_process.returncode} "
                        f"(see pumped [jupyter] output above for the reason)"
                    )
                    break
                if self.is_server_running():
                    ready = True
                    logma.info(
                        f"[notebook] port {port} accepting connections after "
                        f"{attempt} check(s) (~{attempt * 0.5:.1f}s)"
                    )
                    break
                time.sleep(0.5)

            if not ready:
                logma.error(
                    f"[notebook] Jupyter server never became reachable on {self.server_url}; "
                    f"browser will NOT be navigated"
                )
                self.server_running = False
                self.update_status_labels()
                return self

            self.server_running = True
            self.server_url = f"http://localhost:{port}"
            landing_url = f"{self.server_url}/tree"
            logma.info(f"[notebook] Jupyter server READY | server_url={self.server_url} | landing_url={landing_url}")

            # Navigate to the tree landing page Jupyter reports it is serving.
            self._navigate_browser(landing_url)
            self.update_status_labels()

        except Exception as e:
            logma.error(f"[notebook] Error starting Jupyter server: {e}", exc_info=True)
            self.server_running = False
            self.update_status_labels()

        return self

    def stop_jupyter_server(self):
        """Stop the Jupyter notebook server"""
        try:
            if self.jupyter_process:
                self.jupyter_process.terminate()
                try:
                    self.jupyter_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.jupyter_process.kill()
                    self.jupyter_process.wait()

                self.jupyter_process = None
                self.server_running = False
                logma.info("Jupyter server stopped")
            else:
                logma.info("No Jupyter server process to stop")
        except Exception as e:
            logma.error(f"Error stopping Jupyter server: {e}")

        return self

    def start_kernel(self, kernel_name=None):
        """Start a Jupyter kernel for code execution

        Args:
            kernel_name: Name of kernel to start (e.g., 'python3', 'ir', 'julia')
        """
        try:

            if kernel_name is None:
                kernel_name = self.kernel_name

            logma.info(f"Starting kernel: {kernel_name}")

            # Create kernel manager
            self.kernel_manager = KernelManager(kernel_name=kernel_name)
            self.kernel_manager.start_kernel()

            # Create kernel client
            self.kernel_client = self.kernel_manager.client()
            self.kernel_client.start_channels()

            # Wait for kernel to be ready
            import time

            time.sleep(2)

            # Check if kernel is alive
            if self.kernel_client.is_alive():
                self.kernel_running = True
                self.kernel_name = kernel_name
                logma.info(f"Kernel {kernel_name} started successfully")
                self.update_status_labels()
            else:
                logma.error("Kernel failed to start")
                self.kernel_running = False

        except Exception as e:
            logma.error(f"Error starting kernel: {e}")
            self.kernel_running = False

        return self

    def stop_kernel(self):
        """Stop the running kernel"""
        try:
            if self.kernel_client:
                self.kernel_client.stop_channels()
                self.kernel_client = None

            if self.kernel_manager:
                self.kernel_manager.shutdown_kernel()
                self.kernel_manager = None

            self.kernel_running = False
            logma.info("Kernel stopped")
            self.update_status_labels()

        except Exception as e:
            logma.error(f"Error stopping kernel: {e}")

        return self

    def to_dict(self):
        """Serialize notebook state to dict.

        Returns:
            Dict containing document metadata, notebook structure, and all cells.
        """
        doc = {}
        try:
            doc = super().to_dict()
        except Exception:
            pass
        doc["document"] = {"notebook": self.notebook or {"cells": []}}
        cells_list = self.cells if self.cells else []
        doc["document"]["notebook"]["cells"] = cells_list
        return doc

    def to_html(self):
        """Render notebook to basic HTML (fixed from infinite-recursion bug in pyffice).

        Returns:
            HTML string with all cells and their outputs.
        """
        if not self.cells:
            return "<html><body><p>Empty notebook</p></body></html>"

        html_parts = ["<html><body>"]
        for idx, cell in enumerate(self.cells):
            cell_type = cell.get("cell_type", "code")
            source = cell.get("source", "")
            html_parts.append(f"<div class='cell' id='cell-{idx}'>")
            html_parts.append(f"<div class='cell-type'>{cell_type}</div>")
            html_parts.append(f"<pre class='source'>{source}</pre>")
            if cell.get("outputs"):
                html_parts.append("<div class='outputs'>")
                for output in cell["outputs"]:
                    if isinstance(output, dict) and "text" in output:
                        html_parts.append(f"<pre class='output'>{output['text']}</pre>")
                html_parts.append("</div>")
            html_parts.append("</div>")
        html_parts.append("</body></html>")
        return "\n".join(html_parts)

    def update_status_labels(self):
        """Update server and kernel status labels"""
        if hasattr(self, "server_status_label"):
            status = "Running" if self.server_running else "Stopped"
            self.server_status_label.setText(f"Server Status: {status}")

        if hasattr(self, "kernel_status_label"):
            if self.kernel_running:
                kernel_status = f"Running ({self.kernel_name})"
            else:
                kernel_status = "Stopped"
            self.kernel_status_label.setText(f"Kernel Status: {kernel_status}")

        return self

    def _kill_port(self, port):
        """Best-effort kill of whatever process is listening on ``port``.

        Used to clear a stale Jupyter left by a previous run so a fresh server
        with the current flags can bind. Tries fuser, then lsof.
        """
        import subprocess

        for cmd in (["fuser", "-k", f"{port}/tcp"], ["bash", "-lc", f"lsof -ti tcp:{port} | xargs -r kill -9"]):
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                logma.info(f"[notebook] _kill_port {port} via {cmd[0]} rc={r.returncode} out={r.stdout.strip()!r}")
                if r.returncode == 0:
                    return self
            except Exception as e:
                logma.warning(f"[notebook] _kill_port {port} via {cmd[0]} failed: {e}")
        return self

    def _start_output_pump(self, process):
        """Stream a Jupyter subprocess's merged stdout/stderr into the log.

        Jupyter prints the exact URL it is serving (host, port, token) plus any
        startup errors to this stream. Reading it lets us verify the browser is
        being pointed at the same URL Jupyter actually bound to.
        """

        def _pump():
            try:
                for line in iter(process.stdout.readline, ""):
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    logma.info(f"[jupyter:pid{process.pid}] {line}")
                    # Surface the authoritative URL Jupyter reports.
                    low = line.lower()
                    if "http://" in low or "https://" in low:
                        logma.info(f"[notebook] Jupyter-reported URL line: {line.strip()}")
            except Exception as e:
                logma.error(f"[notebook] output pump error: {e}")
            finally:
                try:
                    process.stdout.close()
                except Exception:
                    pass

        thread = threading.Thread(target=_pump, name=f"jupyter-log-pump-{process.pid}", daemon=True)
        thread.start()
        logma.info(f"[notebook] output pump started for pid={process.pid}")
        return thread

    def _wire_browser_load_logging(self):
        """Attach Qt load-signal logging to the embedded QWebEngineView.

        Reports whether QtWebEngine actually starts and finishes loading the
        Jupyter URL (loadFinished carries an ``ok`` flag), which distinguishes a
        failed/refused load from a page that loaded but rendered blank.
        """
        try:
            view = getattr(self.browser, "browser", None)
            if view is None:
                logma.error("[notebook] cannot wire load logging: no underlying web view")
                return self
            # Log the page's profile/storage configuration once. JupyterLab keeps
            # its settings state in localStorage and its shared document (ydoc)
            # state in IndexedDB; if the profile is off-the-record or has no
            # persistent storage path / disabled web storage, the settings
            # registry fails ("reading 'schema'") and the ydoc layer breaks
            # ("Not same Y.Doc"). This pins down whether storage is the cause.
            try:
                page = view.page()
                prof = page.profile() if page is not None else None
                if prof is not None:
                    settings = page.settings()
                    WA = pyqt.QWebEngineSettings.WebAttribute
                    logma.info(
                        "[notebook] page profile | "
                        f"offTheRecord={prof.isOffTheRecord()} | "
                        f"persistentStoragePath={prof.persistentStoragePath()!r} | "
                        f"cachePath={prof.cachePath()!r} | "
                        f"httpCacheType={prof.httpCacheType()} | "
                        f"cookiesPolicy={prof.persistentCookiesPolicy()}"
                    )
                    logma.info(
                        "[notebook] page web-attrs | "
                        f"LocalStorageEnabled={settings.testAttribute(WA.LocalStorageEnabled)} | "
                        f"JavascriptEnabled={settings.testAttribute(WA.JavascriptEnabled)} | "
                        f"LocalContentCanAccessRemoteUrls={settings.testAttribute(WA.LocalContentCanAccessRemoteUrls)}"
                    )
                else:
                    logma.error("[notebook] page profile | no page/profile available to inspect")
            except Exception as e:
                logma.error(f"[notebook] could not log page profile/storage config: {e}", exc_info=True)
            view.loadStarted.connect(self._on_webview_load_started)
            view.loadProgress.connect(self._on_webview_load_progress)

            def _on_url_changed(url):
                # Keep the self-heal target in sync with user-initiated navigation
                # (e.g. double-clicking a .ipynb in the tree -> /notebooks/<name>),
                # so a later stray blank load doesn't yank us back to /tree.
                cur = url.toString() if hasattr(url, "toString") else str(url)
                if cur and cur.startswith(self.server_url):
                    if cur != self._target_url:
                        logma.info(f"[notebook] user navigation -> tracking target={cur}")
                        self._target_url = cur
                        self._nav_retries = 0

            view.urlChanged.connect(_on_url_changed)

            def _fmt_size(w):
                try:
                    s = w.size()
                    return f"{s.width()}x{s.height()} visible={w.isVisible()}"
                except Exception:
                    return "?"

            def _on_load_finished(ok):
                cur = view.url().toString()
                logma.info(f"[notebook] webview loadFinished ok={ok} | current_url={cur} | target={self._target_url}")
                # Geometry check: distinguishes a size-collapse (fill/size-policy
                # problem -> view is ~0 px) from a paint problem (view has real
                # size but shows nothing -> GPU/compositor issue).
                logma.info(
                    f"[notebook] geometry | webview={_fmt_size(view)} | "
                    f"viewer={_fmt_size(self.browser)} | document={_fmt_size(self)}"
                )
                # Self-heal the about:blank clobber race: if the load settled on a
                # blank page but we actually wanted the Jupyter URL, navigate again
                # now that the view has a real surface (bounded retries prevent loops).
                if (
                    self._target_url
                    and cur in ("about:blank", "")
                    and self._target_url not in ("about:blank", "")
                    and self._nav_retries < 3
                ):
                    self._nav_retries += 1
                    logma.info(
                        f"[notebook] load settled on '{cur}' but target is {self._target_url}; "
                        f"re-navigating (retry {self._nav_retries}/3)"
                    )
                    QTimer.singleShot(200, self._retry_navigate_target)

            view.loadFinished.connect(_on_load_finished)
            # Install fetch/WebSocket instrumentation ONCE, at document creation,
            # so it wraps window.fetch/WebSocket before JupyterLab captures them.
            self._install_net_instrumentation(view)
            # Capture uncaught errors + unhandled promise rejections with full
            # stack traces. QtWebEngine reports these as bare "Uncaught (in
            # promise) TypeError: ..." lines with no source/stack; this surfaces
            # the exact module + line so the JupyterLab open regression (e.g.
            # "reading 'insertWidget'"/"reading 'schema'") can be pinpointed.
            self._install_error_instrumentation(view)
            logma.info("[notebook] browser load logging wired")
        except Exception as e:
            logma.error(f"[notebook] failed to wire browser load logging: {e}", exc_info=True)
        return self

    def _install_net_instrumentation(self, view):
        """Wrap window.fetch / window.WebSocket to log failures.

        Installed as a persistent QWebEngineScript at DocumentCreation (before
        page scripts run) so the wrappers are in place BEFORE JupyterLab captures
        references to fetch/WebSocket — a loadFinished runJavaScript runs too late
        and sees nothing.

        Surfaces (via the JS console -> `js:` log lines):
          [netfetch-ERR] <url> :: <reason>   -- a fetch() that threw
          [netfetch] <status> <url>          -- a non-2xx HTTP response
          [netws-open] <url>                 -- a WebSocket was opened
          [netws-close] <url> code=.. reason=.. clean=..  -- WS closed (kernel!)
          [netws-ERR] <url>                  -- WS error
        """
        if getattr(self, "_net_instrumented", False):
            return self
        js = r"""
        (function(){
          if (window.__nchantd_net_wrap) return;
          window.__nchantd_net_wrap = true;
          try {
            var of = window.fetch;
            window.fetch = function(){
              var args = arguments;
              var u = (args[0] && args[0].url) ? args[0].url : String(args[0]);
              return of.apply(this, args).then(function(r){
                if(!r.ok){ console.log('[netfetch] '+r.status+' '+r.url); }
                return r;
              }).catch(function(e){ console.log('[netfetch-ERR] '+u+' :: '+e); throw e; });
            };
            var OWS = window.WebSocket;
            var NWS = function(url, protocols){
              var ws = (protocols !== undefined) ? new OWS(url, protocols) : new OWS(url);
              console.log('[netws-open] '+url);
              ws.addEventListener('error', function(){ console.log('[netws-ERR] '+url); });
              ws.addEventListener('close', function(ev){
                console.log('[netws-close] '+url+' code='+ev.code+' reason='+(ev.reason||'')+' clean='+ev.wasClean);
              });
              return ws;
            };
            NWS.prototype = OWS.prototype;
            NWS.CONNECTING = OWS.CONNECTING; NWS.OPEN = OWS.OPEN;
            NWS.CLOSING = OWS.CLOSING; NWS.CLOSED = OWS.CLOSED;
            window.WebSocket = NWS;
            console.log('[net] instrumentation installed (DocumentCreation)');
          } catch (e) { console.log('[net] instrumentation failed: '+e); }
        })();
        """
        try:
            script = pyqt.QWebEngineScript()
            script.setName("nchantd_net_instrumentation")
            script.setSourceCode(js)
            script.setInjectionPoint(pyqt.QWebEngineScript.DocumentCreation)
            script.setWorldId(pyqt.QWebEngineScript.MainWorld)
            script.setRunsOnSubFrames(True)
            page = view.page()
            if page is not None:
                page.scripts().insert(script)
                self._net_instrumented = True
                logma.info("[notebook] net instrumentation installed at DocumentCreation")
        except Exception as e:
            logma.error(f"[notebook] could not install net instrumentation: {e}", exc_info=True)
        return self

    def _install_error_instrumentation(self, view):
        """Capture uncaught JS errors and unhandled promise rejections.

        Installed as a persistent QWebEngineScript at DocumentCreation (before
        JupyterLab bootstraps) so the global handlers are registered first.

        QtWebEngine's default console output collapses these to opaque lines
        like ``Uncaught (in promise) TypeError: Cannot read properties of null
        (reading 'insertWidget')`` with no source file, line, or stack. These
        handlers re-emit each failure via console.error with the message, the
        originating ``source:line:col``, and the full ``.stack`` so the exact
        JupyterLab module/function can be identified from the logs.

        Surfaces (via the JS console -> logged with [JS/Error] provenance):
          [jserr] <message> @ <source>:<line>:<col>
              <stack>
          [jsrejection] <reason>
              <stack>
        """
        if getattr(self, "_error_instrumented", False):
            return self
        js = r"""
        (function(){
          if (window.__nchantd_err_wrap) return;
          window.__nchantd_err_wrap = true;
          try {
            window.addEventListener('error', function(ev){
              try {
                var e = ev.error;
                var where = (ev.filename||'?')+':'+(ev.lineno||0)+':'+(ev.colno||0);
                var stack = (e && e.stack) ? ('\n'+e.stack) : '';
                console.error('[jserr] '+(ev.message||(e&&e.message)||e||'unknown')+' @ '+where+stack);
              } catch (x) { console.error('[jserr] (handler failed) '+x); }
            }, true);
            window.addEventListener('unhandledrejection', function(ev){
              try {
                var r = ev.reason;
                var msg = (r && (r.message!==undefined)) ? r.message : String(r);
                var stack = (r && r.stack) ? ('\n'+r.stack) : '';
                console.error('[jsrejection] '+msg+stack);
              } catch (x) { console.error('[jsrejection] (handler failed) '+x); }
            });
            console.log('[jserr] error instrumentation installed (DocumentCreation)');
          } catch (e) { console.log('[jserr] instrumentation failed: '+e); }
          // Probe the storage JupyterLab depends on (localStorage for the
          // settings registry, IndexedDB for the ydoc shared model). A failure
          // here directly explains "reading 'schema'" and "Not same Y.Doc".
          try {
            var ls = 'unknown';
            try { window.localStorage.setItem('__nchantd_probe','1'); window.localStorage.removeItem('__nchantd_probe'); ls='ok'; }
            catch (e) { ls='FAIL: '+e; }
            var idb = (typeof window.indexedDB !== 'undefined' && window.indexedDB) ? 'present' : 'MISSING';
            console.log('[storage] localStorage='+ls+' indexedDB='+idb
              +' secureContext='+window.isSecureContext
              +' cookieEnabled='+navigator.cookieEnabled);
          } catch (e) { console.log('[storage] probe failed: '+e); }
        })();
        """
        try:
            script = pyqt.QWebEngineScript()
            script.setName("nchantd_error_instrumentation")
            script.setSourceCode(js)
            script.setInjectionPoint(pyqt.QWebEngineScript.DocumentCreation)
            script.setWorldId(pyqt.QWebEngineScript.MainWorld)
            script.setRunsOnSubFrames(True)
            page = view.page()
            if page is not None:
                page.scripts().insert(script)
                self._error_instrumented = True
                logma.info("[notebook] error instrumentation installed at DocumentCreation")
        except Exception as e:
            logma.error(f"[notebook] could not install error instrumentation: {e}", exc_info=True)
        return self

    def _navigate_browser(self, url):
        """Point the embedded web viewer at ``url``.

        NchantdWebViewer exposes navigation via ``goto_page`` (there is no
        ``load_url`` method); calling the wrong name previously raised an
        AttributeError that was swallowed, leaving the notebook blank.
        """
        if not self.browser:
            logma.error(f"[notebook] cannot navigate: no browser widget (url={url})")
            return self
        # Reset the self-heal retry budget whenever a genuinely new destination is
        # requested (e.g. opening a specific notebook after landing on /tree).
        if url != self._target_url:
            self._nav_retries = 0
        self._target_url = url
        logma.info(f"[notebook] navigating embedded browser -> {url}")
        try:
            self.browser.goto_page(url)
            logma.info(f"[notebook] browser.goto_page issued for {url}")
        except Exception as e:
            logma.error(f"[notebook] browser navigation failed for {url}: {e}", exc_info=True)
        return self

    def _setup_shutdown_hooks(self):
        """Guarantee the Jupyter server is stopped when the app exits.

        Registers, once: QApplication.aboutToQuit (clean Qt quit) and an atexit
        handler (interpreter teardown). Combined with the die-with-parent signal
        set on the subprocess, this covers clean quit, exceptions, and crashes so
        no orphaned server is left holding the port.
        """
        if getattr(self, "_shutdown_hooks_installed", False):
            return self
        self._shutdown_hooks_installed = True
        try:
            app = pyqt.QApplication.instance()
            if app is not None:
                app.aboutToQuit.connect(self.shutdown)
                logma.info("[notebook] shutdown hook wired to QApplication.aboutToQuit")
        except Exception as e:
            logma.error(f"[notebook] could not wire aboutToQuit shutdown hook: {e}")
        try:
            import atexit

            atexit.register(self.stop_jupyter_server)
            logma.info("[notebook] atexit shutdown hook registered")
        except Exception as e:
            logma.error(f"[notebook] could not register atexit shutdown hook: {e}")
        return self


# ====================================================================================================================||
"""
    # nb = nbformat.read("notebook.ipynb", as_version=4)
    # client = NotebookClient(nb, timeout=600, kernel_name="python3")
    #
    # client.execute()  # Runs all cells
    # nbformat.write(nb, "executed.ipynb")  # Save with outputs
"""
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
